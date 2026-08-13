# ADR 005: Real SuperLearner deferred for Step 4's KernelExplainer/PermutationExplainer pairing

## Status
Accepted

## Decision
Step 4's `KernelExplainer + SuperLearner` / `PermutationExplainer + SuperLearner` pairing, as specified in `docs/methods`, is not implemented with real SuperLearner (the CRAN R package) for this round. Both explainers instead explain the already-fitted XGBoost model (the same one `TreeExplainer` explains exactly) as a black box: `python/src/causal_shap_renal/attribution_baseline.py`'s `kernel_shap`/`permutation_shap` rows use engine `xgboost_blackbox`, not a stacked ensemble.

## Context
Real SuperLearner is R-only (CRAN, no Python equivalent package). `KernelExplainer` and `PermutationExplainer` are Python `shap` explainers that query the model many times on synthetic, on-the-fly perturbed feature rows (`KernelExplainer`'s `nsamples="auto"` resolves to `2*M + 2048` calls; `PermutationExplainer`'s `max_evals="auto"` resolves to `10*2*M` calls, per `shap`'s own source - both confirmed against this repo's installed `shap` 0.52.0). Those synthetic rows can't be precomputed and handed off as a file the way Step 3's simulated data or Step 4a's ground truth are - each one is generated during the explainer's own sampling loop. Calling a real R-fitted SuperLearner model from inside that Python loop would require a cross-language runtime bridge (`reticulate` or `rpy2`), which `docs/decisions/001-two-language-repo.md` explicitly rules out: "R and Python never talk to each other at runtime."

`config/model_engines.yaml`'s own note (written for Step 6, not Step 4) already flags SuperLearner's cross-validated candidate-library fitting as expensive in compute time; the same concern compounds here, since every one of `KernelExplainer`/`PermutationExplainer`'s thousands of calls would additionally re-invoke a multi-learner ensemble internally rather than a single model.

Using the already-fitted XGBoost model as the black-box target instead is not just a workaround - it's a genuine validation in its own right, comparing `KernelExplainer`'s/`PermutationExplainer`'s *approximate* Shapley estimates against `TreeExplainer`'s *exact* computation on the identical model. Verified directly: `tree_shap+xgboost` (put on the same log-odds scale as the other three logit-link pairings, see `attribution_baseline.py`'s module docstring) lands in the same magnitude range and rank order as `kernel_shap+xgboost_blackbox` and `permutation_shap+xgboost_blackbox` on this run's data.

The tradeoff: this round's five pairings no longer include a genuinely distinct fourth model class (a stacked ensemble). The "is standard SHAP's failure model-class-specific" question Step 4 asks is answered across {random forest, XGBoost, logistic regression} this round, not across four classes.

The correct fix, deferred rather than built now: compute Kernel/Permutation-style SHAP entirely in R, against a real R-fitted SuperLearner model, using the CRAN `kernelshap` package (`kernelshap()`/`permshap()` - purpose-built black-box Kernel/permutation Shapley values, the direct R-side equivalent of `shap`'s `KernelExplainer`/`PermutationExplainer`). Running the whole pairing in one language needs no runtime bridge at all, and fits the same per-package split already used for Step 6 (`shapr`/`pcalg` in R, `shapflow`/the structural prototype in Python - see ADR 001).

## Consequences
- `results/attributions/step04_baseline_shap.parquet`'s `kernel_shap`/`permutation_shap` rows carry `engine="xgboost_blackbox"`, not a SuperLearner/stacking engine name - any downstream reader (evaluation, write-up) must not describe this round's Step 4 as having tested a stacked-ensemble black box.
- Revisiting real SuperLearner means adding a new R driver (e.g. `pipeline/step04b_superlearner_shap.R`) that fits SuperLearner and computes `kernelshap()`/`permshap()` against it, writing to the same shared attribution Parquet schema (`docs/decisions/002-data-interchange-contract.md`) alongside Step 4a's ground truth and Step 4's Python output - not a change to this ADR's Python code.
- If `kernelshap`/`permshap` turn out not to accept a fitted `SuperLearner` object cleanly, that must be documented explicitly when attempted, not silently worked around.
