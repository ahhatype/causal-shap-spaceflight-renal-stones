# Pipeline status

Tracks the same 13 steps as the methods doc (docs/methods), step by step.
Update this file as work lands. `config/pipeline_status.yaml` is the
machine-readable mirror of this table. Updated 2026-09-03 with the
causal-shap-target-dags consolidation (ADR 007) and the LumaWarp
placeholders (ADR 008).

| Step | Label | Status | Notes |
|---|---|---|---|
| 1 | Exposure/outcome specification | done | Cumulative mission days as exposure; nephrolithiasis (binary incidence) as the sole outcome. See `config/dag_spec.yaml`. |
| 2 | DAG construction and expert-guided augmentation | done | 14-node working subgraph in `config/dag_spec.yaml`. Full 51-node source DAG, the Reynolds ingest, and the concordance record now live under `analysis/` and `references/`. |
| 3 | Synthetic data generation | done | Working subgraph from `config/edge_coefficients.yaml`; full DAG from the DAGitty text via `analysis/generate.R`. Coefficients still pending Robert's calibration sign-off. |
| 4 | Baseline attribution with standard SHAP | done | 5 explainer x model pairings vs. interventional ground truth. See `docs/step04_results.md`. |
| 5 | LumaWarp detector over Step 4 | placeholder | Public contract (`python/src/causal_shap_renal/lumawarp_contract.py`) and driver (`pipeline/step05_lumawarp_detector.py`) in the repo; the provider stays outside until Lucidity signs off. See `docs/lumawarp/README.md`. |
| 6 | Causal SHAP comparison + human-in-the-loop | done | 3 methods run (ASV, Ng et al. Causal SHAP, Shapley Flow) across 3 scripted-revision rounds. Rounds 2-3 are a scripted heuristic, not real expert review. Next: run the ported Heskes-style structural value function (`apps/causal_shap/structural_value.py`) as the fourth method. See `docs/step06_results.md`. |
| 7 | LumaWarp detector over Step 6 | placeholder | Same contract and gate as Step 5; driver `pipeline/step07_lumawarp_reweight.py`. |
| 8 | Structural recovery comparison | pending | PC (reused from Step 6), GES, NOTEARS, LiNGAM. Discovery wrappers and the M1-M5 battery are ported (`apps/causal_shap/discovery.py`, `evaluation.py`, `analysis/run_m1_m5_battery.py`); not yet run on the working subgraph. Add recovery-by-depth and run MGM PC-Stable (causalMGM) alongside plain PC, since the outcome is binary and the Gaussian test pruned every edge into it. |
| 9 | Robustness to the data-generating process | pending, extension | Credence-style validation scaffolding ported (`apps/causal_shap/validation/`). Add a nonlinear-edge generator to price the linearity assumption. |
| 10 | Robustness to spaceflight-epidemiological constraints | pending, extension | One selection regime exists on the full DAG (NASA-like v4). Add mediator measurement noise for E3. |
| 11 | Generalization to out-of-distribution populations | pending, own section | Distinct generalization question, not a robustness pass. |
| 12 | Longitudinal extension | future work | Treatment-confounder feedback (g-methods); no concrete example in the working graph. |
| 13 | Counterfactual recourse extension (DiCE / price and dice) | out of scope | Budget-constrained action selection scaffolded in `apps/causal_shap/policy.py`; for Andy/Lexi to define. |

## Framing and placeholders (2026-09-03)

- Reframing memo: `docs/framing/prediction-vs-intervention.md`. Whiteboard
  transcription: `docs/notes/2026-09-01-whiteboard-transcription.md`.
- Verified citations for the reframing's claims, with gaps:
  `docs/references/claims-to-citations.md`.
- LumaWarp expanded treatment and dichromatic sensitivity filter:
  `docs/lumawarp/README.md` (placeholder outline; results gated).
- Experiments E1 to E3 (two- and three-layer trees, noise on deep layers)
  are specified, not run.

## Log

- 2026-09-03: target-dags ported into this hub (ADR 007); LumaWarp placeholders
  (ADR 008); framing memo, transcription, citations; site rewritten; deployed
  via andystats Pages; Goodenow-Messman corrected; MGM and LAU readings resolved.
- 2026-09-04: E3 corrected (Giffen good was a doodle); depth-washout figure;
  Harrell de-emphasized; site framed as the npj Microgravity companion;
  playbook written; PBI/POA implemented; Box notes ported; manuscript drafted in
  LaTeX with .bib (kept private); Word originals recovered from C:\Lumawarp,
  archived in Box and here, and the source folder deleted; ORIENTATION.md added.
