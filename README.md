# Causal SHAP: Spaceflight-Induced Renal Stones

> This is a parallel project to Andy Wilson's [andystats/causal-shap-target-dags](https://github.com/andystats/causal-shap-target-dags), which already has a working end-to-end pipeline on the renal DAG (ingest, simulate, frozen truth, out-of-box SHAP, ASV, a structural-SHAP prototype). This repo does not depend on or vendor that code. It is standalone, and builds the parts of the paper that repo doesn't cover yet: the human-in-the-loop iteration design, the full 4-method comparison, and the robustness and generalization sweeps.

## What this is

Understanding the causal pathways between spaceflight hazards and health outcomes is a key need for deep space travel, and NASA's Human System Risk Board maintains expert-built directed acyclic graphs (DAGs) for its known risks. SHAP (SHapley Additive exPlanations) is a popular way to explain what a predictive model learned, but out of the box it has no notion of causal structure. It can identify spurious relationships and underweight downstream effects, which risks incorrect causal conclusions if its output is read as if it were causal. Causally informed variants of SHAP are aware of the causal structure and should recover feature importance with more fidelity.

This project runs a systematic comparison of standard, causality-blind SHAP against several causally informed variants, scored against a known ground truth. The primary case study is NASA's Risk of Renal Stone Formation DAG (SA-07566), with nephrolithiasis as the outcome. Data is synthetic, generated from a specified causal structure, so the true feature importance is defined by construction and every method can be scored against it. The comparison also studies whether iterative expert revision of the causal structure improves recovery as the data are degraded toward the constraints typical of spaceflight epidemiology (small samples, selection bias, narrow demographic ranges).

## Tech stack

This is a two-language repo, R and Python side by side. That split isn't a style choice, it's forced by the packages each method needs:

**R only, no real Python substitute:**
- `simcausal`, the sole default data generator (Step 3)
- `pcalg::ida()`, the IDA half of Ng et al.'s Causal SHAP (Step 6). Python's `causal-learn` has PC but no IDA equivalent.

**R native, thin Python wrapper only:**
- `shapr`, for Heskes et al.'s Causal Shapley Values and Frye et al.'s Asymmetric Shapley Values (Step 6)

**Python, the original authors' own implementations:**
- `shap`, for the out-of-box explainers (Step 4): TreeExplainer, LinearExplainer, KernelExplainer, PermutationExplainer
- `shapflow`, for Shapley Flow (Step 6)
- `lingam`, for LiNGAM causal discovery (Step 8)

**Python, canonical reference implementation:**
- NOTEARS (Step 8). R ports exist but aren't well maintained.

**Either language, R is used here:**
- PC and GES (Step 8) exist in both `pcalg` (R) and `causal-learn` (Python). Since PC is already produced in R for Step 6 (to feed IDA), Step 8 reuses that same CPDAG instead of recomputing it in Python.

R and Python never talk to each other at runtime (no `reticulate`, no `rpy2`). They exchange files: YAML for the DAG spec and coefficients, Parquet for simulated data and attribution output. See `docs/decisions/` for the full reasoning.

## Folder structure

```
config/           DAG spec, edge coefficients, pipeline status, all YAML
r/                R package code (renv-managed): DAG utilities, simcausal
                   helpers, pcalg wrappers, shapr wrappers, the R side of
                   the file interchange contract
python/           Python package code (uv-managed): the attribution methods,
                   discovery methods, evaluation metrics, the Python side of
                   the file interchange contract
pipeline/         Thin, numbered driver scripts, one per step or sub-step,
                   traceable 1:1 to the step numbers in docs/methods
data/             raw (source DAG files), interim (reconciled DAG), simulated
                   (Step 3 output), frozen_truth (Step 4 baseline ground
                   truth). Mostly gitignored, large files are regenerated
                   from a seed rather than committed
results/          attributions, discovery, evaluation, figures
notebooks/        exploratory work only, never the system of record
docs/             methods draft, provenance notes, decision records, STATUS.md,
                   dag_README.md + renal_stone_working_subgraph.txt (DAGitty
                   export of the working subgraph)
```

