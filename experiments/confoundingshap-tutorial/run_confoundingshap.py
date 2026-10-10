"""Run ConfoundingSHAP on the tutorial data and compare with the exact answer key.

    python run_confoundingshap.py                                  # data/toy_confounded.csv, exact key + plug-in estimate
    python run_confoundingshap.py --data data/toy_randomized.csv   # the randomized variant: every credit is zero
    python run_confoundingshap.py --tabpfn --device cuda           # add the paper's TabPFN estimator (shapiq's released game)
    python run_confoundingshap.py --tabpfn --device cpu --n-rows 1500   # slower; fewer rows keeps CPU inference short

Three columns come out for each covariate:
  exact     the Shapley credit of the signed global game computed from the generating model (no data)
  plug-in   the same game estimated from the CSV with saturated cell means (every covariate is binary)
  tabpfn    optional: shapiq 1.7.0's GlobalConfoundingXAI with a TabPFN S-learner, the paper's estimator
The credits in every column sum to the crude-minus-adjusted gap of that column. Results go to outputs/.
No environment variables are read; two TabPFN settings (no browser, no telemetry) are set if absent.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from confounding_game import COVARIATES, OUTCOME, ROLES, TREATMENT, estimate_from_sample, exact_credits, masks

HERE = Path(__file__).resolve().parent
COALITIONS = ["{}", "{C}", "{Z}", "{C,Z}", "{P}", "{C,P}", "{Z,P}", "{C,Z,P}"]


def tabpfn_credits(df: pd.DataFrame, device: str, model_version: str, n_estimators: int, seed: int) -> dict:
    """The paper's estimator: shapiq's GlobalConfoundingXAI (signed mode) with a TabPFN S-learner per coalition.

    tau_hat is the fully adjusted S-learner contrast m(x, 1) - m(x, 0), as in the released benchmark.
    The model version is selected explicitly (the paper used 2.5; tabpfn 9.x defaults to 3.5); if the
    installed tabpfn cannot select a version, the default model is used and the note says so.
    """
    os.environ.setdefault("TABPFN_NO_BROWSER", "1")
    os.environ.setdefault("TABPFN_DISABLE_TELEMETRY", "1")
    if device == "cpu":
        # TabPFN refuses more than 1,000 rows on CPU unless told otherwise; --n-rows keeps runs short.
        os.environ.setdefault("TABPFN_ALLOW_CPU_LARGE_DATASET", "1")
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    import torch
    from shapiq import ExactComputer
    from shapiq_games.benchmark.causal_xai import base as upstream
    from tabpfn import TabPFNRegressor

    note = f"TabPFN model {model_version}"
    factory = None
    try:
        from tabpfn.constants import ModelVersion
        version = ModelVersion(model_version)

        def factory(device: str, n_estimators: int = 1):  # noqa: E306
            return TabPFNRegressor.create_default_for_version(
                version, device=device, n_estimators=n_estimators, n_jobs=1, random_state=seed,
                inference_precision=torch.float32, inference_config=upstream._TABPFN_INFERENCE_CONFIG)
    except Exception as exc:  # version selection unavailable in this tabpfn
        note = f"installed tabpfn could not select model {model_version} ({exc.__class__.__name__}); its default model was used"
    original = upstream._make_tabpfn
    if factory is not None:
        upstream._make_tabpfn = factory
    try:
        X = df[COVARIATES].to_numpy(dtype=float)
        A = df[TREATMENT].to_numpy(dtype=float)
        Y = df[OUTCOME].to_numpy(dtype=float)
        m1, m0 = upstream._fit_s_learner(X, A, Y, device=device, n_estimators=n_estimators)
        tau_hat = m1(X) - m0(X)
        game = upstream.GlobalConfoundingXAI(X, A, Y, tau_hat, mode="signed", device=device, n_estimators=n_estimators)
        values = np.asarray(game(masks(3)), dtype=float)
        sv = ExactComputer(n_players=3, game=game)(index="SV", order=1)
        credits = np.array([sv[(j,)] for j in range(3)])
    finally:
        upstream._make_tabpfn = original
    crude = float(Y[A == 1].mean() - Y[A == 0].mean())
    adjusted = float(tau_hat.mean())
    return dict(credits=dict(zip(COVARIATES, credits.tolist())), game=values.tolist(), crude=crude,
                adjusted_ate=adjusted, crude_minus_adjusted=crude - adjusted, note=note, device=device,
                n_estimators=n_estimators, seed=seed, torch=torch.__version__)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=str(HERE / "data" / "toy_confounded.csv"))
    ap.add_argument("--tabpfn", action="store_true", help="also run shapiq's released GlobalConfoundingXAI with TabPFN")
    ap.add_argument("--device", default="cpu", help="cpu or cuda, for --tabpfn")
    ap.add_argument("--model-version", default="v2.5", help="TabPFN model version for --tabpfn (the paper used v2.5)")
    ap.add_argument("--n-estimators", type=int, default=1)
    ap.add_argument("--n-rows", type=int, default=None, help="use the first N rows (keeps CPU TabPFN runs short)")
    ap.add_argument("--seed", type=int, default=20261008)
    args = ap.parse_args()

    data = Path(args.data)
    df = pd.read_csv(data)
    if args.n_rows:
        df = df.head(args.n_rows)
    truth_path = data.with_name(data.stem + "_truth.json")
    randomized = json.loads(truth_path.read_text(encoding="utf-8"))["sample"]["randomized"] if truth_path.exists() else False

    exact = exact_credits(randomized)
    plug = estimate_from_sample(df)
    columns = {"exact": exact["credits"], "plug-in": plug["credits"]}
    totals = {"exact": exact["crude_minus_ate"], "plug-in": plug["crude_minus_adjusted"]}
    tab = None
    if args.tabpfn:
        tab = tabpfn_credits(df, args.device, args.model_version, args.n_estimators, args.seed)
        columns["tabpfn"] = tab["credits"]
        totals["tabpfn"] = tab["crude_minus_adjusted"]

    print(f"\nConfoundingSHAP on {data.name} ({len(df)} rows{', randomized treatment' if randomized else ''})")
    print(f"treatment {TREATMENT}, outcome {OUTCOME}, players {', '.join(COVARIATES)}; smallest (arm, cell) count in the data: {plug['min_cell']}\n")
    head = f"{'covariate':<10} {'role':<34}" + "".join(f"{k:>12}" for k in columns)
    print(head)
    for cov in COVARIATES:
        print(f"{cov:<10} {ROLES[cov]:<34}" + "".join(f"{columns[k][cov]:>12.5f}" for k in columns))
    print(f"{'sum':<10} {'= crude contrast - adjusted ATE':<34}" + "".join(f"{totals[k]:>12.5f}" for k in columns))
    print(f"{'':<10} {'crude contrast':<34}" + f"{exact['crude']:>12.5f}{plug['crude']:>12.5f}" + (f"{tab['crude']:>12.5f}" if tab else ""))
    print(f"{'':<10} {'adjusted ATE (true ATE for exact)':<34}" + f"{exact['ate']:>12.5f}{plug['adjusted_ate']:>12.5f}" + (f"{tab['adjusted_ate']:>12.5f}" if tab else ""))
    print("\ncoalition values v(S) = -(mean residual bias after adjusting for S):")
    print(f"{'S':<10}" + "".join(f"{k:>12}" for k in columns))
    games = {"exact": exact["game"], "plug-in": plug["game"]}
    if tab:
        games["tabpfn"] = tab["game"]
    for k, name in enumerate(COALITIONS):
        print(f"{name:<10}" + "".join(f"{games[c][k]:>12.5f}" for c in games))
    if tab:
        print(f"\nTabPFN: {tab['note']}; device {tab['device']}; torch {tab['torch']}; seed {tab['seed']}")
    print("\nReading: the exact credits are the answer key; plug-in differences are sampling error of the cell means;")
    print("TabPFN differences add the estimator's own error. Z's negative credit is bias amplification, not protection; P's zero credit is exact.")

    out = HERE / "outputs"
    out.mkdir(exist_ok=True)
    stem = data.stem + (f"_n{len(df)}" if args.n_rows else "") + ("_tabpfn" if tab else "")
    rows = [dict(covariate=c, role=ROLES[c], **{k: columns[k][c] for k in columns}) for c in COVARIATES]
    pd.DataFrame(rows).to_csv(out / f"{stem}_credits.csv", index=False)
    (out / f"{stem}_results.json").write_text(json.dumps(dict(data=data.name, n=int(len(df)), randomized=randomized,
                                                               exact=exact, plug_in=plug, tabpfn=tab), indent=1), encoding="utf-8")
    print(f"\nwrote outputs/{stem}_credits.csv and outputs/{stem}_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
