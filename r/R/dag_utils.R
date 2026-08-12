# DAG loading and manipulation helpers.
#
# Reads config/dag_spec.yaml (see docs/decisions/002-data-interchange-contract.md)
# into a dagitty object and exposes it to the rest of the R pipeline.

library(dagitty)
library(yaml)
library(igraph)

#' Load the working DAG spec from config/dag_spec.yaml.
#'
#' Returns the parsed YAML as a plain list (nodes, edges,
#' selection_mechanisms, open_decisions, ...). Use dag_spec_to_dagitty() to
#' turn the nodes/edges into a dagitty object.
read_dag_spec <- function(path = "../config/dag_spec.yaml") {
  yaml::read_yaml(path)
}

#' Compute a deterministic left-to-right layered layout from a parsed
#' dag_spec's nodes/edges: x = each node's longest-path distance from a root
#' (so causes sit left of their effects, exposure at the far left and
#' outcome at the far right), y = even spacing within that layer, ties
#' broken alphabetically by node id. Both axes come purely from graph
#' structure - no randomness anywhere - so this is reproducible
#' byte-for-byte on every run, unlike dagitty::graphLayout() (see
#' write_dagitty()'s docs for why that one isn't).
dag_spec_positions <- function(spec) {
  ids <- vapply(spec$nodes, function(n) n$id, character(1))
  parents <- setNames(vector("list", length(ids)), ids)
  for (e in spec$edges) parents[[e$to]] <- c(parents[[e$to]], e$from)

  depth <- setNames(rep(NA_integer_, length(ids)), ids)
  compute_depth <- function(id) {
    if (!is.na(depth[[id]])) return(depth[[id]])
    ps <- parents[[id]]
    d <- if (is.null(ps)) 0L else 1L + max(vapply(ps, compute_depth, integer(1)))
    depth[[id]] <<- d
    d
  }
  for (id in ids) compute_depth(id)

  positions <- setNames(vector("list", length(ids)), ids)
  for (d in sort(unique(depth))) {
    layer <- sort(ids[depth == d])
    ys <- if (length(layer) == 1) 0 else seq(-1, 1, length.out = length(layer))
    for (i in seq_along(layer)) positions[[layer[i]]] <- c(x = d, y = ys[i])
  }
  positions
}

#' Build a dagitty object from a parsed dag_spec (as returned by read_dag_spec()).
#'
#' Node type "exposure" maps to dagitty's exposure tag and "outcome" maps to
#' dagitty's outcome tag; every other type (confounder, mediator,
#' exogenous_confounder, mediator_countermeasure, ...) is left untagged,
#' since dagitty's own vocabulary only distinguishes exposure/outcome/latent/
#' adjusted for its path-identification features - config/dag_spec.yaml's
#' richer type taxonomy doesn't have a dagitty equivalent and isn't lost,
#' since dag_spec.yaml itself remains the source of truth.
#'
#' selection_mechanisms are deliberately excluded from the graph: dag_spec.yaml
#' documents them as selection mechanisms applied during data generation
#' (Step 10), not causal DAG nodes, so they don't belong here either.
#'
#' Edges flagged interacts_with are included as ordinary directed edges -
#' dagitty's graph model has no native interaction-term annotation, so the
#' fact that a pair of edges also carries a product-interaction term is only
#' recoverable from config/edge_coefficients.yaml, not from the exported
#' dagitty file.
#'
#' Node positions come from dag_spec_positions() (a deterministic layered
#' layout), embedded directly in the model text - see write_dagitty() for
#' why this isn't left to dagitty::graphLayout() instead.
dag_spec_to_dagitty <- function(spec) {
  pos <- dag_spec_positions(spec)

  node_lines <- vapply(spec$nodes, function(n) {
    tag <- if (identical(n$type, "exposure")) "exposure,"
      else if (identical(n$type, "outcome")) "outcome,"
      else ""
    label <- if (!is.null(n$label)) sprintf('label="%s"', gsub('"', "'", n$label)) else ""
    p <- pos[[n$id]]
    pos_attr <- sprintf('pos="%.3f,%.3f"', p[["x"]], p[["y"]])
    attrs <- paste0(tag, pos_attr, ",", label)
    sprintf("%s [%s]", n$id, attrs)
  }, character(1))

  edge_lines <- vapply(spec$edges, function(e) sprintf("%s -> %s", e$from, e$to), character(1))

  model <- paste(
    "dag {",
    paste(node_lines, collapse = "\n"),
    paste(edge_lines, collapse = "\n"),
    "}",
    sep = "\n"
  )
  dagitty::dagitty(model)
}

#' Write a dagitty object to a file in DAGitty's native model syntax -
#' suitable for pasting directly into the model editor at
#' https://dagitty.net/dags.html (Model > Model code).
#'
#' Node positions are expected to already be set (dag_spec_to_dagitty() sets
#' them via dag_spec_positions(), a deterministic layered layout computed in
#' plain R). dagitty::graphLayout() was tried first instead, but it runs a
#' randomized spring-embedder inside an embedded JavaScript engine (dagitty's
#' core is a bundled JS library) whose RNG is invisible to R's set.seed() -
#' so it produces a different-looking (though structurally identical) layout
#' on every run, which defeats the point of a "for keeps" reference file.
#' DAGitty's parser doesn't support comments in the model text, so no
#' provenance header is written into the file itself - see docs/dag/README.md
#' for that.
write_dagitty <- function(dag, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  writeLines(as.character(dag), path)
  invisible(path)
}
