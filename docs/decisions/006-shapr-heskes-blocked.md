# ADR 006: Heskes et al.'s Causal Shapley Values (shapr) blocked in this environment

## Status
Accepted

## Decision
`r/R/shapr_wrappers.R`'s `run_causal_shapley_values()` (Heskes et al., NeurIPS 2020, via `shapr::explain()`) raises an immediate, documented error rather than calling `explain()`. `pipeline/step06a_causal_shapley_asv.R` runs only Frye et al.'s ASV (`run_asymmetric_shapley_values()`, unaffected) across all 3 HITL rounds; Heskes' method is skipped, and the driver's own output says so explicitly rather than silently producing 3 fewer rows than expected.

## Context
`shapr::explain(..., asymmetric = FALSE, causal_ordering = <list>, confounding = <vector>)` is the documented call for Heskes' (symmetric) causal Shapley values (`?shapr::explain`: "If `confounding` is provided, i.e., not `NULL`, then `explain` computes asymmetric/symmetric causal Shapley values"). In this environment, **any `explain()` call with a non-`NULL` `confounding` argument hangs indefinitely** past the "Computing v(S)" progress step - it never reaches "Computing Shapley value estimates". Reproduced and isolated during Step 6 implementation:

- Confirmed with `timeout` at up to 150s on toy problems as small as 5 features / 3 causal-ordering groups / 32 total coalitions - not a slow computation, a genuine hang.
- Confirmed independent of model class: happens with a plain `glm()` (natively supported by shapr, no custom `predict_model`) exactly as it does with an `xgb.Booster`.
- Confirmed independent of `approach` (`"empirical"`, `"gaussian"`, `"independence"` all hang identically).
- Confirmed independent of `asymmetric` (`TRUE` or `FALSE` - only whether `confounding` is `NULL` matters).
- Confirmed independent of `confounding`'s value - scalar `FALSE`, scalar `TRUE`, and an all-`FALSE` vector all hang the same way; only `confounding = NULL` (which selects ASV/conditional Shapley values instead of the causal method) completes.
- Confirmed independent of package versions: reproduced identically after reinstalling `future`/`future.apply`/`globals` at both their originally-installed versions (1.33.2/1.11.2/0.16.3) and current CRAN (1.70.0/1.20.2/0.19.1), and `data.table` at both 1.15.4 and 1.18.2.1.
- Confirmed independent of batching/variance settings: `extra_computation_args = list(vS_batching_method = "forloop", compute_sd = FALSE)` (shapr's own documented sequential-computation escape hatch, bypassing `future.apply` for the v(S) stage entirely) does not change the outcome.
- Confirmed independent of system resource contention: CPU and matrix-multiplication benchmarks on the same machine, run immediately before and after, complete in well under a second with no thermal throttling reported.

By elimination, this isolates the hang to `shapr`'s internal Shapley-weight-combination step specifically for confounding-aware (causal) orderings - a step downstream of `future.apply`-based v(S) batching (which completes fine on its own) and unrelated to the model/data/approach supplied. This is the kind of finding worth reporting upstream (a minimal, model-agnostic reproduction exists), not something to keep working around silently in this codebase.

ASV (`confounding = NULL`) uses a different internal code path and is unaffected: verified at realistic scale (13 features, 800 training rows, 200 explained rows, 500 coalitions) completing in ~8 seconds per call, well within budget for 3 HITL rounds.

### Follow-up investigation (2026-09-01): not fixed upstream, and likely native code, not R/future

Re-opened this after the initial write-up to attempt an actual fix, not just document a workaround:

- **Checked whether a known, already-fixed bug explained this.** `shapr` PR #435 ("Fix cpp pointer bug") looked like a strong match by name and by touching `get_S_causal_steps` (the function that enumerates causal-ordering-respecting coalitions - exactly the step downstream of the "Computing v(S)" progress line this hangs after). Confirmed via the CRAN changelog that this fix has been in every CRAN release since 1.0.2, including the already-installed 1.0.8 - not the explanation.
- **Checked whether a newer, unreleased fix exists.** Installed `shapr` directly from GitHub HEAD (`remotes::install_github("NorskRegnesentral/shapr")`, resolved to `1.0.8.9005`). The minimal glm() reproduction hangs identically on this build. Also checked the GitHub issues list directly for "hang", "freeze", "stuck", "infinite" - no matching reports; this appears to be either unreported or specific to something about this environment not yet identified.
- **Checked whether it's R-level (interruptible) or native-level (uninterruptible) code.** Wrapped the `explain()` call in `setTimeLimit(cpu=, elapsed=, transient=TRUE)` plus a same-frame `withCallingHandlers` (no intervening `tryCatch`, which would unwind the stack before the handler runs) to try to catch the timeout condition mid-computation and print `sys.calls()`. **The time limit never fired at all** - the outer `timeout` (an OS-level `SIGTERM`) was the only thing that ever stopped it. R's `setTimeLimit()` is checked at R bytecode-eval boundaries; a computation that never reaches one - because it's inside a single long-running compiled call, most plausibly one of `shapr`'s own Rcpp/RcppArmadillo routines (`shapr`'s `src/` has `distance.cpp`, `weighted_matrix.cpp`, `features.cpp`, etc., none of which are guaranteed to call `Rcpp::checkUserInterrupt()` internally) - would behave exactly like this. Also confirmed `future::plan(sequential)` explicitly set beforehand does not change the outcome, which argues against this being a `future`/parallelization orchestration issue at the R level at all, despite the traceback superficially passing through `future.apply::future_lapply`.

**Working conclusion:** this looks like a genuine bug in `shapr`'s compiled internals for confounding-aware causal Shapley weighting, most likely an unterminating or pathologically expensive loop inside one of its Rcpp routines for a specific `causal_ordering`/`confounding` combination - not fixable from this codebase, and not something further debugging without attaching a native debugger (`lldb`/`gdb`) to the hung process would be proportionate effort to pursue here. Filing this as a `shapr` GitHub issue (with the minimal glm() reproduction above) is the correct next step if this is revisited, rather than more workaround attempts in this repo.

## Consequences
- `docs/step06_results.md` reports 3 methods with real Step 6 results this round (ASV, Ng et al.'s Causal SHAP, Shapley Flow), not 4 - Heskes' method's row is present in per-round tables only as "blocked, see ADR 006", never fabricated or approximated.
- `results/attributions/step06a_causal_shapley_asv.parquet` contains only `method="asymmetric_shapley_values"` rows (3 rounds); no `method="causal_shapley_values"` rows exist anywhere in `results/attributions/`.
- `heskes_revise_confounding()` and the `confounded_groups` plumbing in `run_causal_shapley_values()` are left implemented, not deleted - if a future `shapr` release fixes this, removing the `stop()` in `run_causal_shapley_values()` is the only change needed to re-enable it.
- If this is revisited: file a GitHub issue against `NorskRegnesentral/shapr` with the minimal glm() reproduction in this ADR (confirmed to still reproduce on GitHub HEAD `1.0.8.9005`, so a CRAN update alone will not resolve it), rather than re-attempting further workarounds in this codebase. Native-level debugging (`lldb` attached to a hung `R --vanilla` process) would be the next real diagnostic step, not anything scriptable from R itself.
