# Direction audit; writes only a separate diagnostic run, never frozen results.
# Run from repository root. Optional first arg is a local R library directory.
args <- commandArgs(trailingOnly = TRUE)
if (length(args)) .libPaths(c(normalizePath(args[1]), .libPaths()))
root <- normalizePath(".", winslash = "/")
out <- file.path(root, "analysis/output/numerical_audit_20260919")
dir.create(out, recursive = TRUE, showWarnings = FALSE)
setwd(file.path(root, "pipeline"))
source("../r/R/simcausal_helpers.R")
source("../r/R/discovery_pcalg.R")
spec <- read_dag_spec("../config/dag_spec.yaml")
features <- model_features(spec)
# Original working-data and Step 6 parquet files are absent in this checkout.
# Reconstruct the configured generator; do not claim byte-identical historical data.
data <- simulate_renal_stone_data(seed = 20260812)
data <- data[, c(features, "nephrolithiasis")]
fixed <- run_pc_ida(data)

# Exactly reproduce the old loop's IDA(min index,max index) request on the SAME
# discovered CPDAG, so comparisons isolate weight handling rather than discovery.
legacy <- fixed
legacy$edges$weight <- vapply(seq_len(nrow(fixed$edges)), function(k) {
  ix <- sort(match(c(fixed$edges$from[k], fixed$edges$to[k]), colnames(data)))
  mean(abs(pcalg::ida(ix[1], ix[2], fixed$covariance, fixed$cpdag,
                     method = "local", type = "cpdag")))
}, numeric(1))
legacy_revise <- function(result) {
  edges <- result$edges
  true_pairs <- vapply(spec$edges, function(e) paste(e$from, e$to), character(1))
  for (k in seq_len(nrow(edges))) {
    if (edges$oriented[k]) next
    forward <- paste(edges$from[k], edges$to[k])
    backward <- paste(edges$to[k], edges$from[k])
    if (backward %in% true_pairs && !(forward %in% true_pairs)) {
      tmp <- edges$from[k]; edges$from[k] <- edges$to[k]; edges$to[k] <- tmp
    }
  }
  pc_reconnect_outcome(edges, data)
}
arms <- list(legacy = legacy$edges, direction_fixed = fixed$edges)
rounds <- list(
  legacy = legacy_revise(legacy),
  direction_fixed_stale_reversal = legacy_revise(fixed),
  direction_and_reversal_fixed = pc_reconnect_outcome(pc_revise_orientation(fixed, spec), data)
)
records <- list()
for (arm in names(arms)) records[[length(records)+1L]] <- transform(arms[[arm]], arm=arm, round=1L)
for (arm in names(rounds)) records[[length(records)+1L]] <- transform(rounds[[arm]], arm=arm, round=2L)
write.csv(do.call(rbind, records), file.path(out, "ida_edge_comparison.csv"), row.names=FALSE)
write.csv(data, file.path(out, "ida_reconstructed_data.csv"), row.names=FALSE)
cpdag <- as(fixed$cpdag, "matrix")
write.csv(cpdag, file.path(out, "ida_cpdag.csv"))
write.csv(fixed$covariance, file.path(out, "ida_covariance.csv"))
writeLines(c(
  "Diagnostic reconstruction, not a replacement for the historical Step 6 run.",
  "Original simulated-data and Step 6 edge/attribution parquet files absent in this checkout.",
  "Generator: current config + simcausal; n=1000, seed=20260812; PC alpha=0.05.",
  "Both arms use the identical reconstructed dataset, covariance, PC output and DAG extension.",
  "Rounds 2 and 3 are the same scripted heuristic, NOT human review; only round2 is stored here.",
  "Fixed weights still average absolute local-IDA TOTAL effects on the original CPDAG.",
  "They are not direct-edge coefficients, nor conditioned on the scripted orientations.",
  sprintf("Discovered adjacent pairs: %d; undirected: %d", nrow(fixed$edges), sum(!fixed$edges$oriented)),
  sprintf("Outcome connected in round1: %s", any(fixed$edges$from=='nephrolithiasis' | fixed$edges$to=='nephrolithiasis')),
  sprintf("Stored reverse-index requests: %d", sum(match(fixed$edges$from,colnames(data)) > match(fixed$edges$to,colnames(data)))),
  sprintf("Round1 weight changes: %d", sum(abs(legacy$edges$weight-fixed$edges$weight)>1e-12)),
  capture.output(sessionInfo())
), file.path(out, "ida_validation.txt"))
inputs <- file.path(root,c("config/dag_spec.yaml","config/edge_coefficients.yaml","r/R/simcausal_helpers.R","r/R/discovery_pcalg.R"))
write.csv(data.frame(file=substring(inputs,nchar(root)+2),md5=unname(tools::md5sum(inputs))), file.path(out,"ida_input_hashes.csv"),row.names=FALSE)
cat(readLines(file.path(out,"ida_validation.txt")),sep="\n")
