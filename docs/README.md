# Documentation map

One hub, two lines of work (ADR 007). Start with the framing memo if you want
the argument, with `STATUS.md` if you want to know what has run.

## The argument

| file | contents |
| --- | --- |
| [`framing/prediction-vs-intervention.md`](framing/prediction-vs-intervention.md) | The reframing: two goals, two playbooks; why the intervention playbook casts a wider net and still prunes; deeper nodes wash out; the linearity assumption; detector and filter; experiments E1 to E3 |
| [`notes/2026-09-01-whiteboard-transcription.md`](notes/2026-09-01-whiteboard-transcription.md) | Transcription of the 1 September 2026 notes the memo is built from |
| [`references/claims-to-citations.md`](references/claims-to-citations.md) | Verified citations for the reframing's claims, with what each supports and what is unsupported |
| [`lumawarp/README.md`](lumawarp/README.md) | Placeholder outline for the expanded LumaWarp detector treatment and the dichromatic sensitivity filter |

## The working subgraph (14 nodes; `config/`, `pipeline/`, `r/`, `python/`)

| file | contents |
| --- | --- |
| `STATUS.md` (gitignored) and [`../config/pipeline_status.yaml`](../config/pipeline_status.yaml) | Step-by-step status against the 13-step protocol |
| [`step03_simulation_review.md`](step03_simulation_review.md) | Coefficient recovery and marginals for the simulated data |
| [`step04_results.md`](step04_results.md) | Baseline SHAP, five pairings, the mediator inversions |
| [`step06_results.md`](step06_results.md) | Three causal SHAP methods over three scripted revision rounds; PC leaving the outcome disconnected |
| [`dag_README.md`](dag_README.md), [`renal_stone_working_subgraph.txt`](renal_stone_working_subgraph.txt) | The working DAG in DAGitty syntax |
| [`provenance.md`](provenance.md) | DAG source and coefficient sourcing for the working subgraph |
| `methods/` (gitignored) | The human-written intro and methods draft. Never machine-rewrite it |

## The full source DAG (51 nodes; `analysis/`, `apps/`)

| file | contents |
| --- | --- |
| [`full_dag/RESEARCH_RECORD.md`](full_dag/RESEARCH_RECORD.md) | Narrative, methods, frozen results (ordering-only null, structural prototype), limitations, roadmap |
| [`full_dag/PROVENANCE_AND_REFERENCES.md`](full_dag/PROVENANCE_AND_REFERENCES.md) | DAG and data lineage, the Reynolds handoff, ACIC lineage, annotated references and claim-to-citation map |
| [`full_dag/REPRODUCIBILITY_AND_SITE.md`](full_dag/REPRODUCIBILITY_AND_SITE.md) | Environments, build and validation commands, site content discipline (paths updated for this hub) |

## Decisions

| ADR | decision |
| --- | --- |
| [001](decisions/001-two-language-repo.md) | R and Python side by side, exchanging files only |
| [002](decisions/002-data-interchange-contract.md) | YAML and Parquet interchange schema |
| [003](decisions/003-lumawarp-excluded.md) | LumaWarp excluded (superseded by 008) |
| [004](decisions/004-xgboost-primary-engine.md) | XGBoost as the primary engine |
| [005](decisions/005-superlearner-deferred.md) | SuperLearner deferred |
| [006](decisions/006-shapr-heskes-blocked.md) | shapr's Heskes path blocked |
| [007](decisions/007-target-dags-consolidation.md) | causal-shap-target-dags consolidated into this hub |
| [008](decisions/008-lumawarp-detector-placeholders.md) | LumaWarp detector placeholders live here; runtime and bridge stay external |

Documentation rule, carried over from Target DAGs: every substantive result
states its estimand and intervention semantics, graph and data regime,
evidence status (teaching, matched comparison, prototype), computational
budget, and uncertainty procedure. Public claims settle here before reaching
the site.
