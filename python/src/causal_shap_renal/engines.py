"""Predictive-engine resolution for Step 6 driver scripts.

A single named switch so each Step 6 driver script asks for "the primary
engine" or "the secondary-check engine" for a given method by name, resolved
from config/model_engines.yaml, rather than hardcoding a specific model call
inline. See docs/decisions/004-xgboost-primary-engine.md for why XGBoost is
the current default and why SuperLearner isn't used here (Step 4's own
KernelExplainer/PermutationExplainer + SuperLearner pairing is untouched by
this module). Mirrors r/R/engines.R - keep the two in sync by hand, same
convention as io_contract.py.
"""

from __future__ import annotations

import yaml


def read_engine_config(path: str = "../config/model_engines.yaml") -> dict:
    """Read config/model_engines.yaml."""
    with open(path) as f:
        return yaml.safe_load(f)


def engine_for_method(method_id: str, config: dict | None = None) -> dict:
    """Look up the engine assignment for a given Step 6 method id (e.g.
    "causal_shapley_values", "shapley_flow", "asv", "causal_shap_ng_et_al"),
    as declared in config/model_engines.yaml's methods list.
    """
    config = config if config is not None else read_engine_config()
    matches = [m for m in config["methods"] if m["method"] == method_id]
    if not matches:
        raise ValueError(
            f"No engine entry for method '{method_id}' in config/model_engines.yaml"
        )
    return matches[0]


def fit_engine(engine_name: str, X, y, **kwargs):
    """Fit a named engine on (X, y) and return a fitted model object.

    Supported engine names: "xgboost", "random_forest". "superlearner" is
    deliberately not implemented here - see engines.superlearner.note in
    config/model_engines.yaml for why it isn't used in Step 6.

    TODO: _fit_xgboost() / _fit_random_forest() are stubs. Wire up the
    actual model-fitting calls (xgboost.XGBClassifier/XGBRegressor,
    sklearn.ensemble.RandomForestClassifier/Regressor) once a Step 6 driver
    script (step06b/step06c) is implemented and has real hyperparameter
    choices to make - only the resolution/dispatch layer in this module is
    meant to be usable now.
    """
    if engine_name == "xgboost":
        return _fit_xgboost(X, y, **kwargs)
    if engine_name == "random_forest":
        return _fit_random_forest(X, y, **kwargs)
    if engine_name == "superlearner":
        raise NotImplementedError(
            "Engine 'superlearner' is not used in Step 6 - see "
            "engines.superlearner.note in config/model_engines.yaml and "
            "docs/decisions/004-xgboost-primary-engine.md"
        )
    raise NotImplementedError(
        f"Unsupported engine: '{engine_name}'. See config/model_engines.yaml "
        "for the currently supported set."
    )


def _fit_xgboost(X, y, **kwargs):
    raise NotImplementedError(
        "wire up xgboost.XGBClassifier/XGBRegressor here when a Step 6 driver script is built"
    )


def _fit_random_forest(X, y, **kwargs):
    raise NotImplementedError(
        "wire up sklearn.ensemble.RandomForestClassifier/Regressor here when a Step 6 driver script is built"
    )
