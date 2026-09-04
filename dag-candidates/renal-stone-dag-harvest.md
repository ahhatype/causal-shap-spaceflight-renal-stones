# Renal Stone DAG Harvest - First Pass

> Ported from the Box project folder on 2026-09-04 (Andy Wilson's July 2026 notes). Paths and links inside refer to the Target DAGs repository as it stood then; the canonical implementations now live under `analysis/` and `apps/` in this hub.

Status: structurally source-aligned to NASA SA-07566; scientific version choice and parameter review remain provisional.

## Source hierarchy

1. **Current machine-readable canonical source:** NASA SA-07566 DAG code in `references/renal-stone-dag-code-SA-07566.txt` (51 nodes / 75 edges) plus `references/renal-stone-risk-dag-narrative-NASA.pdf`.
2. **Exact conversation artifact:** `raw images and figures/renal-stone-dag-ch11-email-inline.png`, the Figure 11.6 image embedded in the 2026-07-08 `Causal SHAP (Space EPI)` email.
3. **Local book chapter:** `references/b5368_Ch-11.pdf`, printed p. 312 / PDF p. 22. The surrounding text says the detailed version expands medical illness into infection, hydronephrosis, renal colic, renal failure, and sepsis.
4. **ASGSR 2023 alternate version:** `references/ASGSR-2023-renal-stone-DAG-analytics.pdf`, labeled 53 entities / 83 edges and separating bone formation from bone resorption.
5. **Primary NASA technical report:** NASA/TP-20220015709, renal-stone DAG and narrative on report pp. 68-70.

These are related but non-identical versions. The source-aligned v3/v4 simulators use SA-07566 because it is the only version supplied with exact machine-readable edge code. See `notes/2026-07-10-dag-concordance.md`.

Chapter 11 Figure 11.2 is a useful orientation only:

`altered gravity -> bone remodeling -> urine chemistry changes -> nephrolithiasis`

The simulator uses the Figure 11.6 mechanistic spine and expanded complication block.

## Modeling cut for the first executable version

Retained:

- Altered gravity, hostile closed environment, CO2, urinary retention, diet, and microbiome contributors.
- Resistive exercise, bisphosphonate, adequate water intake, potassium citrate, and thiazide as transparent prevention levers.
- Bone remodeling, hydration, urine concentration, urine chemistry, mineralized renal material, nephrolithiasis, ureterolithiasis, and urine flow.
- Renal colic, hydronephrosis, infection, sepsis, and renal failure as the expanded medical-illness block.
- Individual readiness, evacuation, crew capability, task performance, mission objectives, mission loss, crew-life loss, and long-term health outcomes.

Deferred from the executable core, but preserved in the source image:

- Vehicle design and the Crew Health and Performance System capability-allocation subgraph.
- Medical monitoring, diagnosis, treatment-capability, surveillance, and flight-recertification subgraphs.
- Explicit ultrasound manipulation, percutaneous nephrostomy, tamsulosin, medications, and detection nodes.

Those capability nodes are important for the later intervention/cost-sensitive DiCE layer, but they would add many illustrative structural equations before the renal mechanism itself is validated.

## Reparameterizations and augmentations

- The NASA node `Urine Flow` is represented as `impaired_urine_flow`, so larger values consistently mean greater risk. Protective interventions therefore have negative coefficients when they are added later.
- Figure 11.6 presents `Astronaut Selection -> Individual Factors`, treating selection as a prevention/capability mechanism. For the version-2 sampling experiment, the source-population data-generating graph instead adds `baseline_fitness`, `individual_susceptibility`, and `age_z` as causes of `selected_astronaut`, then conditions the observed sample on selection. This is an explicit observation-process augmentation motivated by Aimee's 2026-07-09 email, not a claimed correction to NASA's risk DAG.
- `medical_illness` is a deterministic summary of whether any expanded complication is present. The individual complications remain available as features and outcomes.

## Parameter status

All coefficients and intercepts in `analysis/R/renal_stone_simcausal.R` are transparent placeholders selected to produce nondegenerate, reasonably sparse first-pass data. They are not empirical NASA estimates. The generated prevalence and effect sizes are simulation-design choices to be reviewed and calibrated.

## Executable artifacts

- `analysis/01_generate_clean.R` - 10,000 complete observations from the renal DAG.
- `analysis/02_generate_nasa_like.R` - 50,000-person source population, astronaut selection, 450-person observed cohort, and informative measurement sparsity.
- `analysis/validate_outputs.R` - structural/output smoke tests.
- `dag-candidates/renal-stone-core-nodes.csv` - node roles and source mapping.
- `dag-candidates/renal-stone-core-edges.csv` - edges implemented in the first-pass structural equations.

## SME review questions

- Is nephrolithiasis the correct primary endpoint, or should the first paper target medical illness or mission impact?
- Should mineralized renal material be binary, ordinal, or continuous?
- Which contributors/interventions should be fixed by mission design rather than simulated as individual-level variables?
- Are the expanded complication arrows correct, especially infection/sepsis/renal-failure progression?
- Which nodes are actionable, at what time horizon, and with what approximate cost/difficulty?
