# Orientation

This is the master repository for the Space SHAP manuscript, reproducibility
companion and teaching companion. Pages is retired under [ADR 010](docs/decisions/010-repository-companion.md).
The manuscript remains a private coauthor draft; research and teaching sources
are public here.

| What you need | Start here |
| --- | --- |
| Argument, workflow and current results | [README](README.md) |
| Reproduction commands and limits | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Path-length math, detection, causal credit and splines | [Technical note](docs/technical/path-length-and-response-shape.md) |
| Classroom lab, worksheet, answer key and controlled animation | [Teaching companion](docs/classroom/README.md) |
| Public technical citations | [BibTeX](docs/references/technical-companion.bib), [reference map](docs/references/manuscript-references.md) |
| 14-node working-subgraph findings | [Step 4](docs/step04_results.md), [scripted Step 6](docs/step06_results.md) |
| 51-node full-DAG findings | [Research record](docs/full_dag/RESEARCH_RECORD.md) |
| Pipeline status | [config/pipeline_status.yaml](config/pipeline_status.yaml) |
| Original protocol and framework | [Playbook](docs/playbook/README.md), [central workflow](docs/playbook/central-workflow.md) |
| Preserved Pages sources and history | [Archive guide](site/README.md), [preservation map](docs/decisions/010-repository-companion.md) |
| Private manuscript on the writing machine | manuscript/main.tex, introduction-aimee.tex, references.bib, technical-companion.tex and main.pdf |
| Private portable writing package | manuscript/prism-upload/ and manuscript/causal-shap-prism.zip |

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
commands. No Pages publishing is needed. The [previous machine handoff](docs/NEXT_SESSION.md)
is retained as history; its deployment instructions are superseded.
