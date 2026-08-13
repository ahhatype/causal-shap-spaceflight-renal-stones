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

read_dag_spec_yaml <- function(path) {
  stop("not implemented")
}

write_simulated_data <- function(data, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  arrow::write_parquet(data, path)
  invisible(path)
}

#' Write an attribution table to Parquet in ATTRIBUTION_SCHEMA_COLUMNS order.
#'
#' TODO: implement.
write_attributions <- function(df, path) {
  stop("not implemented")
}
