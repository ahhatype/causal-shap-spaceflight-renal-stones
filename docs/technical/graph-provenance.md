# Renal graph sources and working-graph adaptations

The project contains two supplied renal-stone graph versions and a smaller,
adapted simulation graph. They are not interchangeable.

| Graph | Nodes / directed edges | Role |
| --- | --- | --- |
| [Robert Reynolds's supplied graph](../../references/robert-reynolds-2026-07-13/Renal%20Stone%20Risk.txt), *Renal Stone Risk Edge Work DAG CM Final — Errata 20220322* | 53 / 83 | Complete source file received on 13 July 2026; shown as the supplied graph in Figure 1. |
| [Earlier SA-07566 reference](../../references/renal-stone-dag-code-SA-07566.txt) | 51 / 75 | Source topology used for the existing full-DAG simulations. |
| [Working simulation graph](../../config/dag_spec.yaml) | 14 / 21 | Smaller graph with added variables, resolved mechanisms and shortcuts; used by the working-subgraph simulations. |

The two source versions differ in both labels and structure. Their documented
[comparison](../full_dag/PROVENANCE_AND_REFERENCES.md#renal-stone-match-to-the-repository-graph)
does not establish their equivalence. Showing the complete 53-node graph does
not migrate existing 51-node simulation results to that version.

## What the working graph retains and changes

The [edge crosswalk](working-graph-edge-map.csv) checks all 21 working edges
against the 53-node source. The source's directed edges were parsed from the
original DAGitty file and checked against the existing canonical edge CSV;
the two edge sets agree exactly. Every path recorded in the crosswalk follows
arrows in their supplied direction. The categories are conservative:

- **Retained direct relationship (1):** Bone Formation → Urine Chemistry.
- **Collapsed source pathway (2):** Hydration → Urine Concentration → Urine
  Chemistry, and Urine Chemistry → Mineralized Renal Material → Nephrolithiasis.
  The working hydration variable combines hydration and fluid intake; its
  correspondence to the source's distinct Hydration and Water Intake nodes is
  an explicit modeling choice, not an exact variable match.
- **Study-added or adapted relationship (18):** an added variable, an expanded
  mechanism, or a shortcut that is not an exact direct source edge or a simple
  collapse of omitted intermediates. This category describes the modification;
  it does not imply that the relationship lacks biological support.

Two shortcuts need particular care. Nutrients → Urine Chemistry is reachable
in the source through Bone Resorption, and Hydration → Nephrolithiasis is
reachable through Urine Concentration, Urine Chemistry and Mineralized Renal
Material. However, Bone Resorption and Urine Chemistry remain in the working
graph. Calling those added direct links simple reductions would hide a change
in the modeled pathways. They are marked as study adaptations. Whether their
coefficients represent distinct residual mechanisms without double counting
requires substantive review; the existence of a longer source path does not
answer that question.

Duration and in-flight vitamin D are absent as nodes from the supplied graph.
Duration is not an exact substitute for Altered Gravity. Sex, stone history
and hypercalciuria predisposition may help operationalize Individual Factors,
but the supplied topology does not establish a one-to-one mapping for these
variables or their added edges. Similarly, the calcium, oxalate and PTH nodes
resolve mechanisms at a finer level than the source. Literature-informed
additions should be justified as such, without calling them verbatim NASA
relationships.

## Structure and numerical assumptions

The supplied DAG provides directed relationships, not the numerical effects
used in these simulations. Equations, distributions, coefficients and
interactions are study assumptions. In particular, Bone Formation → Urine
Chemistry is present in the supplied graph even though its near-null
simulation coefficient is a study choice. The old `confirmed_mechanism`,
`magnitude_estimate` and `directional_only` fields mix different evidence and
parameterization questions; they are not a defensible source-provenance legend.

Figure 1 should distinguish the supplied graph from the adapted working graph.
Within the latter, any edge styling describes the crosswalk categories above,
not causal strength, empirical confirmation or NASA endorsement of simulation
parameters. This audit documents the existing graph without changing its
equations or frozen results. Robert and the coauthors should review the
adaptations before treating the working graph as an agreed substantive model.

## Editing and exporting the figures

The [complete graph](../images/nasa_supplied_dag.drawio) and
[working graph](../images/working_subgraph_dag.drawio) have native draw.io
sources. Edit these directly and export PDF/SVG for publication. Normal LaTeX
builds consume the figure PDFs and preserve diagram edits.

To regenerate the automatic layouts from the recorded topology, run
`python analysis/source_graph_figure.py` and
`python analysis/working_subgraph_figure.py` from the repository root.
These require Python with `svglib` and `reportlab`, Node.js with `@viz-js/viz`,
and Poppler's `pdftoppm` on PATH. Set `VIZ_JS_MODULE` to the installed
`@viz-js/viz/dist/viz.cjs` if using your own Node installation. Existing
`.drawio` files are preserved unless `--refresh-drawio` is explicitly supplied;
regenerating PDF/SVG replaces their current exports.
