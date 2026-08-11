"""Read/write helpers for the R <-> Python interchange contract.

See docs/decisions/002-data-interchange-contract.md for the schema this
module implements. Mirrors r/R/io_contract.R - keep the two in sync by hand.

TODO: implement once Step 3 (data generation) produces its first Parquet
output for this module to read.
"""

from __future__ import annotations

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
    """Load config/dag_spec.yaml. TODO: implement."""
    raise NotImplementedError


def read_simulated_data(path: str):
    """Load a Step 3 simcausal output Parquet file. TODO: implement."""
    raise NotImplementedError


def write_attributions(df, path: str) -> None:
    """Write an attribution table to Parquet in ATTRIBUTION_SCHEMA_COLUMNS. TODO: implement."""
    raise NotImplementedError
