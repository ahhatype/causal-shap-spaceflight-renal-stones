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

1. **Exposure and outcome specification.** Cumulative mission duration as exposure, nephrolithiasis (binary incidence) as the sole outcome. CaOx supersaturation (Mineralized Renal Material) remains in the graph as an internal mediator only, not a modeled outcome.
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
12. **Longitudinal extension.** Future work, not undertaken in this paper. Vitamin D's dual role as pre-flight confounder and in-flight mediator is a treatment-confounder feedback case, the fix is g-methods.
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
_write-up to come_

### Step 2: DAG construction and expert-guided augmentation
_write-up to come_

### Step 3: Synthetic data generation
_write-up to come_

### Step 4: Baseline attribution with standard SHAP
_write-up to come_

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
