# Step 3: simcausal data generation helpers.
#
# Turns config/dag_spec.yaml + config/edge_coefficients.yaml into simcausal
# structural equations and simulates data. simcausal is the sole default
# generator (see docs/methods, Step 3) - it is R-only, no viable Python
# substitute, which is one of the two reasons this repo is two-language
# (see docs/decisions/001-two-language-repo.md).

library(simcausal)
library(yaml)

#' Simulate data from config/dag_spec.yaml + config/edge_coefficients.yaml.
#'
#' TODO: implement once Robert's coefficient review lands.
simulate_renal_stone_data <- function(n = 1000, seed = NULL) {
  stop("not implemented")
}
