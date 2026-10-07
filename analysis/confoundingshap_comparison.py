"""Bounded signed ConfoundingSHAP comparison (Brockschmidt et al., 2026).

Uses shapiq's released exact allocator with explicitly defined reference games.
The renal nuisance estimator is a saturated binary-cell estimator, NOT the
paper's TabPFN implementation. No LumaWarp score is computed or substituted.
Run with Python >=3.12 and analysis/requirements-confoundingshap.txt.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import itertools
import json
import math
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.special import expit
from shapiq import ExactComputer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis/output/source_aligned_clean/renal_stone_source_aligned_clean_v3.csv"
EDGES = ROOT / "analysis/output/dag_validation/validated_clean_source_edges.csv"
FEATURES = ["medical_prevention_capability", "bisphosphonates", "k_plus_citrate", "water_intake"]
SOURCE_NAMES = ["Medical Prevention Capability", "Bisphosphonates", "K+ Citrate", "Water Intake"]


def masks(p: int) -> np.ndarray:
    return np.array([[bool(i & (1 << j)) for j in range(p)] for i in range(2**p)])


def exact_shapley(values: np.ndarray) -> np.ndarray:
    """Independent factorial-sum check; accepts one scalar per coalition."""
    p = int(round(math.log2(len(values))))
    if len(values) != 2**p:
        raise ValueError("Expected all 2**p coalition values")
    out = np.zeros(p)
    for j in range(p):
        for s in range(2**p):
            if not s & (1 << j):
                k = s.bit_count()
                w = math.factorial(k) * math.factorial(p-k-1) / math.factorial(p)
                out[j] += w * (values[s | (1 << j)] - values[s])
    return out


def package_shapley(values: np.ndarray) -> np.ndarray:
    p = int(round(math.log2(len(values))))

    def game(coalitions):
        indices = np.asarray(coalitions, dtype=int) @ (1 << np.arange(p))
        return values[indices]

    sv = ExactComputer(n_players=p, game=game)(index="SV", order=1)
    out = np.array([sv[(j,)] for j in range(p)])
    np.testing.assert_allclose(out, exact_shapley(values), atol=1e-12, rtol=0)
    np.testing.assert_allclose(out.sum(), values[-1]-values[0], atol=1e-12, rtol=0)
    return out


def projection(states: np.ndarray, weights: np.ndarray, values: np.ndarray, subset: np.ndarray) -> np.ndarray:
    """Exact conditional expectation on a finite population of covariate states."""
    result = np.empty(len(states))
    for i, row in enumerate(states):
        group = np.all(states[:, subset] == row[subset], axis=1)
        result[i] = np.average(values[group], weights=weights[group])
    return result


def conditional_shap_mean_abs(states, weights, output):
    games = np.array([projection(states, weights, output, s) for s in masks(states.shape[1])])
    local = np.array([exact_shapley(games[:, i]) for i in range(len(states))])
    return np.average(np.abs(local), axis=0, weights=weights)


def oracle_case(randomized: bool):
    """Exact population oracle; independently specified illustration, not renal data."""
    states = masks(4).astype(int)
    c, z, h, prognostic = states.T
    weights = np.full(16, 1/16)
    propensity = np.full(16, .4) if randomized else .1 + .3*c + .3*z
    mu0 = c + .7*prognostic
    tau = .5 + 1.2*h
    mu1 = mu0 + tau
    local_game = []
    for subset in masks(4):
        e = projection(states, weights, propensity, subset)
        delta = (projection(states, weights, propensity*mu1, subset)/e
                 - projection(states, weights, (1-propensity)*mu0, subset)/(1-e))
        projected_tau = projection(states, weights, tau, subset)
        local_game.append(projected_tau-delta)
    local_game = np.asarray(local_game)
    global_game = local_game @ weights
    phi = package_shapley(global_game)
    local_phi = np.array([exact_shapley(local_game[:, i]) for i in range(16)])
    np.testing.assert_allclose(local_phi.T @ weights, phi, atol=1e-12)
    np.testing.assert_allclose(local_phi.sum(axis=1), -global_game[0], atol=1e-12)
    expected = np.zeros(4) if randomized else np.array([1753/5280, -103/5280, 0, 0])
    np.testing.assert_allclose(phi, expected, atol=1e-12)
    rows = []
    outcome_shap = conditional_shap_mean_abs(states, weights, mu0)
    cate_shap = conditional_shap_mean_abs(states, weights, tau)
    for j, name in enumerate(["confounder_C", "instrument_Z", "effect_modifier_H", "outcome_only_P"]):
        rows.append(dict(scenario="randomized" if randomized else "confounded_with_instrument",
                         feature=name, confounding_signed=phi[j],
                         control_outcome_conditional_shap_mean_abs=outcome_shap[j],
                         cate_conditional_shap_mean_abs=cate_shap[j]))
    return rows, global_game


def cell_predictions(train, outcome, query, columns):
    """Unsmoothed cell means; never extrapolate into an unsupported cell."""
    fit = train.assign(_response=np.asarray(outcome)).groupby(columns, sort=False)._response.mean()
    index = pd.MultiIndex.from_frame(query[columns]) if len(columns)>1 else pd.Index(query[columns[0]])
    predictions = fit.reindex(index).to_numpy()
    if not np.isfinite(predictions).all():
        raise ValueError(f"Unsupported covariate/treatment cell for {columns}")
    return predictions


def validate_renal_design():
    edges = pd.read_csv(EDGES)
    graph = nx.from_pandas_edgelist(edges, "from", "to", create_using=nx.DiGraph)
    assert len(graph) == 51 and graph.number_of_edges() == 75
    assert set(graph.predecessors("Thiazides")) == {SOURCE_NAMES[0]}
    assert not set(SOURCE_NAMES) & nx.descendants(graph, "Thiazides")
    assert list(nx.all_simple_paths(graph, "Thiazides", "Nephrolithiasis")) == [
        ["Thiazides", "Urine Chemistry", "Mineralized Renal Material", "Nephrolithiasis"]]
    assert set(graph.predecessors("Nephrolithiasis")) == {"Individual Factors", "Mineralized Renal Material"}
    backdoor = graph.copy()
    backdoor.remove_edges_from(list(graph.out_edges("Thiazides")))
    for subset in masks(4):
        separated = nx.is_d_separator(backdoor, {"Thiazides"}, {"Nephrolithiasis"},
                                       set(np.array(SOURCE_NAMES)[subset]))
        assert separated == bool(subset[0])


def renal_split(data, seed):
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(data))
    train, evaluation = data.iloc[order[:6000]], data.iloc[order[6000:]]
    # Canonical source-aligned generator: -.70 * .60 * .60 = -.252
    # along the only A-to-Y path. Reconstruct counterfactual probabilities,
    # preserving each record's structural disturbances; not Bernoulli draws.
    eta = -2.35 + .60*evaluation.individual_factors + .60*evaluation.mineralized_renal_material
    p1 = expit(eta - .252*(1-evaluation.thiazides))
    p0 = expit(eta + .252*evaluation.thiazides)
    states = masks(4).astype(int)
    query = pd.DataFrame(states, columns=FEATURES)
    counts = evaluation.groupby(FEATURES).size().reindex(pd.MultiIndex.from_frame(query), fill_value=0).to_numpy()
    weights = counts/counts.sum()
    if np.any(weights == 0):
        raise ValueError("Evaluation population lacks a covariate state")
    train_counts = train.groupby([*FEATURES, "thiazides"]).size()
    if len(train_counts) != 32:
        raise ValueError("Training split lacks an arm/covariate cell")
    contrasts = []
    for subset in masks(4):
        covariates = list(np.array(FEATURES)[subset])
        y1 = cell_predictions(train, train.nephrolithiasis, query.assign(thiazides=1), [*covariates, "thiazides"])
        y0 = cell_predictions(train, train.nephrolithiasis, query.assign(thiazides=0), [*covariates, "thiazides"])
        contrasts.append(y1-y0)
    contrasts = np.asarray(contrasts)
    full_tau = contrasts[-1]
    adjusted = float(weights @ full_tau)
    # Same estimated full outcome contrast anchors every coalition. The global
    # projected CATE is its fixed evaluation-population average by construction.
    global_game = adjusted-contrasts @ weights
    phi = package_shapley(global_game)
    np.testing.assert_allclose(global_game[-1], 0, atol=1e-14)
    mu0 = cell_predictions(train, train.nephrolithiasis, query.assign(thiazides=0), [*FEATURES, "thiazides"])
    pred_phi = conditional_shap_mean_abs(states, weights, mu0)
    cate_phi = conditional_shap_mean_abs(states, weights, full_tau)
    rows = [dict(seed=seed, feature=f, confounding_signed=phi[j],
                 control_outcome_conditional_shap_mean_abs=pred_phi[j],
                 cate_conditional_shap_mean_abs=cate_phi[j]) for j, f in enumerate(FEATURES)]
    summary = dict(seed=seed, n_train=len(train), n_evaluation=len(evaluation),
                   minimum_training_arm_cell=int(train_counts.min()),
                   crude_train_difference=float(contrasts[0, 0]),
                   plugin_full_adjusted_evaluation_ate=adjusted,
                   dgp_expected_outcome_ate_evaluation=float((p1-p0).mean()),
                   plugin_crude_minus_adjusted=float(-global_game[0]),
                   attribution_sum=float(phi.sum()),
                   minimum_empirical_propensity=float(train.groupby(FEATURES).thiazides.mean().min()),
                   maximum_empirical_propensity=float(train.groupby(FEATURES).thiazides.mean().max()))
    coalitions = [dict(seed=seed, coalition=";".join(np.array(FEATURES)[s]) or "EMPTY",
                       value=global_game[k]) for k, s in enumerate(masks(4))]
    return rows, summary, coalitions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"analysis/output/confoundingshap_pilot")
    args = parser.parse_args()
    validate_renal_design()
    data = pd.read_csv(DATA)
    assert len(data) == 10000
    assert data[[*FEATURES, "thiazides", "nephrolithiasis"]].isin([0, 1]).all().all()
    rows, summaries, coalitions, oracle_rows, oracle_coalitions = [], [], [], [], []
    for randomized in [False, True]:
        result, game = oracle_case(randomized)
        oracle_rows.extend(result)
        oracle_coalitions.extend(dict(randomized=randomized, coalition=k, value=v) for k,v in enumerate(game))
    for seed in range(20260930, 20260935):
        result, summary, games = renal_split(data, seed)
        rows.extend(result); summaries.append(summary); coalitions.extend(games)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, records in [("oracle_attributions", oracle_rows), ("oracle_coalitions", oracle_coalitions),
                          ("renal_attributions", rows), ("renal_splits", summaries), ("renal_coalitions", coalitions)]:
        pd.DataFrame(records).to_csv(args.output/f"{name}.csv", index=False)
    frame = pd.DataFrame(rows)
    metrics = [c for c in frame if c not in {"seed", "feature"}]
    aggregate = frame.groupby("feature")[metrics].agg(["mean", "min", "max"])
    aggregate.columns = ["_".join(c) for c in aggregate.columns]
    aggregate.to_csv(args.output/"renal_summary.csv")
    metadata = dict(paper="https://arxiv.org/abs/2605.10533v1", date="2026-09-30",
        input_path=DATA.relative_to(ROOT).as_posix(), input_sha256=hashlib.sha256(DATA.read_bytes()).hexdigest(),
        edges_sha256=hashlib.sha256(EDGES.read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256((ROOT/"analysis/R/renal_stone_source_aligned_simcausal.R").read_bytes()).hexdigest(),
        versions={p:importlib.metadata.version(p) for p in ["shapiq", "numpy", "pandas", "networkx", "scipy"]},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        treatment="thiazides", outcome="nephrolithiasis", covariates=FEATURES,
        source="Existing 51-node/75-edge source_aligned_clean_v3 simulation; not the 14-node working model or 53-node source",
        estimator="Independent saturated binary-cell plug-in; shapiq exact SV; NOT upstream TabPFN ConfoundingXAI",
        scale="Risk difference for renal outputs; continuous outcome units in synthetic oracle",
        normalization="Signed -mean(residual bias); no absolute-value transformation; 16 exact coalitions",
        comparison="Conditional SHAP of control-outcome prediction and estimated CATE; different estimands, not accuracy competitors",
        dgp_reference="Evaluation-row average of paired counterfactual probabilities under the canonical generator; finite Monte Carlo ATE reference only, not a confounding-attribution oracle",
        uncertainty="Five splits of one frozen dataset; ranges are split sensitivity, NOT confidence intervals or independent DGP replications",
        finite_sample_target="Crude contrast estimated in training rows; adjusted contrasts standardized to held-out covariates. Plug-in discrepancy includes nuisance error and split-composition variation, not solely true confounding",
        validation="Exact synthetic oracles, Shapley efficiency, independent factorial calculation, local/global averaging, graph d-separation, cell support",
        limitations=["No population oracle for renal confounding contributions; noisy estimated CATE may reflect estimation error",
                     "Full adjustment sufficiency comes from assumed graph, not scores",
                     "Historical intervention-effect ranking is a different target and not used as attribution truth",
                     "No LumaWarp provider or detector outputs evaluated",
                     "No continuous-calcium dichotomization or 14-node rerun",
                     "No successful upstream TabPFN estimator run; separate attempt blocked by model-license access before fitting"])
    (args.output/"metadata.json").write_text(json.dumps(metadata, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(pd.DataFrame(oracle_rows).to_string(index=False))
    print(aggregate.to_string())
    print(pd.DataFrame(summaries).to_string(index=False))


if __name__ == "__main__":
    main()
