# DAG loading and manipulation helpers.
#
# Reads config/dag_spec.yaml (see docs/decisions/002-data-interchange-contract.md)
# into a dagitty object and exposes it to the rest of the R pipeline.

library(dagitty)
library(yaml)
library(igraph)

#' Load the working DAG spec from config/dag_spec.yaml.
#'
#' TODO: implement. Should return the parsed YAML plus a dagitty object
#' built from the node/edge list.
read_dag_spec <- function(path = "../config/dag_spec.yaml") {
  stop("not implemented")
}
