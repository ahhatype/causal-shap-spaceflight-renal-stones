# Contributor orientation

Source locations and current development priorities for the Space SHAP project.

| What you need | Start here |
| --- | --- |
| Argument, workflow and current results | [README](README.md) |
| Reproduction commands and limits | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Path-length math, detection, causal credit and splines | [Technical note](docs/technical/path-length-and-response-shape.md) |
| Classroom lab, worksheet and answer key | [Teaching companion](docs/classroom/README.md) |
| Public technical citations | [BibTeX](docs/references/technical-companion.bib), [reference map](docs/references/manuscript-references.md) |
| 14-node working-subgraph findings | [Step 4](docs/step04_results.md), [scripted Step 6](docs/step06_results.md) |
| 51-node full-DAG findings | [Research record](docs/full_dag/RESEARCH_RECORD.md) |
| Pipeline status | [config/pipeline_status.yaml](config/pipeline_status.yaml) |
| Original protocol and framework | [Playbook](docs/playbook/README.md), [central workflow](docs/playbook/central-workflow.md) |
| Archived presentations and repository history | [Archive guide](site/README.md), [preservation map](docs/decisions/010-repository-companion.md) |
| Private manuscript on the writing machine | manuscript/prism-upload/: main.tex, references.bib, figures/ and main.pdf |
| Private writing export and recording script | manuscript/causal-shap-prism.zip; manuscript/coauthor-review/recording-script.md |

## Current priorities

1. Reconcile manuscript scope and unfinished references with Aimee, preserving
   her human-written introduction. The closing intro still mentions a clinical
   example that is not in the completed synthetic work. The marked framing
   subsection also requires human review. Choose the writing master before
   exchanging dated Prism exports.
2. Review the graph with Robert. Step 6 rounds two and three remain scripted
   heuristics; their results are not evidence of human expert review.
3. Prespecify the next experiments: mixed-data discovery on the working graph,
   propagation with unknown or misspecified mechanisms, repeated-seed uncertainty,
   and nonlinear robustness. Preserve the original diagnostic and null result.
4. Resolve the proprietary detector's publication boundary with its owners.
   The detector and filter have no evaluated public results.

The full DAG and working graph have separate coefficients and purposes.
NASA supplies topology, not effects. The propagation prototype receives
known mechanisms and cannot establish method superiority over methods given
less causal information. Attribution remains a prototype input to action
selection, not an action recommendation.

## Quick local checks

```bash
python docs/classroom/lab.py --check
python analysis/build_teaching_animation.py
python analysis/package_classroom.py
python analysis/depth_washout_figure.py --verify-recorded
```

Use the repository Python environment for the depth experiment and research
apps. See the README for installation and the Makefile for R/Python pipeline
commands.

## Repository map

```
config/           DAG spec, edge coefficients, model engines, pipeline status (YAML)
pipeline/         Numbered driver scripts for the working subgraph, one per step
r/                R package for the working subgraph (renv): DAG utilities,
                   simcausal helpers, ground truth, pcalg and shapr wrappers
python/src/       causal_shap_renal: attribution methods, discovery wrappers,
                   evaluation, the file interchange contract, the LumaWarp contract
python/tests/     pytest suite for causal_shap_renal
apps/             causal_shap library (teaching DAGs,
                   discovery, experimental complexity interface, structural value function,
                   validation, M1-M5, action selection, figures); the guided hub,
                   the M1-M5 Workbench, the six-rung ladder app; frozen bundles; tests
analysis/         R pipeline on the full 51-node DAG and
                   its frozen result record under analysis/output/
references/       NASA SA-07566 DAGitty text; Robert Reynolds's 2026-07-13 files
dag-candidates/   Core-graph node and edge CSVs
data/             raw, interim, simulated (gitignored, regenerated from a seed);
                   frozen_truth (committed)
results/          attributions, discovery, evaluation, figures; detector/ (gitignored)
site/             Archived presentations and assets
manuscript/       Private article: prism-upload/ is the sole source; build.py builds
                   its PDF and ZIP; coauthor-review/ holds the recording script and notes
docs/             framing memo, playbook, notes, references, LumaWarp placeholder,
                   decisions, step results, full-DAG record. Index: docs/README.md
```
