"""Step 6: Ng et al.'s Causal SHAP (arXiv:2509.00846).
See docs/methods §9 and python/src/causal_shap_renal/attribution_structural.py.

Consumes pipeline/step06d_pc_ida.R's output (per-round PC/IDA edges)
rather than recomputing PC+IDA - ADR-001's file-only cross-language
interchange. Runs both engines config/model_engines.yaml specifies for
this method (xgboost primary, random_forest secondary check - Ng et al.'s
own paper-native engine) across all 3 HITL rounds; step06d's own driver
already applied the round-2/3 revision heuristics to the edges this reads,
so no further per-round logic is needed here.
"""

import pandas as pd

from causal_shap_renal.attribution_structural import run_structural_causal_shap
from causal_shap_renal.io_contract import (
    attribution_provenance,
    read_dag_spec,
    read_simulated_data,
    write_attributions,
)

if __name__ == "__main__":
    data = read_simulated_data("../data/simulated/renal_stone_simulated.parquet")
    dag_spec = read_dag_spec("../config/dag_spec.yaml")
    pc_ida_edges = pd.read_parquet("../results/attributions/step06d_pc_ida_edges.parquet")

    frames = []
    for round_ in (1, 2, 3):
        for engine in ("xgboost", "random_forest"):
            frames.append(
                run_structural_causal_shap(data, pc_ida_edges, dag_spec, iteration_round=round_, engine=engine)
            )
    attributions = pd.concat(frames, ignore_index=True)
    for col, val in attribution_provenance().items():
        attributions[col] = val
    write_attributions(attributions, "../results/attributions/step06c_causal_shap_ng_et_al.parquet")
    print(f"Wrote {len(attributions)} rows to results/attributions/step06c_causal_shap_ng_et_al.parquet")
