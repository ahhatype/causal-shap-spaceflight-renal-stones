# Direction and meaning of the IDA weights used by the discovery pipeline.
# Run from the repository root:
#   Rscript --vanilla r/tests/test_discovery_pcalg.R
# The optional audit library contains the same CRAN/Bioconductor packages used
# by the pipeline; no packages are downloaded or installed by this test.
audit_library <- file.path(getwd(), ".scratch", "ida-audit-r-library")
if (dir.exists(audit_library)) .libPaths(c(audit_library, .libPaths()))
suppressPackageStartupMessages(source("r/R/discovery_pcalg.R"))

assert_close <- function(actual, expected, tolerance = 1e-9) {
  stopifnot(length(actual) == length(expected),
            all(is.finite(actual)),
            all(abs(actual - expected) < tolerance))
}
assert_error <- function(expr, pattern) {
  result <- tryCatch({ force(expr); NULL }, error = identity)
  stopifnot(inherits(result, "error"),
            grepl(pattern, conditionMessage(result), fixed = TRUE))
}
make_graph <- function(labels, arrows) {
  result <- methods::new("graphNEL", nodes = labels, edgemode = "directed")
  for (arrow in arrows) result <- graph::addEdge(arrow[1], arrow[2], result, 1)
  result
}
known_dag_effect <- function(from, to, covariance, dag) {
  # A fully specified DAG need not be a completed PDAG. Use pcalg's explicit
  # PDAG mode for these mathematical fixtures, without feeding invalid CPDAGs
  # to the production helper (whose input comes from PC).
  pcalg::ida(match(from, colnames(covariance)),
             match(to, colnames(covariance)), covariance, dag,
             method = "local", type = "pdag")
}

# X has variance 1; Y = 2 X + epsilon, with independent unit-variance epsilon.
# Deliberately put Y first so the requested causal direction is not the order
# of covariance columns. graphNEL's outgoing-edge API is the reference for
# arrow identity, rather than an assumed adjacency-matrix convention.
labels <- c("Y", "X")
sigma <- matrix(c(5, 2, 2, 1), 2, dimnames = list(labels, labels))
directed <- make_graph(labels, list(c("X", "Y")))
stopifnot(identical(graph::edges(directed)[["X"]], "Y"),
          length(graph::edges(directed)[["Y"]]) == 0L)
assert_close(known_dag_effect("X", "Y", sigma, directed), 2)
assert_close(known_dag_effect("Y", "X", sigma, directed), 0)

# With an unresolved two-node CPDAG the possible effects are {0, 2} and
# {0, 2/5}, respectively. Their historical mean-absolute summaries differ.
ambiguous <- make_graph(labels, list(c("X", "Y"), c("Y", "X")))
assert_close(ida_edge_weight("X", "Y", sigma, ambiguous), 1)
assert_close(ida_edge_weight("Y", "X", sigma, ambiguous), 0.2)
assert_error(ida_edge_weight("missing", "Y", sigma, ambiguous),
             "IDA edge endpoints must occur in the covariance matrix")

# Exact sample covariance, avoiding a fragile random-discovery fixture.
n <- 1000L
x <- as.numeric(scale(seq_len(n)))
noise <- residuals(stats::lm(cos(seq_len(n)) ~ x))
noise <- as.numeric(scale(noise))
data <- data.frame(Y = 2 * x + noise, X = x)
assert_close(as.vector(stats::cov(data)), as.vector(sigma))

# Check both column orders. Every stored arrow must be an outgoing graphNEL
# edge, and its weight must request IDA in that arrow's direction.
fits <- lapply(list(c("Y", "X"), c("X", "Y")), function(order) {
  fit <- run_pc_ida(data[, order, drop = FALSE])
  stopifnot(nrow(fit$edges) == 1L, !fit$edges$oriented[1],
            identical(fit$weight_definition, "mean_abs_local_IDA_total_effect"))
  for (i in seq_len(nrow(fit$edges))) {
    from <- fit$edges$from[i]
    to <- fit$edges$to[i]
    stopifnot(to %in% graph::edges(fit$dag_extension)[[from]])
    expected <- pcalg::ida(match(from, order), match(to, order),
                           stats::cov(data[, order, drop = FALSE]),
                           fit$cpdag, method = "local", type = "cpdag")
    assert_close(fit$edges$weight[i], mean(abs(expected)))
    assert_close(fit$edges$weight[i], if (from == "X") 1 else 0.2)
  }
  fit
})

# Scripted reversal must re-request the effect on the ORIGINAL CPDAG and
# covariance, not keep the old directional weight (nor silently turn that
# CPDAG into a fully oriented DAG with a different possible-effect set).
for (fit in fits) {
  old <- fit$edges
  target <- list(edges = list(list(from = old$to[1], to = old$from[1])))
  revised <- pc_revise_orientation(fit, target)
  stopifnot(revised$from[1] == old$to[1], revised$to[1] == old$from[1],
            abs(revised$weight[1] - old$weight[1]) > 0.5)
  assert_close(revised$weight[1], if (revised$from[1] == "X") 1 else 0.2)
  # The helper returns revised edges without modifying the original result.
  stopifnot(identical(fit$edges, old))
  legacy <- fit
  legacy$covariance <- NULL
  assert_error(pc_revise_orientation(legacy, target),
               "Reorienting an IDA edge requires the original covariance")
  unchanged_target <- list(edges = list(list(from = old$from[1], to = old$to[1])))
  stopifnot(identical(pc_revise_orientation(legacy, unchanged_target), old))
}

# Semantic counterexample: IDA's total effect is not a direct-edge coefficient.
# X -> M: .5, M -> Y: .4, X -> Y: .3, with independent unit-variance noises.
# Total X -> Y = .3 + .5*.4 = .5. Reusing total effects as edge weights and
# summing their path products counts the mediated contribution twice: .7.
triangle_labels <- c("X", "M", "Y")
triangle <- make_graph(triangle_labels,
                       list(c("X", "M"), c("M", "Y"), c("X", "Y")))
triangle_sigma <- matrix(c(1, .5, .5,
                           .5, 1.25, .65,
                           .5, .65, 1.41), 3,
                         dimnames = list(triangle_labels, triangle_labels))
direct_coefficients <- solve(triangle_sigma[c("X", "M"), c("X", "M")],
                             triangle_sigma[c("X", "M"), "Y"])
assert_close(unname(direct_coefficients), c(.3, .4))
w_xy <- known_dag_effect("X", "Y", triangle_sigma, triangle)
w_xm <- known_dag_effect("X", "M", triangle_sigma, triangle)
w_my <- known_dag_effect("M", "Y", triangle_sigma, triangle)
assert_close(c(w_xy, w_xm, w_my), c(.5, .5, .4))
assert_close(w_xy + w_xm * w_my, .7)
stopifnot(abs(w_xy + w_xm * w_my - .5) > .1)

cat("PASS: IDA arrow direction, covariance column order, scripted reweighting,\n",
    "missing-covariance failure, and total-versus-direct effect counterexample.\n",
    "Two-node mean-absolute effects: X->Y = 1; Y->X = 0.2.\n",
    "Triangle: direct X->Y = 0.3; total = 0.5; total-edge path sum = 0.7.\n",
    sep = "")
