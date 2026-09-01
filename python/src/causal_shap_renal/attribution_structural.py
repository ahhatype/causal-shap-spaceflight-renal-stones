"""Step 6: Ng et al.'s Causal SHAP (arXiv:2509.00846, IJCNN 2025).

No public reference repo - implemented directly from the paper's Algorithm 1
and Equations 4-15 (read in full from the paper's own PDF during Step 6
planning, since no summary online covers the algorithm in this detail).
The PC+IDA stage runs in R (pipeline/step06d_pc_ida.R, see
docs/decisions/001-two-language-repo.md) and is consumed here via its
parquet interchange file (from, to, weight, round), not recomputed.

Algorithm, as implemented:
  1. W_i = sum over every simple directed path p from feature i to the
     outcome (in the round's discovered/revised DAG extension from
     step06d), of the product of p's edge weights (IDA's mean(|effect|)
     per edge). Paths are enumerated with networkx.all_simple_paths.
  2. gamma_i = |W_i| / sum_j |W_j| - the causal weight factor (Eq. ~9-10).
  3. v_c(S), the causal value function: Monte Carlo estimate over M
     samples. For features not in S, sample in the graph's own
     topological order (NOT the true dag_spec.yaml order - this method
     doesn't get privileged access to ground truth, same standard the
     other 3 methods are held to): a root feature (no parents in the
     DISCOVERED graph) samples from its empirical marginal (bootstrap
     from the training data); a non-root feature samples from
     N(mu_i, sigma_i), where mu_i/sigma_i come from a linear regression
     of X_i on its DISCOVERED parents' actual values (already fixed by S
     or already sampled earlier in topological order), fit fresh from
     data - not our known true structural-equation coefficients.
  4. Outer loop, T iterations: draw a uniformly random subset S of
     features, compute v_c(S) once, then for every i not in S compute
     v_c(S u {i}), weight the difference by the standard Shapley kernel
     weight times gamma_i, and accumulate into phi_i^c (Eq. ~11-13).
  5. Normalize for local accuracy: phi_i^n = phi_i^c * (f(x) - E[f(X)])
     / sum_j phi_i^c (Eq. ~14-15).

M=64 (the paper's own finding that AUROC saturates beyond M=64) and T=150
(an LLM-authored tractability choice - see docs/step06_results.md's
"LLM-made decisions" table, not derived from the paper) are both
implementation budgets, not methodological claims. Every v_c(S) call
batches its M samples into one vectorized model.predict() call rather
than M separate calls, which is what keeps this tractable per explained
instance.

engine: "xgboost" primary; "random_forest" secondary check (Ng et al.'s
own paper-native engine - "All experiments used the same Random Forest
model as the black box"), per config/model_engines.yaml.
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from causal_shap_renal.engines import fit_engine
from causal_shap_renal.io_contract import model_features

TARGET = "nephrolithiasis"
M_SAMPLES = 64
T_ITERATIONS = 150


def build_graph(pc_ida_edges: pd.DataFrame) -> nx.DiGraph:
    """One round's edges (from, to, weight) from step06d's parquet output
    into a networkx DiGraph, feature+outcome nodes, weighted edges."""
    g = nx.DiGraph()
    for _, row in pc_ida_edges.iterrows():
        g.add_edge(row["from"], row["to"], weight=float(row["weight"]))
    return g


def causal_weights(graph: nx.DiGraph, features: list[str]) -> dict[str, float]:
    """W_i (path-product-sum to TARGET) and gamma_i (normalized) per
    feature. A feature absent from the graph, or with no path to TARGET
    in the discovered structure, gets W_i = gamma_i = 0 - a real
    consequence of PC missing that feature's connection to the outcome,
    not a bug (see docs/step06_results.md's discussion of PC's recall).
    """
    w = {}
    for f in features:
        if f not in graph or TARGET not in graph:
            w[f] = 0.0
            continue
        total = 0.0
        for path in nx.all_simple_paths(graph, source=f, target=TARGET):
            product = 1.0
            for a, b in zip(path[:-1], path[1:]):
                product *= graph[a][b]["weight"]
            total += product
        w[f] = total
    denom = sum(abs(v) for v in w.values())
    gamma = {f: (abs(v) / denom if denom > 0 else 0.0) for f, v in w.items()}
    return gamma


def _topological_feature_order(graph: nx.DiGraph, features: list[str]) -> list[str]:
    """Topological order restricted to features (drops TARGET, which is
    never a sampling input - only ever the model's output). Features
    absent from the graph entirely (PC found them adjacent to nothing) are
    appended at the end as roots - they have no discovered parents to
    respect an order against.
    """
    sub = graph.subgraph([f for f in features if f in graph]).copy()
    ordered = [n for n in nx.topological_sort(sub) if n in features]
    return ordered + [f for f in features if f not in ordered]


def fit_parent_regressions(
    data: pd.DataFrame, graph: nx.DiGraph, features: list[str]
) -> dict[str, dict]:
    """One linear regression per non-root feature, X_i ~ its DISCOVERED
    parents (from the round's PC/IDA graph, not dag_spec.yaml's true
    parents), fit once from data and reused across every v_c(S) Monte
    Carlo draw - fitting per-draw would be needlessly expensive and
    doesn't change what's being estimated.
    """
    fits = {}
    for f in features:
        parents = [p for p in graph.predecessors(f)] if f in graph else []
        parents = [p for p in parents if p in features]
        if not parents:
            fits[f] = {"parents": [], "marginal": data[f].to_numpy()}
            continue
        reg = LinearRegression().fit(data[parents], data[f])
        resid = data[f].to_numpy() - reg.predict(data[parents])
        fits[f] = {"parents": parents, "model": reg, "sigma": float(np.std(resid))}
    return fits


def _sample_non_S(
    features_order: list[str],
    S: set[str],
    x: pd.Series,
    fits: dict,
    rng: np.random.Generator,
    n_samples: int,
) -> pd.DataFrame:
    """M Monte Carlo draws of every feature not in S, respecting the
    discovered graph's topological order and each non-root feature's
    fitted parent regression - Equations ~4-6's causal-respecting
    sampling. Features in S are held fixed at x's own observed value
    (broadcast across all n_samples rows).
    """
    out = pd.DataFrame(index=range(n_samples), columns=features_order, dtype=float)
    for f in features_order:
        if f in S:
            out[f] = x[f]
            continue
        fit = fits[f]
        if not fit["parents"]:
            out[f] = rng.choice(fit["marginal"], size=n_samples, replace=True)
        else:
            mu = fit["model"].predict(out[fit["parents"]])
            out[f] = mu + rng.normal(0, fit["sigma"], size=n_samples)
    return out


def v_c(
    S: set[str],
    x: pd.Series,
    features: list[str],
    features_order: list[str],
    fits: dict,
    model,
    rng: np.random.Generator,
    m_samples: int = M_SAMPLES,
) -> float:
    """Monte Carlo estimate of the causal value function for coalition S
    at instance x: mean model prediction over m_samples causal-respecting
    draws of the features not in S (Eq. ~7-8). Sampling itself must
    proceed in the graph's topological order (features_order), but the
    model was fit on `features`' own column order - xgboost's
    predict_proba is strict about matching feature order, so reindex
    right before predicting.
    """
    sample = _sample_non_S(features_order, S, x, fits, rng, m_samples)
    return float(np.mean(model.predict_proba(sample[features])[:, 1]))


def causal_shap_one_instance(
    x: pd.Series,
    features: list[str],
    features_order: list[str],
    fits: dict,
    gamma: dict[str, float],
    model,
    expected_value: float,
    rng: np.random.Generator,
    t_iterations: int = T_ITERATIONS,
) -> dict[str, float]:
    """Algorithm 1, steps 2-5, for one explained instance x."""
    n = len(features)
    phi_c = dict.fromkeys(features, 0.0)

    for _ in range(t_iterations):
        coalition_size = rng.integers(0, n)  # |S| in [0, n-1] - always room for one more feature
        S = set(rng.choice(features, size=coalition_size, replace=False)) if coalition_size > 0 else set()
        not_in_S = [f for f in features if f not in S]
        if not not_in_S:
            continue
        v_S = v_c(S, x, features, features_order, fits, model, rng)
        s = len(S)
        kernel_weight = math.factorial(s) * math.factorial(n - s - 1) / math.factorial(n)
        for i in not_in_S:
            v_Si = v_c(S | {i}, x, features, features_order, fits, model, rng)
            phi_c[i] += kernel_weight * gamma[i] * (v_Si - v_S)

    total = sum(phi_c.values())
    prediction = float(model.predict_proba(pd.DataFrame([x[features]]))[:, 1][0])
    if total == 0:
        return dict.fromkeys(features, 0.0)
    scale = (prediction - expected_value) / total
    return {f: phi_c[f] * scale for f in features}


def run_structural_causal_shap(
    data: pd.DataFrame,
    pc_ida_edges: pd.DataFrame,
    dag_spec: dict,
    iteration_round: int = 1,
    engine: str = "xgboost",
    n_explain: int = 30,
    seed: int = 20260812,
) -> pd.DataFrame:
    features = model_features(dag_spec)
    y = data[TARGET]
    model = fit_engine(engine, data[features], y, seed=seed)

    round_edges = pc_ida_edges[pc_ida_edges["round"] == iteration_round]
    graph = build_graph(round_edges)
    gamma = causal_weights(graph, features)
    features_order = _topological_feature_order(graph, features)
    fits = fit_parent_regressions(data, graph, features)

    expected_value = float(model.predict_proba(data[features])[:, 1].mean())
    rng = np.random.default_rng(seed)
    explain_idx = rng.choice(len(data), size=min(n_explain, len(data)), replace=False)

    if sum(gamma.values()) == 0:
        # Every feature's gamma_i is 0 - the discovered graph has no path
        # from ANY feature to the outcome (see docs/step06_results.md).
        # Algorithm 1's math guarantees all-zero attributions in this
        # case (phi_i^c's every term is multiplied by gamma_i) - skip the
        # expensive Monte Carlo loop rather than spend it computing zeros.
        attribution_value = [0.0 for _ in features]
    else:
        per_feature_phi = {f: [] for f in features}
        for idx in explain_idx:
            x = data.iloc[idx]
            phi = causal_shap_one_instance(x, features, features_order, fits, gamma, model, expected_value, rng)
            for f in features:
                per_feature_phi[f].append(phi[f])
        attribution_value = [float(np.mean(np.abs(per_feature_phi[f]))) for f in features]
    return pd.DataFrame(
        {
            "method": "causal_shap_ng_et_al",
            "engine": engine,
            "dag_variant": "renal_stone_baseline",
            "iteration_round": iteration_round,
            "feature": features,
            "attribution_value": attribution_value,
        }
    )
