"""Audit the bounded TabPFN comparison; model fitting is opt-in.

Run in the isolated comparison environment after the main run completes.
Use --cell-parity-only for a download-free numerical assembly check, or
--model-query-check to additionally refit the first coalition and verify its
full-population predictions. This uses the existing local model access configuration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

# Explicitly permit the same 6,000-row CPU fit as the comparison when requested.
os.environ.setdefault("TABPFN_ALLOW_CPU_LARGE_DATASET", "1")

import numpy as np
import pandas as pd

import confoundingshap_comparison as ref
import confoundingshap_tabpfn as comparison


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def split(data, seed):
    order = np.random.default_rng(seed).permutation(len(data))
    return data.iloc[order[:6000]], data.iloc[order[6000:]]


def cell_parity(data, seeds):
    """Supplying cell means must exactly recover the existing reference output."""
    query = pd.DataFrame(ref.masks(4).astype(int), columns=ref.FEATURES)
    largest = 0.0
    for seed in seeds:
        train, evaluation = split(data, seed)
        arms = []
        for arm in (1, 0):
            arms.append(np.array([
                ref.cell_predictions(train, train.nephrolithiasis,
                                     query.assign(thiazides=arm),
                                     [*np.array(ref.FEATURES)[subset], "thiazides"])
                for subset in ref.masks(4)
            ]))
        rows, _, _ = comparison.summarize_predictions(train, evaluation, *arms, seed)
        actual = pd.DataFrame(rows).query('population == "held_out"')
        expected = pd.DataFrame(ref.renal_split(data, seed)[0])
        for column in ("confounding_signed", "control_outcome_conditional_shap_mean_abs",
                       "cate_conditional_shap_mean_abs"):
            difference = float(np.max(np.abs(actual[column].to_numpy() - expected[column].to_numpy())))
            largest = max(largest, difference)
            np.testing.assert_allclose(actual[column], expected[column], atol=1e-12, rtol=0)
    return {"seeds": seeds, "maximum_absolute_difference": largest}


def state_means(frame, predictions):
    """Independently recover the finite-state average of actual row predictions."""
    states = pd.MultiIndex.from_arrays(ref.masks(4).astype(int).T, names=ref.FEATURES)
    return (frame.assign(_prediction=predictions).groupby(ref.FEATURES)._prediction.mean()
            .reindex(states).to_numpy())


def query_refit_check(data, seed, output, tolerance, device):
    """Repeat actual 6,000/4,000-row queries, preserving size and row order."""
    train, evaluation = split(data, seed)
    subset = ref.masks(4)[1]
    with comparison.versioned_factory(seed):
        predictors = comparison.upstream._fit_s_learner(
            train[ref.FEATURES].to_numpy(dtype=float)[:, subset],
            train.thiazides.to_numpy(dtype=float), train.nephrolithiasis.to_numpy(dtype=float),
            device=device, n_estimators=1)
        report = {}
        checkpoint = json.loads((output / f"predictions_{seed}_01.json").read_text())
        for population, frame in (("training", train), ("held_out", evaluation)):
            report[population] = {}
            for arm, predict in zip((1, 0), predictors):
                predictions = predict(frame[ref.FEATURES].to_numpy(dtype=float)[:, subset])
                means = state_means(frame, predictions)
                cached = np.asarray(checkpoint["populations"][population][f"mu{arm}"])
                np.testing.assert_allclose(means, cached, atol=tolerance, rtol=0)
                weighted = comparison.state_weights(frame, ref.masks(4).astype(int)) @ means
                np.testing.assert_allclose(weighted, predictions.mean(), atol=1e-12, rtol=0)
                report[population][str(arm)] = {
                    "n_query_rows": len(predictions),
                    "checkpoint_refit_max_difference": float(np.max(np.abs(means - cached))),
                    "state_weighted_mean_minus_empirical_mean": float(weighted - predictions.mean()),
                }
    return {"seed": seed, "mask": 1, "device": device, "absolute_tolerance": tolerance, "arms": report,
            "scope": "First coalition only; actual 6,000 training and 4,000 held-out rows, both arms."}


def audit(output, baseline):
    metadata = json.loads((output / "metadata.json").read_text())
    old = json.loads((baseline / "metadata.json").read_text())
    provenance = metadata["provenance"]
    assert metadata["status"] == "complete", "Main run is not complete"
    assert provenance["input_sha256"] == old["input_sha256"] == digest(ref.DATA)
    assert provenance["reference_script_sha256"] == digest(ref.__file__)
    assert provenance["baseline_sha256"] == digest(baseline / "renal_attributions.csv")
    assert old["script_sha256"] == digest(ref.__file__), "Reference script changed since baseline"
    assert old["edges_sha256"] == digest(ref.EDGES)
    assert old["generator_sha256"] == digest(ref.ROOT / "analysis/R/renal_stone_source_aligned_simcausal.R")
    assert provenance["script_sha256"] == digest(comparison.__file__)
    assert provenance["upstream_source_sha256"] == digest(comparison.upstream.__file__)
    assert provenance["model_version"] == "2.5" and provenance["n_estimators"] == 1
    assert provenance["inference_precision"] == "float32"
    seeds = metadata["seeds"]
    assert len(seeds) == len(set(seeds)), "Repeated seeds"
    data = pd.read_csv(ref.DATA)
    assert len(data) == 10000
    assert data[[*ref.FEATURES, "thiazides", "nephrolithiasis"]].isin([0, 1]).all().all()
    expected_rows, expected_summaries, expected_games = [], [], []
    support, extrema = [], []
    maximum_within_state_spread = 0.0
    maximum_standardization_error = 0.0
    for seed in seeds:
        train, evaluation = split(data, seed)
        counts = train.groupby([*ref.FEATURES, "thiazides"]).size()
        assert len(counts) == 32 and len(evaluation.groupby(ref.FEATURES)) == 16
        support.append({"seed": seed, "minimum_training_arm_cell": int(counts.min())})
        frames = {"training": train, "held_out": evaluation}
        predictions_by_population = {pop: (np.zeros((16, 16)), np.zeros((16, 16))) for pop in frames}
        for mu1, mu0 in predictions_by_population.values():
            mu1[0] = train.loc[train.thiazides == 1, "nephrolithiasis"].mean()
            mu0[0] = train.loc[train.thiazides == 0, "nephrolithiasis"].mean()
        for mask in range(1, 16):
            record = json.loads((output / f"predictions_{seed}_{mask:02d}.json").read_text())
            assert record["seed"] == seed and record["mask"] == mask
            assert set(record["populations"]) == set(frames)
            for pop, (mu1, mu0) in predictions_by_population.items():
                values_record = record["populations"][pop]
                assert values_record["actual_query_rows"] == len(frames[pop])
                spread = values_record["maximum_within_state_spread"]
                assert np.isfinite(spread) and spread >= 0
                maximum_within_state_spread = max(maximum_within_state_spread, spread)
                for arm, matrix in ((1, mu1), (0, mu0)):
                    values = np.asarray(values_record[f"mu{arm}"])
                    assert values.shape == (16,) and np.isfinite(values).all()
                    weights = comparison.state_weights(frames[pop], ref.masks(4).astype(int))
                    empirical_mean = values_record[f"raw_mean{arm}"]
                    np.testing.assert_allclose(weights @ values, empirical_mean, atol=1e-12, rtol=0)
                    maximum_standardization_error = max(maximum_standardization_error,
                                                        float(abs(weights @ values - empirical_mean)))
                    matrix[mask] = values
        for pop, (mu1, mu0) in predictions_by_population.items():
            extrema.append({"seed": seed, "population": pop, "minimum": float(min(mu1.min(), mu0.min())),
                            "maximum": float(max(mu1.max(), mu0.max()))})
            rows, summaries, games = comparison.summarize_predictions(train, evaluation, mu1, mu0, seed,
                                                                      population_filter=pop)
            expected_rows.extend(rows); expected_summaries.extend(summaries); expected_games.extend(games)
    keys = {
        "renal_attributions": ["seed", "population", "feature"],
        "renal_splits": ["seed", "population"],
        "renal_coalitions": ["seed", "population", "mask"],
    }
    for filename, records in (("renal_attributions", expected_rows), ("renal_splits", expected_summaries),
                              ("renal_coalitions", expected_games)):
        actual = pd.read_csv(output / f"{filename}.csv", keep_default_na=False)
        expected = pd.DataFrame(records)
        key = keys[filename]
        assert not actual.duplicated(key).any()
        actual = actual.sort_values(key).reset_index(drop=True)
        expected = expected.sort_values(key).reset_index(drop=True)
        pd.testing.assert_frame_equal(actual, expected, check_dtype=False, atol=1e-12, rtol=0)
    rows = pd.DataFrame(expected_rows)
    summaries = pd.DataFrame(expected_summaries)
    np.testing.assert_allclose(summaries.attribution_sum,
                               summaries.crude_train_difference - summaries.plugin_full_adjusted_ate,
                               atol=1e-12, rtol=0)
    np.testing.assert_allclose(summaries.full_value, 0, atol=1e-12, rtol=0)
    heldout = rows.query('population == "held_out"')
    old_rows = pd.read_csv(baseline / "renal_attributions.csv")
    matched = heldout.merge(old_rows, on=["seed", "feature"], how="outer", indicator=True,
                            validate="one_to_one", suffixes=("_tabpfn", "_cell"))
    assert (matched._merge == "both").all() and len(matched) == 4 * len(seeds)
    paired = pd.read_csv(output / "paired_comparison.csv")
    sort = ["seed", "feature"]
    pd.testing.assert_frame_equal(paired.sort_values(sort).reset_index(drop=True),
                                  matched.drop(columns="_merge").sort_values(sort).reset_index(drop=True),
                                  check_dtype=False, atol=1e-12, rtol=0)
    warnings = []
    if any(row["minimum"] < 0 or row["maximum"] > 1 for row in extrema):
        warnings.append("Some state-mean regression predictions are outside [0,1]; report rather than silently clip.")
    if maximum_within_state_spread > 1e-6:
        warnings.append("Identical covariate states have numerical prediction variation; conditional SHAP uses population-specific state means.")
    return {"seeds": seeds, "device": provenance["device"], "support": support, "prediction_ranges": extrema,
            "warnings": warnings, "attribution_rows": len(rows), "game_rows": len(expected_games),
            "paired_rows": len(paired), "baseline_csv_sha256": digest(baseline / "renal_attributions.csv"),
            "maximum_within_state_prediction_spread": maximum_within_state_spread,
            "maximum_state_weighted_vs_raw_mean_error": maximum_standardization_error,
            "reference_script_sha256": digest(ref.__file__), "cell_parity": cell_parity(data, seeds)}, data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ref.ROOT / "analysis/output/confoundingshap_tabpfn")
    parser.add_argument("--baseline", type=Path, default=ref.ROOT / "analysis/output/confoundingshap_pilot")
    parser.add_argument("--cell-parity-only", action="store_true")
    parser.add_argument("--model-query-check", action="store_true")
    parser.add_argument("--query-tolerance", type=float, default=1e-6)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--device", choices=["cpu", "cuda"],
                        help="Query-check device; defaults to the completed run's recorded device.")
    args = parser.parse_args()
    comparison.torch.set_num_threads(args.threads)
    if args.cell_parity_only:
        print(json.dumps(cell_parity(pd.read_csv(ref.DATA), list(range(20260930, 20260935))), indent=2))
        return
    report = {"status": "failed", "model_query_check": "not requested"}
    try:
        result, data = audit(args.output, args.baseline)
        report.update(result)
        if args.model_query_check:
            report["model_query_check"] = query_refit_check(data, result["seeds"][0],
                                                                  args.output, args.query_tolerance,
                                                                  args.device or result["device"])
        report["status"] = "passed"
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
