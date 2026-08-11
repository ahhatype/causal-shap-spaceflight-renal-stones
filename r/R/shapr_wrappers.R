# Step 6: Heskes et al.'s Causal Shapley Values and Frye et al.'s Asymmetric
# Shapley Values (ASV), both via the shapr package.
#
# shapr is R-native (see docs/decisions/001-two-language-repo.md) - Heskes'
# method uses the confounding argument in explain(), ASV uses the
# asymmetric + causal_ordering arguments. Reference engine is XGBoost
# (Heskes) and SuperLearner as a fallback (ASV), per docs/methods §9.

library(shapr)

#' Heskes et al.'s Causal Shapley Values.
#'
#' TODO: implement once Step 3 data and config/dag_spec.yaml's edge
#' structure are finalized.
run_causal_shapley_values <- function(data, dag_spec, iteration_round = 1) {
  stop("not implemented")
}

#' Frye et al.'s Asymmetric Shapley Values (causal ordering only, no full DAG).
#'
#' TODO: implement.
run_asymmetric_shapley_values <- function(data, causal_ordering, iteration_round = 1) {
  stop("not implemented")
}
