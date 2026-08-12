# Viewing the working DAG in DAGitty

`renal_stone_working_subgraph.txt` is the 12-node working subgraph from
[`config/dag_spec.yaml`](../config/dag_spec.yaml), exported in DAGitty's
native model syntax.

## How to view it

1. Open <https://dagitty.net/dags.html>.
2. Model menu > Model code (or the "<>" code-view button in the toolbar).
3. Paste in the full contents of `renal_stone_working_subgraph.txt`.
4. Switch back to the graphical view to see the DAG, or use dagitty's
   built-in analysis tools (adjustment sets, testable implications,
   d-separation) directly from the code view.

`duration` is tagged as the exposure and `nephrolithiasis` as the outcome,
matching `config/dag_spec.yaml`'s `outcome:` field - dagitty's own path- and
adjustment-set-finding features key off those two tags.

## Generated, not hand-edited

This file is a generated artifact, not a second source of truth. It's
produced by [`r/R/dag_utils.R`](../r/R/dag_utils.R)'s
`dag_spec_to_dagitty()` / `write_dagitty()`, driven by
[`pipeline/step02_dag_construction.R`](../pipeline/step02_dag_construction.R),
which reads `config/dag_spec.yaml` and writes the same file to
`data/interim/renal_stone_working_dag.txt` (gitignored, since everything
under `data/` is regenerated rather than committed - this docs copy exists
so a browsable version is normally available without running the pipeline).
Positions are a deterministic layered layout (see `dag_spec_positions()` in
`r/R/dag_utils.R`) - regenerating always produces byte-identical output, so
this file only changes when the graph itself does.

If the DAG changes, edit `config/dag_spec.yaml` and regenerate both copies:

```bash
make step02
cp data/interim/renal_stone_working_dag.txt docs/renal_stone_working_subgraph.txt
```

Do not hand-edit `renal_stone_working_subgraph.txt` directly - it will drift
from `config/dag_spec.yaml`, which is exactly the two-sources-of-truth
problem [ADR 002](decisions/002-data-interchange-contract.md) exists to
avoid.

## What's not represented here

- **Node types beyond exposure/outcome** (confounder, mediator,
  exogenous_confounder, mediator_countermeasure, ...) - dagitty's own
  vocabulary doesn't have slots for these, so they're untagged plain nodes
  here. The full typing lives in `config/dag_spec.yaml`.
- **Edge coefficients, magnitudes, and the interaction term**
  (`urinary_calcium_excretion` x `hydration_fluid_intake` ->
  `mineralized_renal_material`) - dagitty's graph model has no attribute for
  a product-interaction term, so that edge appears as an ordinary directed
  edge here. The interaction itself lives in `config/edge_coefficients.yaml`.
- **selection_mechanisms** (astronaut selection, the era/countermeasure
  sampling axis) - `config/dag_spec.yaml` documents these as selection
  mechanisms applied during data generation (Step 10), not causal DAG nodes,
  so they're deliberately excluded from the graph here too.
