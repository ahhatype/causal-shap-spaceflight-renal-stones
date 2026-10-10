# Provenance

## DAG source and handoff
Base DAG: NASA's public SA-07566 "Risk of Renal Stone Formation" DAG, supplied to Andy Wilson and Lexi Pasi by Robert Reynolds (DAGitty source, 2026-07-13 handoff). 53 nodes/83 edges per Robert's version, 51 nodes/75 edges in the prior source-aligned reference. Cohen's kappa 0.978 after semantic node mapping, precision 1.000, recall 0.958, structural Hamming distance 3, with a small number of unmatched edges retained for expert adjudication.

Public sources:
- [DAG narrative (PDF)](https://www.nasa.gov/wp-content/uploads/2025/09/renal-stone-risk-dag-narrative.pdf)
- [DAG code, DAGitty (TXT)](https://www.nasa.gov/wp-content/uploads/2025/09/renal-stone-dag-code-sa-07566.txt)
- [NASA risk page](https://www.nasa.gov/directorates/esdmd/hhp/risk-of-renal-stone-formation/)
- [2017 HRP evidence report](https://humanresearchroadmap.nasa.gov/evidence/reports/Renal.pdf)

## Coefficient sourcing and open decisions
The full node table, edge list, and per-edge citations live in [`config/dag_spec.yaml`](../config/dag_spec.yaml). Structural-equation coefficients live in [`config/edge_coefficients.yaml`](../config/edge_coefficients.yaml). Both files carry estimates for educational/methods purposes only; treat every numeric value in them as a simulation design parameter, not a NASA effect estimate.

## Code provenance and third-party notices

### Code ported from causal-shap-target-dags

The following directories were ported from
[andystats/causal-shap-target-dags](https://github.com/andystats/causal-shap-target-dags)
at its commit `10d582e` (2026-08-30), per [ADR 007](decisions/007-target-dags-consolidation.md):

- `apps/` (the `causal_shap` library, the `hub`, `workbench`, and ladder apps,
  bundles, assets, tests)
- `analysis/` (R pipeline and frozen outputs)
- `references/`, `dag-candidates/`
- `docs/full_dag/`
- `site/theme.scss`, `site/favicon.svg`, `site/data/glossary.yml`
- `.github/workflows/publish-site.yml`

That code was originally released under the MIT License, copyright 2026 Andy
Wilson. On consolidation (2026-09-03) its author relicensed it under
GPL-3.0-or-later, so a single license, `LICENSE` at the repository root,
governs everything here. The original repository was archived on 2026-10-10
([ADR 011](decisions/011-archive-target-dags-and-experiments.md)) and remains
readable under MIT at its own URL; this note records the origin for provenance.

### External source material

- NASA SA-07566 renal-stone DAG (`references/renal-stone-dag-code-SA-07566.txt`)
  is public NASA material and remains subject to its original terms.
- Robert Reynolds's DAGitty files (`references/robert-reynolds-2026-07-13/`)
  were supplied by their author for this project.
- The ACIC 2026 illustrations referenced by the archived site are hosted at
  tao-rwd.com and are not redistributed here.
- The ConfoundingSHAP paper (Brockschmidt et al., 2026, arXiv:2605.10533) read
  by `experiments/confoundingshap-tutorial/` is not redistributed; the tutorial
  cites the arXiv record.
