# Step 6: Heskes Causal Shapley Values + ASV, via shapr.
# See docs/methods §9 and r/R/shapr_wrappers.R.
#
# Heskes' method is BLOCKED in this environment - see
# docs/decisions/006-shapr-heskes-blocked.md. This driver runs ASV only,
# across all 3 HITL iteration rounds - only this script knows how to build
# ASV's own shapr arguments (within_tier_order) round to round; the
# cross-language orchestrator (pipeline/step06_hitl_iteration.py) only
# scores and summarizes already-written output, per ADR-001's file-only
# interchange (no live cross-language calls). Round 1 uses ASV's genuinely
# naive default input (alphabetical tie-break within each depth tier);
# rounds 2-3 apply the scripted heuristic revision documented in
# r/R/shapr_wrappers.R and docs/step06_results.md's "LLM-made decisions"
# table - NOT real expert review.

source("../r/R/dag_utils.R")
source("../r/R/engines.R")
source("../r/R/shapr_wrappers.R")
source("../r/R/io_contract.R")

spec <- read_dag_spec("../config/dag_spec.yaml")
data <- as.data.frame(arrow::read_parquet("../data/simulated/renal_stone_simulated.parquet"))
ground_truth <- as.data.frame(arrow::read_parquet("../data/frozen_truth/ground_truth_total_effects.parquet"))

cat("Heskes Causal Shapley Values: SKIPPED - blocked in this environment, see docs/decisions/006-shapr-heskes-blocked.md\n")

# --- ASV: 3 rounds, one feature promoted to its own causal-ordering group per round ---
a1 <- run_asymmetric_shapley_values(data, spec, iteration_round = 1)
promoted <- asv_revise_promotions(a1, ground_truth, spec, character(0))

a2 <- run_asymmetric_shapley_values(data, spec, iteration_round = 2, promote = promoted)
promoted <- asv_revise_promotions(a2, ground_truth, spec, promoted)

a3 <- run_asymmetric_shapley_values(data, spec, iteration_round = 3, promote = promoted)

all_rows <- rbind(a1, a2, a3)
prov <- attribution_provenance()
all_rows$run_id <- prov$run_id
all_rows$git_sha <- prov$git_sha
all_rows$timestamp <- prov$timestamp

write_attributions(all_rows, "../results/attributions/step06a_causal_shapley_asv.parquet")
cat(sprintf("Wrote %d rows to results/attributions/step06a_causal_shapley_asv.parquet (ASV only)\n", nrow(all_rows)))
