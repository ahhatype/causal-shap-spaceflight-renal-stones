# Editable Supplementary Information

Start with **main.tex**. This is a self-contained LaTeX `article` version of
the explanatory companion, Analytical Workflow and Method Choices, with editable text, tables, equations and BibTeX citations.
The compiled preview is **main.pdf**.

| File or folder | Purpose |
| --- | --- |
| `main.tex` | Article source; refine this directly |
| `references.bib` | References cited by the article; add new entries here |
| `figures/` | Vector PDF figures included by LaTeX |
| `diagrams/` | Editable draw.io sources and export instructions |
| `build.py` | Compile the article without changing its source |
| `.build/` | Ignored temporary build files and logs |

## Build

With Python, pdfLaTeX and BibTeX available, run from this folder:

```text
python build.py
```

Or, from the repository root:

```text
python docs/playbook/supplementary-information/build.py
```

This runs pdfLaTeX, BibTeX, then pdfLaTeX twice, and refreshes `main.pdf`.
It does not regenerate `main.tex` from Markdown or overwrite diagram edits.
The article source is authoritative. From the repository root,
`python analysis/build_spine_guide.py` compiles the same document.
The local `main.tex` is a complete article, usable offline with this folder's
bibliography and figures. In the shared Overleaf project, **edit the full article
in root `supplement.tex`**. Its bibliography, figures and editable diagrams live
in `supplementary-information/`; that folder has no second article source.

To prepare that layout from the local source:

```text
python build.py --export-overleaf
```

This creates `.build/overleaf-supplement.zip` with the complete `supplement.tex`
and supporting folder. The only source transformation is the support-file path;
the generated ZIP is an export, not another editing copy. Downloaded Overleaf
sources also compile offline: keep `supplement.tex` beside its supporting folder
and run pdfLaTeX, BibTeX, then pdfLaTeX twice on `supplement`.

In Overleaf, select **and open** `supplement.tex` before compiling the supplement.
Restore and open root `main.tex` for the manuscript afterward. Merge fresh
collaborator edits back into local `main.tex` before exporting again; the local
support path is empty, whereas the Overleaf path is `supplementary-information/`.
Neither a build nor an export overwrites manually edited text or diagrams.

## Refine the schematics

Open `method-workflow.drawio` or `graph-surgery.drawio` in `diagrams/` using draw.io. Each shape, label and connector
is editable. Export a cropped PDF with the same filename into `figures/`, then
rebuild the article. See [diagram instructions](diagrams/README.md).

The [workflow overview](../README.md) links the supporting method and evidence
notes. The manuscript and this supplement have separate LaTeX entry points within the
shared Overleaf project.

## Journal placement

npj Microgravity does not permit Supplementary Methods: the study's methods
must remain in the main manuscript. This document is explanatory Supplementary
Information and uses the same Step 0–6 sequence. See the
[journal guidance](https://www.nature.com/npjmgrav/for-authors-and-referees/submission-guidelines#supplementary-information).
The final submission should combine any additional supplementary content into
one PDF. This working draft is not a claim of complete submission compliance.
