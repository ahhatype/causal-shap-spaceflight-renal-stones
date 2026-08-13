# ADR 004: XGBoost as the primary predictive engine for Step 6

## Status
Accepted

## Decision
XGBoost is the primary predictive engine for all four Step 6 causal-SHAP methods (Heskes Causal Shapley Values, Shapley Flow, ASV, Ng et al.'s Causal SHAP), held constant across the comparison so engine choice is not a second axis of variation alongside method choice. Ng et al.'s method additionally runs a secondary Random Forest pass - the engine explicitly named in its own paper - as a replication check; Heskes Causal Shapley Values and Shapley Flow need no separate secondary run since XGBoost already is their own papers' engine. ASV's paper names no engine, so it has no secondary check either way. SuperLearner is not used in Step 6 for v1. Engine choice is implemented as a single named, config-driven switch (`config/model_engines.yaml`, `r/R/engines.R`, `python/src/causal_shap_renal/engines.py`) rather than hardcoded per driver script.

## Context
The original design paired each method with the engine used in its own originating publication (XGBoost for Heskes and Shapley Flow, Random Forest for Ng et al., a stacked-ensemble fallback for ASV, whose paper names no engine), plus "at least one common-engine comparison... so that observed differences can be attributed to the method rather than to the learner" - without specifying which engine that common run should use.

SuperLearner was considered as that uniform engine, since it was already the established fallback/black-box engine in Step 4. It was rejected for Step 6 specifically for two reasons:

1. **Cost.** SuperLearner fits a whole candidate library of learners under cross-validation (a 6-learner library at 10-fold CV is roughly 60+ individual model fits behind one `SuperLearner()` call), and every SHAP-style evaluation calls `predict()` on every learner in the library. Step 6's methods already require very large evaluation counts (Ng et al.'s own benchmark: 366s for causal SHAP value computation alone, Monte Carlo-dominated, on a 31-feature dataset), multiplied further by 3 human-in-the-loop iteration rounds across 4 methods. Making SuperLearner the primary engine everywhere would multiply that cost, not just add it once.
2. **No candidate library was ever defined.** "SuperLearner" had been used as a stand-in for "some flexible stacked ensemble" without specifying which base learners it contains - a real design decision that would need resolving before any cost or behavior estimate involving it could be trusted.

XGBoost was chosen instead because it is markedly cheaper (one model, one `predict()` per evaluation, no cross-validated stacking), already the paper-native engine for two of the four methods, and a reasonable fit for this project's own data-generating process: `config/edge_coefficients.yaml` specifies structural equations that are linear (or log-linear, for the logit-linked outcome) on the standardized scale, which gradient-boosted trees approximate well - unlike real unknown data, where a flexible ensemble's ability to adapt to an unknown functional form matters more.

Checking each method's actual integration surface found engine choice isn't blocked by dependencies in general: `shapr` (Heskes, ASV) accepts an arbitrary model via a custom prediction function; Ng et al.'s method is a from-scratch implementation of the paper's Algorithm 1 with no external engine constraint at all. Shapley Flow (`shapflow`) is the one method whose reference implementation is demonstrated only with XGBoost and hasn't been confirmed to accept a different engine cleanly - worth verifying specifically once that package is wired up, not a reason to avoid a config-driven switch for the other three.

This decision is scoped to Step 6 only. Step 4's `KernelExplainer + SuperLearner` / `PermutationExplainer + SuperLearner` pairing is untouched - Step 4's own design deliberately keeps multiple explainer/model combinations to test whether standard SHAP's failure is model-class-specific, which is a different question from Step 6's method-comparison design.

## Consequences
- `config/model_engines.yaml` is the single source of truth for which engine each Step 6 method uses (primary, fallback, and secondary-check), read by both languages.
- `r/R/engines.R` and `python/src/causal_shap_renal/engines.py` provide a named `fit_engine(name, ...)` switch; Step 6 driver scripts ask for an engine by name rather than hardcoding a specific model call. The actual model-fitting bodies (`fit_xgboost`, `fit_random_forest`) are stubs until Step 6 itself is implemented - only the resolution/dispatch layer is real code right now.
- SuperLearner is not deleted from the project's vocabulary, just not used in Step 6 v1: revisiting it requires first defining a candidate library and re-budgeting Step 6's compute cost, not just flipping a config value.
- If Shapley Flow turns out not to accept an XGBoost model cleanly when implemented, that must be documented explicitly in `config/model_engines.yaml`'s note field for that method, not silently worked around.
