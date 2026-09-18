# Editable schematics

The article uses two native diagrams.net/draw.io sources:

- [method-workflow.drawio](method-workflow.drawio): seven method stages, optional discovery, supplied-DAG bypass, prediction and effect-only routes, and evaluation feedback.
- [graph-surgery.drawio](graph-surgery.drawio): observational chain and `do(M=m)`, with the incoming arrow removed and the outgoing arrow retained.

[renal-selection-overlay.drawio](renal-selection-overlay.drawio) remains the supplementary selection illustration.

## Editing

Open a `.drawio` file in the installed draw.io Brave app (Device > Open Existing Diagram), or in another diagrams.net installation. Boxes, labels and connectors are native editable elements. Save the source here, then export a cropped PDF to the corresponding file in `../figures/`. Rebuild the article with `python ../build.py`.

An edit to the draw.io source does not automatically refresh its PDF. SVG and PNG exports are provided for other uses; Inkscape can edit the SVGs.

## Refreshing the workflow exports

`python build_method_workflow.py` reads the current `method-workflow.drawio` and refreshes its PDF/SVG/PNG exports in `../figures/`. It requires ReportLab and uses pdftoppm for PNG exports. It checks XML, connector endpoints, text fit and page bounds, and verifies that the editable source has not changed. The current exports have been visually inspected.

The exporter supports the boxes, text and connected arrows used in this schematic. If adding other draw.io shapes, export directly from draw.io. It does not modify the graph-surgery or selection diagrams, and the normal article build never regenerates editable diagrams.

`build_drawio.py` recreates the selection overlay starting layout and **overwrites manual edits to that diagram**. Normal refinement should take place in draw.io. `analysis/build_selection_schematic.py` exports the selection illustration for the technical note. Neither script rebuilds the article.
