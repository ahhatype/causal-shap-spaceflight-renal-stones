> Historical document: hosting and presentation instructions are superseded by [ADR 010](../docs/decisions/010-repository-companion.md). Use the [current reproducibility guide](../REPRODUCIBILITY.md) and [technical note](../docs/technical/path-length-and-response-shape.md). Do not deploy Pages. Earlier scientific framing is qualified by the current technical note.

# Next session: experiments and teaching companion

Handoff from the Mac presentation session, 2026-09-05.

## What is published

The minimalist tutorial redesign and accessible optional animations were
committed and pushed in `d7b3292`. The live page is
<https://andystats.github.io/causal-shap-target-dags/>. The `?v=d7b3292`
query is a cache-busting label, not an immutable deployment URL.

This session changed presentation, not the experimental results. The new
depth figure uses the recorded `results/figures/depth_washout.csv`; rendering
the site does not run experiments. Responsive, no-JavaScript, reduced-motion,
and animation checks passed on the Mac; the commit's Python and site CI passed.
See [redesign notes](reviews/tutorial-redesign-notes.md) and the
[page review](reviews/tutorial-page-review-2026-09-05.md).

## First on the experiment-capable machine

1. Pull this hub's `main`; read [ORIENTATION.md](../ORIENTATION.md),
   [pipeline status](../config/pipeline_status.yaml), and the
   [full-DAG research record](full_dag/RESEARCH_RECORD.md). Reconcile any
   newer local experiment records before deciding what to rerun.
2. Use Python 3.13 (the CI version; supported range is 3.11–3.13), R and
   Quarto. From the repository root, a Windows setup is:

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -e ".[discovery,workbench,dev]"
   python -m pytest -q
   Set-Location apps
   python -m causal_shap.build validate
   python -m shiny run --port 8010 app.py
   ```

   Open <http://127.0.0.1:8010> for the teaching companion. Stop the server
   and return to the repository root before other root-level commands.
   The separate Workbench is under `apps/workbench/`; the hub is under
   `apps/hub/`. Follow the existing Makefile and
   [reproducibility guide](full_dag/REPRODUCIBILITY_AND_SITE.md) for R stages.
3. Confirm the private LumaWarp runtime and provider are available locally.
   Machine access alone does not remove the vendor publication gate in
   [ADR 008](decisions/008-lumawarp-detector-placeholders.md). Steps 5 and 7
   remain placeholders until the required provider and review are in place.

## Experiment priorities to settle before running

- Prespecify the E1–E3 teaching stress tests and repeated-seed evaluation in
  [the framing memo](framing/prediction-vs-intervention.md) and
  [the detector outline](lumawarp/README.md). Freeze the graph, coefficients,
  estimand, intervention semantics, seeds, sample sizes, noise regimes,
  computation budget and uncertainty procedure before inspecting outcomes.
- For the **14-node working subgraph**, Step 8 discovery comparisons remain
  pending in the status file. Address the binary outcome and the recorded
  disconnected-outcome diagnostic; retain the original diagnostic alongside
  any mixed-data method comparison. Steps 9–11 are also pending extensions.
- For the **51-node full DAG**, the structural propagation result remains a
  prototype. Plan scale and bootstrap checks from the research record;
  preserve the ordering-only null and matched-background comparison.
- Review Step 6 with a human expert. Rounds 2 and 3 remain a **scripted
  heuristic** until that happens. Do not relabel them as expert evidence.

These are next-work priorities, not a claim that experiments ran on this Mac.
Do not start a blanket rebuild of frozen bundles merely to open the app.
Record results and limitations in `docs/` first, then update reviewed bundles,
code, tests, figures and the teaching companion together. Change frozen-output
hash baselines only for intentional, reviewed output changes. Keep teaching
stress tests separate from NASA-topology simulations and distinguish both
graph sizes. Preserve null results; never tune a generator to improve the story.

## Teaching and visual work still open

Andy prefers the richer original GIF to the new, slight “Replay change”
pulse. **That replacement is not yet implemented.** Reuse/adapt
`site/assets/two-goals.gif` (also in `docs/images/`) as the starting point:
its prediction-versus-intervention sequence carries more explanation.
Its bar heights are schematic, not measured SHAP values or causal effects;
make that distinction clear and align its four-node chain with the surrounding
explanation. Preserve the cohesive layout, static fallback, reduced-motion
support and mobile readability; remove redundant motion.

Keep the public page focused on the argument. Put runnable exploration and
technical detail in the existing companion (`apps/app.py`, `apps/causal_shap/`,
`apps/bundles/`) and written guide, linking them clearly from the page.
The Shiny companion is currently local, not deployed by GitHub Pages.

Existing sources worth drawing from, selectively:

- This hub's `site/assets/`, `docs/images/` and `apps/` first.
- The older `causal-shap-target-dags` checkout for provenance; implementation
  belongs in this hub, not a second active copy.
- `tao-of-rwd`: ACIC artwork under `api/public/img/acic-2026/` and
  `brand/public/img/acic-2026/`, plus the causal-SHAP page components.
- Synced Box project `Causal SHAP Target DAGs - Robert Reynolds Lexi Pasi`:
  `raw images and figures/` and `demo-production/`. These were inventoried,
  not exhaustively reviewed or copied. Inspect individual candidates and
  their suitability for publication before reuse.

Mac-specific source paths are in ignored `PROJECT_MAP.md`; reconstruct local
paths on the next machine. CLI orchestration experiments are also local under
ignored `.scratch/agent-delegation/`. Claude worked for visual/editorial review;
Antigravity CLI (`agy`, Gemini model) worked for adversarial review after the
standalone Gemini CLI rejected this account. Recheck installations and sign-ins
on the next machine. Treat either agent's claims as review suggestions requiring
verification, and keep private materials out of review payloads.

## Finish and publish

Run the relevant experiment and bundle validations plus `python -m pytest -q`.
For presentation changes, run `python site/build_tutorial_figures.py` when
regenerating those SVGs, then `quarto render site`; inspect desktop/mobile,
animation replay and reduced-motion behavior. Keep `site/` the only public
Quarto project and the root `index.html` a redirect.

Commit reviewed changes to this hub's `main` and push without force. The hub's
site workflow checks rendering; the deployment workflow lives in the old repo
and reads this hub's `main`:

```bash
gh workflow run publish-site.yml -R andystats/causal-shap-target-dags
gh run list -R andystats/causal-shap-target-dags --workflow publish-site.yml --limit 3
```

Verify deployment completion and the live page. Localhost URLs only work on
the machine running the preview. Keep binaries, credentials, raw logs, private
bridge/block results, `docs/STATUS.md`, `docs/methods/`, and `manuscript/` out of
commits; never force-add them or machine-rewrite the human manuscript introduction.
