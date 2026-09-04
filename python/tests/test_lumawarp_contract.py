"""Tests for the public LumaWarp detector contract (ADR 008)."""

import numpy as np
import pandas as pd
import pytest

from causal_shap_renal.io_contract import ATTRIBUTION_SCHEMA_COLUMNS
from causal_shap_renal.lumawarp_contract import (
    DETECTOR_CHANNELS,
    DETECTOR_SCHEMA_COLUMNS,
    DetectorProvider,
    NullProvider,
    finalize_detector_output,
    load_provider,
    validate_attribution_input,
    validate_detector_output,
)

PROVENANCE = {"run_id": "r", "git_sha": "abc", "timestamp": "2026-09-03T00:00:00+00:00"}
GROUP = {"method": "tree_shap", "engine": "xgboost", "dag_variant": "v14", "iteration_round": 1}


class ConstantDepthProvider:
    name = "constant"
    version = "test"

    def score(self, attributions, data):
        features = list(attributions["feature"])
        return pd.DataFrame(
            {
                "feature": features,
                "depth": np.arange(len(features), dtype=float),
                "importance": attributions["attribution_value"].to_numpy(dtype=float),
                "complexity": 1.0,
            }
        )


def _attributions():
    rows = [{**GROUP, "feature": f, "attribution_value": v, **PROVENANCE} for f, v in
            [("a", 0.1), ("b", 0.5), ("c", 0.9), ("d", 0.2)]]
    return pd.DataFrame(rows)[ATTRIBUTION_SCHEMA_COLUMNS]


def test_null_provider_refuses_to_score():
    with pytest.raises(NotImplementedError):
        NullProvider().score(_attributions(), pd.DataFrame())


def test_validate_attribution_input_rejects_missing_columns():
    with pytest.raises(ValueError):
        validate_attribution_input(pd.DataFrame({"feature": ["a"]}))


def test_finalize_output_matches_schema_and_flags():
    provider = ConstantDepthProvider()
    assert isinstance(provider, DetectorProvider)
    raw = provider.score(_attributions(), pd.DataFrame())
    out = finalize_detector_output(raw, GROUP, provider, PROVENANCE)
    assert list(out.columns) == DETECTOR_SCHEMA_COLUMNS
    validate_detector_output(out)
    # a constant channel standardizes to 0 and never flags
    assert (out["complexity_z"] == 0).all() and not out["complexity_flag"].any()
    # z-scores have mean 0 within the group
    for channel in DETECTOR_CHANNELS:
        assert abs(out[f"{channel}_z"].mean()) < 1e-12
    # the composite is the depth channel alone
    assert (out["composite_flag"] == out["depth_flag"]).all()
    assert out["depth_flag"].sum() == 1


def test_duplicate_features_rejected():
    raw = pd.DataFrame({"feature": ["a", "a"], "depth": [1.0, 2.0], "importance": [0, 0], "complexity": [0, 0]})
    with pytest.raises(ValueError):
        finalize_detector_output(raw, GROUP, ConstantDepthProvider(), PROVENANCE)


def test_load_provider_default_and_bad_spec():
    assert isinstance(load_provider(None), NullProvider)
    with pytest.raises(ValueError):
        load_provider("no-colon")
