# Manuscript: the npj Microgravity article

This folder is the working manuscript, written in LaTeX and tracked in git
(ADR 009: one home for the project). Target: *npj Microgravity*, collection
"Human System Risk Management and Knowledge Graphs for Human Spaceflight,
Vol. II" (<https://www.nature.com/collections/abfcaeggdc>); deadline recorded
as 2026-10-31, confirm against the collection page.

| file | what |
| --- | --- |
| `main.tex` | The article. Introduction is human-written and verbatim from the August Word draft; Methods follow the 13-step flow; Results and Discussion are assembled from the repository's frozen records |
| `references.bib` | Bibliography. Entries marked `TODO verify` were cited from memory in the introduction and need checking; the rest carry a DOI or URL |
| `OUTLINE.md` | The 2026-08-30 outline with the 2026-09-04 reframing addendum; gated LumaWarp detail removed |
| figures | Read from `../docs/images/` (working-subgraph DAG, depth washout, the FIG. 1 spine, the FIG. 2 sufficiency transfer); regenerate with the scripts in `analysis/` |

## Rules

- **The introduction is human-written.** Nature journals restrict LLM-written
  text. Revise it by hand. An LLM may propose edits; it never rewrites.
- Blocks marked `\draftnote{...}` in the source were drafted with an LLM
  from the project's own records and must be rewritten by a human before
  submission. Blocks marked `\todo{...}` are open items. Both render in
  color so they cannot be missed.
- Nothing gated by Lucidity Sciences' sign-off enters this folder (ADR 008).
- Coauthors receive PDF exports in dated `from-github-YYYY-MM-DD/` folders
  in the Box project directory. Box is for exchange, not editing.

## Build

```bash
make manuscript        # latexmk -pdf, output manuscript/main.pdf (gitignored)
```

or, from this folder, `latexmk -pdf main.tex`. MiKTeX 25.4 and latexmk 4.88
were used on 2026-09-04.

## Provenance

- Human-written introduction: `Space SHAP_ Intro & Methods Drafts.docx`,
  last saved 2026-08-10, recovered 2026-09-03 and archived in the Box
  project folder under `manuscript/`.
- Methods steps: the same draft's "Methods (optimistic draft)", which its
  author marked as LLM-generated planning text to be rewritten once the
  scope is settled.
- Results: `docs/step04_results.md`, `docs/step06_results.md`,
  `docs/full_dag/RESEARCH_RECORD.md`, `docs/images/depth_washout.png`.
- Framing: `docs/framing/prediction-vs-intervention.md`; citations:
  `docs/references/`.
