# Research protocol and implementation

The 13-step research protocol, with implementation paths and current status.
The [central workflow](central-workflow.md) groups these steps by analytical
purpose; [pipeline_status.yaml](../../config/pipeline_status.yaml) records status.
Code paths below are relative to the repository root.

| Step | What | Where | Status |
| --- | --- | --- | --- |
| 1 | Exposure and outcome: cumulative mission days; nephrolithiasis (binary) | `config/dag_spec.yaml` | done |
| 2 | DAG construction and augmentation from Robert Reynolds's supplied files | `config/dag_spec.yaml`, `r/R/dag_utils.R`, `analysis/10_ingest_robert_dags.R` | done |
| 3 | Synthetic data (simcausal) | `pipeline/step03_simulate_data.R`, `analysis/generate.R` | done |
| 4 | Baseline attribution with standard SHAP, five pairings | `pipeline/step04*`, `python/src/causal_shap_renal/attribution_baseline.py` | done |
| 5 | LumaWarp detector over Step 4 | `pipeline/step05_lumawarp_detector.py`, `python/src/causal_shap_renal/lumawarp_contract.py` | placeholder, provider gated |
| 6 | Causal SHAP comparison with scripted graph revisions | `pipeline/step06*`, `apps/causal_shap/structural_value.py` | partial: 3 methods run; round 1 unrevised, rounds 2–3 scripted; no human review |
| 7 | LumaWarp detector over Step 6 | `pipeline/step07_lumawarp_reweight.py` | placeholder, provider gated |
| 8 | Structural recovery: PC, GES, NOTEARS, LiNGAM | `pipeline/step08*`, `apps/causal_shap/discovery.py`, `apps/causal_shap/evaluation.py` (M1-M5) | library ported, runs pending |
| 9 | Robustness to the data-generating process | `apps/causal_shap/validation/` | scaffolded, pending |
| 10 | Robustness to spaceflight-epidemiological constraints | `analysis/R/renal_stone_source_aligned_simcausal.R` (NASA-like v4 selection regime) | one regime exists, sweep pending |
| 11 | Generalization to out-of-distribution populations | own section | pending |
| 12 | Longitudinal extension (g-methods) | future work | not undertaken |
| 13 | Cost-constrained recourse | `apps/causal_shap/policy.py`, `action_costs.py`, `shift_estimation.py` | scaffolded, out of the paper's scope |

The full-DAG comparison also contributes to central-workflow stage 6 through
`analysis/07_run_shap_comparison.R` and `apps/causal_shap/build/stages.py`;
these are separate from the numbered working-subgraph drivers.

Working-subgraph records: [simulation checks](../step03_simulation_review.md),
[baseline attribution](../step04_results.md), and
[scripted causal-attribution revisions](../step06_results.md).
See the [full-DAG research record](../full_dag/RESEARCH_RECORD.md) for its
separate methods and results, and the [detector interface](../lumawarp/README.md)
for the unevaluated Steps 5 and 7.
