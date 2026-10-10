# ADR 011: Archive causal-shap-target-dags, add the experiments workspace, consolidate the root

## Status
Accepted, 2026-10-10, at Andy's request.

## Decision
Three things, taken together:

1. **The original repository is retired.** `andystats/causal-shap-target-dags`
   is archived on GitHub (read-only) and its local checkout is removed. Its
   tracked content was already here (ADR 007; the 2026-10-07 inventory in
   ADR 010 found no research implementation missing). What was not tracked
   there, the private LumaWarp material and superseded planning files, is
   preserved as described below.
2. **This repository is the team workspace and sandbox.** Exploratory work
   lives under `experiments/`, one self-contained folder per experiment with
   its own README; the conventions are in `experiments/README.md`. The first
   entry is the stand-alone ConfoundingSHAP tutorial. The public-facing
   pipeline for the manuscript's central experiment is
   `ahhatype/causal-dag-eval-pipeline`; it is being prepared as the version
   shared with the paper, and this repository feeds it rather than competing
   with it.
3. **The root is consolidated.** The README carries the repository map and
   the links to related repositories. `REPRODUCIBILITY.md` moved to
   `docs/REPRODUCIBILITY.md`. `ORIENTATION.md` was folded into the README (map)
   and the ignored `docs/STATUS.md` (restart priorities), as AGENTS.md already
   said orientation belongs in contributor notes. `THIRD_PARTY_NOTICES.md` was
   folded into `docs/provenance.md`. The root `index.html` (a redirect for a
   Pages site that no longer exists), the empty `notebooks/` folder and the root
   `run_hub.bat` (now `apps/run_hub.bat`, beside the package it launches) were
   removed. `CITATION.cff` now points at this repository instead of the
   unpublished Pages URL.

## Where the old checkout's untracked material went

| Material | Location now |
| --- | --- |
| Every git ref of the old checkout, including a local-only rescue branch and two stashes pinned as `archive/stash-*` branches | A git bundle in the project's Box provenance folder, under `archive-2026-10-10-local-repo/`, with a verified test restore |
| Every gitignored or untracked file of the old checkout | A zip with a SHA-256 manifest in the same Box folder |
| The private LumaWarp bridge, its local provider, the per-node flag seam, their tests, the format guide, the HAPrI and LumaWarp result bundles and outputs, the Workbench clinical sample and expert edge list, the local launcher configuration | This checkout, at the paths the existing `.gitignore` (ADR 008) and `.git/info/exclude` already reserve for them, with `app/` renamed to `apps/`. Still never committed. |
| The August working paper, study guide, schematic and manuscript outline | Ignored `manuscript/.build/target-dags-paper-2026-08/` |
| Superseded planning files (PLAN, PROJECT_MAP, the HTML orientation hub, the August app plan and mockup, the pre-consolidation docs archive) | The Box zip only |

`HAPrI-AJCC-reproduction-public` imported the LumaWarp bridge from the old
checkout's `app/`; its default bridge path now points at this checkout's
`apps/` (the `CAUSAL_SHAP_APP_DIR` override is unchanged).

## Context
By October 2026 three repositories carried the npj Microgravity work: the
archived-in-all-but-name original, this hub, and Aimee's pipeline for the
paper's central experiment. The original had no remaining role beyond
provenance (ADR 010 had already retired its Pages site), its private files
were the only thing not yet in one place, and the hub root had grown to
fourteen tracked folders and six Markdown entry points. The team needs one
place to experiment and one clean place to publish.

## Consequences
- ADR 009's location table changes in one row: the old repository is archived
  provenance on GitHub, no longer a deploy shim, and has no local checkout.
- Links to the old repository remain valid (archived repositories stay
  readable). Historical documents under `docs/full_dag/`, `site/` and the
  earlier ADRs keep their wording.
- The frozen records and the two pipelines are untouched: no file under
  `analysis/`, `apps/`, `config/`, `pipeline/`, `r/`, `python/`, `data/`,
  `results/`, `references/` or `dag-candidates/` moved, so hash manifests and
  the R validator still find their inputs.
- New exploratory work goes under `experiments/`; earlier pilots keep their
  paths under `analysis/` because the records and technical notes cite them.
- This repository is public. Experiments committed here are public the moment
  they are pushed; make the repository private before committing anything the
  team is not ready to show.
