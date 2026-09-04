# Repository working agreement

This is the hub for the Space SHAP paper. It carries two lines of work
(ADR 007): the 14-node working subgraph (`config/`, `pipeline/`, `r/`,
`python/`) and the full 51-node source DAG ported from
causal-shap-target-dags (`analysis/`, `apps/`, `docs/full_dag/`).

## Publishing convention

- Work on `main` unless Andy asks for a branch or pull request. Never
  force-push `main`.
- Commits are authored by the human responsible. Assistant `Co-authored-by`
  trailers are allowed here (relaxed 2026-09-03; Claude is already a listed
  contributor on this repository).
- Commit and push when Andy asks.

## Public-site convention

- The only public site is the single-page Quarto project under `site/`;
  the deploy workflow publishes `site/_site`. The root `index.html` is a
  redirect and stays one.
- The page carries the argument (two playbooks, depth, the six rungs, the
  evidence, the placeholders, the status). Methods, references, provenance,
  decisions, and step results stay in `docs/`.
- Settle a claim in `docs/` before it reaches the site. Use "NASA-topology
  simulation", never "NASA effect". Keep the placeholder rungs marked as
  placeholders until they have results.

## Scientific guardrails

- Keep teaching stress tests separate from source-aligned simulations, and
  the working subgraph separate from the full DAG. Say which one a number
  came from.
- Preserve null and diagnostic results. Do not tune a data-generating
  process to manufacture a stronger story.
- Structural attribution is a prototype input to action selection, never a
  recommendation.
- Rounds two and three of the Step 6 expert loop are a scripted heuristic
  until a human expert has reviewed them; keep that label on every number
  they produce.

## LumaWarp boundary (ADR 008)

- Binaries, credentials, raw logs, the Explain bridge, block-level results,
  and the working paper stay outside git. Their paths are in `.gitignore`.
- The public interface is `python/src/causal_shap_renal/lumawarp_contract.py`
  and `docs/lumawarp/README.md`. Nothing in the repository may describe the
  design-vector block semantics until Lucidity Sciences signs off.

## Private files that live here but are ignored

`docs/methods/` (the pre-LaTeX snapshot, superseded by `manuscript/`) and
`docs/STATUS.md` are gitignored on purpose; do not force-add them. The
manuscript itself is tracked under `manuscript/` (ADR 009); its
introduction is human-written and must never be machine-rewritten.
