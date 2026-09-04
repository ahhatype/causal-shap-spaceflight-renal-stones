# LumaWarp detector: placeholder for the expanded treatment

**Status:** placeholder, 2026-09-03. Owners: Lexi Pasi and Andy Wilson.
Governing decision: [ADR 008](../decisions/008-lumawarp-detector-placeholders.md).
Framing: [`../framing/prediction-vs-intervention.md`](../framing/prediction-vs-intervention.md).

This document is the outline of the section the paper still has to write.
Each heading states what belongs there and what is already known. Text in
`TODO` blocks is to be written; text marked **gated** may not be written into
this repository until Lucidity Sciences answers the sign-off questions in
section 8.

## 1. What the detector is for

**The problem, in one sentence: how do we know deep nodes from shallow
nodes?** Total effects shrink with depth, sampling variance and measurement
noise erase the deep ones first, and predictive importance falls off with
depth by construction, so the data alone make a deep cause and a column of
noise look alike. The detector exists to tell them apart.

The intervention playbook casts a wider net than the prediction playbook and
then prunes. The detector is the instrument for the first half: a per-node
signal, derived from a fitted model's internal geometry rather than from its
predictions, that points at nodes whose predictive credit has been absorbed
by something nearer the outcome. It is a pointer for expert review, not an
importance score and not a causal claim. That framing is fixed by the
research record and by the notes ("ELO" and the pruning step); the paper
should hold it.

```
TODO: two paragraphs. (1) The detector's position in the pipeline: after
Step 4 (baseline SHAP) and after Step 6 (causal SHAP), feeding the pruning
and expert-review loop. (2) What "pointer, not score" means operationally:
flags, not weights; per channel, never averaged.
```

## 2. What LumaWarp is (public-safe description)

LumaWarp (Lucidity Sciences, beta) is a learned-kernel classifier. It builds
a reproducing kernel per dataset and represents the data through one learned
one-dimensional kernel per input feature, then classifies with a weighted sum
of kernel evaluations at a small set of support vectors. Its diagnostics
expose, per feature and per optimizer iteration, a fixed-length design
vector. The detector reduces that design vector to per-feature scores.

**Gated:** the names and semantics of the design-vector blocks, the reduction
Lucidity's own script applies, the observed behavior of each block on the
renal, toy, and HAPrI runs, and any figure derived from them. These are in
the private format guide (`docs/LUMAWARP_EXPLAIN_GUIDE.md`, gitignored) and
in `C:\Lumawarp\`.

```
TODO (after sign-off): one paragraph per block, with the vendor's
confirmed definition, replacing the reverse-engineered reading.
```

## 3. Interface contract

Fixed and public: [`python/src/causal_shap_renal/lumawarp_contract.py`](../../python/src/causal_shap_renal/lumawarp_contract.py).

- Input: the shared attribution Parquet schema (ADR 002) plus the simulated
  data, one group per (method, engine, dag_variant, iteration_round).
- Output: one row per feature per group; three channels (`depth`,
  `importance`, `complexity`), each z-scored within the group; a flag per
  channel at z > 1; a composite flag equal to the depth flag; provenance.
- Provider: any object implementing `DetectorProvider`, loaded by dotted path
  by `pipeline/step05_lumawarp_detector.py` and `pipeline/step07_lumawarp_reweight.py`.
  The default provider refuses to score.

The channel names are placeholders for roles, not for LumaWarp internals.
Which internal quantity feeds which channel is the provider's decision and
is gated.

## 4. The depth-sensitivity hypothesis

Deeper nodes carry smaller total effects (product of path coefficients),
wash out faster under measurement noise, and are recovered worse by
constraint-based discovery. A detector that is useful for the intervention
playbook must therefore have sensitivity that does not fall off with depth
as fast as predictive importance does. The single-seed renal observation
(composite near-orthogonal to TreeSHAP; flagged node was the root cause) is
consistent with that and proves nothing on its own.

```
TODO: prespecify the test. For each testbed (E1, E2, E3 below; then the
14-node working subgraph; then the full DAG): record each feature's directed
depth to the outcome, its frozen total effect, its predictive importance,
and its detector channels; report Kendall's tau of each channel against
depth and against truth, per seed, over at least 30 seeds; report the
sensitivity-vs-depth curve directly.
```

## 5. The dichromatic sensitivity filter (Lexi Pasi's proposal)

A single-threshold sensitivity filter trades missed deep nodes against
admitted noise columns. The dichromatic filter runs two channels at
different sensitivities and gates on their pattern of agreement. The
whiteboard lists its components as motivation, color contribution, and
complexity.

```
TODO (Lexi): (1) Define the two channels. (2) Define the gating rule:
which (channel A, channel B) patterns admit a node, which prune it, which
send it to the expert. (3) State what "color contribution" reports: the
share of a node's flag that came from each channel. (4) State how
complexity (PSCI v0 seam in apps/causal_shap/complexity.py, or the
vendor's score) enters: as a third channel, as a prior on the threshold,
or as a cost in Step 13.
```

Closest published analogs, for the related-work paragraph: two-stage
screening (Fan and Lv 2008) and threshold selection against a null-control
channel (Barber and Candès 2015; 2019). No two-channel detection literature
inside causal discovery was found; present the filter as new.

## 6. Experiments E1 to E3

From the 1 September notes; specified in the framing memo, section 7.

| Experiment | Structure | Varies | Measures |
| --- | --- | --- | --- |
| E1 | Two-layer tree: B1 -> A1 -> Y; B2 -> A2 -> Y; B2 -> A3 -> Y | n, noise | Recovery, credit, and flags for the B layer |
| E2 | Three-layer tree (add a C layer) | depth | Precision needed per depth; sensitivity-vs-depth curve |
| E3 | E2 plus variance: shrinking n, then measurement noise on A and C | sampling variance, noise level | Variance at which deep nodes sink into noise; whether the depth channel and the dichromatic filter separate them. Chain version already drawn: `docs/images/depth_washout.png` (`analysis/depth_washout_figure.py`) |

```
TODO: implement as teaching DAGs in apps/causal_shap/teaching_dags.py
(the NodeSpec engine already builds linear-Gaussian trees with exact total
effects) and add a driver under pipeline/ once the provider exists.
```

## 7. Results (placeholder)

```
TODO (gated): per-channel tables for E1-E3, the working subgraph, and the
full DAG; the three-blocks-behave-differently finding restated with the
vendor's definitions; repeated-seed uncertainty.
```

## 8. Sign-off questions for Lucidity Sciences

Recorded here so the gate is visible in the public repository. The full
versions, with file-level detail, are in the private format guide.

1. Confirm or correct the reading of the design-vector blocks and what the
   block index enumerates.
2. Should the reduction key on the WARP validation trajectory or on the
   shipped blend model? They diverged on the imbalanced renal run.
3. Is within-block variance the intended reduction, or a placeholder for
   something else (entropy, a norm ratio)?
4. Which optimizer phases log design vectors?
5. Are the support-vector label columns needed downstream?
6. Which of the following may appear in a public paper and repository: the
   log column format, the block names, the reduction, aggregate per-feature
   outputs, figures?

## 9. Cross-references

- Manuscript outline (private, Box `manuscript/`): section 8 is the gated
  depth-diagnostic section this document expands.
- ACIC 2026 page, "Luma Warp ELO diagnostic" panel:
  <https://www.tao-rwd.com/acic-2026/causal-shap>.
- PSCI v0 registry seam: `apps/causal_shap/complexity.py` and its tests.
