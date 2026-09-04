# Causal SHAP: Spaceflight-Induced Renal Stones

[![Python tests](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/actions/workflows/python-tests.yml)
[![Site](https://img.shields.io/badge/site-andystats.github.io-1a1814)](https://andystats.github.io/causal-shap-target-dags/)

**Your roadmap should follow your goal.** Prediction is often the default
playbook. The goal of intervention is to identify intervenable levers, which
motivates casting a wider net and retaining deeper nodes in the graph. Once a
mediator is measured, a predictor has little use for the cause behind it, so
the mediator collects the credit and the ranking is still right about the
model. Intervention needs the manipulable ancestors whose change would reach
the outcome, and the upstream ones sit where a predictor has the least reason
to look.

<p align="center"><img src="docs/images/two-goals.gif" width="760" alt="A four-node chain. Under prediction, credit pools on the mediator nearest the outcome and the deep cause receives almost none. Under intervention, a signal travels from the deep cause down the chain and the credit returns to it."></p>

This repository is the home of the Space SHAP study, written for *npj
Microgravity* (collection: Human System Risk Management and Knowledge Graphs
for Human Spaceflight, Vol. II). It tests one path from data to an
intervention target on NASA's renal-stone DAG, with data simulated from that
topology under coefficients we chose, so the true total effect of every node
is known and every method is scored against it. Say "NASA-topology
simulation", never "NASA effect".

New here? [ORIENTATION.md](ORIENTATION.md) says where everything is, how to
run it, what is done, and what to pick up next. The one-page version of the
argument is the [site](https://andystats.github.io/causal-shap-target-dags/).

## The path

Seven steps. The first two are the prediction recipe, and it stops there. The
rest is the intervention recipe. The written guide, with inputs, tools, and
the failure each step guards against, is [docs/playbook](docs/playbook/README.md).

| | Step | Question | Protocol steps | Where |
| --- | --- | --- | --- | --- |
| 01 | Data | What do we have, and what do we already believe? | 1 to 3 | `config/dag_spec.yaml`, `pipeline/step03_simulate_data.R` |
| 02 | Predict and explain | What is likely to happen, and what did the model use? | 4 | `pipeline/step04_baseline_shap.py` |
| | *prediction stops here* | | | |
| 03 | Discover | What structure do the data support, under the usual assumptions? | 8 | `apps/causal_shap/discovery.py`, `evaluation.py` (M1 to M5) |
| 04 | Cast wider, then filter | Which discarded nodes deserve a second look, and which are noise? | 5, 7 | `python/src/causal_shap_renal/lumawarp_contract.py` (placeholder, provider gated) |
| 05 | Resolve the graph | Which way do the unresolved arrows point? | 6 | `pipeline/step06*`, [DAG harvest protocol](docs/playbook/dag-harvest-protocol.md) |
| 06 | Propagate | What moves under do()? | 6, 8 | `apps/causal_shap/structural_value.py` |
| 07 | Price | Which affordable action is worth testing? | 13 | `apps/causal_shap/policy.py` (scaffolded, out of the article's scope) |
| | *robustness runs across every step* | | 9 to 11 | `apps/causal_shap/validation/`, `analysis/R/renal_stone_source_aligned_simcausal.R` |

Why the net has to be wider: the manipulable ancestors sit upstream, and
three effects compound against them. In a linear structural model the total
effect along a chain is a product of edge coefficients, so with standardized
coefficients below one every hop multiplies by a fraction. Measurement error
in each mediator leaves the effect unchanged and makes it harder to estimate. Constraint-based discovery loses power as
conditioning sets grow. The figure in `docs/images/depth_washout.png` shows
sampling variance alone removing the deep layers at astronaut-cohort sizes.
The [framing memo](docs/framing/prediction-vs-intervention.md) carries the
argument with citations.

Lineage: the [ACIC 2026 Causal SHAP project](https://www.tao-rwd.com/acic-2026/causal-shap)
illustrated the attribution problem and set out a five-step expert-augmented
workflow; [Target DAGs](https://andystats.github.io/causal-shap-target-dags/target-dags.html)
asked which upstream node to change; this study asks how to find the deeper
nodes the prediction recipe washes out, and how to prune them honestly.
[ADR 007](docs/decisions/007-target-dags-consolidation.md) records what moved
where when the two repositories were consolidated.

## Two lines of work

| | Working subgraph | Full source DAG |
| --- | --- | --- |
| Nodes | 14, scoped from the source graph | 51 nodes, 75 edges, source-exact |
| Where | `config/`, `pipeline/`, `r/`, `python/src/causal_shap_renal/`, `results/`, `docs/step0N_results.md` | `analysis/`, `apps/`, `docs/full_dag/` |
| Generator | `simcausal` from `config/edge_coefficients.yaml` | `simcausal` from the DAGitty text |
| Frozen truth | do(hi) vs do(lo), common random numbers, n = 50,000 | Same recipe, 28 ancestors |
| Headline so far | Predictive attribution misplaces credit along two-hop chains in a direction that depends on the model class; PC pruned every edge into the outcome at n = 1,000; Ng et al.'s method reaches τ 0.714 once the outcome is reconnected | Ordering-only SHAP tied with ordinary SHAP (τ 0.528 vs 0.506); structural propagation τ 0.794, top-five recovery 1.00 (32×32×32 prototype) |
| Record | `docs/step04_results.md`, `docs/step06_results.md` | `docs/full_dag/RESEARCH_RECORD.md` |

The working subgraph is the paper's primary case study. The full DAG carries
the ordering-only null and the propagation result, and is the scale the
paper extends to. They share one Python distribution and one evaluation
vocabulary.

## Protocol

The 13 steps of the methods doc, each pointing at the code that implements
it. Status is tracked in `config/pipeline_status.yaml` (and the gitignored
`docs/STATUS.md`).

| Step | What | Where | Status |
| --- | --- | --- | --- |
| 1 | Exposure and outcome: cumulative mission days; nephrolithiasis (binary) | `config/dag_spec.yaml` | done |
| 2 | DAG construction and expert-guided augmentation | `config/dag_spec.yaml`, `r/R/dag_utils.R`, `analysis/10_ingest_robert_dags.R` | done |
| 3 | Synthetic data (simcausal) | `pipeline/step03_simulate_data.R`, `analysis/generate.R` | done |
| 4 | Baseline attribution with standard SHAP, five pairings | `pipeline/step04*`, `python/src/causal_shap_renal/attribution_baseline.py` | done |
| 5 | LumaWarp detector over Step 4 | `pipeline/step05_lumawarp_detector.py`, `python/src/causal_shap_renal/lumawarp_contract.py` | placeholder, provider gated |
| 6 | Causal SHAP comparison with an expert in the loop | `pipeline/step06*`, `apps/causal_shap/structural_value.py` | done (3 of 4 methods; rounds 2-3 scripted) |
| 7 | LumaWarp detector over Step 6 | `pipeline/step07_lumawarp_reweight.py` | placeholder, provider gated |
| 8 | Structural recovery: PC, GES, NOTEARS, LiNGAM | `pipeline/step08*`, `apps/causal_shap/discovery.py`, `apps/causal_shap/evaluation.py` (M1-M5) | library ported, runs pending |
| 9 | Robustness to the data-generating process | `apps/causal_shap/validation/` (Credence-style) | scaffolded, pending |
| 10 | Robustness to spaceflight-epidemiological constraints | `analysis/R/renal_stone_source_aligned_simcausal.R` (NASA-like v4 selection regime) | one regime exists, sweep pending |
| 11 | Generalization to out-of-distribution populations | own section | pending |
| 12 | Longitudinal extension (g-methods) | future work | not undertaken |
| 13 | Cost-constrained recourse ("price and dice") | `apps/causal_shap/policy.py`, `action_costs.py`, `shift_estimation.py` | scaffolded, out of the paper's scope |

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
                   discovery, PSCI v0 complexity seam, structural value function,
                   validation, M1-M5, action selection, figures); the guided hub,
                   the M1-M5 Workbench, the six-rung ladder app; frozen bundles; tests
analysis/         Ported from Target DAGs. R pipeline on the full 51-node DAG and
                   its frozen result record under analysis/output/
references/       NASA SA-07566 DAGitty text; Robert Reynolds's 2026-07-13 files
dag-candidates/   Core-graph node and edge CSVs
data/             raw, interim, simulated (gitignored, regenerated from a seed);
                   frozen_truth (committed)
results/          attributions, discovery, evaluation, figures; detector/ (gitignored)
site/             Quarto single-page site, deployed to GitHub Pages
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
make site                   # quarto render site
```

The apps run locally by design; a hosted instance cannot pin the environment
behind the published results.

## The site

<https://andystats.github.io/causal-shap-target-dags/> is the one-page
version: the premise, the seven steps, why deeper nodes wash out, the
evidence from both testbeds, and what can be claimed. It is authored in this
repository's `site/` and deployed from
[andystats/causal-shap-target-dags](https://github.com/andystats/causal-shap-target-dags),
whose "Publish site from the hub" workflow checks out this repository's
`main`, renders `site/`, and publishes to that account's GitHub Pages (on
push there, every six hours, or on demand with `gh workflow run`). Pages on
this repository is an owner-only setting and is not enabled; this
repository's own workflow only render-checks the site. The old Target DAGs
page is kept as an archived subpage at `/target-dags.html` with its original
styling in `site/archive.css`. The root `index.html` redirects to the site.

## The manuscript

The article is written in LaTeX under `manuscript/` in this repository
(ADR 009: one home for the project). The folder is gitignored for now, so it
builds from the hub but is not published; coauthors receive PDF exports. The introduction is
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
