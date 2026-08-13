"""Step 4: baseline attribution with standard (causality-blind) SHAP.

Explainer x model pairings, per docs/methods Step 4 spec and the Step 4
implementation plan's design decisions:
  TreeExplainer        + Random Forest   (feature_perturbation="interventional")
  TreeExplainer        + XGBoost         (feature_perturbation="interventional")
  LinearExplainer      + logistic regression (masker = feature covariance)
  KernelExplainer      + XGBoost, as a black box (SuperLearner deferred - see
                          docs/decisions/005-superlearner-deferred.md)
  PermutationExplainer + XGBoost, as a black box (same deferral)

Full breadth (all five) runs only at this step. Steps 6+ narrow to
TreeExplainer+XGBoost and KernelExplainer+SuperLearner once that ADR's
follow-up lands.

FEATURES is derived from config/dag_spec.yaml at runtime (io_contract.py's
model_features()), not hand-listed here - every node except the outcome.
config/dag_spec.yaml has no separate node for NASA's Mineralized Renal
Material / CaOx supersaturation intermediate: it was nephrolithiasis's only
parent in the DAG, so including it as a feature would have collapsed SHAP
onto one feature trivially, so it's collapsed directly onto nephrolithiasis
in the DAG spec itself instead (see nephrolithiasis's own note field there)
rather than excluded from the model as a modeling-only decision. Five
genuine mediators remain in FEATURES (bone_formation, bone_resorption,
vitamin_d_inflight, urinary_calcium_excretion, urine_chemistry), so the
mediation-testing story the methods doc describes - does a causally faithful
method split duration's effect between duration and its mediators, rather
than double-counting it on duration - is still intact. r/R/dag_utils.R's
model_features() is the R mirror, read by pipeline/step04a_ground_truth.R,
so the ground truth's feature list can never drift out of sync with this
module's.

link function is logit throughout (nephrolithiasis is binary), per the
methods doc. shap's own docs, fetched directly and quoted in the Step 4 plan:
  TreeExplainer   (readthedocs shap.TreeExplainer): feature_perturbation=
    "interventional" - "a background dataset `data` is required. The
    dependencies between features are handled according to the rules
    dictated by causal inference."
  LinearExplainer (readthedocs shap.LinearExplainer): masker as "a tuple of
    (mean, covariance)" for the feature-covariance masker (not independence).
  KernelExplainer (readthedocs shap.KernelExplainer): nsamples="auto" ->
    "nsamples = 2 * X.shape[1] + 2048"; background via shap.kmeans().
  PermutationExplainer (github.com/shap/shap shap/explainers/_permutation.py):
    minimum max_evals = 2*num_features + 1; "auto" resolves to 10 * 2 * M
    (10 cycles) - already "a multiple of its enforced minimum" per the
    methods doc, no override needed.

Verified directly against this repo's installed versions (shap 0.52.0,
scikit-learn 1.9.0, xgboost 3.4.0):
  - TreeExplainer(..., model_output="probability") returns shape
    (n, features, n_classes) for a binary classifier - slice [..., 1].
  - PermutationExplainer's callable API (`explainer(X)`) returns a
    shap.Explanation; `.values` is shape (n, features).
  - A logit-link explainer (`KernelExplainer(..., link="logit")` /
    `PermutationExplainer(..., link=shap.links.logit)`) computes
    logit(p) - logit(p') internally; predict_proba landing on exact 0 or 1
    makes that blow up (observed as "invalid value encountered in scalar
    subtract" RuntimeWarnings, silently producing NaN attributions) -
    every logit-link model function clips to [1e-6, 1-1e-6].

SCALE WARNING: attribution_value is NOT on a single common scale across all
five rows-per-feature. linear_shap, kernel_shap, permutation_shap, and
tree_shap+xgboost (model_output="raw", XGBoost's binary:logistic raw margin
IS the log-odds score) are all on the logit/log-odds scale, matching "link
function is logit throughout." tree_shap+random_forest is the one exception:
Random Forest has no internal link function to put on a logit scale (leaf
values already are probability estimates; verified "raw" and "probability"
model_output give an identical TreeExplainer expected_value for it) - it is
left on the probability (0-1) scale, and is NOT directly magnitude-comparable
to the other four pairings. Any cross-pairing comparison (rank correlation is
fine; raw magnitude is not) must account for this.
"""

from __future__ import annotations

import subprocess
import uuid
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from causal_shap_renal.io_contract import model_features

TARGET = "nephrolithiasis"

DAG_VARIANT = "renal_stone_baseline"
ITERATION_ROUND = 0  # Step 6's human-in-the-loop rounds start at 1; 0 marks
# this as the pre-iteration baseline.

_PROB_EPS = 1e-6


def _clipped_proba(model, columns: list[str]):
    """A predict_proba wrapper safe to pass to a logit-link explainer.

    Re-wraps the raw numpy array KernelExplainer/PermutationExplainer pass
    in as a DataFrame with the right column names (avoids sklearn's "X does
    not have valid feature names" warning), and clips away from exact 0/1
    so logit(p) never blows up - see module docstring.
    """

    def f(x: np.ndarray) -> np.ndarray:
        x_df = pd.DataFrame(x, columns=columns)
        p = model.predict_proba(x_df)[:, 1]
        return np.clip(p, _PROB_EPS, 1 - _PROB_EPS)

    return f


