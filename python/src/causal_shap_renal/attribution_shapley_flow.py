"""Step 6: Shapley Flow (Wang, Wiens & Lundberg, AISTATS 2021).

Requires a full directed graph. Attributes to edges, not nodes, which is
what distinguishes it from the other three Step 6 methods. Reference engine
is XGBoost, per the paper's case studies.

TODO: implement once config/dag_spec.yaml is finalized and Step 3 data
exists to fit the XGBoost model this method explains.
"""

from __future__ import annotations


def run_shapley_flow(data, dag_spec, iteration_round: int = 1) -> None:
    raise NotImplementedError
