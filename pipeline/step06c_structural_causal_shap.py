"""Step 6: Ng et al.'s Causal SHAP (arXiv:2509.00846).
See docs/methods §9 and python/src/causal_shap_renal/attribution_structural.py.

Consumes pipeline/step06d_pc_ida.R's output rather than recomputing PC+IDA.

TODO: implement once step06d has a first output to consume.
"""

from causal_shap_renal.attribution_structural import run_structural_causal_shap

if __name__ == "__main__":
    raise NotImplementedError("Step 6c driver not implemented yet")
