# ADR 002: File-based interchange contract between R and Python

## Status
Accepted

## Decision
R and Python exchange data only through files on disk, in one of two formats depending on what's being exchanged. No cross-language runtime bridge is used anywhere in the pipeline.

## Format choices
- **DAG spec and coefficients** (`config/dag_spec.yaml`, `config/edge_coefficients.yaml`): YAML. Both `yaml::read_yaml()` (R) and `pyyaml` (Python) read it with no extra tooling, and it stays human-editable for Robert's review passes.
- **Simulated data, frozen ground truth, PC/CPDAG output**: Parquet via Apache Arrow. `arrow` (R) and `pyarrow`/`pandas` (Python) read and write it natively with types preserved, which CSV does not guarantee across languages (dates, factors/categoricals, integer vs. double).
- **Attribution outputs**, regardless of which language produced them: a single long-format Parquet schema, one row per (method, feature, iteration round):

  ```
  method, engine, dag_variant, iteration_round, feature, attribution_value, run_id, git_sha, timestamp
  ```

  This lets the evaluation layer (Kendall's tau, Spearman's rho, top-k recovery, NDCG@k, PBI, POA) score R-produced attributions (`shapr`'s Heskes/ASV output) and Python-produced attributions (out-of-box SHAP, Shapley Flow, the structural prototype) with the same code path, with no per-method special casing.

## Consequences
- Every step's driver script is responsible for writing its output in the agreed schema before the next step can consume it. `r/R/io_contract.R` and `python/src/causal_shap_renal/io_contract.py` implement matching read/write functions and should be kept in sync by hand (there is no schema codegen here, the schema is small enough not to warrant it).
- No step can silently depend on another language's in-memory state. That's a deliberate constraint: it also enforces the "frozen output artifacts" and "compute ground truth before and independently of the attribution comparison" requirements from the methods doc's reproducibility section.
