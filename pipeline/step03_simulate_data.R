# Step 3: synthetic data generation via simcausal.
# See docs/methods and config/edge_coefficients.yaml.
#
# Builds the structural equation model from config/dag_spec.yaml +
# config/edge_coefficients.yaml (see r/R/simcausal_helpers.R), simulates
# the default clean regime, and writes it to data/simulated/ via
# r/R/io_contract.R's write_simulated_data(). Run via `make step03` or
# `cd pipeline && Rscript step03_simulate_data.R`.

source("../r/R/simcausal_helpers.R")
source("../r/R/io_contract.R")

seed <- 20260812   # fixed for reproducibility; re-running produces byte-identical output

data <- simulate_renal_stone_data(seed = seed)
write_simulated_data(data, "../data/simulated/renal_stone_simulated.parquet")