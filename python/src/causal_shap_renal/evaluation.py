"""Shared evaluation metrics, used to score attributions regardless of
which language produced them (R's shapr output or Python's shap/Shapley
Flow/structural-prototype output), reading the shared Parquet schema from
io_contract.py.

Metrics per docs/methods "Evaluation metrics":
  - Kendall's tau, Spearman's rho (rank agreement vs. ground-truth total effects)
  - top-k recovery
  - NDCG@k
  - proximity bias measures (PBI, POA): a method's tendency to over-credit
    features near the outcome
  - structural recovery (Step 8): structural Hamming distance, edge
    precision/recall
  - paired bootstrap resampling over evaluation records, for locked comparisons

TODO: implement once Step 4 produces its first attribution output to score.
"""

from __future__ import annotations


def kendalls_tau(attributions, ground_truth) -> float:
    raise NotImplementedError


def spearmans_rho(attributions, ground_truth) -> float:
    raise NotImplementedError


def top_k_recovery(attributions, ground_truth, k: int) -> float:
    raise NotImplementedError


def ndcg_at_k(attributions, ground_truth, k: int) -> float:
    raise NotImplementedError


def structural_hamming_distance(recovered_graph, true_graph) -> int:
    raise NotImplementedError
