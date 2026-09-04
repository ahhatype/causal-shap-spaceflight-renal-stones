# Provenance and third-party notices

## Code ported from causal-shap-target-dags

The following directories were ported from
[andystats/causal-shap-target-dags](https://github.com/andystats/causal-shap-target-dags)
at its commit `10d582e` (2026-08-30), per ADR 007:

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
governs everything here. The original repository remains available under MIT
at its own URL; this note records the origin for provenance only.

## External source material

- NASA SA-07566 renal-stone DAG (`references/renal-stone-dag-code-SA-07566.txt`)
  is public NASA material and remains subject to its original terms.
- Robert Reynolds's DAGitty files (`references/robert-reynolds-2026-07-13/`)
  were supplied by their author for this project.
- The ACIC 2026 illustrations referenced by the site are hosted at
  tao-rwd.com and are not redistributed here.
