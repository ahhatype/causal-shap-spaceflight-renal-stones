"""Scientific and support checks for the optional ConfoundingSHAP pilot."""

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("shapiq", reason="Optional ConfoundingSHAP comparison environment")
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "confoundingshap_comparison", ROOT / "analysis" / "confoundingshap_comparison.py"
)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


def test_instrument_can_receive_negative_bias_attribution():
    rows, game = pilot.oracle_case(randomized=False)
    values = {row["feature"]: row for row in rows}
    # An instrument amplifies residual confounding before C is adjusted for.
    assert values["instrument_Z"]["confounding_signed"] == pytest.approx(-103 / 5280)
    assert values["confounder_C"]["confounding_signed"] == pytest.approx(1753 / 5280)
    assert values["effect_modifier_H"]["confounding_signed"] == pytest.approx(0, abs=1e-12)
    assert values["outcome_only_P"]["confounding_signed"] == pytest.approx(0, abs=1e-12)
    assert -game[0] == pytest.approx(5 / 16)


def test_randomization_removes_bias_without_removing_heterogeneity():
    rows, game = pilot.oracle_case(randomized=True)
    np.testing.assert_allclose(game, 0, atol=1e-12)
    np.testing.assert_allclose([r["confounding_signed"] for r in rows], 0, atol=1e-12)
    values = {row["feature"]: row for row in rows}
    assert values["effect_modifier_H"]["cate_conditional_shap_mean_abs"] == pytest.approx(0.6)
    assert values["confounder_C"]["control_outcome_conditional_shap_mean_abs"] == pytest.approx(0.5)
    assert values["outcome_only_P"]["control_outcome_conditional_shap_mean_abs"] == pytest.approx(0.35)


def test_renal_adjustment_set_is_reviewed_against_frozen_graph():
    # All sixteen candidate sets are checked: precisely those containing
    # Medical Prevention Capability satisfy the backdoor criterion here.
    pilot.validate_renal_design()


def test_cell_predictions_preserve_query_order():
    train = pd.DataFrame({"x": [1, 0, 1, 0], "a": [0, 1, 1, 0]})
    query = pd.DataFrame({"x": [0, 1, 0, 1], "a": [0, 1, 1, 0]})
    result = pilot.cell_predictions(train, [10, 1, 11, 0], query, ["x", "a"])
    np.testing.assert_array_equal(result, [0, 11, 1, 10])


def test_cell_predictions_refuse_unsupported_treatment_cell():
    train = pd.DataFrame({"x": [0, 0, 1], "a": [0, 1, 0]})
    query = pd.DataFrame({"x": [1], "a": [1]})
    with pytest.raises(ValueError, match="Unsupported covariate/treatment cell"):
        pilot.cell_predictions(train, [0, 1, 0], query, ["x", "a"])


def test_local_global_identity_uses_signed_not_absolute_average():
    # A prediction game whose local allocations have opposite signs.
    # Its population-average game is zero, but its mean absolute credit is not.
    states = np.array([[0], [1]])
    weights = np.array([0.5, 0.5])
    values = np.array([-2.0, 2.0])
    local_games = np.array([
        pilot.projection(states, weights, values, subset) for subset in pilot.masks(1)
    ])
    local = np.array([pilot.exact_shapley(local_games[:, i]) for i in range(2)])
    global_phi = pilot.package_shapley(local_games @ weights)
    np.testing.assert_allclose(global_phi, weights @ local, atol=1e-12)
    np.testing.assert_allclose(global_phi, 0, atol=1e-12)
    np.testing.assert_allclose(weights @ np.abs(local), [2.0], atol=1e-12)
