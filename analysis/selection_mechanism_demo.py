"""Exact exploratory selection example; NOT a fitted or calibrated renal model.

Uses four baseline strata, so no Monte Carlo error or third-party packages.
The existing 14-node and 51-node simulations and frozen results are untouched.
Run: python analysis/selection_mechanism_demo.py --check
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def expit(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def strata() -> list[dict]:
    """H is preflight stone history; F is a hypothetical fitness indicator."""
    rows = []
    for h in (0, 1):
        for f in (0, 1):
            # H and F are independent in the candidate source population.
            p = (0.2 if h else 0.8) * 0.5
            risks = [expit(-2.0 + 0.8 * h - 0.3 * f - a * (0.5 + 0.4 * h))
                     for a in (0, 1)]
            rows.append(dict(h=h, f=f, source_weight=p, risk0=risks[0],
                             risk1=risks[1], effect=risks[1] - risks[0]))
    return rows


def selection_probability(regime: str, row: dict) -> float:
    if regime == "no_selection":
        return 1.0
    if regime == "random_half":
        return 0.5
    if regime == "soft_selection":
        return expit(0.2 + 1.2 * row["f"] - 1.4 * row["h"])
    if regime == "hard_exclusion":
        return 0.0 if row["h"] else expit(0.2 + 1.2 * row["f"])
    raise ValueError(regime)


def summarize(regime: str) -> dict:
    rows = strata()
    ps = [selection_probability(regime, r) for r in rows]
    retained = sum(r["source_weight"] * s for r, s in zip(rows, ps))
    weights = [r["source_weight"] * s / retained for r, s in zip(rows, ps)]

    def mean(key: str) -> float:
        return sum(w * r[key] for w, r in zip(weights, rows))

    mh, mf = mean("h"), mean("f")
    covariance = sum(w * (r["h"] - mh) * (r["f"] - mf)
                     for w, r in zip(weights, rows))
    variance_product = mh * (1 - mh) * mf * (1 - mf)
    correlation = covariance / math.sqrt(variance_product) if variance_product > 0 else None
    support = sum(r["source_weight"] for r, s in zip(rows, ps) if s > 0)
    # Restore the entire candidate source population only with full support.
    # Do not replace an unidentified target contrast with an extrapolated number.
    ipw_effect = None
    if support >= 1 - 1e-12:
        norm = sum(w / s for w, s in zip(weights, ps))
        ipw_effect = sum(w / s * r["effect"] for w, s, r in zip(weights, ps, rows)) / norm
    return dict(regime=regime, retained_fraction=retained,
                history_prevalence=mh, history_fitness_correlation=correlation,
                risk_a0=mean("risk0"), risk_a1=mean("risk1"),
                selected_risk_difference=mean("effect"),
                source_support_coverage=support, source_ipw_risk_difference=ipw_effect)


def checks(results: list[dict]) -> None:
    baseline, random, soft, hard = results
    for key in ("risk_a0", "risk_a1", "selected_risk_difference", "history_prevalence"):
        assert math.isclose(baseline[key], random[key], abs_tol=1e-12), key
    assert abs(baseline["history_fitness_correlation"]) < 1e-12
    assert soft["history_fitness_correlation"] > 0
    for row in (baseline, random, soft):
        assert math.isclose(row["source_ipw_risk_difference"],
                            baseline["selected_risk_difference"], abs_tol=1e-12)
        assert math.isclose(row["risk_a1"] - row["risk_a0"],
                            row["selected_risk_difference"], abs_tol=1e-12)
    assert hard["source_ipw_risk_difference"] is None
    assert math.isclose(hard["source_support_coverage"], 0.8, abs_tol=1e-12)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent /
                        "output" / "selection_exploration")
    args = parser.parse_args()
    results = [summarize(r) for r in
               ("no_selection", "random_half", "soft_selection", "hard_exclusion")]
    if args.check:
        checks(results)
        print("Selection identity, random-selection null, collider and support checks passed.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "exact_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    metadata = dict(status="exploratory analytic example; not calibrated to NASA data",
                    graph_scope="four-variable outcome model plus selection; neither the 14-node nor 51-node simulation",
                    method="exact enumeration of four baseline strata; no model fitting or random draws",
                    intervention="A is a hypothetical binary hydration strategy; no dose units assigned",
                    population="hypothetical preflight candidate source; hard exclusion is a support stress test, not NASA policy",
                    assumptions="baseline selection, independent H and F, randomized A, unchanged outcome mechanism across selection regimes",
                    results=results)
    (args.output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
