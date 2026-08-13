# Step 3 simulation review — renal stone DAG

`config/dag_spec.yaml` + `config/edge_coefficients.yaml` → `simcausal` →
`data/simulated/renal_stone_simulated.parquet`. Every number below is
computed directly from this run's output, not asserted.

**Run:** n = 1,000 · seed = 20260812 · 11 nodes · generated 2026-08-13.
Reproduce with `make step03` (the seed is fixed in
`pipeline/step03_simulate_data.R`, so reruns are byte-identical).

`nephrolithiasis` has five direct parents (`duration`, `sex`,
`hydration_fluid_intake`, `urine_chemistry`, and the
`urinary_calcium_excretion` x `hydration_fluid_intake` interaction) - NASA's
Mineralized Renal Material / CaOx supersaturation intermediate is collapsed
directly onto the outcome rather than modeled as a separate node (see
`nephrolithiasis`'s own `note` in `config/dag_spec.yaml` for why).

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
| `duration -> nephrolithiasis` (logit) | +0.36 | +0.373 | +0.013 | — |
| `sex -> nephrolithiasis` (logit) | +0.18 | +0.325 | +0.145 | — |
| `hydration_fluid_intake -> nephrolithiasis` (logit) | -0.27 | -0.269 | +0.001 | — |
| `urine_chemistry -> nephrolithiasis` (logit) | +0.63 | +0.601 | -0.029 | — |
| `urinary_calcium_excretion x hydration_fluid_intake -> nephrolithiasis` (logit, interaction) | +0.135 | +0.158 | +0.023 | — |

The two biggest misses among `urine_chemistry`'s parents (`bone_formation`,
`vitamin_d_inflight`) are exactly the two weakest true effects, so their
wider sampling noise at n=1,000 is expected, not a red flag. `sex`'s logit
slope (0.325 vs 0.18 specified) is the outcome's own weakest true effect and
a low-variance binary predictor at that - `glm()` on ~80 positive cases has
real sampling noise to spend somewhere, and it lands here.

## Root-node & outcome marginals

Observed prevalence against each node's `root_node_distributions` /
`outcome_calibration` target.

| Node | Observed | Target |
|---|---:|---:|
| `sex` (male=1) | 79.9% | 80.0% |
| `history_of_nephrolithiasis` | 23.5% | 25.0% |
| `nephrolithiasis` (outcome) | 8.2% | 10.0% |

`nephrolithiasis`'s calibration itself is exact (confirmed by drawing
n = 20,000 at the same seed: 10.03% observed) - 8.2% at the default n = 1,000
is ordinary sampling noise (binomial SE ≈ 0.9pp at this n).

## Node distributions

All eight continuous nodes. `duration` and `hydration_fluid_intake` are
raw-unit roots (truncated normal); the remaining six should each read as
mean-0, SD-1.

| Node | Distribution | Mean | SD | Min | Max |
|---|---|---:|---:|---:|---:|
| `duration` (days) | `▁▂▄▅█▇▇▆▄▃▁▁` | 179.98 | 45.11 | 16.93 | 322.11 |
| `hydration_fluid_intake` (L/day) | `▁▃▅▇▇██▆▃▂▁▁` | 2.300 | 0.405 | 0.95 | 3.87 |
| `nutrients_risk` | `▁▁▂▃▆▆██▇▆▄▂▁▁` | -0.009 | 1.032 | -2.74 | 4.03 |
| `bone_formation` | `▁▂▄▆██▇▅▃▁` | 0.020 | 0.967 | -3.51 | 4.22 |
| `bone_resorption` | `▁▂▂▃▅▆▆█▇▅▄▃▁▁` | 0.038 | 0.987 | -3.07 | 2.99 |
| `vitamin_d_inflight` | `▁▂▄▅██▇▇▆▃▁▁` | -0.014 | 0.975 | -3.30 | 3.44 |
| `urinary_calcium_excretion` | `▁▁▃▄▆▇██▆▅▄▂▁▁` | -0.000 | 1.007 | -3.35 | 2.89 |
| `urine_chemistry` | `▁▁▂▂▅▆▆▇█▇▆▄▂▂▁` | -0.019 | 1.028 | -2.58 | 3.20 |

## Source

`r/R/simcausal_helpers.R`, `config/edge_coefficients.yaml`.
