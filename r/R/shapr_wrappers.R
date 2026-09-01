# Step 6: Heskes et al.'s Causal Shapley Values and Frye et al.'s Asymmetric
# Shapley Values (ASV), both nominally via the shapr package's single
# explain() call: per ?shapr::explain, asymmetric=FALSE + confounding=
# <vector> gives Heskes et al. (2020)'s (symmetric) causal Shapley values;
# asymmetric=TRUE + confounding=NULL gives Frye et al. (2020)'s ASV.
# Reference engine is XGBoost for both - see config/model_engines.yaml
# (neither method has a different paper-native engine).
#
# HESKES' METHOD IS CURRENTLY BLOCKED - see
# docs/decisions/006-shapr-heskes-blocked.md. Any explain() call with a
# non-NULL `confounding` argument (required for Heskes' method - scalar
# or vector, TRUE or FALSE, doesn't matter) hangs indefinitely past
# "Computing v(S)" in this environment; confounding=NULL (ASV) is
# unaffected and completes in seconds. Reproduced on a minimal 5-feature
# synthetic glm() model with no custom wrapper involved, ruling out
# xgboost/data/our own code as the cause - isolated to shapr 1.0.8's
# internal Shapley-weight-combination step for confounding-aware causal
# orderings specifically. run_causal_shapley_values() below raises a
# clear error rather than attempting the call; pipeline/
# step06a_causal_shapley_asv.R runs ASV only and reports this explicitly.
#
# explain()'s model is NOT passed as the raw xgb.Booster from
# r/R/engines.R's fit_xgboost(), even though shapr has native
# predict_model support for that class (get_supported_models() lists
# "xgb.Booster"): the installed xgboost (3.2.1.1) stores the Booster's
# handle as a custom ALTREP class ("XGBAltrepPointerClass") that shapr's
# internal future.apply::future_lapply() batch computation cannot export
# safely, crashing every run with "ALTLIST classes must provide a Set_elt
# method" regardless of future/globals package version (tried 1.33.2/
# 1.70.0 and 0.16.3/0.19.1) or the future.globals.onReference option -
# a genuine environment limitation, not a usage error, verified by
# reproducing it from a minimal explain() call during Step 6
# implementation. Fixed by wrapping the fitted model as raw serialized
# bytes (xgb.save.raw()) in a plain list - see xgb_predict_wrapper()
# below - which shapr treats as an "unsupported" model class via explicit
# predict_model/get_model_specs functions (both documented as always
# honored, even for natively-supported classes, per ?shapr::explain).
# A plain "raw" vector has no custom ALTREP class, so it exports cleanly.

library(shapr)

#' Wrap a fitted xgb.Booster as a plain-list model shapr can export safely
#' across its internal future_lapply() batches - see this file's header
#' comment for why the raw Booster object can't be passed directly.
#' Returns a list with $predict_model and $get_model_specs functions ready
#' to pass straight through to explain()'s own arguments of the same name.
xgb_predict_wrapper <- function(model, features) {
  raw <- xgboost::xgb.save.raw(model)
  # predict_model() is called once per coalition (potentially thousands of
  # times per explain() call) - xgb.load.raw() deserializes the whole
  # Booster from bytes, which is expensive to repeat that often. Cache the
  # deserialized Booster in this closure's own environment so it's loaded
  # at most once per R process, verified necessary by timing a single
  # explain() call during Step 6 implementation (it did not finish in 150s
  # against a 200-row/50-coalition toy case before this fix, and completed
  # in a few seconds after it).
  cache <- new.env(parent = emptyenv())
  list(
    model = list(raw = raw, feature_names = features),
    predict_model = function(x, newdata, ...) {
      if (is.null(cache$booster)) cache$booster <- xgboost::xgb.load.raw(x$raw)
      predict(cache$booster, as.matrix(newdata))
    },
    get_model_specs = function(x) {
      list(
        labels = x$feature_names,
        classes = setNames(rep(NA, length(x$feature_names)), x$feature_names),
        factor_levels = setNames(vector("list", length(x$feature_names)), x$feature_names)
      )
    }
  )
}

#' Cap on the number of feature coalitions shapr's iterative procedure may
#' sample (of 2^13 = 8192 possible for this DAG's 13 features) - bounds
#' runtime to a tractable range. 500 is an implementation choice (an
#' LLM-authored one, not derived from the shapr package or either paper -
#' see docs/step06_results.md's "LLM-made decisions" table), traded off
#' against wall-clock time across 6 shapr calls per driver run (2 methods
#' x 3 rounds).
SHAPR_MAX_COALITIONS <- 500