## Protocol

This lists all 13 steps from the methods doc, in order, so the numbering stays legible against it. Steps 5 and 7 (LumaWarp) run in a separate repo, owned by Lexi Pasi and Andy Wilson, and are listed here only to keep the sequence intact.

1. **Exposure and outcome specification.** Cumulative mission duration as exposure, nephrolithiasis (binary incidence) as the sole outcome. CaOx supersaturation (Mineralized Renal Material), NASA's own intermediate step toward stone formation, is collapsed directly onto the outcome rather than modeled as a separate node - see Step 1 below.
2. **DAG construction and expert-guided augmentation.** An 11-node working subgraph scoped from Robert Reynolds's 53-node source DAG.
3. **Synthetic data generation.** simcausal, seeded from the DAG, with literature-informed placeholder coefficients pending Robert's calibration.
4. **Baseline attribution with standard SHAP.** Five explainer/model pairings, run once at full breadth to see whether standard SHAP fails consistently or only for some model classes.
5. **Complexity-aware reweighting.** LumaWarp. Runs in a separate repo.
6. **Causal SHAP comparison and human-in-the-loop iteration.** Four methods (Heskes Causal Shapley Values, Shapley Flow, ASV, Ng et al.'s Causal SHAP), each revised by the domain expert over three rounds.
7. **Complexity-aware reweighting of Step 6 outputs.** LumaWarp. Runs in a separate repo.
8. **Structural recovery comparison.** PC (reused from Step 6), GES, NOTEARS, LiNGAM, scored against the known generating structure.
9. **Robustness to the data-generating process.** Extension. Re-runs Steps 4 through 8 on data from additional simulators.
10. **Robustness to spaceflight-epidemiological constraints.** Extension. Re-runs the narrowed pipeline under sampling regimes that emulate small N, selection bias, and narrow demographic ranges.
11. **Generalization to out-of-distribution populations.** Its own section, not a robustness pass. Commercial spaceflight participants, exploration-duration missions.
12. **Longitudinal extension.** Future work, not undertaken in this paper. A variable that's both a baseline confounder pre-flight and a duration-driven mediator in-flight is a treatment-confounder feedback case; the fix is g-methods.
13. **Counterfactual recourse extension (cost-sensitive DiCE).** Out of scope. For Andy and Lexi to define and own.

## Implementation

What exists right now is the environment and the folder scaffolding, not the step logic itself. Set up both environments like this:

```bash
# R
cd r
Rscript -e 'renv::restore(prompt = FALSE)'

# Python
cd python
uv sync --extra discovery --extra shapley-flow --extra dev
```

Or from the repo root: `make setup`.

Below is a placeholder for each step, to be filled in as it's built.

### Step 1: Exposure and outcome specification

Exposure is `duration`, cumulative mission days. Outcome is `nephrolithiasis`, binary
kidney-stone incidence - NASA's own DAG target, and the 2nd most likely reason for ISS
emergency medical evacuation per NASA's Integrated Medical Model. Unlike the bone track
(which needed a rodent-mechanical-testing proxy to translate to human outcomes),
nephrolithiasis is directly, clinically observable in humans (ultrasound, CT), so no
translational proxy is needed - a single binary outcome, logit link throughout (see
`config/dag_spec.yaml`'s `outcome`/`outcome_type` fields). Mineralized Renal Material
(CaOx supersaturation) has the richest quantitative evidence in the source DAG (25%
pre-flight -> 46% post-flight elevated prevalence) and is NASA's own confirmed
intermediate step toward stone formation, but this working subgraph collapses it
directly onto `nephrolithiasis` rather than modeling it as a separate node - see Step 2
below for why.

### Step 2: DAG construction and expert-guided augmentation

`config/dag_spec.yaml` is the 11-node working subgraph scoped down from Robert
Reynolds's 53-node source DAG (SA-07566), source-aligned to the published NASA graph.
Every node carries a `type` (`exposure`, `outcome`, `confounder`, `mediator`,
`exogenous_confounder`, `confounder_countermeasure`, `mediator_countermeasure`), a
`measure`, and a `source` citation; every edge carries a `status`
(`confirmed_mechanism` / `magnitude_estimate` / `directional_only`) and its evidence
basis. `bone_formation`/`bone_resorption` carry over from an earlier bone-fracture DAG
track (dropped as a separate direction; they sit directly upstream in NASA's renal
reference graph). `history_of_nephrolithiasis` (personal/family history) is the
exogenous confounder on the `urine_chemistry` pathway - a well-established,
independent stone-risk predictor in its own right, and a cleaner fit for this paper's
static-DAG scope than modeling in-flight Vitamin D dynamics, which would need the
treatment-confounder-feedback machinery (g-methods) deferred to Step 12.

Mineralized Renal Material (CaOx supersaturation) is NASA's own confirmed intermediate
step between `urine_chemistry` and `nephrolithiasis`, but is not a separate node here:
it was `nephrolithiasis`'s *only* parent in the DAG, so every downstream node reached
the outcome exclusively through it - a real problem for a repo whose whole point is
comparing feature-attribution methods, since any method (causal or not) would correctly
collapse 100% of the outcome's variance onto that one feature and 0% onto everything
else. `nephrolithiasis`'s own `note` field in `config/dag_spec.yaml` and the `note` on
the `urine_chemistry -> nephrolithiasis` edge in `config/edge_coefficients.yaml` record
exactly how the two collapsed steps' coefficients (0.70 and 0.90) combine, and which of
the DAG's other coefficients were rescaled by the same factor as a result.

`r/R/dag_utils.R` turns the spec into a `dagitty` object (`dag_spec_to_dagitty()`) with
a deterministic, reproducible layered layout (`dag_spec_positions()` - longest-path
depth from a root, no `dagitty::graphLayout()` randomness). `pipeline/step02_dag_construction.R`
writes it to `data/interim/renal_stone_working_dag.txt`; a browsable copy lives at
`docs/renal_stone_working_subgraph.txt` (regenerate both together, see `docs/dag_README.md`
for the exact `make step02` + copy commands and for pasting into https://dagitty.net/dags.html).

### Step 3: Synthetic data generation

`r/R/simcausal_helpers.R` turns `config/dag_spec.yaml` (topology) + `config/edge_coefficients.yaml`
(path coefficients, root-node distributions, the `urinary_calcium_excretion` x
`hydration_fluid_intake` interaction term, outcome calibration target) into a `simcausal`
structural equation model, entirely config-driven - a coefficient changing in the YAML
never requires touching the R code. `pipeline/step03_simulate_data.R` writes
`data/simulated/renal_stone_simulated.parquet` (gitignored - regenerated from a seed,
n = 1,000 default, seed fixed at 20260812 for byte-identical reruns).

Three things worth knowing if you're reading the code: `simcausal::node()` rejects any
name containing `_`, so every snake_case id is aliased to an underscore-free name
internally and mapped back on the output columns (`node_alias()`/`dealias_columns()`).
Binary root nodes (`sex`, `history_of_nephrolithiasis`) are mean-centered - not scaled -
wherever they enter another node's formula, so they don't shift a downstream
standardized node's mean away from 0 (`zterm()`). Residual/noise SD per node is
calibrated empirically (`empirical_residual_sd()` - simulate the DAG built so far and
measure the actual variance of the new node's formula against it) rather than assumed
independent, since some nodes' parents reach them through more than one path.
`nephrolithiasis`'s logit intercept is likewise calibrated empirically against
`outcome_calibration`'s target prevalence (`calibrate_intercept()`, via `uniroot()`).
See `docs/step03_simulation_review.md` for a full run review: coefficient recovery
(every node's generating formula refit via `lm()`/`glm()` against the simulated data and
compared back to the YAML), root-node and outcome marginals, and per-node distributions.

### Step 4: Baseline attribution with standard SHAP

Two parts: a DAG-derived ground truth (R, `pipeline/step04a_ground_truth.R`), computed
independently of and before any attribution method so there's no leakage; and the five
explainer/model pairings themselves (Python, `pipeline/step04_baseline_shap.py`). The
model's feature set is every non-outcome node in `config/dag_spec.yaml`
(`model_features()` in `r/R/dag_utils.R` / `python/src/causal_shap_renal/io_contract.py`
- read once from the DAG spec, not hand-listed in either language, so it can never drift
out of sync between the ground truth and the attribution models). Five genuine mediators
sit in that feature set (`bone_formation`, `bone_resorption`, `vitamin_d_inflight`,
`urinary_calcium_excretion`, `urine_chemistry`), so the mediation-testing question - does
a causally faithful method split `duration`'s effect between `duration` and its
mediators, rather than double-counting it on `duration` - has somewhere real to land.

**Ground truth (`data/frozen_truth/ground_truth_total_effects.parquet`).** For each of
the 10 candidate features, `r/R/ground_truth.R` computes a standardized total effect as
an interventional (`do()`-style) risk difference, not a correlation or a fitted model's
coefficient:

1. Two levels are defined per feature - `hi` and `lo` - depending on what kind of node
   it is: binary root nodes (`sex`, `history_of_nephrolithiasis`) use 1 vs. 0;
   raw-unit continuous roots (`duration`, `hydration_fluid_intake`) use their own
   mean + SD vs. mean − SD, in real-world units; every other (already-standardized)
   continuous node uses +1 vs. −1.
2. `simcausal`'s `action()` mechanism forces the feature to each constant in turn,
   severing its normal causal parents (`do(feature = hi)` / `do(feature = lo)`), and
   simulates the rest of the calibrated 11-node DAG forward from there.
3. Both counterfactual draws come from a single `sim()` call sharing one seed - common
   random numbers - so every other node's noise term is identical between the two
   scenarios; only what the intervention itself changes differs. n = 50,000 per
   scenario, matching the sibling repo's own precedent for this exact computation.
4. `true_total_effect = mean(nephrolithiasis | do(feature = hi)) - mean(nephrolithiasis | do(feature = lo))`
   - the change in P(nephrolithiasis = 1) from moving the feature from its low level to
     its high level, marginalized over the rest of the DAG's randomness.
   `true_total_effect_abs` is also stored.

Because this comes directly from `config/edge_coefficients.yaml`'s known structural
equations rather than from any fitted model or SHAP output, it's a fixed target every
attribution method (Step 4 onward) can be scored against, computed once and frozen.

**Attributions (`results/attributions/step04_baseline_shap.parquet`).** TreeExplainer x
{Random Forest, XGBoost} (interventional), LinearExplainer x logistic regression
(empirical covariance masker), and KernelExplainer/PermutationExplainer x XGBoost as a
black box (SuperLearner deferred - see `docs/decisions/005-superlearner-deferred.md`).
Link function is logit throughout; see `attribution_baseline.py`'s module docstring for
the one scale exception (`tree_shap` + `random_forest` has no logit margin to sit on and
stays on the probability scale, unlike the other four pairings).

### Step 6: Causal SHAP comparison and human-in-the-loop iteration
_write-up to come_

### Step 8: Structural recovery comparison
_write-up to come_

### Step 9: Robustness to the data-generating process
_write-up to come_

### Step 10: Robustness to spaceflight-epidemiological constraints
_write-up to come_

### Step 11: Generalization to out-of-distribution populations
_write-up to come_

Steps 5 and 7 (LumaWarp) live in a separate repo. Steps 12 and 13 are future work and out of scope, respectively, see the Protocol section above.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE), share and share alike: you're free to use, modify, and distribute this work, provided derivative works remain open under the same license.
