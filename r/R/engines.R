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

#' Fit an xgboost::xgboost() binary classifier. Returns the raw xgb.Booster
#' object (not wrapped) so shapr's explain() can use its native
#' predict_model.xgb.Booster dispatch directly - shapr has built-in support
#' for this class, verified during Step 6 planning.
#'
#' Uses the xgboost>=3 R API (x=/y= rather than the older data=/label=/
#' params=list(...) form - the installed version, 3.2.1.1, deprecates the
#' old form with warnings and shapr's internal handling of the resulting
#' Booster object requires the new-API object shape).
fit_xgboost <- function(X, y, seed = 20260812, nrounds = 100, ...) {
  xgboost::xgboost(
    x = as.matrix(X),
    y = factor(y),
    objective = "binary:logistic",
    eval_metric = "logloss",
    nrounds = nrounds,
    seed = seed,
    verbosity = 0,
    ...
  )
}

#' Fit a randomForest::randomForest() binary classifier (y as a factor, so
#' predict(..., type = "prob") returns class probabilities). shapr has no
#' native support for this class - callers that need shapr-compatible
#' output should use fit_xgboost() instead; this is provided for Step 6
#' driver scripts (and Step 8) that call predict() directly.
fit_random_forest <- function(X, y, seed = 20260812, ntree = 500, ...) {
  set.seed(seed)
  randomForest::randomForest(x = X, y = factor(y), ntree = ntree, ...)
}
