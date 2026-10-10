# Experiments

The team sandbox. Each experiment is one self-contained folder with its own
README, data or generator, requirements and outputs. Nothing here is a frozen
result or a manuscript claim: the frozen records stay under `analysis/output/`
and `results/`, and the manuscript's central experiment lives in
[ahhatype/causal-dag-eval-pipeline](https://github.com/ahhatype/causal-dag-eval-pipeline).

## Conventions

- One folder per experiment, named for the question, with a README that states
  the question, the answer key or reference, how to run it and what came out.
- Keep an experiment runnable on its own: its README's commands work from that
  folder, with its own `requirements.txt` when the repository environment is
  not enough.
- Commit small inputs and outputs (CSV, JSON, figures) so a reader can check
  numbers without running anything. Large or regenerable artifacts stay local.
- Third-party PDFs are not committed; cite the record instead.
- Keep teaching stress tests and synthetic toys visibly separate from the renal
  simulations, and say which graph a number came from.
- When an experiment graduates into the paper, its code moves to the pipeline
  that produces the manuscript's results, and this folder keeps the record of
  the exploration.

## Index

| Folder or location | Question | Status |
| --- | --- | --- |
| [`confoundingshap-tutorial/`](confoundingshap-tutorial/README.md) | What ConfoundingSHAP (Brockschmidt et al., 2026) computes, shown on a three-covariate DAG with an exact answer key; what it reports when a pretreatment collider is measured | Complete, 8 October 2026; outside the Space SHAP study |
| `analysis/confoundingshap_comparison.py`, `analysis/output/confoundingshap_pilot/` | ConfoundingSHAP adjustment-bias pilot on the 51-node clean simulation, thiazides as treatment, cell-mean estimator | Complete, 30 September 2026; see the [technical note](../docs/technical/do-shapley.md) |
| `analysis/confoundingshap_tabpfn.py`, `analysis/output/confoundingshap_tabpfn/` | The same pilot with the paper's TabPFN estimator over five fixed splits | Complete, 30 September 2026; estimator sensitivity is noted in [`analysis/README.md`](../analysis/README.md) |
| `analysis/audit_ida_*.py`, `analysis/audit_ida_*.R`, `analysis/audit_bootstrap_reconciliation.R`, `analysis/output/numerical_audit_20260919/` | Numerical audit of IDA direction and reversal weights and of the full-DAG tau bootstrap | Complete, 19 September 2026; see [`docs/step06_results.md`](../docs/step06_results.md) |
| `analysis/selection_mechanism_demo.py`, `analysis/output/selection_exploration/` | Exact four-stratum selection example and population targets | Complete; see [`docs/technical/selection-mechanism.md`](../docs/technical/selection-mechanism.md) |
| `analysis/depth_washout_figure.py`, `results/figures/depth_washout.csv` | Path length and detection power in a chain with coefficient 0.6 on every edge | Complete; teaching experiment, see [`docs/technical/path-length-and-response-shape.md`](../docs/technical/path-length-and-response-shape.md) |
| `analysis/run_m1_m5_battery.py` | M1-M5 discovery battery on the toy and renal simulations | Smoke-tested in CI; the version-2 full run is not checked in (see `analysis/README.md`) |
| [`docs/lumawarp/README.md`](../docs/lumawarp/README.md), experiments E1 to E3 | Depth sensitivity of the proprietary detector and the dichromatic filter | Specified, not run; gated by Lucidity Sciences sign-off (ADR 008) |

Earlier pilots keep their current paths because their outputs are cited from
the records and technical notes. New experiments start here.
