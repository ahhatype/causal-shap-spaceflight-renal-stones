# ConfoundingSHAP, the simplest possible example

A stand-alone tutorial: one binary treatment, one outcome, three binary covariates from a DAG whose confounding structure is known exactly, and a Python script that runs ConfoundingSHAP (Brockschmidt et al., 2026, arXiv:2605.10533) on the data and compares the credits with the exact answer key. Read `study-guide.pdf` first; the paper is [arXiv:2605.10533](https://arxiv.org/abs/2605.10533) (a local copy, `ConfoundingSHAP paper.pdf`, is not committed).

| File | What it is |
| --- | --- |
| `study-guide.tex`, `study-guide.pdf` | What ConfoundingSHAP does, the toy DAG with its exact answer key, setup, how to read the output, pitfalls. |
| `confounding_game.py` | The signed global game on a finite population of binary states: exact arithmetic for the answer key and the saturated cell-mean plug-in for the data. No fitting. |
| `make_data.py` | Writes `data/toy_confounded.csv` (and `--randomized`, `data/toy_randomized.csv`) with the answer key beside it as JSON. |
| `run_confoundingshap.py` | Prints exact, plug-in and (with `--tabpfn`) the paper's TabPFN estimator credits side by side, and the eight coalition values. Writes `outputs/`. |
| `collider_check.py` | The toy DAG with a measured pretreatment collider added: shows that the collider earns a credit with the confounder's sign and that the method's "adjusted ATE" is the biased one. Section 8 of the study guide. Writes `data/toy_collider.csv`. |
| `data/` | The CSVs and their `_truth.json` answer keys (regenerate with `make_data.py` and `collider_check.py`). |
| `requirements.txt` | Python 3.12; numpy, pandas, scipy, shapiq 1.7.0; TabPFN optional. |

Quick start (Python 3.12):

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe make_data.py
.venv\Scripts\python.exe run_confoundingshap.py
```

The optional `--tabpfn` run needs torch, `tabpfn==9.1.0`, the TabPFN-2.5 licence and a Hugging Face login; section 5 of the study guide walks through it. On a CPU use `--n-rows 1500` (about a minute); the outputs of such a run are named with the row count, `outputs/toy_confounded_n1500_tabpfn_*`.

Results on this machine (8 October 2026): exact credits C 0.33201, Z −0.01951, P 0; cell-mean plug-in at n = 4,000: 0.35776, −0.02913, 0.00816; TabPFN-2.5 at n = 1,500 on CPU: 0.33375, −0.00950, −0.00543. The study guide's section 4 explains the differences. Collider check: with a pretreatment collider K in X the exact credits are C 0.31782 and K 0.03537, and the reference "adjusted ATE" is 0.45931 against a true 0.5 (section 8).

This tutorial is outside the Space SHAP study: it exists so that the method, its question and its answer key can be seen on something small before anyone decides whether it belongs in the paper.
