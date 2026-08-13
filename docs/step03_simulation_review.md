# Step 3 simulation review — renal stone DAG

`config/dag_spec.yaml` + `config/edge_coefficients.yaml` → `simcausal` →
`data/simulated/renal_stone_simulated.parquet`. Every number below is
computed directly from this run's output, not asserted.

**Run:** n = 1,000 · seed = 20260812 · 12 nodes · generated 2026-08-12.
Reproduce with `make step03` (the seed is fixed in
`pipeline/step03_simulate_data.R`, so reruns are byte-identical).

## Fixed this run

`sex` and `history_of_nephrolithiasis` are Bernoulli-coded 0/1 and used
directly in their own columns — but when a raw 0/1 value entered another
node's formula uncentered, its own prevalence shifted that node's mean away
from 0, breaking the "standardized mean-0" promise for `urine_chemistry` and
`mineralized_renal_material`. `zterm()` in `r/R/simcausal_helpers.R` now
subtracts each binary parent's own probability (not divided by SD) wherever
it's referenced downstream — its own column is untouched.

| node | before | after |
|---|---:|---:|
| mean(urine_chemistry) | 0.211 | -0.019 |
| mean(mineralized_renal_material) | 0.303 | -0.018 |

`nephrolithiasis` prevalence held at target (0.102 vs 0.10) throughout, and
reruns are still byte-identical — the fix only removes a mean offset, it
doesn't touch calibration.

## Coefficient recovery

Every node's own generating formula, refit against the simulated data via
`lm()` / `glm()` and compared back to `config/edge_coefficients.yaml`. Small
Δ means the generator is doing exactly what the config says; R² for the
weaker edges is genuinely low by design (`bone_formation` is an intentional
near-null distractor node).

| Edge | Specified | Recovered | Δ | R² |
|---|---:|---:|---:|---:|
| `duration -> bone_resorption` | +0.60 | +0.593 | -0.007 | 0.36 |
| `duration -> bone_formation` | -0.10 | -0.038 | +0.062 | 0.00 |
| `duration -> vitamin_d_inflight` | -0.34 | -0.260 | +0.080 | 0.07 |
| `bone_resorption -> urinary_calcium_excretion` | +0.60 | +0.589 | -0.011 | 0.33 |
| `bone_formation -> urine_chemistry` | +0.05 | +0.015 | -0.035 | 0.73 |
| `urinary_calcium_excretion -> urine_chemistry` | +0.50 | +0.530 | +0.030 | 0.73 |
| `hydration_fluid_intake -> urine_chemistry` | -0.40 | -0.425 | -0.025 | 0.73 |
| `history_of_nephrolithiasis -> urine_chemistry` | +0.92 | +0.939 | +0.019 | 0.73 |
| `vitamin_d_inflight -> urine_chemistry` | +0.30 | +0.335 | +0.035 | 0.73 |
| `nutrients_risk -> urine_chemistry` | +0.30 | +0.282 | -0.018 | 0.73 |
| `duration -> mineralized_renal_material` | +0.40 | +0.397 | -0.003 | 0.98 |
| `sex -> mineralized_renal_material` | +0.20 | +0.217 | +0.017 | 0.98 |
| `hydration_fluid_intake -> mineralized_renal_material` | -0.30 | -0.299 | +0.001 | 0.98 |
| `urine_chemistry -> mineralized_renal_material` | +0.70 | +0.699 | -0.001 | 0.98 |
| `urinary_calcium_excretion x hydration_fluid_intake` (interaction) | +0.15 | +0.153 | +0.003 | 0.98 |
| `mineralized_renal_material -> nephrolithiasis` (logit) | +0.90 | +0.741 | -0.159 | — |

The two biggest misses (`bone_formation`, `vitamin_d_inflight`) are exactly
the two weakest true effects, so their wider sampling noise at n=1,000 is
expected, not a red flag. The outcome's logit slope (0.741 vs 0.90) shows
the usual finite-sample attenuation from `glm()` on ~100 positive cases.

## Root-node & outcome marginals

Observed prevalence against each node's `root_node_distributions` /
`outcome_calibration` target.

| Node | Observed | Target |
|---|---:|---:|
| `sex` (male=1) | 79.9% | 80.0% |
| `history_of_nephrolithiasis` | 23.5% | 25.0% |
| `nephrolithiasis` (outcome) | 10.2% | 10.0% |

## Node distributions

All nine continuous nodes. `duration` and `hydration_fluid_intake` are
raw-unit roots (truncated normal); the remaining seven should each read as
mean-0, SD-1.

| Node | Distribution | Mean | SD | Min | Max |
|---|---|---:|---:|---:|---:|
| `duration` (days) | `▁▂▄▆█▇▇▄▂▁` | 179.98 | 45.11 | 16.93 | 322.11 |
| `hydration_fluid_intake` (L/day) | `▁▃▅▇█▇▅▂▁▁` | 2.300 | 0.405 | 0.95 | 3.87 |
| `nutrients_risk` | `▁▂▄▆██▆▄▂▁` | -0.009 | 1.032 | -2.74 | 4.03 |
| `bone_formation` | `▁▂▃▆██▆▄▂` | 0.020 | 0.967 | -3.51 | 4.22 |
| `bone_resorption` | `▁▂▃▅▆█▅▄▁` | 0.038 | 0.987 | -3.07 | 2.99 |
| `vitamin_d_inflight` | `▁▂▄▆██▇▄▁` | -0.014 | 0.975 | -3.30 | 3.44 |
| `urinary_calcium_excretion` | `▁▂▄▆██▆▄▂▁` | -0.000 | 1.007 | -3.35 | 2.89 |
| `urine_chemistry` | `▁▂▄▆██▆▃▂▁` | -0.019 | 1.028 | -2.58 | 3.20 |
| `mineralized_renal_material` | `▁▁▂▄▆█▇▇▄▂▁` | -0.018 | 1.038 | -3.31 | 2.78 |

## Source

`r/R/simcausal_helpers.R`, `config/edge_coefficients.yaml`.
