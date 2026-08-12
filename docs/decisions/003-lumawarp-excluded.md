# ADR 003: LumaWarp (Steps 5 and 7) excluded from this repo

## Status
Accepted

## Decision
Steps 5 and 7 (complexity-aware reweighting, built on Lucidity Sciences' LumaWarp tool and its PSCI complexity score) are not built in this repo. They are tracked as external, owned by Lexi Pasi and Andy Wilson, and will run in a separate repo (due to the proprietary nature of the tool).

## Context
Per the methods doc, both steps are provisional at the time of writing: the interface between the complexity-scoring tool and the attribution outputs from Steps 4 and 6 has not been specified by the tool's developers, and the tool itself is not yet integrated into any pipeline. Building scaffolding for an unspecified interface would just create churn once the real interface lands.

## Consequences
- `pipeline/_deferred/` holds a stub only, no real code, pointing back to this ADR.
- `docs/STATUS.md` and `config/pipeline_status.yaml` mark Steps 5 and 7 as `deferred_external`.
- The README's Protocol section lists Steps 5 and 7 in their place in the sequence (so the numbering stays legible against the methods doc) but flags them as happening in the other repo.
- When the LumaWarp interface is finalized, this repo's Steps 4 and 6 outputs (in the shared attribution Parquet schema, see ADR 002) are the contract the other repo should consume.