#' 80/20 train/explain split, same convention as Step 4's
#' attribution_baseline.py (train_test_split, stratified on the outcome).
#' shapr's own computational cost scales mainly with the number of
#' coalitions and x_train's size (used to estimate each v(S)), not
#' x_explain's row count, but explaining a held-out slice rather than the
#' full training set matches Step 4's practice and keeps x_explain's own
#' prediction step cheap too.
shapr_train_explain_split <- function(data, features, seed = 20260812, explain_frac = 0.2) {
  set.seed(seed)
  n <- nrow(data)
  n_explain <- max(50, round(n * explain_frac))
  explain_idx <- sample.int(n, n_explain)
  list(
    x_train = data[-explain_idx, features],
    y_train = data[["nephrolithiasis"]][-explain_idx],
    x_explain = data[explain_idx, features]
  )
}

#' Build shapr's causal_ordering (a list of character vectors, one per
#' topological depth layer) from config/dag_spec.yaml, via
#' dag_spec_positions()'s already-computed depth layering (r/R/dag_utils.R).
#' Excludes the outcome - shapr's causal_ordering only covers x_explain's
#' own features. Ties within a layer break alphabetically, matching
#' dag_spec_positions()'s own tie-break.
#'
#' promote: feature names to split OUT of their tied depth-layer into their
#' own new singleton group placed immediately before the rest of that
#' layer - asserting "more upstream than the naive depth-tie assumed".
#' Verified necessary during Step 6 implementation: shapr's causal_ordering
#' treats each list element as an unordered SET (ties are computed
#' symmetrically among a group's own members; only the sequence of GROUPS
#' constrains anything) - simply re-sorting names within one vector, an
#' earlier version of this function's approach, is a silent no-op against
#' explain()'s actual output. Promoting a feature into its own group is
#' the smallest change that genuinely alters the causal ordering shapr
#' computes against.
build_causal_ordering <- function(spec, promote = character(0)) {
  pos <- dag_spec_positions(spec)
  is_outcome <- vapply(spec$nodes, function(n) identical(n$type, "outcome"), logical(1))
  outcome_id <- spec$nodes[[which(is_outcome)]]$id
  pos[[outcome_id]] <- NULL

  depths <- vapply(pos, function(p) p[["x"]], numeric(1))
  ordering <- lapply(sort(unique(depths)), function(d) sort(names(depths)[depths == d]))

  for (feat in promote) {
    for (i in seq_along(ordering)) {
      if (!(feat %in% ordering[[i]])) next
      rest <- setdiff(ordering[[i]], feat)
      if (length(rest) == 0) break  # already its own group - nothing to split
      ordering <- append(ordering, list(feat), after = i - 1)
      ordering[[i + 1]] <- rest
      break
    }
  }
  ordering
}

#' Heskes et al.'s Causal Shapley Values (NeurIPS 2020).
#'
#' BLOCKED in this environment - see this file's header comment and
#' docs/decisions/006-shapr-heskes-blocked.md. Raises immediately rather
#' than calling explain() with a non-NULL `confounding` argument, which
#' hangs indefinitely rather than erroring (confirmed via `timeout`,
#' reproduced down to a minimal synthetic case with no custom wrapper).
#' Left implemented (not deleted) so this becomes a one-line fix - drop
#' the stop() below - if/when a shapr release fixes the underlying issue.
run_causal_shapley_values <- function(data, dag_spec, iteration_round = 1,
                                       confounded_groups = NULL,
                                       within_tier_order = NULL,
                                       seed = 20260812) {
  stop(
    "run_causal_shapley_values() is blocked in this environment: shapr::explain() ",
    "hangs indefinitely whenever `confounding` is non-NULL (required for Heskes' ",
    "method), regardless of model/data/approach. See ",
    "docs/decisions/006-shapr-heskes-blocked.md for the full reproduction. ",
    "ASV (run_asymmetric_shapley_values(), confounding=NULL) is unaffected."
  )
}

#' Frye et al.'s Asymmetric Shapley Values (NeurIPS 2020) - causal ordering
#' only (no confounding argument).
#'
#' promote: passed straight through to build_causal_ordering() - round 1
#' passes character(0) (the naive depth-tie ordering, no promotions, a
#' genuinely uninformed default); round 2/3 pass features flagged by
#' asv_revise_promotions()'s scripted heuristic.
run_asymmetric_shapley_values <- function(data, dag_spec, iteration_round = 1,
                                           promote = character(0),
                                           seed = 20260812) {
  features <- model_features(dag_spec)
  split <- shapr_train_explain_split(data, features, seed = seed)

  model <- fit_xgboost(split$x_train, split$y_train, seed = seed)
  wrapped <- xgb_predict_wrapper(model, features)
  ordering <- build_causal_ordering(dag_spec, promote = promote)

  set.seed(seed)
  explanation <- explain(
    model = wrapped$model,
    x_explain = split$x_explain,
    x_train = split$x_train,
    approach = "empirical",
    phi0 = mean(split$y_train),
    asymmetric = TRUE,
    causal_ordering = ordering,
    confounding = NULL,
    max_n_coalitions = SHAPR_MAX_COALITIONS,
    seed = seed,
    verbose = NULL,
    predict_model = wrapped$predict_model,
    get_model_specs = wrapped$get_model_specs
  )
  shapr_explanation_to_long(explanation, features, "asymmetric_shapley_values", "xgboost", dag_spec, iteration_round)
}

