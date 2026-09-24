"""Paired diagnostic of IDA-direction fixes; never replaces frozen Step 6 results.

Run from the repository root with its scientific Python environment. Inputs are
the separately reconstructed September 19 audit, not missing historical data.
The three round-2 arms have identical arrows, hence identical fitted parent
regressions, predictive models and coalition draws. Only gamma changes.

For each instance let b_i be the common pre-gamma Monte Carlo accumulator,
D=f(x)-mean(f(X)), and z_i=D*b_i/sum(b). The existing helper with gamma=1
returns z. For arm g, phi_i=D*g_i*z_i/sum(g*z), algebraically equal to
D*g_i*b_i/sum(g*b). We verify this against the actual helper with matched RNG
states before the full run. Zero denominators/gaps fail closed rather than
claiming that a lost accumulator can be recovered from normalized zeros.

These remain heuristic total-effect edge weights. Products of IDA total effects
are not direct-coefficient path effects; this audit fixes direction only.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import sys
import time
from datetime import datetime, timezone

import networkx as nx
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python/src"))
from causal_shap_renal import attribution_structural as structural
from causal_shap_renal.engines import fit_engine
from causal_shap_renal.io_contract import model_features

OUT = ROOT / "analysis/output/numerical_audit_20260919"
ARMS = ["legacy", "direction_fixed_stale_reversal", "direction_and_reversal_fixed"]
SEED = 20260812
N_EXPLAIN = 6
T_ITERATIONS = 150
VALIDATION_T = 5
MAX_SECONDS = 600


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_json_value(value):
    """Keep model sentinels explicit without emitting invalid JSON NaN/Infinity."""
    if isinstance(value, float) and not math.isfinite(value):
        return f"nonfinite:{value}"
    if isinstance(value, dict):
        return {key: strict_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [strict_json_value(item) for item in value]
    return value


def reweight(z: np.ndarray, gamma: np.ndarray, gap: float) -> np.ndarray:
    weighted = z * gamma
    denominator = float(np.sum(weighted))
    if gap == 0 or denominator == 0 or not np.isfinite(denominator):
        raise ArithmeticError("Cannot recover normalized attribution: zero/nonfinite denominator or gap")
    values = gap * weighted / denominator
    if not np.all(np.isfinite(values)):
        raise ArithmeticError("Nonfinite reweighted attribution")
    np.testing.assert_allclose(values.sum(), gap, rtol=1e-9, atol=1e-12)
    return values


def main() -> None:
    started = time.perf_counter()
    data_path = OUT / "ida_reconstructed_data.csv"
    edges_path = OUT / "ida_edge_comparison.csv"
    data = pd.read_csv(data_path)
    edges = pd.read_csv(edges_path)
    spec_path = ROOT / "config/dag_spec.yaml"
    features = model_features(yaml.safe_load(spec_path.read_text(encoding="utf-8")))
    assert structural.M_SAMPLES == 64
    assert structural.T_ITERATIONS == T_ITERATIONS
    gamma_rows, graphs, gammas = [], {}, {}
    for (arm, round_number), subset in edges.groupby(["arm", "round"], sort=False):
        graph = structural.build_graph(subset)
        assert nx.is_directed_acyclic_graph(graph)
        gamma = structural.causal_weights(graph, features)
        gamma_rows.extend(dict(arm=arm, round=int(round_number), feature=f, gamma=gamma[f])
                          for f in features)
        if round_number == 2:
            graphs[arm] = graph
            gammas[arm] = gamma
    pd.DataFrame(gamma_rows).to_csv(OUT / "ida_gamma_by_arm_round.csv", index=False)
    for arm in ARMS:
        assert set(graphs[arm].edges) == set(graphs["legacy"].edges)
        assert list(graphs[arm].nodes) == list(graphs["legacy"].nodes)
    order = structural._topological_feature_order(graphs["legacy"], features)
    fits = structural.fit_parent_regressions(data, graphs["legacy"], features)
    units = dict.fromkeys(features, 1.0)
    metadata = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "diagnostic_only": True,
        "source": "Reconstructed data; original Step 6 data and PC/IDA artifacts unavailable",
        "interpretation": "Round 2 is a scripted orientation/reconnection heuristic, not human expert review",
        "remaining_limitation": "Mean absolute IDA TOTAL effects used as edge weights; path products not causal coefficients",
        "python": sys.version, "platform": platform.platform(),
        "versions": {name: importlib.metadata.version(name)
                     for name in ["numpy", "pandas", "networkx", "scikit-learn", "xgboost"]},
        "seed": SEED, "n_explain": N_EXPLAIN, "M": structural.M_SAMPLES,
        "T": T_ITERATIONS, "validation_T": VALIDATION_T,
        "maximum_seconds": MAX_SECONDS,
        "pairing": "Same round-2 topology, parent fits, engine model, explained rows and coalition draws across arms",
        "algebra": "z_i=D*b_i/sum(b); phi_i(g)=D*g_i*z_i/sum(g*z)",
        "input_sha256": {str(p.relative_to(ROOT)): digest(p) for p in [
            data_path, edges_path, spec_path,
            ROOT / "python/src/causal_shap_renal/attribution_structural.py",
            ROOT / "python/src/causal_shap_renal/engines.py", Path(__file__)]},
        "engines": {}, "status": "running",
    }
    meta_path = OUT / "ida_attribution_metadata.json"
    def save_metadata():
        metadata["elapsed_seconds"] = time.perf_counter() - started
        meta_path.write_text(json.dumps(strict_json_value(metadata), indent=2, allow_nan=False),
                             encoding="utf-8")
    save_metadata()
    rows, verification = [], []
    for engine in ["xgboost", "random_forest"]:
        engine_start = time.perf_counter()
        if engine_start - started > MAX_SECONDS:
            metadata["status"] = "bounded_stop_before_engine"
            break
        print(f"Fitting {engine}; elapsed {engine_start-started:.1f}s", flush=True)
        model = fit_engine(engine, data[features], data[structural.TARGET], seed=SEED)
        expected = float(model.predict_proba(data[features])[:, 1].mean())
        rng = np.random.default_rng(SEED)
        indices = rng.choice(len(data), size=min(N_EXPLAIN, len(data)), replace=False)
        metadata["engines"][engine] = {
            "model_parameters": model.get_params(), "expected_value": expected,
            "explain_indices_zero_based": indices.tolist(), "completed_instances": 0,
        }
        # Separate verification stream: validation never advances the main RNG.
        x = data.iloc[indices[0]]
        gap = float(model.predict_proba(pd.DataFrame([x[features]]))[:, 1][0]) - expected
        validation_seed = SEED + 1
        base_check = structural.causal_shap_one_instance(
            x, features, order, fits, units, model, expected,
            np.random.default_rng(validation_seed), t_iterations=VALIDATION_T)
        z = np.array([base_check[f] for f in features])
        for arm in ARMS:
            direct = structural.causal_shap_one_instance(
                x, features, order, fits, gammas[arm], model, expected,
                np.random.default_rng(validation_seed), t_iterations=VALIDATION_T)
            reconstructed = reweight(z, np.array([gammas[arm][f] for f in features]), gap)
            actual = np.array([direct[f] for f in features])
            np.testing.assert_allclose(reconstructed, actual, rtol=1e-9, atol=1e-12)
            verification.append(dict(engine=engine, arm=arm, seed=validation_seed,
                                     T=VALIDATION_T, M=64,
                                     maximum_absolute_difference=float(np.max(abs(reconstructed-actual)))))
        print(f"{engine}: reweighting equality verified", flush=True)
        for index in indices:
            if time.perf_counter() - started > MAX_SECONDS:
                metadata["status"] = "bounded_stop_between_instances"
                break
            x = data.iloc[index]
            gap = float(model.predict_proba(pd.DataFrame([x[features]]))[:, 1][0]) - expected
            base = structural.causal_shap_one_instance(
                x, features, order, fits, units, model, expected, rng,
                t_iterations=T_ITERATIONS)
            z = np.array([base[f] for f in features])
            for arm in ARMS:
                values = reweight(z, np.array([gammas[arm][f] for f in features]), gap)
                rows.extend(dict(engine=engine, arm=arm, round=2,
                                 row_index=int(index), feature=f, gamma=gammas[arm][f],
                                 prediction_gap=gap, attribution=float(v))
                            for f, v in zip(features, values))
            metadata["engines"][engine]["completed_instances"] += 1
            pd.DataFrame(rows).to_csv(OUT / "ida_paired_instance_attributions.csv", index=False)
            save_metadata()
            print(f"{engine}: {metadata['engines'][engine]['completed_instances']}/{N_EXPLAIN} instances; "
                  f"elapsed {time.perf_counter()-started:.1f}s", flush=True)
        metadata["engines"][engine]["elapsed_seconds"] = time.perf_counter() - engine_start
        if metadata["status"] != "running":
            break
    table = pd.DataFrame(rows)
    table["absolute_attribution"] = table.attribution.abs()
    summary = table.groupby(["engine", "arm", "round", "feature"], as_index=False).agg(
        mean_absolute_attribution=("absolute_attribution", "mean"),
        n_instances=("row_index", "nunique"), gamma=("gamma", "first"))
    summary["rank"] = summary.groupby(["engine", "arm"])["mean_absolute_attribution"].rank(
        ascending=False, method="average")
    legacy = summary[summary.arm == "legacy"][["engine", "feature", "mean_absolute_attribution", "rank"]].rename(
        columns={"mean_absolute_attribution": "legacy_mean_absolute_attribution", "rank": "legacy_rank"})
    summary = summary.merge(legacy, on=["engine", "feature"], validate="many_to_one")
    summary["attribution_delta_from_legacy"] = summary.mean_absolute_attribution - summary.legacy_mean_absolute_attribution
    summary["rank_delta_from_legacy"] = summary["rank"] - summary.legacy_rank
    summary.to_csv(OUT / "ida_paired_attribution_summary.csv", index=False)
    pd.DataFrame(verification).to_csv(OUT / "ida_reweighting_verification.csv", index=False)
    # Check the failure policy explicitly, rather than silently accepting zeros.
    try:
        reweight(np.zeros(len(features)), np.ones(len(features)), 1.0)
    except ArithmeticError:
        metadata["zero_denominator_fail_closed_verified"] = True
    else:
        raise AssertionError("Zero denominator did not fail closed")
    if metadata["status"] == "running":
        metadata["status"] = "complete"
    save_metadata()
    print(summary[(summary.arm == ARMS[-1]) & (summary.legacy_mean_absolute_attribution == 0)
                  & (summary.mean_absolute_attribution > 0)].to_string(index=False), flush=True)
    print(f"Audit {metadata['status']}; elapsed {metadata['elapsed_seconds']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
