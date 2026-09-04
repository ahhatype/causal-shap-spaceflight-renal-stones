"""Shared evaluation metrics, used to score attributions regardless of
which language produced them (R's shapr output or Python's shap/Shapley
Flow/structural-prototype output), reading the shared Parquet schema from
io_contract.py.

Metrics per docs/methods "Evaluation metrics":
  - Kendall's tau, Spearman's rho (rank agreement vs. ground-truth total effects)
  - top-k recovery
  - NDCG@k
  - proximity bias measures (PBI, POA, proximal mass): a method's tendency
    to over-credit features near the outcome. Definitions from the
    2026-07-10 proposal in docs/full_dag/proximity-bias-metrics.md, the same
    ones the full-DAG record reports (analysis/R/shap_distance_metrics.R).
  - structural recovery (Step 8): structural Hamming distance, edge
    precision/recall - structural_hamming_distance() below is still a
    stub, Step 8's concern, not needed for Step 6's node-level attribution
    comparison.
  - paired bootstrap resampling over evaluation records, for locked
    comparisons - not implemented here either (future work).

attributions/ground_truth below are both indexed by feature name: either a
pandas Series (index=feature) or a dict, matching what Step 6's drivers
already hold in memory (a feature -> attribution_value / feature ->
true_total_effect_abs mapping) rather than requiring a specific DataFrame
shape.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import kendalltau, spearmanr


def _aligned(attributions, ground_truth) -> tuple[np.ndarray, np.ndarray]:
    """Align two feature-indexed mappings on their common features, in a
    fixed (sorted) order so every metric below compares the same pairing.
    """
    common = sorted(set(attributions) & set(ground_truth))
    if not common:
        raise ValueError("attributions and ground_truth share no features")
    a = np.array([attributions[f] for f in common], dtype=float)
    g = np.array([ground_truth[f] for f in common], dtype=float)
    return a, g


def kendalls_tau(attributions, ground_truth) -> float:
    """Kendall's tau-b rank correlation between a method's attribution
    magnitudes and ground-truth total effects."""
    a, g = _aligned(attributions, ground_truth)
    return float(kendalltau(a, g).statistic)


def spearmans_rho(attributions, ground_truth) -> float:
    """Spearman's rank correlation between a method's attribution
    magnitudes and ground-truth total effects."""
    a, g = _aligned(attributions, ground_truth)
    return float(spearmanr(a, g).statistic)


def top_k_recovery(attributions, ground_truth, k: int) -> float:
    """Fraction of ground truth's top-k features (by true_total_effect_abs)
    that also appear in the attribution method's own top-k (by
    |attribution_value|). 1.0 = perfect overlap, 0.0 = no overlap."""
    common = sorted(set(attributions) & set(ground_truth))
    k = min(k, len(common))
    if k == 0:
        raise ValueError("attributions and ground_truth share no features")
    top_gt = set(sorted(common, key=lambda f: -abs(ground_truth[f]))[:k])
    top_attr = set(sorted(common, key=lambda f: -abs(attributions[f]))[:k])
    return len(top_gt & top_attr) / k


def ndcg_at_k(attributions, ground_truth, k: int) -> float:
    """NDCG@k: rank features by |attribution_value| (descending), using
    ground truth's own |true_total_effect_abs| as each feature's graded
    relevance. Standard log2 discount, normalized against the best
    possible (ground-truth-sorted) ranking's DCG@k."""
    common = sorted(set(attributions) & set(ground_truth))
    k = min(k, len(common))
    if k == 0:
        raise ValueError("attributions and ground_truth share no features")
    relevance = {f: abs(ground_truth[f]) for f in common}

    def dcg(order: list[str]) -> float:
        return sum(
            relevance[f] / np.log2(i + 2) for i, f in enumerate(order[:k])
        )

    ranked_by_attr = sorted(common, key=lambda f: -abs(attributions[f]))
    ranked_by_gt = sorted(common, key=lambda f: -relevance[f])
    ideal = dcg(ranked_by_gt)
    if ideal == 0:
        return 0.0
    return dcg(ranked_by_attr) / ideal


# --- proximity bias (docs/full_dag/proximity-bias-metrics.md) -----------------


def directed_distances(edges, outcome: str) -> dict[str, int]:
    """Shortest directed hop count from each ancestor to the outcome.

    ``edges`` is an iterable of (from, to) pairs or of dicts with "from"/"to"
    keys (config/dag_spec.yaml's edge list works as-is). Nodes with no
    directed path to the outcome are omitted: they are non-ancestors and the
    proposal gives them infinite distance, so they carry no attribution mass
    in these metrics and should be reported separately as off-path mass.
    """
    parents: dict[str, list[str]] = {}
    for edge in edges:
        src, dst = (edge["from"], edge["to"]) if isinstance(edge, dict) else edge
        parents.setdefault(dst, []).append(src)
    distances = {outcome: 0}
    frontier = [outcome]
    while frontier:
        nxt = []
        for node in frontier:
            for parent in parents.get(node, []):
                if parent not in distances:
                    distances[parent] = distances[node] + 1
                    nxt.append(parent)
        frontier = nxt
    distances.pop(outcome)
    return distances


def _mass(values, features) -> dict[str, float]:
    """Normalize |values| over ``features`` to a probability mass; all-zero maps to zeros."""
    absolute = {f: abs(float(values[f])) for f in features}
    total = sum(absolute.values())
    return {f: (v / total if total > 0 else 0.0) for f, v in absolute.items()}


def _on_path_features(attributions, ground_truth, distances) -> list[str]:
    common = sorted(set(attributions) & set(ground_truth) & set(distances))
    if not common:
        raise ValueError("attributions, ground_truth, and distances share no features")
    return common


def proximity_bias_index(attributions, ground_truth, distances) -> float:
    """PBI = mean directed distance under truth minus under the method.

    Positive: the method concentrates mass closer to the outcome than the
    truth does. Zero: correct mean causal depth. Negative: too far upstream.
    """
    features = _on_path_features(attributions, ground_truth, distances)
    p, q = _mass(attributions, features), _mass(ground_truth, features)
    return float(sum(q[f] * distances[f] for f in features) - sum(p[f] * distances[f] for f in features))


def distance_concentration(mass, distances, k_max: int) -> list[float]:
    """C(k) for k = 1..k_max: cumulative mass within k hops of the outcome."""
    return [sum(m for f, m in mass.items() if distances[f] <= k) for k in range(1, k_max + 1)]


def proximal_over_attribution_area(attributions, ground_truth, distances) -> float:
    """POA = mean over k = 1..K-1 of C_method(k) - C_truth(k), K = deepest hop.

    Positive values mean excess cumulative importance near the outcome.
    Report the curve itself alongside this scalar.
    """
    features = _on_path_features(attributions, ground_truth, distances)
    p, q = _mass(attributions, features), _mass(ground_truth, features)
    k_max = max(distances[f] for f in features)
    if k_max < 2:
        return 0.0
    cp = distance_concentration(p, distances, k_max - 1)
    cq = distance_concentration(q, distances, k_max - 1)
    return float(np.mean([a - b for a, b in zip(cp, cq)]))


def proximal_mass(attributions, distances, k: int = 2) -> float:
    """Share of a method's attribution mass within ``k`` hops of the outcome."""
    features = sorted(set(attributions) & set(distances))
    if not features:
        raise ValueError("attributions and distances share no features")
    return float(sum(m for f, m in _mass(attributions, features).items() if distances[f] <= k))


def structural_hamming_distance(recovered_graph, true_graph) -> int:
    raise NotImplementedError("Step 8's concern - not needed for Step 6's node-level metrics")
