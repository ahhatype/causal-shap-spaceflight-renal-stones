# Step 3: simcausal data generation helpers.
#
# Turns config/dag_spec.yaml + config/edge_coefficients.yaml into simcausal
# structural equations and simulates data. simcausal is the sole default
# generator (see docs/methods, Step 3) - it is R-only, no viable Python
# substitute, which is one of the two reasons this repo is two-language
# (see docs/decisions/001-two-language-repo.md).
#
# Everything here is config-driven.
#
# simcausal usage here follows the package vignette
# (https://cran.r-project.org/web/packages/simcausal/vignettes/simcausalVignette.pdf):
# DAG.empty() + node() + set.DAG() + sim() (Sec. 2.1, p.5), our single
# time-point structure mirrors the worked example in Sec. 3.1 (p.12)
# exactly (root nodes via rnorm/rbern/rnorm_trunc, mediators via rnorm with
# a linear-combination mean, the binary outcome via rbern(plogis(...))).

library(simcausal)
library(yaml)

source("../r/R/dag_utils.R")   

rnorm_trunc <- function(n, mean, sd, minval = 0) {
  out <- rnorm(n = n, mean = mean, sd = sd)
  minval <- minval[1]
  out[out < minval] <- minval
  out
}

rnorm_trunc2 <- function(n, mean, sd, minval, maxval) {
  out <- rnorm(n = n, mean = mean, sd = sd)
  out[out < minval[1]] <- minval[1]
  out[out > maxval[1]] <- maxval[1]
  out
}

# simcausal's node() rejects any name containing "_" 
node_alias <- function(id) gsub("_", "", id, fixed = TRUE)

dealias_columns <- function(df, spec) {
  ids <- vapply(spec$nodes, function(nd) nd$id, character(1))
  alias_to_id <- setNames(ids, node_alias(ids))
  matched <- names(df) %in% names(alias_to_id)
  names(df)[matched] <- alias_to_id[names(df)[matched]]
  df
}

root_lookup <- function(coefs) {
  setNames(
    coefs$root_node_distributions,
    vapply(coefs$root_node_distributions, function(rn) rn$node, character(1))
  )
}

add_root_node <- function(D, rn) {
  D + do.call(node, c(list(name = node_alias(rn$node), distr = rn$distr), rn$params))
}

zterm <- function(node_id, coefs) {
  root <- root_lookup(coefs)[[node_id]]
  alias <- node_alias(node_id)
  if (!is.null(root) && !is.null(root$unit)) {
    # raw-unit continuous root node: full z-score
    sprintf("((%s - %s) / %s)", alias, root$params$mean, root$params$sd)
  } else if (!is.null(root) && identical(root$distr, "rbern")) {
    # binary root node: mean-centered only (not scaled by SD) so it doesn't
    # shift a downstream standardized node's mean away from 0 - its own
    # column stays raw 0/1, only its use as a predictor elsewhere changes
    sprintf("(%s - %s)", alias, root$params$prob)
  } else {
    alias
  }
}

build_mean_formula <- function(node_id, coefs) {
  edges_in <- Filter(function(e) identical(e$to, node_id), coefs$coefficients)
  terms <- vapply(edges_in, function(e) {
    if (!is.null(e$interacts_with)) {
      sprintf("%s * %s * %s", e$coefficient, zterm(e$from, coefs), zterm(e$interacts_with, coefs))
    } else {
      sprintf("%s * %s", e$coefficient, zterm(e$from, coefs))
    }
  }, character(1))
  paste(terms, collapse = " + ")
}

#' Residual/noise SD so a node's total variance equals 1
#' (composite_node_parameterization's residual_rule), computed empirically
#' rather than as a sum of independent coefficient^2*parent_variance terms.
#' The independent-paths assumption is wrong whenever a node's parents are
#' themselves correlated - e.g. urinary_calcium_excretion reaches
#' nephrolithiasis both directly (the interaction term) and indirectly
#' through urine_chemistry, so their contributions covary rather than
#' adding independently. D_partial already contains every node up to
#' (not including) node_id, in topological order, so simulating it and
#' evaluating node_id's own formula against that draw measures the
#' explained variance exactly, correlations included, instead of
#' approximating it. Same underlying idea as calibrate_intercept() below,
#' generalized from a binary intercept to a continuous residual SD.
empirical_residual_sd <- function(D_partial, node_id, coefs, cal_n = 20000, seed = NULL) {
  cal_data <- sim(DAG = set.DAG(D_partial), n = cal_n, rndseed = seed)
  explained <- eval(str2lang(build_mean_formula(node_id, coefs)), envir = as.list(cal_data))
  var_explained <- var(explained)
  if (var_explained >= 1) {
    warning(sprintf(
      "%s: incoming paths explain >=100%% of variance empirically (%.3f) - flag for Robert's calibration review",
      node_id, var_explained
    ))
    return(0.01)
  }
  sqrt(1 - var_explained)
}

