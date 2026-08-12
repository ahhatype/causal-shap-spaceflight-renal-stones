# PC discovery and IDA, used in two places:
#   Step 6: the PC stage of Ng et al.'s Causal SHAP (pipeline/step06d_pc_ida.R)
#   Step 8: DAG recovery comparison, reusing Step 6's PC/CPDAG rather than
#           recomputing it (see docs/decisions, "Step 8 reuses Step 6's PC output")
#
# pcalg::ida() is R-only - causal-learn (Python) has PC but no IDA equivalent.

library(pcalg)
library(graph)

#' Run PC to get a CPDAG, then IDA for causal-effect bounds.
#'
#' TODO: implement once Step 3 data exists to run discovery against.
run_pc_ida <- function(data, alpha = 0.05) {
  stop("not implemented")
}

#' Run GES (Step 8, score-based discovery family).
#'
#' TODO: implement.
run_ges <- function(data) {
  stop("not implemented")
}