#' Count each dag_spec node's number of incoming edges.
n_parents <- function(spec) {
  ids <- vapply(spec$nodes, function(n) n$id, character(1))
  parents <- setNames(rep(0L, length(ids)), ids)
  for (e in spec$edges) parents[[e$to]] <- parents[[e$to]] + 1L
  parents
}

#' Step 6 HITL round-2/3 scripted revision heuristic for Heskes Causal
#' Shapley Values: flags a causal_ordering GROUP (not an individual
#' feature - confounding is shapr's per-group argument) as confounding=TRUE
#' if any of its features has >1 parent in dag_spec.yaml AND the prior
#' round's |attribution - ground truth| exceeds that round's median error
#' across all features.
#'
#' This is an LLM-authored scripted stand-in for the methods doc's "Robert
#' reviews and revises" step, NOT a finding from the shapr package or the
#' Heskes et al. paper - both the >1-parent trigger and the median-error
#' threshold are implementation choices with no basis in either source.
#' See docs/step06_results.md's "LLM-made decisions" table for the full
#' list, including that pipeline/step06a_causal_shapley_asv.R accumulates
#' flagged groups monotonically across rounds (round 3 keeps everything
#' round 2 flagged, plus anything newly high-error) rather than
#' recomputing fresh each round.
heskes_revise_confounding <- function(prior_round_attributions, ground_truth, dag_spec, ordering) {
  gt <- setNames(ground_truth$true_total_effect_abs, ground_truth$feature)
  attr_val <- setNames(prior_round_attributions$attribution_value, prior_round_attributions$feature)
  common <- intersect(names(gt), names(attr_val))
  err <- abs(attr_val[common] - gt[common])
  threshold <- stats::median(err)
  parents <- n_parents(dag_spec)
  high_error_multi_parent <- names(err)[err > threshold & parents[names(err)] > 1]

  flagged <- integer(0)
  for (i in seq_along(ordering)) {
    if (any(ordering[[i]] %in% high_error_multi_parent)) flagged <- c(flagged, i)
  }
  flagged
}

#' Step 6 HITL round-2/3 scripted revision heuristic for ASV: promote the
#' single feature with the highest prior-round |attribution - ground
#' truth| (among features not already promoted, and only from a tied
#' depth-tier with >1 member - promoting an already-singleton feature is a
#' no-op, see build_causal_ordering()) into its own earlier causal_ordering
#' group. Accumulates monotonically across rounds, same convention as
#' heskes_revise_confounding() (round 3's `promote` vector is round 2's
#' plus one more name).
#'
#' This is an LLM-authored scripted stand-in for the methods doc's "Robert
#' reviews and revises" step, NOT a finding from the shapr package or the
#' Frye et al. paper - both "promote the single worst feature" and
#' "highest prior-round error" are implementation choices with no basis in
#' either source. See docs/step06_results.md's "LLM-made decisions" table.
asv_revise_promotions <- function(prior_round_attributions, ground_truth, dag_spec, already_promoted) {
  gt <- setNames(ground_truth$true_total_effect_abs, ground_truth$feature)
  attr_val <- setNames(prior_round_attributions$attribution_value, prior_round_attributions$feature)
  common <- intersect(names(gt), names(attr_val))
  err <- abs(attr_val[common] - gt[common])

  ordering <- build_causal_ordering(dag_spec)
  tie_size <- setNames(rep(1L, length(common)), common)
  for (group in ordering) tie_size[intersect(group, common)] <- length(group)

  candidates <- setdiff(names(err)[tie_size[names(err)] > 1], already_promoted)
  if (length(candidates) == 0) return(already_promoted)
  worst <- candidates[which.max(err[candidates])]
  union(already_promoted, worst)
}

#' shapr's explain() returns a shapr object whose $shapley_values_est is a
#' data.table (one row per explained observation: explain_id, none, one
#' column per feature). Global feature importance here means the same thing
#' Step 4's baseline does (docs/step04_results.md): mean |SHAP value|
#' across the explained set. Pivots to ATTRIBUTION_SCHEMA_COLUMNS long
#' format so this feeds write_attributions() the same way every other
#' Step 6 method's output does.
shapr_explanation_to_long <- function(explanation, features, method, engine, dag_spec, iteration_round) {
  sv <- as.data.frame(explanation$shapley_values_est)
  mean_abs <- vapply(features, function(f) mean(abs(sv[[f]])), numeric(1))
  data.frame(
    method = method,
    engine = engine,
    dag_variant = "renal_stone_baseline",
    iteration_round = iteration_round,
    feature = features,
    attribution_value = as.numeric(mean_abs),
    stringsAsFactors = FALSE
  )
}
