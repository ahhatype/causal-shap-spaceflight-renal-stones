# Manuscript references: the spaceflight and DAG-program side

**Status:** ported 2026-09-04 from the Box reference register (2026-07-10),
with the private links removed. These are the references the article needs
for the NASA DAG program, the venue, and the epidemiology framing; the
attribution-method references are in
[`../full_dag/PROVENANCE_AND_REFERENCES.md`](../full_dag/PROVENANCE_AND_REFERENCES.md)
and the reframing's claims in [`claims-to-citations.md`](claims-to-citations.md).

## Venue

*npj Microgravity*, collection "Human System Risk Management and Knowledge
Graphs for Human Spaceflight, Vol. II":
<https://www.nature.com/collections/abfcaeggdc>. Deadline recorded as
2026-10-31 from the public collection page (2026-07-10); confirm.

## NASA DAG program

- Antonsen, E., Reynolds, R.J., Charvat, J., et al. (2024). Causal diagramming for assessing human system risk in spaceflight. *npj Microgravity* 10:32. <https://doi.org/10.1038/s41526-024-00375-7>
  The drawing method behind the HSRB DAGs.
- Ward, J., et al. (2024). Levels of evidence for human system risk evaluation. *npj Microgravity*. <https://doi.org/10.1038/s41526-024-00372-w>
  The evidence-level system used to annotate edges; `config/dag_spec.yaml`'s `status` field follows its spirit.
- Reynolds, R.J., et al. (2022). Validating Causal Diagrams of Human Health Risks for Spaceflight: An Example Using Bone Data from Rodents. *Biomedicines* 10(9):2187. <https://doi.org/10.3390/biomedicines10092187>
  Testing a DAG's implied independencies against data; the model for Step 4's DAG-derived expectations.
- Reynolds, R.J. (2026). Living DAGs: the future of DAGs in epidemiology. *American Journal of Epidemiology* 195(5):1365. <https://doi.org/10.1093/aje/kwag029>
  DAGs as cumulative epistemic infrastructure; supports the "Living DAGs to intervention prioritization" argument.
- Antonsen, E., et al. (2024). Networks and Analytic Approaches. In *Systems Medicine for Human Spaceflight*. World Scientific. <https://doi.org/10.1142/9789811287695_0011>
  Section 11.6 onward carries the network-science material and the renal-stone mechanistic chain (altered gravity, bone remodeling, urine chemistry, nephrolithiasis).
- NASA DAG guidance documentation: <https://ntrs.nasa.gov/citations/20220006812>
- NASA HSRB DAG report (renal-stone DAG and narrative, pp. 68-70): <https://ntrs.nasa.gov/citations/20220015709>
- NASA renal-stone risk page: <https://www.nasa.gov/directorates/esdmd/hhp/risk-of-renal-stone-formation/>

Robert Reynolds's related DAG papers, for the methods-review paragraph:

- The cerebral palsy DAG: a structural causal model of aetiology. *Developmental Medicine and Child Neurology*. <https://doi.org/10.1111/dmcn.70267>
- Causal diagrams for research about childhood-onset disabilities. *Developmental Medicine and Child Neurology*. <https://doi.org/10.1111/dmcn.70064>
- A Zenodo preprint on translational validity was shared (<https://zenodo.org/records/19872878>); title and preferred citation unverified.

## Epidemiology framing

- Galea, S. (2013). An argument for a consequentialist epidemiology. *American Journal of Epidemiology* 178(8):1185-1191.
  Epidemiology judged by what it changes; the intervention playbook's motivation in one citation.

## Renal-stone DAG versions in hand

Three related, non-identical versions exist (see
`dag-candidates/renal-stone-dag-harvest.md`): the SA-07566 machine-readable
graph (51 nodes, 75 edges; the executable reference), the Chapter 11 Figure
11.6 image with an expanded medical-illness block, and the ASGSR 2023 poster
version (53 nodes, 83 edges; splits bone formation from resorption). Robert
Reynolds's 2026-07-13 file matches the last of these. The article should say
which version each result was generated from.

## Still to follow up (from the July register)

- Robert's node metadata: actionable vs hazard, mediator, proxy; rough cost
  or difficulty; which placeholder coefficients to replace.
- Whether Robert's network-analysis papers are now shareable.
- Whether and how to cite the Zenodo preprint.
- Lexi's compact LumaWarp method specification (now the gated section 8).
