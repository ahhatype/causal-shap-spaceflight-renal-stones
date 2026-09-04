# ADR 009: One home for the project, including the manuscript

## Status
Accepted, 2026-09-04.

## Context
By early September 2026 the project's material lived in at least six
places: this hub; the original causal-shap-target-dags repository; the Box
project folder (notes, references, whiteboards, a stale July code clone,
dated output snapshots); `C:\Lumawarp\experiments and causal discovery\`
(the manuscript Word drafts, which a 2026-08-12 move to Box never actually
delivered; recovered 2026-09-03); an OneDrive "offline sandbox" with LumaWarp
study material; and, inside this hub, two gitignored folders (`docs/methods/`,
`docs/manuscript/`) holding manuscript text. The article deadline is
2026-10-31 and the coauthors need one place to look.

## Decision
The hub is the single home for everything the project produces, and the
manuscript is written here, in LaTeX, under `manuscript/`:

| Location | Role from now on |
| --- | --- |
| This hub (`ahhatype/causal-shap-spaceflight-renal-stones`) | Code, results, docs, site source, **and the manuscript** (`manuscript/main.tex`, `references.bib`), the latter gitignored for now |
| `andystats/causal-shap-target-dags` | Frozen provenance and the GitHub Pages deploy shim (ADR 007). No edits except the deploy workflow |
| Box project folder | Coauthor exchange only: Word or PDF exports of the LaTeX manuscript in dated `from-github-YYYY-MM-DD/` folders, the recovered August Word originals in `manuscript/` as an archive, reference PDFs, whiteboard photos. Not a place to edit text |
| `C:\Lumawarp\` | LumaWarp runtime and frozen logs only. `_to_delete_2026-08-12\` may be deleted once the Box and hub copies are confirmed |
| OneDrive `offline sandbox\Lucidity stuff` | Archive of LumaWarp study material; nothing project-critical |
| `docs/methods/` (gitignored) | Superseded by `manuscript/main.tex`; kept locally as the pre-LaTeX snapshot, not updated further |
| `docs/manuscript/` (gitignored) | Retired; its outline moved to `manuscript/OUTLINE.md` |

## What the manuscript folder may and may not contain
- The human-written introduction is reproduced verbatim from the August
  Word draft and is marked as such in the source. It is revised by humans
  only; an LLM may propose, never rewrite.
- Methods follow the 13-step flow of the original repository.
- Nothing gated by Lucidity Sciences' sign-off (ADR 008) enters the
  manuscript source: the depth-diagnostic section is a placeholder that
  names the detector's role and the interface and stops there.
- No coauthor correspondence, no credentials, no private PDFs.

## Consequences
- `manuscript/` is gitignored (decided 2026-09-04, same day): the folder
  lives in the hub and builds from it, but the draft is not published until
  the coauthors agree. It appeared in one public commit (`7913fa7`) before
  the decision and was removed from the tree in the next; the history still
  holds that version unless it is rewritten. Removing the `.gitignore` line
  publishes it.
- `make manuscript` builds the PDF with latexmk. CI does not build it.
- `.gitignore` drops the `docs/manuscript/` entry.
- Box receives a PDF export whenever the draft goes to coauthors, in a
  dated `from-github-` folder, and nothing else changes there.
