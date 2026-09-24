# PC discovery and IDA, used in two places:
#   Step 6: the PC stage of Ng et al.'s Causal SHAP (pipeline/step06d_pc_ida.R)
#   Step 8: DAG recovery comparison, reusing Step 6's PC/CPDAG rather than
#           recomputing it (see docs/decisions, "Step 8 reuses Step 6's PC output")
#
# pcalg::ida() is R-only - causal-learn (Python) has PC but no IDA equivalent.

library(pcalg)
library(graph)

# IDA returns possible TOTAL effects, not direct-edge coefficients. This
# mean-absolute local-IDA summary is the historical implementation's heuristic
# weight. Local multiplicities are not frequencies of DAGs in the equivalence
# class; neither their mean nor a product of these weights is an identified
# total effect. Keep the requested direction explicit and label the weight.
ida_edge_weight <- function(from, to, covariance, cpdag) {
  positions <- match(c(from, to), colnames(covariance))
  if (anyNA(positions)) stop("IDA edge endpoints must occur in the covariance matrix")
  effects <- pcalg::ida(positions[1], positions[2], covariance, cpdag,
                        method = "local", type = "cpdag")
  if (!length(effects) || any(!is.finite(effects))) {
    stop(sprintf("Non-finite or empty IDA effects for %s -> %s", from, to))
  }
  mean(abs(effects))
}

#' Run PC to get a CPDAG, then IDA for causal-effect bounds on every
#' adjacent pair. Returns a list:
#'   cpdag           - the discovered CPDAG (a graphNEL, pcalg's pc()$graph)
#'   dag_extension   - one consistent fully-directed extension of the CPDAG
#'                     (pdag2dag()'s own arbitrary-but-valid choice), needed
#'                     because Ng et al.'s method (pipeline/step06c) requires
#'                     unambiguous topological/path structure to enumerate
#'                     simple paths - a CPDAG's undirected edges alone don't
#'                     give that.
#'   edges           - data.frame(from, to, weight, oriented) for every
#'                     adjacent pair in the CPDAG, in dag_extension's chosen
#'                     direction. weight = mean(|ida() effect estimates|)
#'                     from local parent configurations for that direction.
#'                     This is a study summary of TOTAL effects, not pcalg's
#'                     direct-edge weight or a uniform average over DAGs.
#'                     oriented = TRUE if PC itself
#'                     resolved this edge's direction (v-structure or Meek
#'                     rule), FALSE if pdag2dag() had to pick arbitrarily
#'                     among an undirected edge's two directions - this
#'                     flag is what pipeline/step06d_pc_ida.R's round-2/3
#'                     revision heuristic uses to decide which edges are
#'                     eligible for reorientation.
run_pc_ida <- function(data, alpha = 0.05) {
  nodes <- colnames(data)
  x <- as.matrix(data)
  n <- nrow(x)
  suff_stat <- list(C = stats::cor(x), n = n)
  pc_fit <- pc(suff_stat, indepTest = gaussCItest, alpha = alpha, labels = nodes, verbose = FALSE)
  cpdag <- pc_fit@graph

  cpdag_amat <- as(cpdag, "matrix")[nodes, nodes, drop = FALSE]
  dag_ext <- pdag2dag(cpdag)$graph
  dag_amat <- as(dag_ext, "matrix")[nodes, nodes, drop = FALSE]
  mcov <- stats::cov(x)

  pairs <- list()
  for (i in seq_along(nodes)) {
    for (j in seq_along(nodes)) {
      if (i >= j) next
      adjacent <- cpdag_amat[i, j] == 1 || cpdag_amat[j, i] == 1
      if (!adjacent) next
      undirected_in_cpdag <- cpdag_amat[i, j] == 1 && cpdag_amat[j, i] == 1
      # dag_extension's chosen direction for this pair
      if (dag_amat[i, j] == 1) {
        from <- nodes[i]; to <- nodes[j]
      } else {
        from <- nodes[j]; to <- nodes[i]
      }
      pairs[[length(pairs) + 1]] <- data.frame(
        from = from, to = to,
        weight = ida_edge_weight(from, to, mcov, cpdag),
        oriented = !undirected_in_cpdag,
        stringsAsFactors = FALSE
      )
    }
  }
  edges <- if (length(pairs) > 0) do.call(rbind, pairs) else {
    data.frame(from = character(0), to = character(0), weight = numeric(0), oriented = logical(0))
  }

  list(cpdag = cpdag, dag_extension = dag_ext, edges = edges,
       covariance = mcov, weight_definition = "mean_abs_local_IDA_total_effect")
}

