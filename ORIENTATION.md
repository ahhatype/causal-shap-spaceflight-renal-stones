# Orientation

Start here. Last updated 2026-09-04. The premise: **your roadmap should
follow your goal.** Prediction is the default playbook; intervention casts a
wider net, then prunes. The project
tests that playbook on NASA's renal-stone DAG with an answer key we wrote,
for an *npj Microgravity* article (deadline recorded as 2026-10-31).

## Where everything is

| What | Where | Notes |
| --- | --- | --- |
| Everything | This repository (`ahhatype/causal-shap-spaceflight-renal-stones`) | The single home (ADR 009) |
| The argument in one page | <https://andystats.github.io/causal-shap-target-dags/> | Authored in `site/` here; deployed by the old repo's workflow. Redeploy: `gh workflow run "Publish site from the hub" -R andystats/causal-shap-target-dags` |
| The written guide | `docs/playbook/README.md` | Rungs 0 to 6 with tools and guards; FIG. 1 and FIG. 2 |
| Why the reframing | `docs/framing/prediction-vs-intervention.md` | From the 1 Sept whiteboard (`docs/notes/`) |
| Citations | `docs/references/` | Verified claims map; manuscript-side references |
| The manuscript | `manuscript/` (gitignored, local) | `main.tex`, `references.bib`, `OUTLINE.md`, the archived Word originals. `make manuscript` |
| Working-subgraph results | `docs/step04_results.md`, `docs/step06_results.md` | 14 nodes; the primary case study |
| Full-DAG results | `docs/full_dag/RESEARCH_RECORD.md` | 51 nodes; the ordering null and the propagation result |
| Decisions | `docs/decisions/` | 001 to 009; 007 (consolidation), 008 (LumaWarp gate), 009 (one home) matter most |
| Step status | `config/pipeline_status.yaml`, `docs/STATUS.md` (gitignored) | |
| Coauthor exchange | Box `Causal SHAP Target DAGs - Robert Reynolds Lexi Pasi/` | PDF exports in `from-github-YYYY-MM-DD/`; Word originals archived in `manuscript/`. Not for editing |
| LumaWarp runtime | `C:\Lumawarp\` | Binaries, logs, the private format guide. Never enters git |
| Old repo | `andystats/causal-shap-target-dags` | Frozen; deploy shim only |

## The two lines of work

| | Working subgraph | Full source DAG |
| --- | --- | --- |
| Code | `config/`, `pipeline/`, `r/`, `python/src/causal_shap_renal/` | `analysis/`, `apps/` (the `causal_shap` library and three Shiny apps) |
| Generator | `simcausal` from `config/edge_coefficients.yaml` | `simcausal` from the DAGitty text |
| Headline | Predictive credit along two-hop chains lands by model class, on one chain nearly zero for the parent and on another inverted onto it; PC pruned every edge into the binary outcome at n = 1,000; Ng et al. reaches τ 0.714 once reconnected | Ordering-only τ 0.528 tied with ordinary 0.506; structural propagation τ 0.794 (prototype) |

## How to run

```bash
make setup-py            # py -3.13 venv + editable install of both packages
make test-py             # 151 tests across both packages
make step02 step03 step04 step06   # working-subgraph pipeline (R + Python)
make full-dag-validate   # R validator + frozen-output hash gate
make hub | ladder | workbench      # the Shiny apps, local only
make figures             # depth washout, working-subgraph DAG, FIG. 1 and 2
make manuscript          # latexmk -> manuscript/main.pdf
make site                # quarto render site
```

R side: `make setup-r` (renv) for the working subgraph;
`Rscript analysis/install_dependencies.R` for the full DAG.

## What is done (as of 2026-09-04)

- Steps 1 to 4 and 6 on the working subgraph, with results docs.
- Full-DAG frozen record ported: ordering null, propagation prototype,
  teaching trap, M1 to M5 battery, action selection.
- LumaWarp placeholders: public contract (`lumawarp_contract.py`), Step 5
  and 7 drivers that refuse to score without a provider, `docs/lumawarp/`.
- Proximity-bias metrics (PBI, POA, proximal mass) implemented and tested.
- Depth-washout figure (E3, chain version) computed.
- Site rewritten as the article companion; archived Target DAGs page kept.
- Manuscript drafted in LaTeX with the human-written intro verbatim,
  Methods in the 13-step flow, results tables, and a `.bib`.

## What is private or gated

- `manuscript/` is gitignored until the coauthors agree to publish (it was
  public in one commit, `7913fa7`).
- `docs/methods/` and `docs/STATUS.md` are gitignored.
- LumaWarp block semantics and results wait on Lucidity's six sign-off
  questions (`docs/lumawarp/README.md` section 8). Nothing about them
  enters git.

## Conventions that bite

- Say "NASA-topology simulation", never "NASA effect".
- Never machine-rewrite the human-written introduction. Blue
  `\draftnote{}` blocks in the manuscript are LLM drafts to be rewritten by
  hand; red `\todo{}` blocks are open items.
- Rounds two and three of Step 6 are a scripted heuristic, not expert
  review; every number from them carries that label.
- Goodenow-Messman, not Goodenow.

## Pick up tomorrow

1. `git pull`, `make test-py`. Both should be quiet.
2. Manuscript: read the red and blue markers in `manuscript/main.tex`.
   The first thing to write by hand is the paragraph the draft asked for:
   what causally informed SHAP is and how each method depends on the DAG
   (Methods, Step 6, has the material). Then verify the six `TODO verify`
   entries in `references.bib` (Li 2023, Sanders 2023, Scott 2023, Antonsen
   2023, the Annals of Epidemiology 2025 piece, Hooker and Mentch 2019).
3. Step 6, fourth method: run the Heskes-style structural value function
   (`apps/causal_shap/structural_value.py`) on the working subgraph. It
   needs a `LinearLogisticSCM` built from `config/edge_coefficients.yaml`;
   `apps/causal_shap/nasa_scm.py` is the pattern.
4. Step 8 on the working subgraph: PC, GES, LiNGAM, and MGM PC-Stable
   (`causalMGM` in R, because the outcome is binary), scored with the
   M1 to M5 battery (`apps/causal_shap/evaluation.py`) and by node depth.
5. E1 to E3 as teaching DAGs (`apps/causal_shap/teaching_dags.py`), so the
   detector has a prespecified test when a provider arrives.
6. Ask Lexi for the dichromatic gating rule and which two channels it
   pairs; send Lucidity the six questions; ask Robert about the canonical
   graph version, the three unmatched edges, and actionable nodes.
7. Decide with the coauthors whether `manuscript/` can be public.
