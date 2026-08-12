# Predictive-engine resolution for Step 6 driver scripts.
#
# A single named switch so each Step 6 driver script asks for "the primary
# engine" or "the secondary-check engine" for a given method by name,
# resolved from config/model_engines.yaml, rather than hardcoding a
# specific model call inline. See docs/decisions/004-xgboost-primary-engine.md
# for why XGBoost is the current default and why SuperLearner isn't used
# here (Step 4's own KernelExplainer/PermutationExplainer + SuperLearner
# pairing is untouched by this file).

library(yaml)

#' Read config/model_engines.yaml.
read_engine_config <- function(path = "../config/model_engines.yaml") {
  yaml::read_yaml(path)
}

#' Look up the engine assignment for a given Step 6 method id (e.g.
#' "causal_shapley_values", "shapley_flow", "asv", "causal_shap_ng_et_al"),
#' as declared in config/model_engines.yaml's methods list.
engine_for_method <- function(method_id, config = read_engine_config()) {
  matched <- Filter(function(m) identical(m$method, method_id), config$methods)
  if (length(matched) == 0) {
    stop(
      "No engine entry for method '", method_id,
      "' in config/model_engines.yaml"
    )
  }
  matched[[1]]
}

#' Fit a named engine on (X, y) and return a fitted model object.
#'
#' Supported engine names: "xgboost", "random_forest". "superlearner" is
#' deliberately not implemented here - see engines.superlearner.note in
#' config/model_engines.yaml for why it isn't used in Step 6.
#'
#' TODO: fit_xgboost() / fit_random_forest() are stubs. Wire up the actual
#' model-fitting calls (xgboost::xgboost(), randomForest::randomForest() or
#' ranger::ranger()) once a Step 6 driver script (step06a/b/c/d) is
#' implemented and has real hyperparameter choices to make - only the
#' resolution/dispatch layer in this file is meant to be usable now.
fit_engine <- function(engine_name, X, y, ...) {
  switch(engine_name,
    xgboost = fit_xgboost(X, y, ...),
    random_forest = fit_random_forest(X, y, ...),
    superlearner = stop(
      "Engine 'superlearner' is not used in Step 6 - see engines.superlearner.note ",
      "in config/model_engines.yaml and docs/decisions/004-xgboost-primary-engine.md"
    ),
    stop(
      "Unsupported engine: '", engine_name,
      "'. See config/model_engines.yaml for the currently supported set."
    )
  )
}

fit_xgboost <- function(X, y, ...) {
  stop("not implemented - wire up xgboost::xgboost() here when a Step 6 driver script is built")
}

fit_random_forest <- function(X, y, ...) {
  stop("not implemented - wire up randomForest::randomForest() or ranger::ranger() here when a Step 6 driver script is built")
}
