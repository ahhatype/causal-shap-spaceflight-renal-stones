"""Step 6: orchestrates the 3-round human-in-the-loop iteration across all
four causal SHAP methods (step06a-d). See docs/methods §9-10.

Each round: run methods with current input -> Robert reviews attributions
against the Step 4 DAG-derived baseline -> revises input -> rerun. Tracks
RMSE against ground truth and rank-stability round over round.

TODO: implement once step06a-d each produce a first-round output.
"""

if __name__ == "__main__":
    raise NotImplementedError("Step 6 human-in-the-loop orchestrator not implemented yet")
