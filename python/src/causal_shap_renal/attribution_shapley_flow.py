"""Step 6: Shapley Flow (Wang, Wiens & Lundberg, AISTATS 2021).

Requires a full directed graph. Attributes to edges, not nodes, which is
what distinguishes it from the other three Step 6 methods. Reference engine
is XGBoost, per the paper's case studies.

Verified directly against the installed shapflow 0.0.1 (flow.py) during
Step 6 implementation, since there's no shipped example/notebook and no
public usage docs beyond the package's own docstrings:

  - build_feature_graph(X, causal_links, target_name=..., method=...) adds
    one Node per X.columns PLUS a separate target Node - X must therefore
    be the FEATURES-ONLY dataframe (not the target's own column), and every
    feature stays a direct input to the fitted model regardless of which
    inter-feature edges are declared.
  - CausalLinks.add_causes_effects(causes, effects, models=[f]) wires every
    node in `causes` as a parent of every node in `effects`. Passing our
    own already-fitted XGBoost model here (wrapped via
    flow.create_xgboost_f, which expects a raw xgboost.Booster, not an
    sklearn XGBClassifier) for the ALL_FEATURES -> nephrolithiasis edge
    means shapflow explains the actual fitted classifier, not a refit
    approximation. Any additional inter-feature edges (e.g.
    bone_resorption -> parathyroid_suppression) are declared WITHOUT a
    model and get auto-fit from data via Graph.fit_missing_links().
  - GraphExplainer(graph, bg, nruns=...) supports exactly one background
    row (bg[:1], a real reference-point limitation of this reference
    implementation, not a bug on our end) - shap_values(X) can still
    explain many foreground rows at once against that one fixed baseline.
  - REPRODUCIBILITY GAP, not fully closed: even with np.random.seed() set
    (below) and the fitted XGBoost model forced to nthread=1 (both
    verified to make their own piece deterministic in isolation),
    back-to-back calls in the SAME process still produce small
    (2nd-3rd-decimal) attribution_value drift - traced to GraphExplainer's
    internal Monte Carlo credit-flow computation, not to model fitting or
    to the two seeded steps here. Rankings are stable across the drift in
    every run checked, but exact values are not bit-for-bit reproducible
    the way every other Step 6 method's output is - flagged explicitly in
    docs/step06_results.md rather than claimed otherwise.
  - shap_values(X).edge_credit is {source_node: {target_node: array of
    per-explained-row credit}} - EDGE-level, not node-level. A feature's
    node-level attribution_value is the mean |credit| across its outgoing
    edges' summed per-row credit (see _node_level_importance()).

Design choice (round-1 "naive" input, an LLM-authored decision - see
docs/step06_results.md's "LLM-made decisions" table): round 1 declares
ONLY the ALL_FEATURES -> nephrolithiasis block, no inter-feature edges at
all - every feature enters the model as if causally independent, which is
what "no causal graph provided" means for this method. This is NOT the
plan's originally-stated "direct-to-outcome edges only, flattening
mediation" framing (which would have required re-fitting the model on
feature subsets, breaking Shapley Flow's own point of explaining the
actual fitted classifier); it is functionally equivalent for a method that
already keeps every feature as a genuine model input, and better tests the
method's actual selling point - redistributing a feature's already-earned
model credit further upstream once real inter-feature causal edges are
declared.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import xgboost
from shapflow.flow import CausalLinks, GraphExplainer, build_feature_graph, create_xgboost_f

from causal_shap_renal.io_contract import model_features

TARGET = "nephrolithiasis"
SEED = 20260812


def true_inter_feature_edges(dag_spec: dict) -> list[tuple[str, str]]:
    """dag_spec.yaml's edges among FEATURES only (excludes any edge whose
    `to` is the outcome - those are already covered by the single
    ALL_FEATURES -> nephrolithiasis block every round declares). This is
    the candidate pool the Step 6 HITL round-2/3 revision heuristic below
    draws from.
    """
    return [(e["from"], e["to"]) for e in dag_spec["edges"] if e["to"] != TARGET]


def shapley_flow_revise_edges(
    prior_round_attributions: dict[str, float],
    ground_truth: dict[str, float],
    dag_spec: dict,
    already_added: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Step 6 HITL round-2/3 scripted revision heuristic: add ONE new
    inter-feature edge per round - among dag_spec.yaml's true edges not
    yet added, the one whose CHILD has the highest prior-round
    |attribution - ground truth|. Accumulates monotonically (round 3
    keeps round 2's edge, plus one more), same convention as
    r/R/shapr_wrappers.R's heskes_revise_confounding().

    This is an LLM-authored scripted stand-in for the methods doc's
    "Robert reviews and revises" step, NOT a finding from shapflow or the
    Wang/Wiens/Lundberg paper - both "one edge per round" and "highest
    prior-round error" are implementation choices with no basis in either
    source. See docs/step06_results.md's "LLM-made decisions" table.
    """
    candidates = [e for e in true_inter_feature_edges(dag_spec) if e not in already_added]
    if not candidates:
        return already_added
    error = {f: abs(prior_round_attributions.get(f, 0.0) - ground_truth.get(f, 0.0)) for f in ground_truth}
    best = max(candidates, key=lambda e: error.get(e[1], 0.0))
    return already_added + [best]


