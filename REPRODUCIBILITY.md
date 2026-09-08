# Reproducing the examples and research record

This repository is the master companion. GitHub Pages is retired under
[ADR 010](docs/decisions/010-repository-companion.md); no hosted page is
needed for these instructions. The manuscript remains a private coauthor
draft under `manuscript/`.

## Choose a level

| Task | Start here | Requirements |
| --- | --- | --- |
| Work the exact causal-credit example | [Worksheet](docs/classroom/worksheet.md), [answer key](docs/classroom/educator-guide.md), [lab](docs/classroom/README.md) | Browser or Python standard library |
| Understand path length and the equations | [Technical note](docs/technical/path-length-and-response-shape.md) and [BibTeX](docs/references/technical-companion.bib) | GitHub math rendering |
| Verify the recorded depth experiment | `python analysis/depth_washout_figure.py --verify-recorded` | Repository Python environment |
| Inspect working-subgraph results | [Step 4](docs/step04_results.md), [scripted Step 6](docs/step06_results.md) | No installation to read |
| Inspect full-DAG results | [Research record](docs/full_dag/RESEARCH_RECORD.md) | No installation to read |
| Validate frozen bundles | `python -m causal_shap.build validate` from `apps/` | Repository Python environment |
| Rerun the renal pipelines | [Existing build guide](docs/full_dag/REPRODUCIBILITY_AND_SITE.md), [Makefile](Makefile) | Python 3.11–3.13, R/renv and recorded dependencies |

```bash
python docs/classroom/lab.py --check
python analysis/package_classroom.py
```

The second command creates `dist/causal-shap-classroom.zip`, including the
offline lab and four-node animation. Alternatively download this repository
with GitHub's **Code → Download ZIP**, extract it, and open
`docs/classroom/index.html` or `animation.html`. GitHub displays HTML source;
it does not execute these files in the repository view. No Pages hosting is
required. The package includes the repository license.

For research, create the Python environment using the root README. Frozen
simulations are separate from the exact classroom examples. The depth
verification does not overwrite its CSV; a full renal rerun can regenerate
outputs and should be done with an explicitly chosen experiment plan.

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

## Manuscript handoff

The ignored local `manuscript/main.tex` includes Aimee's introduction from
`introduction-aimee.tex`; the bibliography is `references.bib`. Figure sources
and public technical notes are in this repository. A private
`manuscript/prism-upload/` snapshot packages these with relative figure paths
and a compiled PDF. Agree a writing master before exchanging dated exports;
the repository, Prism import and Google Doc are not automatically synchronized.
