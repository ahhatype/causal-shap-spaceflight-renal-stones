# ADR 008: LumaWarp detector placeholders live here; runtime and bridge stay external

## Status
Accepted, 2026-09-03. Supersedes ADR 003.

## Decision
Steps 5 and 7 (the LumaWarp detector and its reweighting of Step 4 and Step
6 outputs) are now represented in this repository by three public-safe
things:

1. an interface contract, `python/src/causal_shap_renal/lumawarp_contract.py`,
   that fixes the input (the shared attribution Parquet schema, ADR 002) and
   the output (one row per feature with per-channel detector scores and a
   flag), with tests;
2. two pipeline drivers, `pipeline/step05_lumawarp_detector.py` and
   `pipeline/step07_lumawarp_reweight.py`, that validate inputs, declare the
   output path, and stop with a clear message until a detector provider is
   registered;
3. a documentation placeholder, `docs/lumawarp/README.md`, laying out the
   expanded treatment the paper needs: the detector's role in the
   intervention playbook, the depth-sensitivity hypothesis, the dichromatic
   sensitivity filter proposed by Lexi Pasi, and the experiments E1-E3 that
   would test them.

The LumaWarp binaries, credentials, configuration, raw logs, the Python bridge
that reproduces Lucidity's Explain reduction, and any block-level results
(the h0/h1/eig behaviors) stay outside this repository until Lucidity
Sciences answers the six sign-off questions recorded in the private format
guide. Their paths remain in `.gitignore`.

## Context
ADR 003 excluded LumaWarp entirely because the interface between the
detector and the attribution outputs was unspecified. Two things changed.
First, the consolidation (ADR 007) brought the PSCI v0 complexity registry
seam (`apps/causal_shap/complexity.py`) into this repository, which is the
public half of that interface. Second, the 1 September 2026 whiteboard notes
reframed the detector's job: not a reweighting of importance scores but a
way to identify deeper nodes that the prediction playbook washes out, under
the working assumption that direct relationships tend to be linear. That
reframing is a claim the paper has to argue in public, so its scaffolding
has to be public too.

## Consequences
- `docs/STATUS.md` and `config/pipeline_status.yaml` move Steps 5 and 7 from
  `deferred_external` to `placeholder`, owner unchanged.
- `pipeline/_deferred/README.md` no longer lists Steps 5 and 7.
- A detector provider is registered by implementing
  `causal_shap_renal.lumawarp_contract.DetectorProvider` in a file outside
  this repository (or in a gitignored one) and pointing the drivers at it
  with `--provider`. The contract module is the only place the drivers and
  the provider need to agree.
- Nothing in this repository may describe the design-vector block semantics
  or reproduce Lucidity's reduction until sign-off. Reviewers should treat
  any such text in a pull request as a blocker.
