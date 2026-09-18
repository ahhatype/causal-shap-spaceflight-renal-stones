# Editable study guide

Start with **main.tex**. This is a self-contained LaTeX `article` version of
the seven-stage manuscript-aligned method guide, with editable text, tables, equations and BibTeX citations.
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
python docs/playbook/study-guide-latex/build.py
```

This runs pdfLaTeX, BibTeX, then pdfLaTeX twice, and refreshes `main.pdf`.
It does not regenerate `main.tex` from Markdown or overwrite diagram edits.
The article source is authoritative. The repository-root compatibility command
`python analysis/build_spine_guide.py` also refreshes the linked `study-guide.pdf` copy.
For Overleaf, upload `main.tex`, `references.bib` and the `figures` folder to
a project and choose pdfLaTeX with `main.tex` as its main document.

## Refine the schematics

Open `method-workflow.drawio` or `graph-surgery.drawio` in `diagrams/` using draw.io. Each shape, label and connector
is editable. Export a cropped PDF with the same filename into `figures/`, then
rebuild the article. See [diagram instructions](diagrams/README.md).

Draw.io is installed on this computer as a Brave web app. Inkscape 1.4.2 and
PowerPoint are also installed. Inkscape can edit the original SVGs in
`../../images/`; draw.io is the more direct option for moving connected nodes.

## Source and linked PDF

This folder holds the current manuscript-aligned guide, revised on 16 September
2026. `../study-guide.md` is its entry page; `../study-guide.pdf` is a compatibility
copy of `main.pdf`. Use `python analysis/build_spine_guide.py` from the repository
root to compile the article and refresh both PDFs. The main manuscript and
shared Overleaf project are separate.
