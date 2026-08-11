# Pipeline status

Tracks the same 13 steps as the methods doc (docs/methods), step by step.
Update this file as work lands. `config/pipeline_status.yaml` is the
machine-readable mirror of this table.

| Step | Label | Status | Notes |
|---|---|---|---|
| 1 | Exposure/outcome specification | done | Cumulative mission days as exposure; nephrolithiasis as primary outcome, CaOx supersaturation as continuous secondary outcome. See `config/dag_spec.yaml`. |
| 2 | DAG construction and expert-guided augmentation | done | 12-node working subgraph scoped from Robert's 53-node source DAG (SA-07566). See `config/dag_spec.yaml`. |
| 3 | Synthetic data generation | pending | simcausal structural equations drafted with placeholder coefficients (`config/edge_coefficients.yaml`), pending Robert's calibration sign-off. |
| 4 | Baseline attribution with standard SHAP | pending | Explainer x model pairings specced (TreeExplainer, LinearExplainer, KernelExplainer, PermutationExplainer). Not yet run. |
| 5 | Complexity-aware reweighting | deferred, external | LumaWarp. Owned by Lexi/Andy, runs in a separate repo. Not built here. |
| 6 | Causal SHAP comparison + human-in-the-loop | pending | 4-method comparison (Heskes Causal Shapley Values, Shapley Flow, ASV, Ng et al. Causal SHAP) and the 3-round expert-revision design. Not yet run. |
| 7 | Complexity-aware reweighting of Step 6 outputs | deferred, external | LumaWarp reassessment. Owned by Lexi/Andy, runs in a separate repo. Not built here. |
| 8 | Structural recovery comparison | pending | PC (reused from Step 6), GES, NOTEARS, LiNGAM. Not yet run. |
| 9 | Robustness to the data-generating process | pending, extension | May be reported in compressed form. |
| 10 | Robustness to spaceflight-epidemiological constraints | pending, extension | Selection and sampling degradation regimes. |
| 11 | Generalization to out-of-distribution populations | pending, own section | Distinct generalization question, not a robustness pass. |
| 12 | Longitudinal extension | future work | Vitamin D treatment-confounder feedback; not undertaken in this paper. |
| 13 | Counterfactual recourse extension (DiCE) | out of scope | For Andy/Lexi to define and own. |
