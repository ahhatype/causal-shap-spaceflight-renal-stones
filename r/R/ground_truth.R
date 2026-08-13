# Step 4: DAG-derived ground truth total effects.
#
# Computes each candidate feature's true standardized total effect on
# P(nephrolithiasis=1) via a do()-style intervention (simcausal action()),
# independent of and prior to any fitted model or SHAP attribution - see
# docs/methods "Reproducibility and provenance": "the ground-truth total
# effects are computed before and independently of the attribution
# comparison to prevent leakage."

source("../r/R/simcausal_helpers.R")

#' High/low intervention levels per feature. Continuous nodes already on the
#' standardized scale (mediators + latents) use +-1 SD directly. duration/
#' hydration_fluid_intake are raw-unit roots - use their own mean +- SD
#' (config/edge_coefficients.yaml's root_node_distributions params). Binary
#' root nodes use 1 vs 0.
feature_levels <- function(node_id, coefs) {
  root <- root_lookup(coefs)[[node_id]]
  if (!is.null(root) && identical(root$distr, "rbern")) return(list(hi = 1, lo = 0))
  if (!is.null(root) && !is.null(root$unit)) {
    return(list(hi = root$params$mean + root$params$sd, lo = root$params$mean - root$params$sd))
  }
  list(hi = 1, lo = -1)   # standardized continuous node (root latent or mediator)
}

#' Standardized total effect of each candidate feature on P(nephrolithiasis=1):
#' mean(nephrolithiasis | do(feature = hi)) - mean(nephrolithiasis | do(feature = lo)),
#' common random numbers (same seed, same sim() call, shared draws for every
#' other node). cal_n=50000 matches the sibling repo's own precedent for this
#' exact kind of ground-truth computation (docs/methods Sec. 4b: "50,000
#' common-random-number simulations, standardized absolute total risk
#' difference for 28 ancestors").
compute_ground_truth_total_effects <- function(features, cal_n = 50000, seed = NULL) {
  built <- build_calibrated_dag(seed = seed)
  D1set <- set.DAG(built$D1)

  results <- lapply(features, function(f) {
    lv <- feature_levels(f, built$coefs)
    # node()'s NSE capture mis-tokenizes a `$`-access expression like lv$hi
    # as if it referenced a node literally named "hi" - verified directly
    # against the installed package (fails with "Undefined variable: hi").
    # Extract to plain local variables first.
    hi_val <- lv$hi
    lo_val <- lv$lo
    alias <- node_alias(f)
    D_actions <- D1set +
      action("hi", nodes = node(alias, distr = "rconst", const = hi_val)) +
      action("lo", nodes = node(alias, distr = "rconst", const = lo_val))
    out <- sim(DAG = D_actions, actions = c("hi", "lo"), n = cal_n, rndseed = seed)
    effect <- mean(out[["hi"]]$nephrolithiasis) - mean(out[["lo"]]$nephrolithiasis)
    data.frame(feature = f, true_total_effect = effect, true_total_effect_abs = abs(effect))
  })
  do.call(rbind, results)
}
