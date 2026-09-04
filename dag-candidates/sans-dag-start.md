# SANS DAG - Provisional Start

> Ported from the Box project folder on 2026-09-04 (Andy Wilson's July 2026 notes). Paths and links inside refer to the Target DAGs repository as it stood then; the canonical implementations now live under `analysis/` and `apps/` in this hub.

Status: provisional. Do not use for analysis until Robert provides or confirms the causal structure.

## Why This DAG

Robert identified SANS as the higher-interest option. He noted concern around a series of outcomes including globe flattening/vision changes, chorioretinal folds, vascular edema at the back of the eye, and cotton wool spots.

## Candidate Nodes

- `spaceflight_exposure`
- `microgravity`
- `cephalad_fluid_shift`
- `intracranial_pressure_or_related_pressure_state`
- `ocular_pressure_or_globe_shape_change`
- `optic_disc_or_retinal_changes`
- `globe_flattening`
- `chorioretinal_folds`
- `vascular_edema`
- `cotton_wool_spots`
- `vision_change`
- `task_readiness_or_mission_impact`

## Candidate Edge Sketch

```csv
from,to
spaceflight_exposure,microgravity
microgravity,cephalad_fluid_shift
cephalad_fluid_shift,intracranial_pressure_or_related_pressure_state
intracranial_pressure_or_related_pressure_state,ocular_pressure_or_globe_shape_change
ocular_pressure_or_globe_shape_change,globe_flattening
ocular_pressure_or_globe_shape_change,chorioretinal_folds
ocular_pressure_or_globe_shape_change,vascular_edema
optic_disc_or_retinal_changes,cotton_wool_spots
globe_flattening,vision_change
chorioretinal_folds,vision_change
vascular_edema,vision_change
cotton_wool_spots,vision_change
vision_change,task_readiness_or_mission_impact
```

## Simulation Notes

This DAG should stress-test attribution because several clinical findings may be strong predictors while sitting downstream of earlier causal mechanisms. That makes it useful for demonstrating ordinary SHAP mediator/proxy inflation versus DAG-aware attribution.

## Robert Confirmation Needed

- Actual HSRB SANS node list and edge structure.
- Whether pressure-state language is acceptable or should be replaced with more precise SANS mechanisms.
- Which ocular findings are causes, mediators, parallel outcomes, or diagnostic indicators.
- Which nodes are actionable intervention targets.
- Which endpoint should be modeled: any SANS finding, vision change, or mission/task impact.
