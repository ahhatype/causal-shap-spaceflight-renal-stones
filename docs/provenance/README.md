# Provenance

## DAG source and handoff
Base DAG: NASA's public SA-07566 "Risk of Renal Stone Formation" DAG, supplied to Andy Wilson and Lexi Pasi by Robert Reynolds (DAGitty source, 2026-07-13 handoff). 53 nodes/83 edges per Robert's version, 51 nodes/75 edges in the prior source-aligned reference. Cohen's kappa 0.978 after semantic node mapping, precision 1.000, recall 0.958, structural Hamming distance 3, with a small number of unmatched edges retained for expert adjudication.

Public sources:
- [DAG narrative (PDF)](https://www.nasa.gov/wp-content/uploads/2025/09/renal-stone-risk-dag-narrative.pdf)
- [DAG code, DAGitty (TXT)](https://www.nasa.gov/wp-content/uploads/2025/09/renal-stone-dag-code-sa-07566.txt)
- [NASA risk page](https://www.nasa.gov/directorates/esdmd/hhp/risk-of-renal-stone-formation/)
- [2017 HRP evidence report](https://humanresearchroadmap.nasa.gov/evidence/reports/Renal.pdf)

## Coefficient sourcing and open decisions
The full node table, edge list, and per-edge citations live in [`config/dag_spec.yaml`](../../config/dag_spec.yaml). Placeholder structural-equation coefficients live in [`config/edge_coefficients.yaml`](../../config/edge_coefficients.yaml). Both files carry `status: PLACEHOLDER` and are pending Robert Reynolds's review; treat every numeric value in them as a simulation design parameter, not a NASA effect estimate.

Open decisions (age arrow direction, sex as direct effect vs. interaction, which outcome measure to lead with) are logged at the bottom of `config/dag_spec.yaml`.

## Superseded direction
Bone fracture was the original primary track, dropped in favor of renal stone. Not wasted work: the Bone Formation and Bone Resorption mediator nodes carry over directly, since Bone Remodeling sits immediately upstream of the renal pathway in NASA's own reference graph. The bone-specific outcome measures (FRAX, F.Load, HR-pQCT) are no longer used.
