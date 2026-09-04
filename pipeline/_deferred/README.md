# Deferred steps

Nothing in this directory runs. It exists so the step numbering stays legible against the methods doc.

- **Step 5** and **Step 7** (LumaWarp detector) are no longer deferred. They have placeholder drivers, `pipeline/step05_lumawarp_detector.py` and `pipeline/step07_lumawarp_reweight.py`, and a public interface contract, `python/src/causal_shap_renal/lumawarp_contract.py`. The detector provider itself stays outside this repository. See [`docs/decisions/008-lumawarp-detector-placeholders.md`](../../docs/decisions/008-lumawarp-detector-placeholders.md) and [`docs/lumawarp/README.md`](../../docs/lumawarp/README.md).
- **Step 12** (longitudinal extension): future work, not undertaken in this paper.
- **Step 13** (counterfactual recourse / cost-sensitive DiCE): out of scope for the paper. The budget-constrained action-selection machinery ported from causal-shap-target-dags (`apps/causal_shap/policy.py`, `action_costs.py`, `shift_estimation.py`) is the starting point when Andy and Lexi scope it; see [`docs/full_dag/RESEARCH_RECORD.md`](../../docs/full_dag/RESEARCH_RECORD.md).
