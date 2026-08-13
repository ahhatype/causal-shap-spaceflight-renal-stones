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
    sprintf("((%s - %s) / %s)", alias, root$params$mean, root$params$sd)
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
#' themselves correlated - e.g. mineralized_renal_material reaches
#' urinary_calcium_excretion both directly (the interaction term) and
#' indirectly through urine_chemistry, so their contributions covary rather
#' than adding independently. D_partial already contains every node up to
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

calibrate_intercept <- function(driver_draws, coefficient, target_prevalence) {
  f <- function(b0) mean(plogis(b0 + coefficient * driver_draws)) - target_prevalence
  uniroot(f, interval = c(-10, 10))$root
}

#' Simulate data from config/dag_spec.yaml + config/edge_coefficients.yaml.
#'
#' Two-pass: a calibration-only draw (discarded) to solve for
#' nephrolithiasis's intercept against outcome_calibration's target
#' prevalence, then the real output draw of size n with the calibrated
#' outcome node included. See vignette Sec. 3.2 (p.14) for sim()/rndseed.
simulate_renal_stone_data <- function(n = NULL, seed = NULL) {
  spec  <- read_dag_spec("../config/dag_spec.yaml")
  coefs <- yaml::read_yaml("../config/edge_coefficients.yaml")
  if (is.null(n)) n <- coefs$sample_size$default

  D0 <- build_dag(spec, coefs, seed = seed)   # everything except nephrolithiasis
  D0set <- set.DAG(D0)                  
  cal_data <- sim(DAG = D0set, n = max(20000, n), rndseed = seed)

  oc <- coefs$outcome_calibration
  neph_edge <- Filter(function(e) identical(e$to, oc$node), coefs$coefficients)[[1]]
  intercept <- calibrate_intercept(
    cal_data[[node_alias(neph_edge$from)]], neph_edge$coefficient, oc$target_marginal_prevalence
  )

  outcome_formula <- sprintf("plogis(%s + %s * %s)", intercept, neph_edge$coefficient, node_alias(neph_edge$from))
  D1 <- D0 + do.call(node, list(name = node_alias(oc$node), distr = "rbern", prob = str2lang(outcome_formula)))
  D1set <- set.DAG(D1)
  dealias_columns(sim(DAG = D1set, n = n, rndseed = seed), spec)
}