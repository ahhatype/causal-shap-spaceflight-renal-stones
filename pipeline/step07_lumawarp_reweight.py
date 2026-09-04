"""Step 7: LumaWarp detector pass over Step 6's causal-SHAP attributions.

Same placeholder driver as Step 5 (ADR 008), pointed at the Step 6 tables.
Every Step 6 method writes the shared attribution schema, so the detector
runs per (method, engine, dag_variant, iteration_round) group across all of
them at once and the output can be joined back to docs/step06_results.md's
tables by those keys.

    python pipeline/step07_lumawarp_reweight.py
    python pipeline/step07_lumawarp_reweight.py --provider lw_private.provider:LumaWarpProvider

Reads:  results/attributions/step06a_causal_shapley_asv.parquet
        results/attributions/step06b_shapley_flow.parquet
        results/attributions/step06c_causal_shap_ng_et_al.parquet
        data/simulated/renal_stone_simulated.parquet
Writes: results/detector/step07_lumawarp_reweight.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from step05_lumawarp_detector import REPO, run_detector

STEP06_TABLES = [
    "step06a_causal_shapley_asv.parquet",
    "step06b_shapley_flow.parquet",
    "step06c_causal_shap_ng_et_al.parquet",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", default=None, help="module:Class implementing DetectorProvider")
    parser.add_argument("--data", default=REPO / "data/simulated/renal_stone_simulated.parquet", type=Path)
    parser.add_argument("--output", default=REPO / "results/detector/step07_lumawarp_reweight.parquet", type=Path)
    args = parser.parse_args(argv)

    present = [REPO / "results/attributions" / t for t in STEP06_TABLES if (REPO / "results/attributions" / t).exists()]
    if not present:
        print("step07: no Step 6 attribution tables found; run `make step06` first", file=sys.stderr)
        return 1
    combined = args.output.parent / "_step06_combined_input.parquet"
    combined.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([pd.read_parquet(p) for p in present], ignore_index=True).to_parquet(combined, index=False)
    try:
        out = run_detector(combined, args.data, args.output, args.provider)
    except NotImplementedError as exc:
        print(f"step07: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"step07: {exc}", file=sys.stderr)
        return 1
    finally:
        combined.unlink(missing_ok=True)
    print(f"step07: wrote {len(out)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
