"""Shared evaluation metrics, used to score attributions regardless of
which language produced them (R's shapr output or Python's shap/Shapley
Flow/structural-prototype output), reading the shared Parquet schema from
io_contract.py.

Metrics per docs/methods "Evaluation metrics":
  - Kendall's tau, Spearman's rho (rank agreement vs. ground-truth total effects)
  - top-k recovery
  - NDCG@k
  - proximity bias measures (PBI, POA): a method's tendency to over-credit
    features near the outcome - NOT implemented here, no formula is
    specified anywhere in the methods doc; left as future work rather
    than guessed at.
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


def structural_hamming_distance(recovered_graph, true_graph) -> int:
    raise NotImplementedError("Step 8's concern - not needed for Step 6's node-level metrics")
