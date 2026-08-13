"""Read/write helpers for the R <-> Python interchange contract.

See docs/decisions/002-data-interchange-contract.md for the schema this
module implements. Mirrors r/R/io_contract.R - keep the two in sync by hand.
"""

from __future__ import annotations

import os

import pandas as pd
import yaml

ATTRIBUTION_SCHEMA_COLUMNS = [
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


def read_dag_spec(path: str) -> dict:
    """Load config/dag_spec.yaml."""
    with open(path) as f:
        return yaml.safe_load(f)


def read_simulated_data(path: str) -> pd.DataFrame:
    """Load a Step 3 simcausal output Parquet file."""
    return pd.read_parquet(path)


def read_ground_truth(path: str) -> pd.DataFrame:
    """Load a Step 4a (r/R/ground_truth.R) DAG-derived ground-truth Parquet file."""
    return pd.read_parquet(path)


def model_features(dag_spec: dict) -> list[str]:
    """Node ids to use as model input features for attribution models (Step 4+):
    every node in config/dag_spec.yaml except the outcome (type: outcome).
    Single source of truth so the feature list is never hand-duplicated
    across driver scripts or languages - see model_features() in
    r/R/dag_utils.R for the R mirror.
    """
    return [n["id"] for n in dag_spec["nodes"] if n.get("type") != "outcome"]


def write_attributions(df: pd.DataFrame, path: str) -> None:
    """Write an attribution table to Parquet in ATTRIBUTION_SCHEMA_COLUMNS order."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df[ATTRIBUTION_SCHEMA_COLUMNS].to_parquet(path, index=False)
