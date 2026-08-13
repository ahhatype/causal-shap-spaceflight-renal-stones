"""Step 4: baseline attribution with standard SHAP.
See docs/methods and python/src/causal_shap_renal/attribution_baseline.py.

Loads data/simulated/ output (written by pipeline/step03_simulate_data.R),
runs the five explainer x model pairings, writes to results/attributions/.
Run via `make step04` or `cd python && uv run python ../pipeline/step04_baseline_shap.py`.
"""

from causal_shap_renal.attribution_baseline import run_baseline_shap
from causal_shap_renal.io_contract import read_dag_spec, read_simulated_data, write_attributions

if __name__ == "__main__":
    data = read_simulated_data("../data/simulated/renal_stone_simulated.parquet")
    dag_spec = read_dag_spec("../config/dag_spec.yaml")
    attributions = run_baseline_shap(data, dag_spec)
    write_attributions(attributions, "../results/attributions/step04_baseline_shap.parquet")
    print(f"Wrote {len(attributions)} rows to results/attributions/step04_baseline_shap.parquet")