def _node_level_importance(edge_credit: dict, features: list[str]) -> dict[str, float]:
    """A feature's node-level attribution_value: sum its outgoing edges'
    per-row credit (a feature with 2 outgoing edges - e.g. bone_resorption
    once parathyroid_suppression is wired in - gets credit for both), then
    mean |.| across the explained rows. Matches the mean-|SHAP value|
    global-importance convention used everywhere else in this repo.

    edge_credit is keyed by shapflow's own Node objects, not strings -
    Node has no __eq__/__hash__ override (only a name-returning __repr__,
    which makes printed keys LOOK like plain strings), so this rebuilds a
    name-indexed view first rather than looking features up directly,
    verified necessary by testing this exact mismatch during Step 6
    implementation (a naive `edge_credit.get(feature_name)` silently
    returns nothing for every feature).
    """
    by_name = {node.name: edges_out for node, edges_out in edge_credit.items()}
    importance = {}
    for f in features:
        edges_out = by_name.get(f, {})
        if not edges_out:
            importance[f] = 0.0
            continue
        total_per_row = sum(np.asarray(credit, dtype=float) for credit in edges_out.values())
        importance[f] = float(np.mean(np.abs(total_per_row)))
    return importance


def run_shapley_flow(
    data: pd.DataFrame,
    dag_spec: dict,
    iteration_round: int = 1,
    inter_feature_edges: list[tuple[str, str]] | None = None,
    seed: int = SEED,
) -> pd.DataFrame:
    # shapflow's GraphExplainer has no seed parameter of its own - it
    # samples children permutations via np.random.permutation(), relying
    # on numpy's global RNG state (verified directly against the
    # installed shapflow 0.0.1's flow.py; same class of gap Step 4's
    # KernelExplainer has - see attribution_baseline.py's module
    # docstring). Reproduced drift between two otherwise-identical runs
    # without this seed call during Step 6 implementation.
    np.random.seed(seed)

    features = model_features(dag_spec)
    X = data[features]
    y = data[TARGET]

    # nthread=1: multi-threaded histogram building can sum floating-point
    # values in a different order run to run, producing tiny tree-value
    # drift despite a fixed seed - verified necessary during Step 6
    # implementation (two back-to-back calls in the same process produced
    # different attribution_value even with seed fixed, traced to this).
    booster = xgboost.train(
        {
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "seed": seed,
            "max_depth": 3,
            "eta": 0.1,
            "nthread": 1,
        },
        xgboost.DMatrix(X, label=y),
        num_boost_round=100,
    )
    model_fn = create_xgboost_f(features, booster)

    causal_links = CausalLinks()
    causal_links.add_causes_effects(causes=features, effects=[TARGET], models=[model_fn])
    for parent, child in inter_feature_edges or []:
        causal_links.add_causes_effects(causes=[parent], effects=[child])

    graph = build_feature_graph(X, causal_links, target_name=TARGET, method="xgboost")

    rng = np.random.RandomState(seed)
    bg = X.iloc[[rng.randint(len(X))]]
    explainer = GraphExplainer(graph, bg, nruns=100, silent=True)

    x_explain = X.sample(n=min(200, len(X)), random_state=seed)
    cf = explainer.shap_values(x_explain)
    importance = _node_level_importance(cf.edge_credit, features)

    return pd.DataFrame(
        {
            "method": "shapley_flow",
            "engine": "xgboost",
            "dag_variant": "renal_stone_baseline",
            "iteration_round": iteration_round,
            "feature": features,
            "attribution_value": [importance[f] for f in features],
        }
    )
