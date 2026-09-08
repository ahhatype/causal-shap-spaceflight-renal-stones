# Causal SHAP: a benchmark using a spaceflight risk graph

[![Python tests](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/actions/workflows/python-tests.yml)
[Reproducibility guide](REPRODUCIBILITY.md) · [Teaching companion](docs/classroom/README.md) · [Technical notes and math](docs/technical/path-length-and-response-shape.md)

A prediction ranking explains a fitted model. To assess what would happen
after changing a variable, we also need assumptions about the causal
relationships. This study compares those answers using synthetic data based
on NASA's renal-stone graph, with numerical mechanisms chosen by the study
team. It is being developed for *npj Microgravity*.

<p align="center"><img src="docs/images/two-goals.gif" width="760" alt="Schematic X to A to M to Y chain: a prediction can rely on M while an intervention on X still reaches Y."></p>

**The animation is schematic:** its bars are not fitted SHAP values or
effect sizes, and their totals are not comparable across phases. With full
mediation and exact measurement, an ideal predictor can use M alone. A
specified change to X can still affect Y through A and M. This does not mean
all methods discard upstream variables or that the best action is upstream.
The [offline animation](docs/classroom/animation.html) provides controlled
playback after download; the [technical note](docs/technical/path-length-and-response-shape.md)
gives its assumptions. This repository is the master companion; Pages is retired.

Read the [central workflow](#the-central-workflow), follow the
[worked example](#worked-example-and-simulation), or use the
[educator guide](#teaching-materials). [ORIENTATION.md](ORIENTATION.md)
locates the project files; the [documentation index](docs/README.md) links
methods, evidence, provenance and decisions.

## The central workflow

These seven stages organize the project. The completed simulations test
parts of the workflow; the entire sequence has not been validated end to
end. A supplied graph can be evaluated directly, and discovery and review
can be revisited. A prediction study can finish after stage 2; causal
analysis does not require running SHAP first.

| Stage | Purpose | Protocol steps | Current evidence |
| --- | --- | --- | --- |
| 1. Define the study | Specify the outcome, graph assumptions and intervention contrasts. | 1–3 | Two renal graph scales and frozen simulated truth. |
| 2. Fit and explain predictions | Compare what different fitted models credit. | 4 | Five model–explainer pairings on the working subgraph. |
| 3. Examine candidate graphs | Assess structures under stated discovery assumptions. | 6 (diagnostic), 8 (pending) | A disconnected-outcome diagnostic; broader working-subgraph comparisons pending. |
| 4. Reconsider excluded candidates | Investigate discarded variables and filter noise. | 5, 7 | Detector and filter placeholders, with no evaluated results. |
| 5. Review graph assumptions | Record biological evidence and unresolved directions. | 6 | Rounds two and three use a scripted heuristic standing in for expert review. |
| 6. Follow changes through the graph | Compare causal attribution games and propagate specified interventions. | 6, 8; full-DAG pipeline | Separate full-DAG ordering-only comparison and propagation prototype. |
| 7. Evaluate feasible actions | Estimate benefit, uncertainty, feasibility and cost. | 13 | Scaffold only; outside completed article scope. |

Robustness runs across stages (protocol steps 9–11); longitudinal extension
(step 12) is future work. The [workflow and evidence map](docs/playbook/central-workflow.md)
connects each stage to its example, implementation and limits. The
[protocol crosswalk](docs/playbook/README.md#the-seven-steps-one-flow-five-tellings)
preserves coauthor Aimee Harrison's original 13-step plan and the six-rung framework.

## Worked example and simulation

The [classroom worksheet](docs/classroom/worksheet.md) combines the
animation's intermediate A into the X-to-M relation. For M = 0.6X + eM,
Y = 0.6M + eY, independent mean-zero disturbances, x = 1 and eM = 0.2:

| Quantity | X | M | What it answers |
| --- | ---: | ---: | --- |
| Predictive model-interventional Shapley credit | 0 | 0.48 | Which inputs contribute to this prediction? |
| Symmetric structural Shapley credit | 0.18 | 0.30 | How does a specified causal game distribute credit? |
| Mean effect of setting X from 0 to 1 | 0.36 | — | How much does the expected outcome change? |

The two credit allocations each sum to the prediction relative to a zero
background. The intervention contrast asks a different question. The
[answer key](docs/classroom/educator-guide.md) derives the numbers. This
exact two-player example explains stages 1, 2 and 6, using an ideal predictor in place of fitting one; it does not run the
other stages or numerically reproduce the full-DAG prototype.

The renal simulations add competing predictors, multiple pathways, an
interaction and a binary outcome. NASA supplies topology, not effect
estimates. Each model is scored against contrasts computed from the
chosen simulation mechanisms.

| Testbed | What it contributes | Result and limitation | Record |
| --- | --- | --- | --- |
| Five-node teaching stress test | A deliberately constructed attribution failure. | An outcome descendant receives 45.6% of ordinary SHAP mass despite zero total effect. Not a renal result or the classroom chain. | [Full record](docs/full_dag/RESEARCH_RECORD.md) |
| 14-node working subgraph | The primary renal case study; five model–explainer pairings and graph diagnostics. | Credit shifts in both directions by chain and model. Gaussian PC isolates the binary outcome at n = 1,000. After rounds two and three of a scripted heuristic standing in for expert review, XGBoost Kendall’s tau changes from 0.231 to 0.205 for ASV, 0.077 to 0.154 for Shapley Flow, and undefined to 0.714 for Ng et al. Method budgets and revision rules differ; no human reviewed these rounds. One seed. | [Step 4](docs/step04_results.md), [Step 6](docs/step06_results.md) |
| 51-node source DAG, 75 edges | A matched ordinary/ordering-only comparison and a separate propagation prototype with additional mechanism information. | Ordinary versus ordering-only tau 0.506 / 0.528: no detected difference. Structural propagation tau 0.794, top-five recovery 1.00: a prototype using known mechanisms and a smaller budget, without repeated-seed uncertainty; this does not establish method superiority. | [Full research record](docs/full_dag/RESEARCH_RECORD.md) |

The 14-node working graph is scoped and augmented, with coefficients
specified separately from the full simulator. It is not an unchanged subset
of the 51-node graph. Working data use n = 1,000, seed 20260812; full-DAG
clean-v3 uses n = 10,000, generation seed 20260710.

The full-DAG ordering comparison shares one fitted XGBoost model,
64 evaluation records, 128 background records and 128 permutations each; the ordering method receives the
true graph's constraints. The propagation prototype uses 32 evaluation records, 32 background records and 32 permutations. It additionally receives
the known simulation mechanisms, propagates interventions, and scores that
fitted predictor. Its budget and causal information are not matched to the ordering comparison. It is a feasibility comparison with supplied mechanisms,
not recovery of unknown mechanisms. The working-subgraph script uses the
known graph to orient unresolved edges and marginal correlation to reconnect
the isolated outcome; some other revision rules consult errors against truth.

Both renal outcomes are binary. The ranking target is the absolute change
in simulated nephrolithiasis probability between high and low settings,
computed with 50,000 common-random-number draws. Continuous contrasts are
±1 SD in the working subgraph and Q25 versus Q75 in the full DAG; binary
contrasts are 0 versus 1. See [comparison inputs and intervention definitions](docs/playbook/central-workflow.md#what-information-each-comparison-receives).

Kendall’s tau measures agreement with simulated total-effect rankings. Scores across these testbeds are not one head-to-head comparison. The
working-subgraph generator is in `config/` and `pipeline/`; the full-DAG
generator and frozen results are in `analysis/` and `apps/`.

## Path length, math and response shape

![Path length and detection](docs/images/depth-detection.svg)

A separate [depth teaching figure](docs/images/depth_washout.png) shows
how a marginal-slope test loses power along a chain with coefficient 0.6
on every edge. It is not a graph-discovery experiment. A direct arrow does
not guarantee a straight response, and greater path length does not always
mean a smaller effect. The binary-logit and interaction mechanisms already
go beyond a wholly linear-Gaussian model. Nonlinear robustness is pending.

The [technical companion](docs/technical/path-length-and-response-shape.md)
derives the path-product formula, the 0.6^d chain, the detection statistic,
the worked Shapley values and nonlinear counterexamples. It also explains
affine splines and Wahba’s smoothing framework as a possible sensitivity
analysis, not a completed comparison. [BibTeX references](docs/references/technical-companion.bib)
are available independently of the private manuscript.

```bash
python analysis/depth_washout_figure.py --verify-recorded
```

This reproduces the frozen teaching curves without overwriting them. The
recorded cutoff is |t| > 1.96, an approximate 5% rule; this is not a test
of causal-discovery accuracy.

## Teaching materials

The [educator guide](docs/classroom/educator-guide.md) includes a 50-minute
lesson, a 90-minute extension and an answer key. The
[student worksheet](docs/classroom/worksheet.md), offline interactive lab
and standard-library Python examples are in [docs/classroom](docs/classroom/README.md).
Use GitHub’s **Code → Download ZIP**, extract the repository and open
`docs/classroom/index.html` for the interactive calculation or `animation.html`
for the four-node comparison. GitHub displays HTML source rather than
executing it. To build a compact offline kit, run
`python analysis/package_classroom.py`; the ZIP is written to `dist/`. No astronaut data or proprietary runtime is
needed. Coauthor-reviewed slides and a guided renal-reproduction notebook
remain future work.

```bash
python docs/classroom/lab.py --check
```

For research exploration, the existing [Shiny companion](apps/README.md),
[hub](apps/hub/) and [Workbench](apps/workbench/README.md) run
locally with the research environment. They are distinct from the offline
classroom lesson and are not hosted by GitHub Pages.

[Protocol](#protocol) · [Repository map](#repository-map) · [Quickstart](#quickstart) · [Preserved Pages material](#preserved-pages-material) · [Manuscript](#the-manuscript)

## Protocol

The 13 steps of the methods doc, each pointing at the code that implements
it. Status is tracked in `config/pipeline_status.yaml` (and the gitignored
`docs/STATUS.md`).

| Step | What | Where | Status |
| --- | --- | --- | --- |
| 1 | Exposure and outcome: cumulative mission days; nephrolithiasis (binary) | `config/dag_spec.yaml` | done |
| 2 | DAG construction and augmentation from Robert Reynolds's supplied files | `config/dag_spec.yaml`, `r/R/dag_utils.R`, `analysis/10_ingest_robert_dags.R` | done |
| 3 | Synthetic data (simcausal) | `pipeline/step03_simulate_data.R`, `analysis/generate.R` | done |
| 4 | Baseline attribution with standard SHAP, five pairings | `pipeline/step04*`, `python/src/causal_shap_renal/attribution_baseline.py` | done |
| 5 | LumaWarp detector over Step 4 | `pipeline/step05_lumawarp_detector.py`, `python/src/causal_shap_renal/lumawarp_contract.py` | placeholder, provider gated |
| 6 | Causal SHAP comparison with scripted graph revisions | `pipeline/step06*`, `apps/causal_shap/structural_value.py` | partial: 3 methods run; round 1 unrevised, rounds 2–3 scripted; no human review |
| 7 | LumaWarp detector over Step 6 | `pipeline/step07_lumawarp_reweight.py` | placeholder, provider gated |
| 8 | Structural recovery: PC, GES, NOTEARS, LiNGAM | `pipeline/step08*`, `apps/causal_shap/discovery.py`, `apps/causal_shap/evaluation.py` (M1-M5) | library ported, runs pending |
| 9 | Robustness to the data-generating process | `apps/causal_shap/validation/` | scaffolded, pending |
| 10 | Robustness to spaceflight-epidemiological constraints | `analysis/R/renal_stone_source_aligned_simcausal.R` (NASA-like v4 selection regime) | one regime exists, sweep pending |
| 11 | Generalization to out-of-distribution populations | own section | pending |
| 12 | Longitudinal extension (g-methods) | future work | not undertaken |
| 13 | Cost-constrained recourse | `apps/causal_shap/policy.py`, `action_costs.py`, `shift_estimation.py` | scaffolded, out of the paper's scope |

The full-DAG comparison also contributes to central-workflow stage 6 through
`analysis/07_run_shap_comparison.R` and `apps/causal_shap/build/stages.py`;
these are separate from the numbered working-subgraph drivers.

Detail for Steps 1 to 6 on the working subgraph is in
`docs/step03_simulation_review.md`, `docs/step04_results.md`, and
`docs/step06_results.md`. The full-DAG methods and results are in
`docs/full_dag/RESEARCH_RECORD.md`. The LumaWarp placeholders and what is
gated are in `docs/lumawarp/README.md` and [ADR 008](docs/decisions/008-lumawarp-detector-placeholders.md).

## Repository map

```
config/           DAG spec, edge coefficients, model engines, pipeline status (YAML)
pipeline/         Numbered driver scripts for the working subgraph, one per step
r/                R package for the working subgraph (renv): DAG utilities,
                   simcausal helpers, ground truth, pcalg and shapr wrappers
python/src/       causal_shap_renal: attribution methods, discovery wrappers,
                   evaluation, the file interchange contract, the LumaWarp contract
python/tests/     pytest suite for causal_shap_renal
apps/             Ported from Target DAGs. causal_shap library (teaching DAGs,
                   discovery, experimental complexity interface, structural value function,
                   validation, M1-M5, action selection, figures); the guided hub,
                   the M1-M5 Workbench, the six-rung ladder app; frozen bundles; tests
analysis/         Ported from Target DAGs. R pipeline on the full 51-node DAG and
                   its frozen result record under analysis/output/
references/       NASA SA-07566 DAGitty text; Robert Reynolds's 2026-07-13 files
dag-candidates/   Core-graph node and edge CSVs
data/             raw, interim, simulated (gitignored, regenerated from a seed);
                   frozen_truth (committed)
results/          attributions, discovery, evaluation, figures; detector/ (gitignored)
site/             Archived Quarto presentations and assets; no Pages deployment
manuscript/       The npj Microgravity article (LaTeX, .bib, outline); gitignored for now
docs/             framing memo, playbook, notes, references, LumaWarp placeholder,
                   decisions, step results, full-DAG record. Index: docs/README.md
```

## Quickstart

One Python environment for both packages (pip and a venv; ADR 007). R is
managed by renv for the working subgraph and by `analysis/install_dependencies.R`
for the full DAG.

```bash
py -3.13 -m venv .venv
.venv/Scripts/python -m pip install -e ".[discovery,workbench,dev]"
.venv/Scripts/python -m pytest
```

Or `make setup-py` and `make test-py`. On macOS or Linux use `python3.13`
and `.venv/bin/python`.

Working-subgraph pipeline, step by step:

```bash
make step02 step03 step04 step06
```

Full-DAG record, validation, and the apps:

```bash
make full-dag-validate      # R validator + frozen-output hash gate
make hub                    # guided discovery hub, http://localhost:8002
make workbench              # M1-M5 Workbench, http://localhost:8001
make ladder                 # six-rung teaching app, http://localhost:8000
make classroom              # build the offline teaching ZIP
make depth-check            # verify frozen teaching curves without writing outputs
```

The apps run locally by design; a hosted instance cannot pin the environment
behind the published results.

## Preserved Pages material

This repository is the master for the manuscript and both companions.
Pages deployment is retired under [ADR 010](docs/decisions/010-repository-companion.md).
The technical content, teaching tools and reproduction commands are linked
above. Both generations of the former presentation and their editable
assets remain in [site/](site/README.md), while the old repository retains
its history. No Pages deployment is needed to read or reproduce the work.

## The manuscript

The article is written in LaTeX under `manuscript/` in this repository
(ADR 009: one home for the project). The folder is gitignored for now, so it
builds from the hub but is not published. The introduction is
human-written and stays that way; Methods follow the 13 steps above;
Results and Discussion are assembled from the frozen records in this
repository. `make manuscript` builds the PDF; `make figures` regenerates the
figures it reads from `docs/images/`. Coauthors receive dated PDF exports in
the Box project folder, which is for exchange, not editing.

## What is gated

LumaWarp is a proprietary Lucidity Sciences tool. The public interface
(channels, flags, provenance) is in the repository; the runtime, the bridge
that reproduces its Explain reduction, block-level results, and the working
paper are not, and stay out until Lucidity signs off. The paths are listed
in `.gitignore` under the LumaWarp boundary.

## License

GPL-3.0-or-later (`LICENSE`), for the whole repository. The code ported from
Target DAGs was originally released under MIT by the same author and was
relicensed under GPL-3.0-or-later on consolidation; `THIRD_PARTY_NOTICES.md`
records the origin. External source material remains subject to its original
terms.
