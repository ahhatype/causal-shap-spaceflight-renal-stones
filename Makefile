.PHONY: setup-r setup-py setup step02 step03 step04 step06 step08 test-r test-py test

# --- environment setup ---

setup-r:
	cd r && Rscript -e 'renv::restore(prompt = FALSE)'

setup-py:
	cd python && uv sync --extra discovery --extra shapley-flow --extra dev

setup: setup-r setup-py

# --- pipeline steps (each stub raises NotImplementedError / stop() until built) ---

step02:
	cd pipeline && Rscript step02_dag_construction.R

step03:
	cd pipeline && Rscript step03_simulate_data.R

step04:
	cd python && uv run python ../pipeline/step04_baseline_shap.py

step06:
	cd pipeline && Rscript step06a_causal_shapley_asv.R
	cd pipeline && Rscript step06d_pc_ida.R
	cd python && uv run python ../pipeline/step06b_shapley_flow.py
	cd python && uv run python ../pipeline/step06c_structural_causal_shap.py
	cd python && uv run python ../pipeline/step06_hitl_iteration.py

step08:
	cd pipeline && Rscript step08_dag_recovery.R
	cd python && uv run python ../pipeline/step08_dag_recovery.py

# --- tests ---

test-r:
	cd r && Rscript -e 'testthat::test_dir("tests")'

test-py:
	cd python && uv run pytest

test: test-r test-py