#' Step 6 HITL round-2/3 scripted revision heuristic for Ng et al.'s Causal
#' SHAP: reorient any edge PC left undirected (oriented == FALSE) to match
#' config/dag_spec.yaml's true direction, IF that pair is adjacent in the
#' true DAG (in either direction). Edges PC already oriented itself, or
#' didn't find adjacent at all, are left untouched - a scope limit (this
#' resolves genuine CPDAG ambiguity, it does not add or remove edges PC
#' missed or invented), not a finding. This is an LLM-authored scripted
#' stand-in for the methods doc's "Robert reviews and revises" step, NOT a
#' capability of pcalg or a step from Ng et al.'s paper - see
#' docs/step06_results.md's "LLM-made decisions" table.
pc_revise_orientation <- function(pc_ida_result, dag_spec) {
  edges <- pc_ida_result$edges
  true_pairs <- vapply(dag_spec$edges, function(e) paste(e$from, e$to), character(1))

  for (i in seq_len(nrow(edges))) {
    if (edges$oriented[i]) next
    forward <- paste(edges$from[i], edges$to[i])
    backward <- paste(edges$to[i], edges$from[i])
    if (backward %in% true_pairs && !(forward %in% true_pairs)) {
      tmp <- edges$from[i]
      edges$from[i] <- edges$to[i]
      edges$to[i] <- tmp
      if (is.null(pc_ida_result$covariance)) {
        stop("Reorienting an IDA edge requires the original covariance; rerun run_pc_ida()")
      }
      # Recompute for the NEW requested direction on the ORIGINAL CPDAG.
      # This fixes directional consistency; it does not condition the IDA
      # equivalence class on the scripted orientations or estimate a direct edge.
      edges$weight[i] <- ida_edge_weight(edges$from[i], edges$to[i],
                                        pc_ida_result$covariance,
                                        pc_ida_result$cpdag)
    }
  }
  edges
}

#' Step 6 HITL round-2/3 scripted revision heuristic for Ng et al.'s Causal
#' SHAP, second half: if the outcome ends up with NO edges at all (PC's
#' skeleton-pruning phase can remove every one of its connections when a
#' densely-connected hub node like urine_chemistry sits between it and
#' everything else - a real, reproduced finding at this DAG's n=1000/
#' alpha=0.05, not a bug; see docs/step06_results.md), add one edge from
#' the feature with the strongest marginal |correlation| to the outcome.
#' Algorithm 1 (pipeline's Python side) weights every feature's causal
#' SHAP value by gamma_i, itself entirely a function of paths reaching the
#' outcome in the discovered graph - leaving the outcome disconnected
#' forces every gamma_i to 0 and the whole method to degenerate to
#' all-zero attributions. Reconnection is a scripted sensitivity choice;
#' a disconnected estimate alone does not justify adding an edge.
#' The marginal-correlation weight is a stand-in for
#' IDA's effect estimate (the disconnected CPDAG supplies no causal path) - an
#' LLM-authored heuristic, not a finding from pcalg or Ng et al.'s paper;
#' see docs/step06_results.md's "LLM-made decisions" table.
pc_reconnect_outcome <- function(edges, data, outcome = "nephrolithiasis") {
  if (any(edges$to == outcome | edges$from == outcome)) return(edges)  # already connected
  candidates <- setdiff(unique(c(edges$from, edges$to)), outcome)
  if (length(candidates) == 0) candidates <- setdiff(colnames(data), outcome)
  cors <- vapply(candidates, function(f) abs(stats::cor(data[[f]], data[[outcome]])), numeric(1))
  best <- candidates[which.max(cors)]
  rbind(edges, data.frame(from = best, to = outcome, weight = cors[[best]], oriented = TRUE))
}

#' Run GES (Step 8, score-based discovery family).
#'
#' TODO: implement.
run_ges <- function(data) {
  stop("not implemented")
}
