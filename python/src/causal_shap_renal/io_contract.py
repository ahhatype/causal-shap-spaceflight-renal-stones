"""Read/write helpers for the R <-> Python interchange contract.

See docs/decisions/002-data-interchange-contract.md for the schema this
module implements. Mirrors r/R/io_contract.R - keep the two in sync by hand.
"""

from __future__ import annotations

import os
import subprocess
import uuid
from datetime import datetime, timezone

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


def attribution_provenance() -> dict:
    """Provenance columns for an attribution table: run_id (uuid4),
    git_sha (short git SHA, "unknown" if git isn't available), timestamp
    (UTC ISO 8601). One call per driver script run, attached to every row
    that run produces - was previously duplicated inline in
    attribution_baseline.py's _git_sha()/uuid.uuid4() calls; centralized
    here for the Step 6 Python drivers (step06b/step06c) too. Mirrors
    r/R/io_contract.R's attribution_provenance().
    """
    try:
        git_sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        git_sha = "unknown"
    return {
        "run_id": str(uuid.uuid4()),
        "git_sha": git_sha,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def write_attributions(df: pd.DataFrame, path: str) -> None:
    """Write an attribution table to Parquet in ATTRIBUTION_SCHEMA_COLUMNS order."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df[ATTRIBUTION_SCHEMA_COLUMNS].to_parquet(path, index=False)
