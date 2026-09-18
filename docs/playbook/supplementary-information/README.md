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
For a separate Overleaf project, upload this folder's `main.tex`,
`references.bib` and `figures/`, and select `main.tex`. In the shared manuscript
project these files live under `supplementary-information/`. The root
`supplement.tex` launcher contains:

```tex
\def\SupplementRoot{supplementary-information/}
\input{supplementary-information/main.tex}
```

Choose `supplement.tex` as the main document and open that launcher in the
editor before compiling the supplement. To compile the manuscript, choose
and open the root `main.tex`. Overleaf can compile an open standalone document
in preference to the configured main file. Edit the source inside the
supplement folder, not the launcher. Its bibliography and figures stay separate
from the manuscript's files. Bring any collaborator edits back from Overleaf
before replacing an uploaded version.

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