add_generic_node <- function(D, node_id, coefs, seed = NULL) {
  node_args <- list(
    name = node_alias(node_id),
    distr = "rnorm",
    mean = str2lang(build_mean_formula(node_id, coefs)),
    sd = empirical_residual_sd(D, node_id, coefs, seed = seed)
  )
  D + do.call(node, node_args)
}

#' dag_spec_positions() pre-allocates its result list keyed by
#' dag_spec.yaml's raw declaration order and only fills in values, so its
#' key order is NOT topological - sort explicitly by the depth (x) it
#' computes, alphabetical tie-break to match its own layer ordering.
node_order <- function(spec) {
  pos <- dag_spec_positions(spec)
  depth <- vapply(pos, function(p) p[["x"]], numeric(1))
  names(depth)[order(depth, names(depth))]
}

build_dag <- function(spec, coefs, seed = NULL) {
  order <- node_order(spec)
  roots <- root_lookup(coefs)
  D <- DAG.empty()
  for (id in order) {
    if (identical(id, coefs$outcome_calibration$node)) next   # added after calibration, see below
    if (id %in% names(roots)) {
      D <- add_root_node(D, roots[[id]])
    } else {
      D <- add_generic_node(D, id, coefs, seed = seed)
    }
  }
  D
}

#' Solve for the logistic intercept b0 so that mean(plogis(b0 + driver_draws))
#' hits target_prevalence, where driver_draws is the outcome's full linear
#' predictor (already summed across every incoming edge - see
#' build_calibrated_dag()'s use of build_mean_formula()), not a single term.
calibrate_intercept <- function(driver_draws, target_prevalence) {
  f <- function(b0) mean(plogis(b0 + driver_draws)) - target_prevalence
  uniroot(f, interval = c(-10, 10))$root
}

#' nephrolithiasis has multiple incoming edges (duration, sex,
#' hydration_fluid_intake, urine_chemistry, and the urinary_calcium_excretion
#' x hydration_fluid_intake interaction - config/dag_spec.yaml collapses the
#' Mineralized Renal Material intermediate directly onto this node, see its
#' own note), so its driver is built the same way any generic node's mean
#' formula is (build_mean_formula()), then calibrated as a whole rather than
#' scaled from a single edge's coefficient.
build_calibrated_dag <- function(seed = NULL) {
  spec  <- read_dag_spec("../config/dag_spec.yaml")
  coefs <- yaml::read_yaml("../config/edge_coefficients.yaml")

  D0 <- build_dag(spec, coefs, seed = seed)   # everything except nephrolithiasis
  D0set <- set.DAG(D0)
  cal_data <- sim(DAG = D0set, n = max(20000, coefs$sample_size$default), rndseed = seed)

  oc <- coefs$outcome_calibration
  driver_formula <- build_mean_formula(oc$node, coefs)
  driver_draws <- eval(str2lang(driver_formula), envir = as.list(cal_data))
  intercept <- calibrate_intercept(driver_draws, oc$target_marginal_prevalence)

  outcome_formula <- sprintf("plogis(%s + %s)", intercept, driver_formula)
  D1 <- D0 + do.call(node, list(name = node_alias(oc$node), distr = "rbern", prob = str2lang(outcome_formula)))
  list(D1 = D1, spec = spec, coefs = coefs)
}

simulate_renal_stone_data <- function(n = NULL, seed = NULL) {
  built <- build_calibrated_dag(seed = seed)
  if (is.null(n)) n <- built$coefs$sample_size$default
  dealias_columns(sim(DAG = set.DAG(built$D1), n = n, rndseed = seed), built$spec)
}