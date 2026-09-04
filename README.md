# Causal SHAP: Spaceflight-Induced Renal Stones

[![Python tests](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/actions/workflows/python-tests.yml)
[![Site](https://img.shields.io/badge/GitHub%20Pages-open%20site-2563eb)](https://andystats.github.io/causal-shap-target-dags/)

**Prediction is the default playbook. Intervention casts a wider net, then prunes.**

This is the hub for the Space SHAP paper. It consolidates
[andystats/causal-shap-target-dags](https://github.com/andystats/causal-shap-target-dags)
(the full 51-node source DAG, the teaching DAGs, the structural value
function, the Shiny apps) with the 14-node working-subgraph pipeline built
here. Lineage: the [ACIC 2026 Causal SHAP project](https://www.tao-rwd.com/acic-2026/causal-shap)
established the attribution problem; [Target DAGs](https://andystats.github.io/causal-shap-target-dags/)
asked which upstream node to change; this hub asks how to find the deeper
nodes the prediction playbook washes out, and how to prune them honestly.
See [ADR 007](docs/decisions/007-target-dags-consolidation.md) for what moved
where.

## What this is

NASA's Human System Risk Board maintains expert-built directed acyclic
graphs (DAGs) for its known spaceflight risks. SHAP (SHapley Additive
exPlanations) is the standard way to explain a predictive model, and out of
the box it has no notion of causal structure. On a causal graph a mediator
can screen off its ancestors for prediction while still transmitting their
intervention effects, so predictive credit pools near the outcome and the
upstream nodes an intervention would have to touch drop out of the ranking.

The paper's reframing ([framing memo](docs/framing/prediction-vs-intervention.md))
follows Harrell's *Regression Modeling Strategies* in treating prediction
and intervention as different goals with different recipes. The prediction
recipe is the default in explainable AI and is fine for prediction. The
intervention recipe has to cast a wider net, re-admitting candidates the
predictor discarded, and then prune with structure. Deeper nodes make that
hard: their total effects shrink with every hop (product of path
coefficients), measurement noise attenuates them further, and
constraint-based discovery recovers them worse. The methods under test are
the instruments for that job: a detector for depth (LumaWarp), a two-channel
filter for noise (dichromatic sensitivity gating, proposed by Lexi Pasi), and
structural propagation for pruning, all working under the assumption that
direct relationships tend to be linear.

Everything is synthetic, generated from NASA's SA-07566 renal-stone
topology with coefficients we chose, so the true total effect of every node
is known by construction and every method is scored against it. Say
"NASA-topology simulation", never "NASA effect".

## Two lines of work

| | Working subgraph | Full source DAG |
| --- | --- | --- |
| Nodes | 14, scoped from the source graph | 51 nodes, 75 edges, source-exact |
| Where | `config/`, `pipeline/`, `r/`, `python/src/causal_shap_renal/`, `results/`, `docs/step0N_results.md` | `analysis/`, `apps/`, `docs/full_dag/` |
| Generator | `simcausal` from `config/edge_coefficients.yaml` | `simcausal` from the DAGitty text |
| Frozen truth | do(hi) vs do(lo), common random numbers, n = 50,000 | Same recipe, 28 ancestors |
| Headline so far | Four of five predictive pairings invert a two-hop mediation chain; PC pruned every edge into the outcome at n = 1,000; Ng et al.'s method reaches τ 0.714 once the outcome is reconnected | Ordering-only SHAP tied with ordinary SHAP (τ 0.528 vs 0.506); structural propagation τ 0.794, top-five recovery 1.00 (32×32×32 prototype) |
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
docs/             framing memo, notes, references, LumaWarp placeholder, decisions,
                   step results, full-DAG record. Index: docs/README.md
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

<https://andystats.github.io/causal-shap-target-dags/> is the
single-page argument: two playbooks, why deeper nodes wash out, the six-rung
intervention playbook with its two placeholder rungs, the evidence from both
testbeds, the detector and filter placeholders, and what the hub can claim.
The page is authored in this repository's `site/` and deployed from
[andystats/causal-shap-target-dags](https://github.com/andystats/causal-shap-target-dags),
whose "Publish site from the hub" workflow checks out this repository's
`main`, renders `site/`, and publishes to that account's GitHub Pages (on
push there, every six hours, or on demand with `gh workflow run`). Pages on
this repository is an owner-only setting and is not enabled; this
repository's own workflow only render-checks the site. The old Target DAGs
page is kept as an archived subpage at `/target-dags.html`. The root
`index.html` redirects to the site.

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
