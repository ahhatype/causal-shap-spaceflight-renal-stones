"""Step 6: Ng et al.'s Causal SHAP (arXiv:2509.00846).

No public reference repo. Implemented from the paper's Algorithm 1: PC
discovers a CPDAG, IDA quantifies causal strength, then a structural value
function does do(X_S), propagates through descendants, and scores a fixed
model. The PC+IDA stage runs in R (pipeline/step06d_pc_ida.R, see
docs/decisions/001-two-language-repo.md) - this module consumes that
output rather than recomputing it. Reference engine is Random Forest, per
the paper's own experiments.

TODO: implement once pipeline/step06d_pc_ida.R produces its first CPDAG output.
"""

from __future__ import annotations


def run_structural_causal_shap(data, pc_ida_output, iteration_round: int = 1) -> None:
    raise NotImplementedError
