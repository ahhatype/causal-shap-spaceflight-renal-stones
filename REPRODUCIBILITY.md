# Reproducing the examples and research record

## Choose a level

| Task | Start here | Requirements |
| --- | --- | --- |
| Work the exact causal-credit example | [Worksheet](docs/classroom/worksheet.md), [answer key](docs/classroom/educator-guide.md), [lab](docs/classroom/README.md) | Browser or Python standard library |
| Understand path length and the equations | [Technical note](docs/technical/path-length-and-response-shape.md) and [BibTeX](docs/references/technical-companion.bib) | GitHub math rendering |
| Verify the recorded depth experiment | `python analysis/depth_washout_figure.py --verify-recorded` | Repository Python environment |
| Inspect working-subgraph results | [Step 4](docs/step04_results.md), [scripted Step 6](docs/step06_results.md) | No installation to read |
| Inspect full-DAG results | [Research record](docs/full_dag/RESEARCH_RECORD.md) | No installation to read |
| Validate frozen bundles | `python -m causal_shap.build validate` from `apps/` | Repository Python environment |
| Rerun the renal pipelines | [Build guide](docs/full_dag/REPRODUCIBILITY_AND_SITE.md), [Makefile](Makefile) | Python 3.11–3.13, R/renv and recorded dependencies |

```bash
python docs/classroom/lab.py --check
python analysis/package_classroom.py
```

The second command creates `dist/causal-shap-classroom.zip`. Extract it and
open `index.html` for the interactive lesson.

For research, create the Python environment using the [quickstart](README.md#quickstart).
R dependencies are managed by `renv` for the working subgraph and by
`analysis/install_dependencies.R` for the full DAG. Common commands:

```bash
make step02 step03 step04 step06  # working-subgraph pipeline
make full-dag-validate           # R validation and frozen-output hash check
make depth-check                # verify recorded teaching curves without rewriting them
make hub                        # discovery hub, localhost:8002
make workbench                  # M1–M5 Workbench, localhost:8001
make ladder                     # six-rung teaching app, localhost:8000
```

The [build guide](docs/full_dag/REPRODUCIBILITY_AND_SITE.md) gives full-DAG
reproduction commands. A pipeline rerun may regenerate outputs; the
validation and depth-check commands check existing records.

## Reproducibility limits that matter

- The 14-node working graph is scoped and augmented, with separate
  coefficients from the 51-node source graph. NASA supplies topology.
- Working-subgraph data use n=1,000, seed 20260812. Full-DAG clean-v3 uses
  n=10,000, generation seed 20260710. Keep their scores separate.
- The matched full-DAG ordering comparison uses the same predictor and
  64/128/128 evaluation/background/permutation counts. The propagation
  prototype uses 32/32/32 and additional known simulation mechanisms. It is
  not a controlled demonstration of method superiority.
- Step 6 rounds two and three are a scripted heuristic, not human review.
  Shapley Flow has documented residual Monte Carlo drift. The original
  failures, undefined score and null comparison remain in the records.
- Detector/filter results, broader discovery comparisons, nonlinear
  robustness and action evaluation remain incomplete. See the
  [workflow evidence map](docs/playbook/central-workflow.md).
