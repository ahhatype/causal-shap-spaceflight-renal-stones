"""Step 5: LumaWarp detector pass over Step 4's baseline attributions.

Placeholder driver (ADR 008). It validates the inputs, declares the output
location and schema, and runs whichever detector provider is registered.
The default provider refuses to score, so running this without --provider
stops with an explanation rather than writing a table of zeros.

    python pipeline/step05_lumawarp_detector.py
    python pipeline/step05_lumawarp_detector.py --provider lw_private.provider:LumaWarpProvider

Reads:  results/attributions/step04_baseline_shap.parquet
        data/simulated/renal_stone_simulated.parquet
Writes: results/detector/step05_lumawarp_detector.parquet
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

from causal_shap_renal.io_contract import attribution_provenance, read_simulated_data
from causal_shap_renal.lumawarp_contract import (
    GROUP_COLUMNS,
    NullProvider,
    finalize_detector_output,
    load_provider,
    validate_attribution_input,
    validate_detector_output,
)

REPO = Path(__file__).resolve().parents[1]


def run_detector(attribution_path: Path, data_path: Path, output_path: Path, provider_spec: str | None) -> pd.DataFrame:
    # Resolve the provider before touching any file so the placeholder state
    # (no provider registered) is reported ahead of any missing-input error.
    provider = load_provider(provider_spec)
    if isinstance(provider, NullProvider):
        provider.score(pd.DataFrame(), pd.DataFrame())  # raises NotImplementedError with the ADR 008 message
    for path, label in ((attribution_path, "attribution table"), (data_path, "simulated data")):
        if not Path(path).exists():
            raise FileNotFoundError(f"{label} not found at {path}; run the earlier pipeline steps first (see Makefile)")
    attributions = pd.read_parquet(attribution_path)
    validate_attribution_input(attributions)
    data = read_simulated_data(str(data_path))
    provenance = attribution_provenance()

    tables = []
    for group_values, group in attributions.groupby(GROUP_COLUMNS, sort=True):
        raw = provider.score(group.reset_index(drop=True), data)
        tables.append(finalize_detector_output(raw, dict(zip(GROUP_COLUMNS, group_values)), provider, provenance))
    out = pd.concat(tables, ignore_index=True)
    validate_detector_output(out)
    os.makedirs(output_path.parent, exist_ok=True)
    out.to_parquet(output_path, index=False)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", default=None, help="module:Class implementing DetectorProvider")
    parser.add_argument("--attributions", default=REPO / "results/attributions/step04_baseline_shap.parquet", type=Path)
    parser.add_argument("--data", default=REPO / "data/simulated/renal_stone_simulated.parquet", type=Path)
    parser.add_argument("--output", default=REPO / "results/detector/step05_lumawarp_detector.parquet", type=Path)
    args = parser.parse_args(argv)
    try:
        out = run_detector(args.attributions, args.data, args.output, args.provider)
    except NotImplementedError as exc:
        print(f"step05: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"step05: {exc}", file=sys.stderr)
        return 1
    print(f"step05: wrote {len(out)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
