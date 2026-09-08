# ADR 010: Repository companion and retirement of Pages

Accepted, 2026-09-07, at Andy's request. Supersedes the hosting portions of
ADRs 007 and 009 and the earlier public-site convention.

The master is `ahhatype/causal-shap-spaceflight-renal-stones`. Priorities are
the manuscript, the GitHub reproducibility companion and the teaching
companion. No Pages deployment or migration to Aimee's Pages account is
planned. The old host's automatic deployment is disabled; its published
Pages site was unpublished after preservation and the hub update.
The old repository and its history remain available as provenance.

## Preservation map

| Material | Canonical or retained location |
| --- | --- |
| Reader-facing argument and seven-stage workflow | Root README and `docs/playbook/central-workflow.md` |
| Worked calculation and educator lesson | `docs/classroom/` |
| Path-length derivation, detection rule, response shape and splines | `docs/technical/path-length-and-response-shape.md` |
| Depth experiment and frozen curves | `analysis/depth_washout_figure.py`, `results/figures/depth_washout.csv` |
| Simplified detection graphic | `docs/images/depth-detection.svg` |
| Original GIF, revised controlled sequence | `docs/images/two-goals.gif`; offline `docs/classroom/animation.html` generated from the preserved SVG |
| Public technical BibTeX | `docs/references/technical-companion.bib` |
| Renal code, records, references and apps | Existing ADR 007 mapping into `analysis/`, `apps/`, `references/`, `docs/full_dag/` |
| Both generations of Pages presentation and their assets | `site/`, retained as an archive; root `index.html` redirects to GitHub |
| Private manuscript and portable coauthor package | Ignored `manuscript/`; never added to public Git |

Inventory of the old repository at `0b24137251bfdeb5dd33e2fc526d0b244a62d8ff`
(the verified remote main on this date): 227 tracked paths. Under the ADR 007
research-directory mapping, 177 files were byte-identical, 37 had existing
hub versions, and two auxiliary paths had been superseded: `app/.python-version`
by the root Python 3.13 setup/CI, and `docs/README.md` by `docs/README.md`
in this hub. No research implementation was missing from that mapping.
Existing hub revisions were preserved rather than overwritten with older
copies. The original index presentation is retained in `site/target-dags.qmd`;
the latest presentation is `site/index.qmd`. No source or old repository
history is deleted to retire hosting.

Retirement verified after hub commit `2cedcc2`: GitHub reports the old
workflow as `disabled_manually` and the old Pages resource as absent
(HTTP 404). The old repository's README now points readers here, in commit
`0d7778e`. Hub CI passed. Local validation passed 151 tests with one skip,
all 90 frozen depth rows reproduced, and the seven-file offline kit passed
its analytic and archive-integrity checks. No frozen renal results changed.

The classroom package builds independently of Quarto. The archived site can
still render manually for provenance, but does not publish. A future change
to hosting requires a new decision. Human introduction text, private result
boundaries and scientific status labels remain protected.
