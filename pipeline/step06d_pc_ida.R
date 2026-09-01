# Step 6 (Ng et al.'s Causal SHAP, first stage) and Step 8 (reused here,
# not recomputed) - PC discovery and IDA effect bounds.
# See docs/methods §9, §11 and r/R/discovery_pcalg.R.
#
# Writes 3 rounds of edges (round 1: PC's discovered CPDAG with
# pdag2dag()'s arbitrary orientation of any undirected edge; rounds 2-3:
# the scripted revision heuristics in r/R/discovery_pcalg.R -
# pc_revise_orientation() (reorient toward dag_spec.yaml's truth) and
# pc_reconnect_outcome() (reconnect the outcome if PC left it fully
# disconnected - a real finding this DAG reproduces, see that function's
# docs) - NOT real expert review; see docs/step06_results.md's "LLM-made
# decisions" table) for pipeline/step06c_structural_causal_shap.py
# (Python) to consume, per ADR-001's file-only cross-language interchange.

source("../r/R/dag_utils.R")
source("../r/R/discovery_pcalg.R")
source("../r/R/io_contract.R")

spec <- read_dag_spec("../config/dag_spec.yaml")
features <- model_features(spec)
data <- as.data.frame(arrow::read_parquet("../data/simulated/renal_stone_simulated.parquet"))
data <- data[, c(features, "nephrolithiasis")]

result <- run_pc_ida(data, alpha = 0.05)
outcome_connected <- any(result$edges$to == "nephrolithiasis" | result$edges$from == "nephrolithiasis")

round1 <- result$edges
round1$round <- 1L

round2_edges <- pc_revise_orientation(result, spec)
round2_edges <- pc_reconnect_outcome(round2_edges, data)
round2 <- round2_edges
round2$round <- 2L

# Round 3 is identical to round 2 for these heuristics: both are
# idempotent (everything resolvable, resolved in round 2; the outcome,
# once reconnected, stays connected) - documented explicitly, not hidden,
# in docs/step06_results.md.
round3 <- round2_edges
round3$round <- 3L

all_edges <- rbind(round1, round2, round3)
dir.create("../results/attributions", recursive = TRUE, showWarnings = FALSE)
arrow::write_parquet(all_edges, "../results/attributions/step06d_pc_ida_edges.parquet")

cat(sprintf(
  "PC found %d adjacent pairs (%d left undirected by PC, resolved via dag_spec.yaml where possible in rounds 2-3).\n",
  nrow(result$edges), sum(!result$edges$oriented)
))
if (!outcome_connected) {
  cat("PC left the outcome (nephrolithiasis) with NO edges in round 1 - a real finding (see r/R/discovery_pcalg.R's pc_reconnect_outcome() docs), reconnected via the scripted heuristic starting round 2.\n")
}
cat(sprintf("Wrote %d rows to results/attributions/step06d_pc_ida_edges.parquet\n", nrow(all_edges)))
