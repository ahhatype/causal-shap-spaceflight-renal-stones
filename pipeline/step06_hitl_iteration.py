"""Step 6: scores and summarizes the 3-round human-in-the-loop iteration
across the 4 causal SHAP methods (step06a-d). See docs/methods §9-10.

This does NOT orchestrate live execution across methods or languages -
each of step06a-d's own driver scripts runs its own 3 rounds internally
(applying its own scripted revision heuristic between rounds) and writes
its results to results/attributions/ before this script ever runs, per
ADR-001's file-only cross-language interchange (no live R<->Python calls).
This script's only job is: read what's already on disk, score every
(method, engine, iteration_round) combination against Step 4's ground
truth via evaluation.py's metrics, and write one summary table other code
(docs/step06_results.md) reads from - so every number in that report
traces back to a parquet file, not a number typed by hand.

Heskes Causal Shapley Values has no output at all this round - blocked,
see docs/decisions/006-shapr-heskes-blocked.md - so it is absent from the
summary rather than scored as zero or missing-data.

Every round-2/3 number scored here reflects a scripted heuristic revision
(see each method's own module/driver for exactly what that heuristic is),
NOT real domain-expert review - see docs/step06_results.md's "LLM-made
decisions" table before treating any round-over-round change as a finding
about the method itself.
"""

import glob

import pandas as pd

from causal_shap_renal.evaluation import kendalls_tau, ndcg_at_k, spearmans_rho, top_k_recovery
from causal_shap_renal.io_contract import read_ground_truth

TOP_K = 5


def load_step06_attributions() -> pd.DataFrame:
    paths = sorted(glob.glob("../results/attributions/step06[abc]_*.parquet"))
    frames = [pd.read_parquet(p) for p in paths]
    return pd.concat(frames, ignore_index=True)


def score_all(attributions: pd.DataFrame, ground_truth: pd.DataFrame) -> pd.DataFrame:
    gt_map = dict(zip(ground_truth["feature"], ground_truth["true_total_effect_abs"]))
    rows = []
    group_cols = ["method", "engine", "dag_variant", "iteration_round"]
    for keys, group in attributions.groupby(group_cols):
        attr_map = dict(zip(group["feature"], group["attribution_value"]))
        rows.append(
            dict(zip(group_cols, keys))
            | {
                "kendalls_tau": kendalls_tau(attr_map, gt_map),
                "spearmans_rho": spearmans_rho(attr_map, gt_map),
                f"top_{TOP_K}_recovery": top_k_recovery(attr_map, gt_map, TOP_K),
                f"ndcg_at_{TOP_K}": ndcg_at_k(attr_map, gt_map, TOP_K),
            }
        )
    return pd.DataFrame(rows).sort_values(["method", "engine", "iteration_round"]).reset_index(drop=True)


if __name__ == "__main__":
    ground_truth = read_ground_truth("../data/frozen_truth/ground_truth_total_effects.parquet")
    attributions = load_step06_attributions()
    summary = score_all(attributions, ground_truth)

    out_path = "../results/attributions/step06_hitl_summary.parquet"
    summary.to_parquet(out_path, index=False)
    print(summary.to_string(index=False))
    print(f"\nWrote {len(summary)} rows to {out_path}")
