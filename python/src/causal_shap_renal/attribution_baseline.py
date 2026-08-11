"""Step 4: baseline attribution with standard (causality-blind) SHAP.

Explainer x model pairings, per docs/methods Step 4 spec:
  TreeExplainer  + Random Forest   (feature_perturbation="interventional")
  TreeExplainer  + XGBoost         (feature_perturbation="interventional")
  LinearExplainer + linear/logistic regression (masker = feature covariance)
  KernelExplainer + SuperLearner   (black box)
  PermutationExplainer + SuperLearner (black box)

Full breadth (all five) runs only at this step. Steps 6+ narrow to
TreeExplainer+XGBoost and KernelExplainer+SuperLearner.

TODO: implement once Step 3 (data generation) has produced simulated data.
"""

from __future__ import annotations


def run_baseline_shap(data, dag_spec) -> None:
    raise NotImplementedError
