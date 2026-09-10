# Documentation map

Start with the [central workflow](playbook/central-workflow.md) for the
study's argument or the [reproducibility guide](../REPRODUCIBILITY.md) to run
the examples and research code.

## The argument

| file | contents |
| --- | --- |
| [`playbook/protocol.md`](playbook/protocol.md) | 13-step protocol, implementation paths and status |
| [`playbook/central-workflow.md`](playbook/central-workflow.md) | Central workflow, exact classroom calculation, simulation mapping and limits |
| [`classroom/README.md`](classroom/README.md) | Educator guide, worksheet, interactive lab and Python examples |
| [`../ORIENTATION.md`](../ORIENTATION.md) | Project orientation: the premise, workflow, code, results and next steps |
| [`framing/prediction-vs-intervention.md`](framing/prediction-vs-intervention.md) | Historical framing proposal and planned experiments |
| [`notes/2026-09-01-whiteboard-transcription.md`](notes/2026-09-01-whiteboard-transcription.md) | Transcription of the 1 September 2026 notes the memo is built from |
| [`references/claims-to-citations.md`](references/claims-to-citations.md) | Verified citations for the reframing's claims, with what each supports and what is unsupported |
| [`lumawarp/README.md`](lumawarp/README.md) | Placeholder outline for the expanded LumaWarp detector treatment and the dichromatic sensitivity filter |
| [`playbook/README.md`](playbook/README.md) | Framework and protocol mappings; [`playbook/dag-harvest-protocol.md`](playbook/dag-harvest-protocol.md) is rung 0 |
| [`references/manuscript-references.md`](references/manuscript-references.md) | Venue, NASA DAG-program references, and the epidemiology framing citations |

## The working subgraph (14 nodes; `config/`, `pipeline/`, `r/`, `python/`)

| file | contents |
| --- | --- |
| [`../config/pipeline_status.yaml`](../config/pipeline_status.yaml) | Step-by-step status against the 13-step protocol |
| [`step03_simulation_review.md`](step03_simulation_review.md) | Coefficient recovery and marginals for the simulated data |
| [`step04_results.md`](step04_results.md) | Baseline SHAP, five pairings, the mediator inversions |
| [`step06_results.md`](step06_results.md) | Three causal SHAP methods over three scripted revision rounds; PC leaving the outcome disconnected |
| [`dag_README.md`](dag_README.md), [`renal_stone_working_subgraph.txt`](renal_stone_working_subgraph.txt) | The working DAG in DAGitty syntax |
| [`provenance.md`](provenance.md) | DAG source and coefficient sourcing for the working subgraph |
| [`../dag-candidates/`](../dag-candidates/) | Core-graph CSVs plus the July 2026 harvest notes and provisional renal and SANS edge lists |

## The full source DAG (51 nodes; `analysis/`, `apps/`)

| file | contents |
| --- | --- |
| [`full_dag/RESEARCH_RECORD.md`](full_dag/RESEARCH_RECORD.md) | Narrative, methods, frozen results (ordering-only null, structural prototype), limitations, roadmap |
| [`full_dag/PROVENANCE_AND_REFERENCES.md`](full_dag/PROVENANCE_AND_REFERENCES.md) | DAG and data lineage, the Reynolds handoff, ACIC lineage, annotated references and claim-to-citation map |
| [`full_dag/REPRODUCIBILITY_AND_SITE.md`](full_dag/REPRODUCIBILITY_AND_SITE.md) | Environments, build and validation commands |
| [`full_dag/proximity-bias-metrics.md`](full_dag/proximity-bias-metrics.md) | The 2026-07-10 proposal defining directed target distance, PBI, POA, and the distance-concentration curve; now implemented in `causal_shap_renal.evaluation` |

## Technical and reproducibility companion

- [Reproduction routes and commands](../REPRODUCIBILITY.md).
- [Do-Shapley math tutorial and benchmark targets](technical/do-shapley.md).
- [Path length, causal credit, response shape and splines](technical/path-length-and-response-shape.md).
- [Technical BibTeX](references/technical-companion.bib).

## Repository decisions

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
| [010](decisions/010-repository-companion.md) | Repository consolidation and presentation archive |
| [009](decisions/009-single-home.md) | One home for the project, including the manuscript; Box is exchange only |
