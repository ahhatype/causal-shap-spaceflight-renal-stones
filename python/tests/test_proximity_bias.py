"""Proximity-bias metrics (docs/full_dag/proximity-bias-metrics.md)."""

import pytest

from causal_shap_renal.evaluation import (
    directed_distances,
    proximal_mass,
    proximal_over_attribution_area,
    proximity_bias_index,
)

# A -> B -> C -> Y with a side node Z that is not an ancestor of Y.
EDGES = [("A", "B"), ("B", "C"), ("C", "Y"), ("Y", "Z")]


def test_directed_distances_omit_non_ancestors():
    d = directed_distances(EDGES, "Y")
    assert d == {"C": 1, "B": 2, "A": 3}
    assert directed_distances([{"from": "C", "to": "Y"}], "Y") == {"C": 1}


def test_pbi_sign_and_zero():
    d = directed_distances(EDGES, "Y")
    truth = {"A": 1.0, "B": 1.0, "C": 1.0}          # mean depth 2
    proximal = {"A": 0.0, "B": 0.0, "C": 1.0}       # mean depth 1
    upstream = {"A": 1.0, "B": 0.0, "C": 0.0}       # mean depth 3
    assert proximity_bias_index(proximal, truth, d) == pytest.approx(1.0)
    assert proximity_bias_index(upstream, truth, d) == pytest.approx(-1.0)
    assert proximity_bias_index(truth, truth, d) == pytest.approx(0.0)


def test_poa_positive_when_mass_sits_near_outcome():
    d = directed_distances(EDGES, "Y")
    truth = {"A": 1.0, "B": 1.0, "C": 1.0}
    proximal = {"A": 0.0, "B": 0.0, "C": 1.0}
    # K = 3, so k = 1, 2: C_p = (1, 1), C_q = (1/3, 2/3); mean difference = 0.5
    assert proximal_over_attribution_area(proximal, truth, d) == pytest.approx(0.5)
    assert proximal_over_attribution_area(truth, truth, d) == pytest.approx(0.0)


def test_proximal_mass_ignores_off_path_and_uses_abs():
    d = directed_distances(EDGES, "Y")
    attr = {"A": -1.0, "B": 1.0, "C": 2.0, "Z": 100.0}
    assert proximal_mass(attr, d, k=2) == pytest.approx(0.75)
