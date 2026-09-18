# Editable schematics

The article uses two native diagrams.net/draw.io sources:

- [method-workflow.drawio](method-workflow.drawio): seven method stages, optional discovery, supplied-DAG bypass, predictive route and evaluation feedback.
- [graph-surgery.drawio](graph-surgery.drawio): observational chain and `do(M=m)`, with the incoming arrow removed and the outgoing arrow retained.

[renal-selection-overlay.drawio](renal-selection-overlay.drawio) remains the supplementary selection illustration.

## Editing

Open a `.drawio` file in the installed draw.io Brave app (Device > Open Existing Diagram), or in another diagrams.net installation. Boxes, labels and connectors are native editable elements. Save the source here, then export a cropped PDF to the corresponding file in `../figures/`. Rebuild the article with `python ../build.py`.

An edit to the draw.io source does not automatically refresh its PDF. SVG and PNG exports are provided for other uses; Inkscape can edit the SVGs.

## Recreating the starting layouts

`build_method_workflow.py` generates the two current draw.io documents and matching PDF/SVG/PNG exports. It requires ReportLab and uses pdftoppm for PNG exports. Its XML, endpoints, text fit and page bounds are checked, and the rendered starting layouts have been visually inspected.

**Running the generator overwrites manual changes to those diagrams and exports.** Normal refinement should take place in draw.io. `build_drawio.py` recreates only the selection overlay starting layout; it also overwrites manual edits to that diagram. `analysis/build_selection_schematic.py` exports the selection illustration for the technical note. Neither script rebuilds the article.
