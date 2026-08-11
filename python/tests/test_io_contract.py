"""Placeholder test. Replace once io_contract.py has a real implementation."""

from causal_shap_renal.io_contract import ATTRIBUTION_SCHEMA_COLUMNS


def test_attribution_schema_columns_defined():
    assert ATTRIBUTION_SCHEMA_COLUMNS == [
        "method",
        "engine",
        "dag_variant",
        "iteration_round",
        "feature",
        "attribution_value",
        "run_id",
        "git_sha",
        "timestamp",
    ]
