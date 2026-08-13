# Step 4a: DAG-derived ground truth total effects.
# See docs/methods Step 4 spec and r/R/ground_truth.R.
#
# Computed independently of and before any fitted model or SHAP attribution.

source("../r/R/ground_truth.R")
source("../r/R/io_contract.R")

spec <- read_dag_spec("../config/dag_spec.yaml")
FEATURES <- model_features(spec)

gt <- compute_ground_truth_total_effects(FEATURES, seed = 20260812)
dir.create("../data/frozen_truth", recursive = TRUE, showWarnings = FALSE)
arrow::write_parquet(gt, "../data/frozen_truth/ground_truth_total_effects.parquet")
