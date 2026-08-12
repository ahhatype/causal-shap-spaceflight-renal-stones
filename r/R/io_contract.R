# Read/write helpers for the R <-> Python interchange contract.
#
# Mirrors python/src/causal_shap_renal/io_contract.py -
# keep the two in sync by hand.

library(arrow)
library(yaml)

ATTRIBUTION_SCHEMA_COLUMNS <- c(
  "method", "engine", "dag_variant", "iteration_round",
  "feature", "attribution_value", "run_id", "git_sha", "timestamp"
)

#' Load config/dag_spec.yaml.
#'
#' TODO: implement.
read_dag_spec_yaml <- function(path) {
  stop("not implemented")
}

#' Write simulated data (Step 3) to Parquet for Python consumers to read.
#'
#' TODO: implement.
write_simulated_data <- function(data, path) {
  stop("not implemented")
}

#' Write an attribution table to Parquet in ATTRIBUTION_SCHEMA_COLUMNS order.
#'
#' TODO: implement.
write_attributions <- function(df, path) {
  stop("not implemented")
}
