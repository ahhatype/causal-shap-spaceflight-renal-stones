.PHONY: setup-r setup-py setup step02 step03 step04 step05 step06 step07 step08 \
        test-r test-py test full-dag-r full-dag-validate full-dag-battery \
        hub ladder workbench site

# One Python environment for both packages (ADR 007). pip + venv, not uv.
ifeq ($(OS),Windows_NT)
PY := $(abspath .venv/Scripts/python.exe)
PY_BOOT := py -3.13
else
PY := $(abspath .venv/bin/python)
PY_BOOT := python3.13
endif

# --- environment setup ---

setup-r:
	cd r && Rscript -e 'renv::restore(prompt = FALSE)'

setup-py:
	$(PY_BOOT) -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[discovery,workbench,dev]"

setup: setup-r setup-py

# --- working-subgraph pipeline (14 nodes; config/ + pipeline/ + r/ + python/) ---

step02:
	cd pipeline && Rscript step02_dag_construction.R

step03:
	cd pipeline && Rscript step03_simulate_data.R

step04:
	cd pipeline && Rscript step04a_ground_truth.R
	cd pipeline && $(PY) step04_baseline_shap.py

# Placeholder until a detector provider is registered (ADR 008); exits 2 with the reason.
step05:
	$(PY) pipeline/step05_lumawarp_detector.py $(if $(PROVIDER),--provider $(PROVIDER),)

step06:
	cd pipeline && Rscript step06a_causal_shapley_asv.R
	cd pipeline && Rscript step06d_pc_ida.R
	cd pipeline && $(PY) step06b_shapley_flow.py
	cd pipeline && $(PY) step06c_structural_causal_shap.py
	cd pipeline && $(PY) step06_hitl_iteration.py

step07:
	$(PY) pipeline/step07_lumawarp_reweight.py $(if $(PROVIDER),--provider $(PROVIDER),)

step08:
	cd pipeline && Rscript step08_dag_recovery.R
	cd pipeline && $(PY) step08_dag_recovery.py

# --- full source DAG (51 nodes; analysis/ + apps/, ported per ADR 007) ---

full-dag-r:
	Rscript analysis/run_all.R

full-dag-validate:
	Rscript analysis/validate_outputs.R
	cd apps && $(PY) -m causal_shap.build validate

full-dag-battery:
	$(PY) analysis/run_m1_m5_battery.py --example toy --output-dir .scratch/battery-smoke

# --- apps (run locally; not hosted) ---

hub:
	$(PY) -m shiny run --port 8002 --app-dir apps hub.app:app

ladder:
	cd apps && $(PY) -m shiny run --port 8000 app.py

workbench:
	cd apps/workbench && $(PY) -m shiny run --port 8001 app.py

# --- site ---

site:
	quarto render site

# --- tests ---

test-r:
	cd r && Rscript -e 'testthat::test_dir("tests")'

test-py:
	$(PY) -m pytest

test: test-r test-py
