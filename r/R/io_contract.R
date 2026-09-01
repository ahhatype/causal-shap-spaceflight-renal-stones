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

#' Provenance columns for an attribution table: run_id (a UUID-like random
#' hex string, avoiding an extra package dependency for one id per run),
#' git_sha (short git SHA, "unknown" if git isn't available), timestamp
#' (UTC ISO 8601). One call per driver script run, attached to every row
#' that run produces - mirrors each Python Step 4/6 driver's own
#' uuid.uuid4()/_git_sha() pattern (see attribution_baseline.py).
attribution_provenance <- function() {
  git_sha <- tryCatch(
    {
      out <- system2("git", c("rev-parse", "--short", "HEAD"), stdout = TRUE, stderr = FALSE)
      if (length(out) == 0) "unknown" else out[1]
    },
    error = function(e) "unknown"
  )
  list(
    run_id = paste(sample(c(0:9, letters[1:6]), 32, replace = TRUE), collapse = ""),
    git_sha = git_sha,
    timestamp = format(Sys.time(), "%Y-%m-%dT%H:%M:%OS6Z", tz = "UTC")
  )
}

#' Write an attribution table to Parquet in ATTRIBUTION_SCHEMA_COLUMNS order.
#'
#' Mirrors write_attributions() in python/src/causal_shap_renal/io_contract.py:
#' same column order, same parquet output, no other transformation.
write_attributions <- function(df, path) {
  missing_cols <- setdiff(ATTRIBUTION_SCHEMA_COLUMNS, names(df))
  if (length(missing_cols) > 0) {
    stop("write_attributions(): missing column(s): ", paste(missing_cols, collapse = ", "))
  }
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  arrow::write_parquet(df[ATTRIBUTION_SCHEMA_COLUMNS], path)
  invisible(path)
}
