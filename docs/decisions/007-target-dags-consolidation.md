# ADR 007: Consolidate causal-shap-target-dags into this repository

## Status
Accepted, 2026-09-03. Supersedes the README's earlier "parallel project, does
not vendor that code" stance.

## Decision
This repository is the single hub for the Space SHAP paper. The public,
git-tracked contents of
[andystats/causal-shap-target-dags](https://github.com/andystats/causal-shap-target-dags)
were ported here at that repository's commit `10d582e` (2026-08-30). The
original repository stays online as provenance and as the home of its
published GitHub Pages site, but new work lands here.

## What moved where

| Source (target-dags) | Here | Role |
| --- | --- | --- |
| `app/causal_shap/` | `apps/causal_shap/` | Tested library: teaching DAGs, discovery (PC/GES with CPDAG extension), PSCI v0 complexity seam, the intervention-propagating structural value function, Credence-style validation, M1-M5 graph evaluation, cost-constrained action selection, figures |
| `app/hub/`, `app/workbench/`, `app/app.py`, `app/stages/`, `app/bundles/`, `app/assets/` | `apps/...` | The three Shiny apps (guided hub, M1-M5 Workbench, six-rung ladder) and their frozen bundles |
| `app/tests/` | `apps/tests/` | Library and app tests (unittest style; collected by pytest) |
| `analysis/` | `analysis/` | The R pipeline on the full 51-node source DAG and its frozen result record (`analysis/output/`) |
| `references/` | `references/` | NASA SA-07566 DAGitty text and Robert Reynolds's 2026-07-13 renal and SANS files |
| `dag-candidates/` | `dag-candidates/` | The two public core-graph CSVs |
| `docs/RESEARCH_RECORD.md`, `PROVENANCE_AND_REFERENCES.md`, `REPRODUCIBILITY_AND_SITE.md` | `docs/full_dag/` | The scientific record for the full-DAG line of work |
| `site/` | `site/` | Quarto single-page site; content rewritten for this hub, theme kept |
| `.github/workflows/publish-site.yml` | same | GitHub Pages deploy |
| `pyproject.toml` | root `pyproject.toml` | Merged with `python/pyproject.toml` (see below) |

Only files tracked by git in the source repository were copied. That
boundary excludes, by construction, the private LumaWarp bridge and its
tests, the reverse-engineered LumaWarp format guide, the working paper and
study guide, the HAPrI and LumaWarp result bundles, the clinical-row
Workbench sample, and the private planning files. Their gitignore entries
were carried over so they stay excluded here too (ADR 008).

## Two lines of work, one repository

The port does not replace the pipeline that already existed here. The
repository now carries two deliberately different scales of the same
problem:

- **Working subgraph** (14 nodes, config-driven): `config/`, `pipeline/`,
  `r/`, `python/src/causal_shap_renal/`, results under `results/` and
  `docs/step0N_results.md`. This is the paper's primary case study.
- **Full source DAG** (51 nodes, source-exact): `analysis/`, `apps/`,
  `docs/full_dag/`. This is where the ordering-only null (tau 0.528 vs
  0.506) and the structural prototype (tau 0.794) were produced, and where the
  teaching DAGs and the recommendation-candidate machinery live.

The two share the DAG source, the interventional-truth recipe (common random
numbers, do(hi) vs do(lo)), the evaluation vocabulary, and, after this ADR,
one Python distribution. They do not share simulators: the working subgraph
is generated from `config/edge_coefficients.yaml` through `r/R/simcausal_helpers.R`;
the full DAG is generated from the DAGitty text through
`analysis/R/renal_stone_source_aligned_simcausal.R`. That duplication is
intentional. The two graphs are different objects and the paper compares
them.

## One Python distribution

The source repository used setuptools with Python 3.13; this repository used
a uv-managed `python/pyproject.toml` pinned to Python <3.13, which no local
machine had installed. The two were merged into one root `pyproject.toml`:

- setuptools, `requires-python = ">=3.11,<3.14"`;
- package roots `apps/` (`causal_shap`, `hub`, `workbench`, `stages`) and
  `python/src/` (`causal_shap_renal`);
- one dependency list, the stricter pin wherever the two overlapped
  (`causal-learn==0.1.4.8`, `shap<0.53`, `numba<0.63`);
- pytest collects both `python/tests` and `apps/tests`.

`python/uv.lock` and `python/.python-version` were removed. ADR 001's
two-language rule is unchanged; only the Python package manager changed
(pip and a plain venv instead of uv).

## Deliberate redundancies and their resolution

| Overlap | Resolution |
| --- | --- |
| `causal_shap_renal.evaluation` (rank metrics) vs `causal_shap.evaluation` (M1-M5 graph metrics) | Different questions, kept both. PBI and POA, which the working-subgraph module flagged as unimplemented, are computed in `analysis/R/shap_distance_metrics.R` and `apps/causal_shap/build/stages.py`; wiring them into `causal_shap_renal.evaluation` is a follow-up |
| `causal_shap_renal.attribution_structural` (Ng et al. Algorithm 1) vs `causal_shap.structural_value` (Heskes-style do-value function) | Different methods. The second is the natural replacement for the shapr Heskes path that ADR 006 found blocked; running it on the working subgraph is the first follow-up |
| `docs/provenance.md` vs `docs/full_dag/PROVENANCE_AND_REFERENCES.md` | Kept both: the short one records this repository's coefficient sourcing; the long one carries the Reynolds handoff, ACIC lineage, and annotated references |
| Two license texts (GPL-3.0 here, MIT there) | Relicensed outright: the author (Andy Wilson) placed the ported code under GPL-3.0-or-later on 2026-09-03, so one license governs the repository. `THIRD_PARTY_NOTICES.md` records the MIT origin for provenance |
| `AGENTS.md`, `CONTRIBUTING.md`, `CITATION.cff` | Adapted to this repository |

## Consequences
- The README describes both lines of work and points each step of the
  13-step protocol at the code that implements it, regardless of origin.
- `docs/STATUS.md` and `config/pipeline_status.yaml` gain entries for what
  the port made available (Step 8 discovery library, Step 9 validation
  scaffolding, Step 13 action-selection machinery).
- The GitHub Pages site for this hub lives at
  `https://ahhatype.github.io/causal-shap-spaceflight-renal-stones/` once
  Pages is enabled on the repository (Settings > Pages > Source: GitHub
  Actions).
- The original repository should get a pointer commit saying that
  development moved here. That commit is the owner's to make.
