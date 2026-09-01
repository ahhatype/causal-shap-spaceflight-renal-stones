# Step 3 simulation review — renal stone DAG

`config/dag_spec.yaml` + `config/edge_coefficients.yaml` → `simcausal` →
`data/simulated/renal_stone_simulated.parquet`. Every number below is
computed directly from this run's output, not asserted.

**Run:** n = 1,000 · seed = 20260812 · 14 nodes · generated 2026-08-14.
Reproduce with `make step03` (the seed is fixed in
`pipeline/step03_simulate_data.R`, so reruns are byte-identical).

Three new nodes deepen two existing pathways and add one confounder with real
fan-out, all grounded in renal-stone/spaceflight physiology literature (see
each node's `source` in `config/dag_spec.yaml`):

- `parathyroid_suppression` splits `bone_resorption -> urinary_calcium_excretion`
  into a direct mechanism plus a PTH-mediated one (bone-released calcium
  suppresses PTH; lower PTH raises renal calcium excretion).
- `urinary_oxalate_excretion` splits `nutrients_risk -> urine_chemistry` into a
  residual (calcium/magnesium) mechanism plus an oxalate-specific one.
- `hypercalciuria_predisposition` is a new exogenous confounder feeding both
  `bone_resorption` and `urinary_calcium_excretion` - distinct from
  `history_of_nephrolithiasis` (personal/family stone *history*): this is the
  underlying calcium-handling phenotype itself.

## Coefficient recovery

Every node's own generating formula, refit against the simulated data via
`lm()` / `glm()` and compared back to `config/edge_coefficients.yaml`.

| Edge | Specified | Recovered | Δ | R² |
|---|---:|---:|---:|---:|
| `duration -> bone_resorption` | +0.60 | +0.668 | +0.068 | 0.42 |
| `duration -> bone_formation` | -0.10 | -0.108 | -0.008 | 0.01 |
| `duration -> vitamin_d_inflight` | -0.34 | -0.328 | +0.012 | 0.11 |
| `hypercalciuria_predisposition -> bone_resorption` | +0.20 | +0.186 | -0.014 | 0.03 |
| `bone_resorption -> parathyroid_suppression` | +0.55 | +0.549 | -0.001 | 0.33 |
| `nutrients_risk -> urinary_oxalate_excretion` | +0.55 | +0.601 | +0.051 | 0.30 |
| `bone_resorption -> urinary_calcium_excretion` | +0.30 | +0.258 | -0.042 | — |
| `parathyroid_suppression -> urinary_calcium_excretion` | +0.35 | +0.394 | +0.044 | — |
| `hypercalciuria_predisposition -> urinary_calcium_excretion` | +0.40 | +0.386 | -0.014 | 0.57* |
| `bone_formation -> urine_chemistry` | +0.05 | +0.040 | -0.010 | — |
| `urinary_calcium_excretion -> urine_chemistry` | +0.50 | +0.502 | +0.002 | — |
| `hydration_fluid_intake -> urine_chemistry` | -0.40 | -0.387 | +0.013 | — |
| `history_of_nephrolithiasis -> urine_chemistry` | +0.92 | +0.935 | +0.015 | — |
| `vitamin_d_inflight -> urine_chemistry` | +0.30 | +0.334 | +0.034 | — |
| `nutrients_risk -> urine_chemistry` | +0.10 | +0.111 | +0.011 | — |
| `urinary_oxalate_excretion -> urine_chemistry` | +0.45 | +0.443 | -0.007 | 0.89* |

*R² shown once for the full multi-predictor `lm()` each row belongs to
(`urinary_calcium_excretion`'s 3-parent fit, `urine_chemistry`'s 7-parent fit).

Recovery is tight everywhere except `duration -> bone_resorption` (+0.068,
still well within sampling noise given R²=0.42 on this edge) and
`hypercalciuria_predisposition -> bone_resorption` (weakest true effect among
the new edges, R²=0.03 - exactly the pattern already established for weak
edges at this n).

## Residual variance check

The two nodes with the most incoming paths after this change -
`urinary_calcium_excretion` (3 parents) and `urine_chemistry` (7 parents) -
were the ones flagged as worth watching before running this. No
`empirical_residual_sd()` "explains >=100% of variance" warning fired, and
every node's simulated SD lands close to the target 1.0:

| Node | SD |
|---|---:|
| `bone_formation` | 0.987 |
| `bone_resorption` | 1.039 |
| `vitamin_d_inflight` | 0.995 |
| `parathyroid_suppression` | 0.994 |
| `urinary_oxalate_excretion` | 1.028 |
| `urinary_calcium_excretion` | 1.013 |
| `urine_chemistry` | 1.001 |
| `hypercalciuria_predisposition` | 1.032 |
| `nutrients_risk` | 0.938 |

## Root-node & outcome marginals

| Node | Observed | Target |
|---|---:|---:|
| `sex` (male=1) | 79.9% | 80.0% |
| `history_of_nephrolithiasis` | 23.5% | 25.0% |
| `nephrolithiasis` (outcome) | 9.1% | 10.0% |

## Node distributions

All eleven continuous nodes. `duration` and `hydration_fluid_intake` are
raw-unit roots (truncated normal); the remaining nine should each read as
mean-0, SD-1.

| Node | Distribution | Mean | SD | Min | Max |
|---|---|---:|---:|---:|---:|
| `duration` (days) | `▁▂▄▅█▇▇▆▄▃▁▁` | 179.98 | 45.11 | 16.93 | 322.11 |
| `hydration_fluid_intake` (L/day) | `▁▃▅▇▇██▆▃▂▁▁` | 2.300 | 0.405 | 0.95 | 3.87 |
| `nutrients_risk` | `▁▂▃▆▆▇█▇▆▄▂▁` | -0.018 | 0.938 | -3.13 | 3.06 |
| `bone_formation` | `▁▁▂▃▄▅▇███▆▄▂▁▁` | 0.048 | 0.987 | -2.88 | 2.98 |
| `bone_resorption` | `▁▁▁▃▃▅▆▇█▆▇▄▃▁▁` | -0.014 | 1.039 | -3.23 | 3.10 |
| `urinary_oxalate_excretion` | `▁▁▂▅▆▇█▆▄▃▁▁` | -0.034 | 1.028 | -4.03 | 3.24 |
| `vitamin_d_inflight` | `▁▁▃▅▇██▇▅▃▁▁` | 0.003 | 0.995 | -3.26 | 4.06 |
| `parathyroid_suppression` | `▂▂▄▅▇█▇▇▆▃▂▁` | -0.044 | 0.994 | -2.93 | 3.62 |
| `urinary_calcium_excretion` | `▁▂▂▄▇▆█▇▆▅▄▂▁▁` | -0.005 | 1.013 | -2.67 | 3.43 |
| `urine_chemistry` | `▁▃▄▆▆██▇▆▄▃▁▁▁` | -0.016 | 1.001 | -3.20 | 3.02 |
| `hypercalciuria_predisposition` | `▁▁▂▃▆▆██▇▆▄▂▁▁` | -0.009 | 1.032 | -2.74 | 4.03 |

## Source

`r/R/simcausal_helpers.R`, `config/edge_coefficients.yaml`. No R/Python code changes
were needed to add the three new nodes - `node_order()`, `build_dag()`,
`build_mean_formula()`, and `empirical_residual_sd()` all read `config/dag_spec.yaml`
and `config/edge_coefficients.yaml` generically at runtime.
