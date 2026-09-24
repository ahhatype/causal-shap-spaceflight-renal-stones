# Recompute frozen evaluation-record bootstrap summaries without refitting a model
# or writing into the historical result directory. Run from the repository root:
# Rscript analysis/audit_bootstrap_reconciliation.R
source("analysis/R/paths.R")
frozen_dir <- file.path(analysis_dir, "output", "shap_nephrolithiasis_clean_v3")
audit_dir <- file.path(analysis_dir, "output", "numerical_audit_20260919")
dir.create(audit_dir, recursive = TRUE, showWarnings = FALSE)
frozen_files <- list.files(frozen_dir, full.names = TRUE)
hashes_before <- tools::md5sum(frozen_files)
old_output <- Sys.getenv("SHAP_BOOTSTRAP_OUTPUT_DIR", unset = NA_character_)
Sys.setenv(SHAP_BOOTSTRAP_OUTPUT_DIR = file.path(audit_dir, "tau_bootstrap"))
tryCatch(source(file.path(analysis_dir, "08_bootstrap_shap_comparison.R")),
         finally = {
           if (is.na(old_output)) Sys.unsetenv("SHAP_BOOTSTRAP_OUTPUT_DIR") else
             Sys.setenv(SHAP_BOOTSTRAP_OUTPUT_DIR = old_output)
         })

historical_draws <- read.csv(file.path(frozen_dir, "paired_bootstrap_draws.csv"))
historical_summary <- read.csv(file.path(frozen_dir, "paired_bootstrap_summary.csv"))
table_metrics <- read.csv(file.path(frozen_dir, "attribution_summary_metrics.csv"))
draw_max_error <- max(abs(as.matrix(draws) - as.matrix(historical_draws)))
summary_numeric <- setdiff(names(historical_summary), "metric")
summary_max_error <- max(abs(as.matrix(bootstrap_summary[, summary_numeric]) -
                              as.matrix(historical_summary[, summary_numeric])))
ordinary_table <- table_metrics[table_metrics$method == "Ordinary interventional SHAP", ]
causal_table <- table_metrics[table_metrics$method == "DAG-constrained asymmetric SHAP", ]
stopifnot(draw_max_error < 1e-12, summary_max_error < 1e-12,
          abs(ordinary_point$kendall_tau - ordinary_table$kendall_tau_vs_truth) < 1e-12,
          abs(causal_point$kendall_tau - causal_table$kendall_tau_vs_truth) < 1e-12,
          identical(hashes_before, tools::md5sum(frozen_files)))

# Independently derive tau-b from concordant/discordant and tied feature pairs.
# Also expose which pair orderings change on resampling; pairs are NOT resampled.
pairs <- utils::combn(seq_along(features), 2)
pair_sign <- function(score) sign(score[pairs[1, ]] - score[pairs[2, ]])
truth_sign <- pair_sign(truth_values)
ordinary_sign <- pair_sign(colMeans(abs(ordinary)))
causal_sign <- pair_sign(colMeans(abs(causal)))
tau_from_pairs <- function(score_sign) {
  sum(score_sign * truth_sign) /
    sqrt(sum(score_sign != 0) * sum(truth_sign != 0))
}
stopifnot(abs(tau_from_pairs(ordinary_sign) - ordinary_point$kendall_tau) < 1e-12,
          abs(tau_from_pairs(causal_sign) - causal_point$kendall_tau) < 1e-12)
ordinary_agreement <- causal_agreement <- numeric(ncol(pairs))
set.seed(bootstrap_seed)
for (iteration in seq_len(n_bootstrap)) {
  indices <- sample.int(nrow(ordinary), nrow(ordinary), replace = TRUE)
  ordinary_agreement <- ordinary_agreement +
    pair_sign(colMeans(abs(ordinary[indices, , drop = FALSE]))) * truth_sign
  causal_agreement <- causal_agreement +
    pair_sign(colMeans(abs(causal[indices, , drop = FALSE]))) * truth_sign
}
pair_table <- data.frame(
  first = features[pairs[1, ]], second = features[pairs[2, ]], truth_sign,
  ordinary_point_agreement = ordinary_sign * truth_sign,
  asymmetric_point_agreement = causal_sign * truth_sign,
  ordinary_bootstrap_mean_agreement = ordinary_agreement / n_bootstrap,
  asymmetric_bootstrap_mean_agreement = causal_agreement / n_bootstrap
)
pair_table$point_agreement_difference <-
  pair_table$asymmetric_point_agreement - pair_table$ordinary_point_agreement
pair_table$bootstrap_mean_agreement_difference <-
  pair_table$asymmetric_bootstrap_mean_agreement -
  pair_table$ordinary_bootstrap_mean_agreement
write.csv(pair_table, file.path(audit_dir, "tau_feature_pair_audit.csv"), row.names = FALSE)
point_table <- data.frame(
  method = c("Ordinary interventional SHAP", "DAG-constrained asymmetric SHAP"),
  point_tau_b = c(ordinary_point$kendall_tau, causal_point$kendall_tau),
  bootstrap_mean_tau_b = c(mean(draws$ordinary_kendall_tau), mean(draws$causal_kendall_tau)),
  concordant_pairs = c(sum(ordinary_sign * truth_sign > 0), sum(causal_sign * truth_sign > 0)),
  discordant_pairs = c(sum(ordinary_sign * truth_sign < 0), sum(causal_sign * truth_sign < 0)),
  score_tied_pairs = c(sum(ordinary_sign == 0), sum(causal_sign == 0)),
  truth_tied_pairs = sum(truth_sign == 0)
)
write.csv(point_table, file.path(audit_dir, "tau_point_reconciliation.csv"), row.names = FALSE)
write.csv(data.frame(file = basename(frozen_files), md5 = unname(hashes_before)),
          file.path(audit_dir, "tau_frozen_input_hashes.csv"), row.names = FALSE)
writeLines(c(
  paste("R version:", R.version.string),
  paste("Maximum absolute difference across all historical bootstrap draw fields:", format(draw_max_error)),
  paste("Maximum absolute difference across historical summary numeric fields:", format(summary_max_error)),
  "All frozen output file hashes unchanged; point tau independently checked from pair counts.",
  paste("Evaluation records:", nrow(ordinary), "; ranked ancestor features:", length(features)),
  paste("Original-sample tau difference:", format(point_differences["delta_kendall_tau"], digits = 16)),
  paste("Mean of resampled tau differences:", format(mean(draws$delta_kendall_tau), digits = 16)),
  paste("Percentile 95% interval:", paste(format(quantile(draws$delta_kendall_tau, c(.025, .975)), digits = 16), collapse = ", ")),
  "Conclusion: 0.022 is the original-sample difference; 0.008 is the bootstrap mean.",
  "They are different summaries of the same statistic, not discrepant runs or feature sets.",
  "The conditional evaluation-record interval includes zero; no general superiority is established.",
  "Fixed: fitted model, attributed values, graph, background, permutations, and intervention-effect reference.",
  "The bootstrap does not cover model fitting, graph discovery, truth Monte Carlo, or simulation-seed uncertainty."
), file.path(audit_dir, "tau_validation.txt"))
print(point_table)
message("Verified bootstrap reconstruction and preservation of frozen evidence.")