def _summarize(method: str, engine: str, shap_values: np.ndarray, features: list[str]) -> list[dict]:
    """Global per-feature importance: mean absolute SHAP value across the
    explained set. ATTRIBUTION_SCHEMA_COLUMNS has no per-row/observation
    column, so this is the schema's implied granularity - one row per
    (method, engine, feature)."""
    mean_abs = np.abs(shap_values).mean(axis=0)
    return [
        {"method": method, "engine": engine, "feature": f, "attribution_value": float(v)}
        for f, v in zip(features, mean_abs)
    ]


def _git_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


SEED = 20260812


def run_baseline_shap(data: pd.DataFrame, dag_spec: dict) -> pd.DataFrame:
    # KernelExplainer has no seed parameter of its own - it samples coalitions
    # from numpy's global RNG state, verified by rerunning this function twice
    # and observing attribution_value drift (~1e-3) without this. seeding here
    # covers it; PermutationExplainer below takes an explicit seed=.
    np.random.seed(SEED)

    features = model_features(dag_spec)
    X = data[features]
    y = data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=20260812, stratify=y
    )
    background = X_train.sample(n=100, random_state=20260812)  # held-out background

    rf = RandomForestClassifier(random_state=0).fit(X_train, y_train)
    # enable_categorical=False: xgboost >=3 defaults enable_categorical=True,
    # which makes shap.TreeExplainer's interventional mode refuse to run
    # ("Categorical split is not yet supported") even though none of our
    # int-coded columns (sex, history_of_nephrolithiasis) are pandas
    # 'category' dtype - verified directly against xgboost 3.4.0/shap 0.52.0.
    xgb = XGBClassifier(eval_metric="logloss", random_state=0, enable_categorical=False).fit(
        X_train, y_train
    )
    logit = LogisticRegression(max_iter=1000).fit(X_train, y_train)
    # No SuperLearner/StackingClassifier this round - see
    # docs/decisions/005-superlearner-deferred.md. KernelExplainer/
    # PermutationExplainer explain the already-fitted xgb model instead, as
    # a black box - validates their *approximate* output against
    # TreeExplainer's *exact* output on the same model.

    rows: list[dict] = []

    # TreeExplainer x {Random Forest, XGBoost}, interventional, held-out background.
    # model_output differs by engine, not a mistake: XGBoost's binary:logistic
    # "raw" margin IS the log-odds score (verified: sigmoid(mean(raw)) tracks
    # the model's own predicted-probability scale), so "raw" puts it on the
    # same logit scale as linear_shap/kernel_shap/permutation_shap below,
    # matching the methods doc's "link function is logit throughout." Random
    # Forest has no such link function internally (leaf values already ARE
    # probability estimates, nothing to invert) - verified "raw" and
    # "probability" give an identical expected_value for it - so
    # tree_shap+random_forest is unavoidably left on the probability scale,
    # NOT directly magnitude-comparable to the other four pairings. Flag this
    # explicitly wherever attribution_value is compared across method/engine.
    for engine, model, model_output in [
        ("random_forest", rf, "probability"),
        ("xgboost", xgb, "raw"),
    ]:
        explainer = shap.TreeExplainer(
            model, data=background, feature_perturbation="interventional", model_output=model_output
        )
        sv = explainer.shap_values(X_test)
        sv = sv[..., 1] if np.ndim(sv) == 3 else sv  # binary classifier: positive-class slice
        rows += _summarize("tree_shap", engine, sv, features)

    # LinearExplainer x logistic regression, empirical covariance masker
    masker = (X_train.mean().values, np.cov(X_train.values, rowvar=False))
    explainer = shap.LinearExplainer(logit, masker)
    sv = explainer.shap_values(X_test)
    rows += _summarize("linear_shap", "logistic_regression", sv, features)

    # KernelExplainer x XGBoost-as-black-box, k=50 k-means background, logit link
    kmeans_bg = shap.kmeans(X_train, 50)
    explainer = shap.KernelExplainer(_clipped_proba(xgb, features), kmeans_bg, link="logit")
    sv = explainer.shap_values(X_test, nsamples="auto")
    rows += _summarize("kernel_shap", "xgboost_blackbox", sv, features)

    # PermutationExplainer x XGBoost-as-black-box, "auto" (10x the 2M+1 floor)
    explainer = shap.PermutationExplainer(
        _clipped_proba(xgb, features), background, link=shap.links.logit, seed=SEED
    )
    sv = explainer(X_test).values
    rows += _summarize("permutation_shap", "xgboost_blackbox", sv, features)

    run_id = str(uuid.uuid4())
    git_sha = _git_sha()
    timestamp = datetime.now(timezone.utc).isoformat()
    for row in rows:
        row["dag_variant"] = DAG_VARIANT
        row["iteration_round"] = ITERATION_ROUND
        row["run_id"] = run_id
        row["git_sha"] = git_sha
        row["timestamp"] = timestamp

    return pd.DataFrame(rows)
