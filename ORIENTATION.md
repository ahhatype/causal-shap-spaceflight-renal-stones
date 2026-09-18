# Contributor orientation

Source locations and current development priorities for the Space SHAP project.

| What you need | Start here |
| --- | --- |
| Argument, workflow and current results | [README](README.md) |
| Reproduction commands and limits | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Path-length math, detection, causal credit and splines | [Technical note](docs/technical/path-length-and-response-shape.md) |
| Existing classroom materials (development paused) | [Teaching companion](docs/classroom/README.md) |
| Public technical citations | [BibTeX](docs/references/technical-companion.bib), [reference map](docs/references/manuscript-references.md) |
| Supplied graph and working-model adaptations | [Graph provenance and edge crosswalk](docs/technical/graph-provenance.md) |
| 14-node working-subgraph findings | [Step 4](docs/step04_results.md), [scripted Step 6](docs/step06_results.md) |
| 51-node full-DAG findings | [Research record](docs/full_dag/RESEARCH_RECORD.md) |
| Pipeline status | [config/pipeline_status.yaml](config/pipeline_status.yaml) |
| Method playbook and manuscript crosswalk | [Playbook](docs/playbook/README.md), [central workflow](docs/playbook/central-workflow.md) |
| Archived presentations and repository history | [Archive guide](site/README.md), [preservation map](docs/decisions/010-repository-companion.md) |
| Private manuscript on the writing machine | manuscript/prism-upload/: main.tex, references.bib, figures/ and main.pdf |
| Private writing export and correspondence | manuscript/causal-shap-prism.zip; manuscript/coauthor-review/correspondence.md |

## Restart point — 18 September 2026

The [Supplementary Information](docs/playbook/supplementary-information/main.pdf)
follows the manuscript's methods: goal; data and predictive reference; optional
PC discovery; graph review; causal game and surgery; causal attribution;
validation under data constraints. Refine its [LaTeX source](docs/playbook/supplementary-information/main.tex)
and [native diagrams](docs/playbook/supplementary-information/diagrams/README.md) directly.
The [method appendix](docs/playbook/method-choices.md) expands alternatives within
stages. The [selection example](docs/technical/selection-mechanism.md) is an exact
illustration, separate from both renal simulations.

The manuscript and supplement share Step 0–6 numbering; original work-package
IDs remain only in the implementation crosswalk. Before syncing, compare the
latest Overleaf source with the private sync manifest and local source. The
human-written introduction remains protected. Current sync status, reviewer
findings and editorial flags are in docs/STATUS.md and manuscript/coauthor-review/.

## Current priorities

1. Audit IDA edge-direction/weight consistency and the reported tau/interval
   discrepancy; reconcile abstract claims with completed evidence. Preserve frozen
   results until any corrective run is documented.
2. Review the 14-node model adaptations against Robert's complete 53-node source
   graph using the edge crosswalk. The existing full-DAG results use the earlier
   51-node version. Step 6 rounds two and three remain scripted
   heuristics; their results are not evidence of human expert review.
3. Prespecify a bounded comparison across clean and degraded data: mixed-data
   discovery, matched attribution targets and causal information, repeated fits,
   then sample size, selection and measurement changes. The full method-setting
   grid is outside scope; preserve existing diagnostic and null results.
4. Resolve the proprietary detector's publication boundary with its owners.
   The detector and filter have no evaluated public results. Educator-companion
   development is paused; do not deploy Pages.

The full DAG and working graph have separate coefficients and purposes.
NASA supplies topology, not effects. The propagation prototype receives
known mechanisms and cannot establish method superiority over methods given
less causal information. Attribution remains a prototype input to action
selection, not an action recommendation.

## Quick local checks

```bash
python analysis/selection_mechanism_demo.py --check
python analysis/build_spine_guide.py
```

The guide build requires pdfLaTeX and BibTeX; it preserves editable text and
schematics. Research-pipeline commands and environments are documented in
REPRODUCIBILITY.md. No broad renal experiment is required for a prose edit.

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
                   its PDF and ZIP; coauthor-review/ holds correspondence and open review notes
docs/             framing memo, playbook, notes, references, LumaWarp placeholder,
                   decisions, step results, full-DAG record. Index: docs/README.md
```
