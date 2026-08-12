# ADR 001: Two-language repo (R and Python)

## Status
Accepted

## Decision
This repo runs both R and Python as first-class languages, rather than picking one.

## Context
The methods doc names specific packages per step, and they split cleanly by language with no good way around it:

- `simcausal` (Step 3, the sole default data generator) is R-only.
- `pcalg::ida()` (Ng et al.'s Causal SHAP in Step 6 needs PC plus IDA) is R-only. `causal-learn` in Python has PC but no IDA equivalent.
- `shapr` (Heskes Causal Shapley Values and ASV, Step 6) is R-native. A Python port exists but is a thin wrapper that calls R underneath, not a native implementation.
- `shap`'s named explainers (TreeExplainer, LinearExplainer, KernelExplainer, PermutationExplainer, Step 4), `shapflow` (Shapley Flow, Step 6), and `lingam` (Step 8) are the original authors' own Python implementations.
- NOTEARS (Step 8) has a canonical Python reference implementation; R ports exist but are not well maintained.
- PC and GES (Step 8) exist in both `pcalg` (R) and `causal-learn` (Python). Since PC is already produced in R for Step 6 (to feed IDA), Step 8 reuses that same R-produced CPDAG rather than recomputing it in Python.

## Consequences
- R handles: DAG ingestion, `simcausal` data generation, `shapr` (Heskes + ASV), PC/IDA, GES.
- Python handles: out-of-box SHAP (Step 4), Shapley Flow, the structural Causal SHAP prototype, NOTEARS, LiNGAM, and the evaluation/metrics layer.
- The two languages talk to each other only through files, never a runtime bridge (no `reticulate`, no `rpy2`). See ADR 002 for the interchange format.
- Two separate locked environments (`r/renv.lock`, `python/uv.lock`) need to be kept in sync when dependencies change.
