# Whiteboard notes, 1 September 2026 (transcription)

Source: two handwritten pages photographed into `Book Sep 3, 2026.pdf`
(Box `Sandbox`). Transcribed 2026-09-03. Bracketed text is the transcriber's
reading where the handwriting is ambiguous; question marks mark readings that
should be confirmed by the author. Interpretation lives in
[`../framing/prediction-vs-intervention.md`](../framing/prediction-vs-intervention.md);
this file only records what the page says.

## Page 1

- Simpler DAG. `simCausal()` => do() => ground truth.
- Lame causal discovery (linear SHAP). Arrow up: model dependent.
- <LW> detector. [LW = LumaWarp]
- Causal SHAP ~ OK (delicate). Fragile => obstacle course ever rougher,
  "more realistic".
- Pruning step (with LW). Sub-items: ELO; spectral elements are bossy.
  [ELO = the LumaWarp entanglement ranking shown on the ACIC page; "spectral
  elements" most likely = the eig block of the LumaWarp design vector.]
- Goal: topological question / misdirect => helping to avoid these traps.
  Narrower focus: 1) stolen valor; 2) other problems.
- Goal of intervention (vs. prediction) => wider net, but still prune.
  - Motivation
  - Color contribution
  - Complexity
- Margin, vertical: DSG (dichromatic sensitivity gating); dichromatic
  sensitivity system. [Lexi's proposal; the three bullets above appear to be
  its components.]
- Sketch, bottom right: a curve that starts high and falls off, y-axis
  unlabeled (sensitivity), x-axis "# nodes". Annotation: "deeper nodes need
  higher sensitivity".

## Page 2 (continued)

- Axiom => right atoms in a DAG. Direct relationships tend to be linear.
- E1 (example or experiment 1): B1 -> A1 -> Y; B2 -> A2 -> Y; B2 -> A3 -> Y.
  A two-layer tree feeding one outcome.
- MGM PC-stable (OK for shallow trees). [Confirmed by the author 2026-09-03:
  MGM = the PC-Stable stage of the CausalMGM framework, which learns an
  undirected mixed-type skeleton first and then orients it with PC-Stable.]
  - One-layer tree => problems go away.
  - Run in reverse, problems get worse the deeper the DAG.
- Key assumption [LAU]: direct relationships tend to be linear. [Confirmed by
  the author 2026-09-03: "LAU" was a marginal question about whether to treat
  this like a law, that is, how strongly to enforce the assumption; it is not
  an initialism.]
  - Empirical isomorphism => discriminate between two without introducing new
    data.
- Sensitivity filter => dichromatic filter (o -> o -> Y). Even Robert's DAG:
  columns of noise.
- Measurement. Variance.
- E2: Deeper nodes need more measurement for proper adjudication (need more
  precision to be captured). => How do we know a deep node from a shallow node?
  [The author confirmed 2026-09-04 that this question is the core problem
  LumaWarp is meant to solve.]
- Deeper nodes wash out faster, accelerated by noise.
- E3: Giffen good (sinking into noise). [Corrected by the author 2026-09-04:
  the words are "Giffen good", an economics doodle about a related idea (a
  good whose demand rises with its price), not part of the experiment. E3 is
  about deeper nodes sinking into noise as variance grows.]

## Readings to confirm with the author

1. Resolved 2026-09-03: "mbm" reads MGM (CausalMGM's PC-Stable).
2. Resolved 2026-09-03: "LAU" was a question about treating linearity like a
   law, i.e. how strongly to enforce the assumption.
3. Resolved 2026-09-04: E3 reads "Giffen good", a side doodle; E1 to E3 are
   treated as candidate experiments.
4. (was 3) Whether E1, E2, E3 are numbered experiments to run or numbered examples.
   This transcription treats them as candidate experiments; see the framing
   memo.
