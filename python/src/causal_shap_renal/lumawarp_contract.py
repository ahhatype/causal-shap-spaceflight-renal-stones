"""Interface contract for the LumaWarp detector (Steps 5 and 7).

This module is the public half of the detector interface (ADR 008). It fixes
what a detector run consumes and what it must produce, so the pipeline
drivers, the private provider, and the paper's evaluation code agree on one
shape without any of them needing to know how the detector works inside.

Input: an attribution table in the shared Parquet schema (ADR 002,
io_contract.ATTRIBUTION_SCHEMA_COLUMNS), plus the simulated data the model was
fitted on. The detector is run per (method, engine, dag_variant,
iteration_round) group; Step 5 groups come from Step 4's baseline table and
Step 7 groups from Step 6's causal-SHAP tables.

Output: one row per feature per group, with

  - the grouping columns carried through unchanged;
  - one score per detector channel (DETECTOR_CHANNELS), each a z-score across
    features within the group, so channels are comparable and a flag threshold
    means the same thing everywhere;
  - a per-channel flag (score > FLAG_Z) and a composite flag;
  - provenance: run_id, git_sha, timestamp, provider name and version.

The channel names are deliberately generic. The framing memo
(docs/framing/prediction-vs-intervention.md) and the whiteboard notes describe
the detector as a two-channel ("dichromatic") sensitivity filter proposed by
Lexi Pasi: one channel meant to respond to nodes the prediction playbook
under-credits (depth), one that tracks predictive importance itself, plus a
complexity channel. Which internal quantity feeds which channel is the
provider's business and is not described here until Lucidity Sciences signs
off (ADR 008).

Nothing in this file computes a detector score. A provider implements
DetectorProvider outside this repository (or in a gitignored file) and the
Step 5/7 drivers load it by dotted path.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
import pandas as pd

from .io_contract import ATTRIBUTION_SCHEMA_COLUMNS

GROUP_COLUMNS = ["method", "engine", "dag_variant", "iteration_round"]

#: Detector channels. "depth" is the channel the intervention playbook needs:
#: it should rise for nodes whose total effect is real but whose predictive
#: credit has been absorbed by a mediator. "importance" should echo predictive
#: importance and exists so the two can be contrasted. "complexity" is the
#: registry seam already used by apps/causal_shap/complexity.py (PSCI v0).
DETECTOR_CHANNELS = ["depth", "importance", "complexity"]

#: A channel flags a feature when its within-group z-score exceeds this.
FLAG_Z = 1.0

DETECTOR_SCHEMA_COLUMNS = (
    GROUP_COLUMNS
    + ["feature"]
    + [f"{c}_z" for c in DETECTOR_CHANNELS]
    + [f"{c}_flag" for c in DETECTOR_CHANNELS]
    + ["composite_flag", "provider", "provider_version", "run_id", "git_sha", "timestamp"]
)


@runtime_checkable
class DetectorProvider(Protocol):
    """What a detector implementation must offer.

    ``score`` receives one attribution group (all rows share the GROUP_COLUMNS
    values) and the simulated data, and returns a DataFrame with one row per
    feature and one raw score column per channel named exactly as in
    DETECTOR_CHANNELS. Standardization, flagging, and provenance are applied
    by ``finalize_detector_output`` so providers stay small.
    """

    name: str
    version: str

    def score(self, attributions: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame: ...


class NullProvider:
    """Placeholder provider that refuses to score.

    Registered by default so the Step 5/7 drivers fail loudly, with the reason,
    instead of silently producing zeros that a later step could mistake for a
    result.
    """

    name = "null"
    version = "0"

    def score(self, attributions: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError(
            "No LumaWarp detector provider is registered. Steps 5 and 7 are placeholders "
            "until Lucidity Sciences signs off on the interface (ADR 008). Pass "
            "--provider module:Class to the driver to use a provider kept outside this repo."
        )


def validate_attribution_input(df: pd.DataFrame) -> None:
    """Fail early if the input is not in the shared attribution schema."""
    missing = [c for c in ATTRIBUTION_SCHEMA_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"attribution table is missing schema columns: {missing}")
    if df.empty:
        raise ValueError("attribution table is empty")


def zscore_within_group(scores: pd.DataFrame) -> pd.DataFrame:
    """Standardize each channel across features. A constant channel maps to 0."""
    out = scores.copy()
    for channel in DETECTOR_CHANNELS:
        values = out[channel].to_numpy(dtype=float)
        sd = values.std(ddof=0)
        out[f"{channel}_z"] = np.zeros_like(values) if sd == 0 else (values - values.mean()) / sd
    return out


def finalize_detector_output(
    raw: pd.DataFrame,
    group_values: dict,
    provider: DetectorProvider,
    provenance: dict,
) -> pd.DataFrame:
    """Turn a provider's raw per-feature scores into the contract's output rows."""
    required = ["feature", *DETECTOR_CHANNELS]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(f"provider {provider.name} returned no column(s) {missing}")
    if raw["feature"].duplicated().any():
        raise ValueError(f"provider {provider.name} returned duplicate feature rows")

    out = zscore_within_group(raw[required])
    for channel in DETECTOR_CHANNELS:
        out[f"{channel}_flag"] = out[f"{channel}_z"] > FLAG_Z
    # The composite is the depth channel alone. Averaging channels that
    # behave differently discards the finding the detector is for.
    out["composite_flag"] = out["depth_flag"]
    for column in GROUP_COLUMNS:
        out[column] = group_values[column]
    out["provider"] = provider.name
    out["provider_version"] = provider.version
    for key in ("run_id", "git_sha", "timestamp"):
        out[key] = provenance[key]
    return out[DETECTOR_SCHEMA_COLUMNS].reset_index(drop=True)


def validate_detector_output(df: pd.DataFrame) -> None:
    """Check a detector table against the contract before anything reads it."""
    missing = [c for c in DETECTOR_SCHEMA_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"detector table is missing columns: {missing}")
    if df.duplicated(subset=GROUP_COLUMNS + ["feature"]).any():
        raise ValueError("detector table has duplicate (group, feature) rows")
    for channel in DETECTOR_CHANNELS:
        if not np.isfinite(df[f"{channel}_z"].to_numpy(dtype=float)).all():
            raise ValueError(f"detector channel {channel}_z has non-finite values")


def load_provider(spec: str | None) -> DetectorProvider:
    """Resolve ``module:Class`` to a provider instance; default is NullProvider."""
    if not spec:
        return NullProvider()
    module_name, _, class_name = spec.partition(":")
    if not module_name or not class_name:
        raise ValueError("provider spec must look like package.module:ClassName")
    import importlib

    provider = getattr(importlib.import_module(module_name), class_name)()
    if not isinstance(provider, DetectorProvider):
        raise TypeError(f"{spec} does not implement DetectorProvider")
    return provider
