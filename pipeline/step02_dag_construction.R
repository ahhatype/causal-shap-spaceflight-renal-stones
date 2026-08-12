# Step 2: DAG construction and expert-guided augmentation.
# See config/dag_spec.yaml.
#
# Builds the dagitty object for the working subgraph from config/dag_spec.yaml
# and writes it to data/interim/ in DAGitty's native model syntax. Run via
# `make step02` or `cd pipeline && Rscript step02_dag_construction.R`.

source("../r/R/dag_utils.R")

spec <- read_dag_spec("../config/dag_spec.yaml")
dag <- dag_spec_to_dagitty(spec)
write_dagitty(dag, "../data/interim/renal_stone_working_dag.txt")
