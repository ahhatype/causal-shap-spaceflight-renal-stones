# Causal SHAP in the classroom

Starter kit, September 7, 2026. A 50-minute lesson or 90-minute lab for learners who know regression, conditional expectation, and basic DAGs. No astronaut data, credentials, proprietary runtime, or installed SHAP library is needed.

**Start:** open `index.html` in a browser. It runs offline. Then run `python lab.py` (Python 3.10 or newer, standard library only). `python lab.py --check` verifies the analytic examples. Print `worksheet.md`; keep `educator-guide.md` as the answer key.

Learning outcomes: distinguish a prediction explanation from an intervention contrast; state which coalition game a Shapley calculation uses; explain screening-off; supply a counterexample to “direct causes are linear”; and distinguish an observed benchmark from a proposed detector.

The lab uses an exactly specified two-feature model, not the paper's renal simulation. Its values must never be reported as new renal results. The symmetric two-player causal game is also not a numerical reproduction of the repository's DAG-asymmetric structural prototype.

## Source map for an optional research extension

Repository: https://github.com/ahhatype/causal-shap-spaceflight-renal-stones

This directory is the canonical classroom source. The companion runs locally without Pages. Use GitHub Code → Download ZIP,
extract the repository, and open docs/classroom/index.html. Open
[animation.html](animation.html) for the preserved four-node comparison.
Run `python analysis/package_classroom.py` from the repository root to
create a standalone kit in dist/ (including the license). See [the central workflow](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/playbook/central-workflow.md) for the relationship between this two-player lab, the four-node animation, the five-node stress test and the renal simulations. Research links require an internet connection; the included lesson runs offline.

| What to explore | Repository source |
| --- | --- |
| Existing toy worlds | `apps/causal_shap/teaching_dags.py` |
| Structural coalition value | `apps/causal_shap/structural_value.py` |
| Baseline output scales | `python/src/causal_shap_renal/attribution_baseline.py` |
| Working graph / coefficients | `config/dag_spec.yaml`, `config/edge_coefficients.yaml` |
| Four-figure and depth lesson sources | `analysis/depth_washout_figure.py`, `docs/images/` |
| Fixed-model uncertainty example | `analysis/08_bootstrap_shap_comparison.R` and `analysis/output/shap_nephrolithiasis_clean_v3/paired_bootstrap_summary.csv` |
| Research findings | `docs/step04_results.md`, `docs/step06_results.md`, `docs/full_dag/RESEARCH_RECORD.md` |

Those research scripts have additional Python/R dependencies documented by the repository. The included lab is deliberately independent. Read the repository license before redistributing its code; this kit does not bundle the research code or private LumaWarp materials.

## Technical extension

The [technical note](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/technical/path-length-and-response-shape.md) supplies
path-length math, detection assumptions, nonlinear counterexamples and
[BibTeX references](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/references/technical-companion.bib).

## What the next kit version needs

Coauthor-reviewed slides, a pinned environment/notebook for reproducing selected renal outputs, learner feedback, and accessible downloadable figures. The current kit is a usable lesson prototype, not a completed course or verified replication package.
