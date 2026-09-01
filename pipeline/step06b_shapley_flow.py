"""Step 6: Shapley Flow (Wang, Wiens & Lundberg, AISTATS 2021).
See docs/methods §9 and python/src/causal_shap_renal/attribution_shapley_flow.py.

Runs across all 3 HITL iteration rounds: round 1 is the genuinely naive
"no inter-feature edges" input; rounds 2-3 apply
attribution_shapley_flow.py's scripted revision heuristic
(shapley_flow_revise_edges(), one inter-feature edge added per round,
picked by prior-round attribution error against Step 4's ground truth) -
NOT real expert review, see docs/step06_results.md's "LLM-made decisions"
table.
"""

import pandas as pd

from causal_shap_renal.attribution_shapley_flow import run_shapley_flow, shapley_flow_revise_edges
from causal_shap_renal.io_contract import (
    attribution_provenance,
    read_dag_spec,
    read_ground_truth,
    read_simulated_data,
    write_attributions,
)

if __name__ == "__main__":
    data = read_simulated_data("../data/simulated/renal_stone_simulated.parquet")
    dag_spec = read_dag_spec("../config/dag_spec.yaml")
    ground_truth = read_ground_truth("../data/frozen_truth/ground_truth_total_effects.parquet")
    gt_map = dict(zip(ground_truth["feature"], ground_truth["true_total_effect_abs"]))

    r1 = run_shapley_flow(data, dag_spec, iteration_round=1)
    edges = shapley_flow_revise_edges(dict(zip(r1["feature"], r1["attribution_value"])), gt_map, dag_spec, [])

    r2 = run_shapley_flow(data, dag_spec, iteration_round=2, inter_feature_edges=edges)
    edges = shapley_flow_revise_edges(dict(zip(r2["feature"], r2["attribution_value"])), gt_map, dag_spec, edges)

    r3 = run_shapley_flow(data, dag_spec, iteration_round=3, inter_feature_edges=edges)

    attributions = pd.concat([r1, r2, r3], ignore_index=True)
    for col, val in attribution_provenance().items():
        attributions[col] = val
    write_attributions(attributions, "../results/attributions/step06b_shapley_flow.parquet")
    print(f"Wrote {len(attributions)} rows to results/attributions/step06b_shapley_flow.parquet")
    print(f"Inter-feature edges added by round 2/3: {edges}")
