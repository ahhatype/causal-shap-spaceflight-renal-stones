"""What ConfoundingSHAP reports when a pretreatment collider is among the covariates.

The toy DAG with Z and P made latent and given a measured common effect K:

    C -> A, C -> Y, A -> Y        as in the toy
    U1 -> A                       latent, the toy's Z
    U2 -> Y                       latent, the toy's P
    U1 -> K <- U2                 K is measured, pretreatment, and a collider

Observed columns: C, K, A, Y. The valid adjustment set is {C}. Conditioning on K opens the path
A <- U1 -> K <- U2 -> Y (M-bias), so {C, K} is not a valid adjustment set. ConfoundingSHAP takes the full
observed set as its reference, so its "adjusted ATE" is the biased {C, K} contrast, its credits sum to the
gap between the crude contrast and that biased reference, and K receives a credit with the same sign as the
confounder's. Nothing in the output distinguishes the two.

    python collider_check.py              # exact game on the population, then the cell-mean plug-in on a sample
    python collider_check.py --n 40000    # a larger sample

Writes data/toy_collider.csv (columns C, K, A, Y) and data/toy_collider_truth.json. No environment
variables are read.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from confounding_game import estimate_from_sample, exact_shapley, masks, projection

HERE = Path(__file__).resolve().parent
K_BASE, K_SLOPE = 0.1, 0.4          # P(K = 1 | U1, U2) = K_BASE + K_SLOPE * (U1 + U2)
NAMES = ["C", "U1", "U2", "K"]      # state columns; U1 and U2 are latent


def collider_model() -> dict:
    """Population over (C, U1, U2, K): C, U1, U2 independent Bernoulli(1/2); K | U1, U2 as above;
    A | C, U1 ~ Bernoulli(0.1 + 0.3 C + 0.3 U1); E[Y | A = 0, C, U2] = C + 0.7 U2; tau = 0.5 for every unit."""
    states = masks(4).astype(int)
    c, u1, u2, k = states.T
    pk = K_BASE + K_SLOPE * (u1 + u2)
    weights = (1 / 8) * np.where(k == 1, pk, 1 - pk)
    propensity = 0.1 + 0.3 * c + 0.3 * u1
    mu0 = c + 0.7 * u2
    return dict(states=states, weights=weights, propensity=propensity, mu0=mu0, mu1=mu0 + 0.5)


def observational_game(obs: np.ndarray, weights: np.ndarray, propensity: np.ndarray,
                       mu0: np.ndarray, mu1: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[float]]:
    """The signed global game as the method computes it: the reference effect is the contrast given the full
    observed set, whether or not that set is a valid adjustment set. Rows of obs repeat where only latent
    variables differ; projection averages over them, which is what an analyst who cannot see them gets.
    Returns the game, the reference effect per state, and the adjust-for-S estimate of the ATE per coalition."""
    p = obs.shape[1]

    def delta(subset: np.ndarray) -> np.ndarray:
        e = projection(obs, weights, propensity, subset)
        return (projection(obs, weights, propensity * mu1, subset) / e
                - projection(obs, weights, (1 - propensity) * mu0, subset) / (1 - e))

    tau_ref = delta(np.ones(p, dtype=bool))
    deltas = [delta(s) for s in masks(p)]
    game = np.array([-float(weights @ (d - projection(obs, weights, tau_ref, s))) for d, s in zip(deltas, masks(p))])
    return game, tau_ref, [float(weights @ d) for d in deltas]


def coalition_name(subset: np.ndarray, names: list[str]) -> str:
    return "{" + ",".join(n for n, inside in zip(names, subset) if inside) + "}"


def exact(model: dict, players: list[int]) -> dict:
    names = [NAMES[j] for j in players]
    obs = model["states"][:, players]
    w = model["weights"]
    game, tau_ref, adjusted = observational_game(obs, w, model["propensity"], model["mu0"], model["mu1"])
    credits = exact_shapley(game)
    reference = float(w @ tau_ref)
    np.testing.assert_allclose(credits.sum(), adjusted[0] - reference, atol=1e-12)
    np.testing.assert_allclose(game[-1], 0.0, atol=1e-12)
    return dict(covariates=names, credits=dict(zip(names, credits.tolist())),
                game={coalition_name(s, names): float(v) for s, v in zip(masks(len(players)), game)},
                adjust_for={coalition_name(s, names): a for s, a in zip(masks(len(players)), adjusted)},
                crude=adjusted[0], reference_ate=reference, true_ate=float(w @ (model["mu1"] - model["mu0"])),
                crude_minus_reference=adjusted[0] - reference)


def generate(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    c, u1, u2 = (rng.integers(0, 2, n) for _ in range(3))
    k = (rng.random(n) < K_BASE + K_SLOPE * (u1 + u2)).astype(int)
    a = (rng.random(n) < 0.1 + 0.3 * c + 0.3 * u1).astype(int)
    y = c + 0.7 * u2 + 0.5 * a + rng.normal(0, 0.5, n)
    return pd.DataFrame(dict(C=c, K=k, A=a, Y=np.round(y, 6)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=20261008)
    args = ap.parse_args()

    model = collider_model()
    with_k = exact(model, [0, 3])          # X = {C, K}: what an analyst who measured K and passed it in gets
    without_k = exact(model, [0])          # X = {C}: the valid adjustment set
    df = generate(args.n, args.seed)
    plug_with = estimate_from_sample(df, covariates=["C", "K"])
    plug_without = estimate_from_sample(df, covariates=["C"])

    print("\nCollider check. DAG: C -> A, C -> Y, A -> Y; U1 -> A and U2 -> Y latent; U1 -> K <- U2 measured.")
    print(f"True ATE {with_k['true_ate']:.4f}; crude contrast {with_k['crude']:.4f}; sample n = {len(df)}, "
          f"smallest (arm, cell) count {plug_with['min_cell']}\n")
    cols = {"exact X={C,K}": (with_k["credits"], with_k["crude_minus_reference"], with_k["crude"], with_k["reference_ate"]),
            "exact X={C}": (without_k["credits"], without_k["crude_minus_reference"], without_k["crude"], without_k["reference_ate"]),
            "plug-in X={C,K}": (plug_with["credits"], plug_with["crude_minus_adjusted"], plug_with["crude"], plug_with["adjusted_ate"]),
            "plug-in X={C}": (plug_without["credits"], plug_without["crude_minus_adjusted"], plug_without["crude"], plug_without["adjusted_ate"])}
    print(f"{'':<34}" + "".join(f"{k:>18}" for k in cols))
    for cov, role in (("C", "confounder"), ("K", "collider")):
        print(f"{'credit ' + cov + ', ' + role:<34}"
              + "".join(f"{v[0][cov]:>18.5f}" if cov in v[0] else f"{'not in X':>18}" for v in cols.values()))
    print(f"{'sum = crude - reference':<34}" + "".join(f"{v[1]:>18.5f}" for v in cols.values()))
    print(f"{'crude contrast':<34}" + "".join(f"{v[2]:>18.5f}" for v in cols.values()))
    print(f"{'reference (the adjusted ATE)':<34}" + "".join(f"{v[3]:>18.5f}" for v in cols.values()))

    print("\nExact ATE estimate after adjusting for S only (X = {C, K}); the method treats the last row as the truth:")
    for s, est in with_k["adjust_for"].items():
        print(f"  adjust for {s:<8} {est:.5f}   v(S) = {with_k['game'][s]:+.5f}")

    print("\nReading: K is a pretreatment variable with no effect on A or Y, yet it earns a credit with the same sign as")
    print("the confounder's. The method's reference is the {C, K} contrast, biased by the path A <- U1 -> K <- U2 -> Y")
    print("that conditioning on K opens; the credits, the efficiency check and v(all) = 0 are all consistent with it.")
    print("Only the comparison with X = {C} shows the problem, and that comparison needs the DAG, not the credits.")

    out = HERE / "data"
    out.mkdir(exist_ok=True)
    df.to_csv(out / "toy_collider.csv", index=False)
    (out / "toy_collider_truth.json").write_text(json.dumps(dict(
        model=dict(C="Bernoulli(1/2)", U1="Bernoulli(1/2), latent", U2="Bernoulli(1/2), latent",
                   K=f"Bernoulli({K_BASE} + {K_SLOPE} * (U1 + U2))", A="Bernoulli(0.1 + 0.3 C + 0.3 U1)",
                   Y="C + 0.7 U2 + 0.5 A + Normal(0, 0.5^2)"),
        sample=dict(n=int(len(df)), seed=args.seed, columns=list(df.columns)),
        exact_with_K=with_k, exact_without_K=without_k, plug_in_with_K=plug_with, plug_in_without_K=plug_without),
        indent=1), encoding="utf-8")
    print("\nwrote data/toy_collider.csv and data/toy_collider_truth.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
