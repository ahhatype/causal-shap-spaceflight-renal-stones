# Renal Stone DAG - Provisional Start

> Ported from the Box project folder on 2026-09-04 (Andy Wilson's July 2026 notes). Paths and links inside refer to the Target DAGs repository as it stood then; the canonical implementations now live under `analysis/` and `apps/` in this hub.

Status: provisional. Must be corrected or approved by Robert before analysis.

## Why This DAG

Robert identified renal stone formation as the better-supported option, with existing work and new Spaceflight Epidemiology Analysis Working Group activity. The Systems Medicine chapter attachment also includes a high-level renal stone path.

## Candidate Nodes

- `spaceflight_exposure`
- `altered_gravity`
- `bone_unloading`
- `bone_remodeling_imbalance`
- `serum_calcium`
- `urine_calcium`
- `urine_chemistry`
- `hydration_status`
- `urinary_stasis`
- `renal_stone_formation`
- `renal_colic_or_medical_event`
- `mission_or_task_impact`

## Candidate Edges

```csv
from,to
spaceflight_exposure,altered_gravity
altered_gravity,bone_unloading
bone_unloading,bone_remodeling_imbalance
bone_remodeling_imbalance,serum_calcium
serum_calcium,urine_calcium
urine_calcium,urine_chemistry
hydration_status,urine_chemistry
hydration_status,urinary_stasis
urine_chemistry,renal_stone_formation
urinary_stasis,renal_stone_formation
renal_stone_formation,renal_colic_or_medical_event
renal_colic_or_medical_event,mission_or_task_impact
```

## Simulation Notes

This DAG is well suited for the Causal SHAP demonstration because ordinary SHAP may give high credit to measured mediators such as urine chemistry, while a causal attribution/risk-management view may prioritize upstream modifiable targets such as hydration or countermeasures for bone remodeling.

## Robert Confirmation Needed

- Which nodes are in the official or preferred renal stone DAG?
- Should `altered_gravity` and `spaceflight_exposure` be separate nodes?
- Which nodes are actionable intervention targets versus non-actionable hazards?
- Are hydration and urinary stasis in the actual DAG?
- What outcome should be modeled: stone formation, clinical event, or mission impact?
