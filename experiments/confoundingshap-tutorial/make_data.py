"""Generate the tutorial data from a three-covariate DAG with a known answer key.

    C -> A and C -> Y        C is a confounder
    Z -> A                   Z affects treatment only (an instrument-like variable)
    P -> Y                   P affects the outcome only (a prognostic variable)
    A -> Y                   the treatment effect is 0.5 for every unit

C, Z, P are independent Bernoulli(1/2). A ~ Bernoulli(0.1 + 0.3 C + 0.3 Z), or Bernoulli(0.4) with
--randomized (no confounding). Y = C + 0.7 P + 0.5 A + noise, noise ~ Normal(0, 0.5^2).

Writes data/<name>.csv (columns C, Z, P, A, Y) and data/<name>_truth.json: the generating model, the
exact global game and the exact Shapley credits. The answer key is computed from population
probabilities, not from the sample, so it is the same for every seed.

    python make_data.py                      # data/toy_confounded.csv, n = 4000, seed 20261008
    python make_data.py --randomized         # data/toy_randomized.csv
    python make_data.py --n 20000 --seed 7 --name big
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from confounding_game import COVARIATES, ROLES, exact_credits

HERE = Path(__file__).resolve().parent


def generate(n: int, seed: int, randomized: bool) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    c, z, p = (rng.integers(0, 2, n) for _ in range(3))
    propensity = np.full(n, 0.4) if randomized else 0.1 + 0.3 * c + 0.3 * z
    a = (rng.random(n) < propensity).astype(int)
    y = c + 0.7 * p + 0.5 * a + rng.normal(0.0, 0.5, n)
    return pd.DataFrame({"C": c, "Z": z, "P": p, "A": a, "Y": np.round(y, 6)})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--randomized", action="store_true", help="A ~ Bernoulli(0.4): no confounding, every credit is zero")
    ap.add_argument("--name", default=None, help="file stem under data/ (default toy_confounded or toy_randomized)")
    args = ap.parse_args()
    name = args.name or ("toy_randomized" if args.randomized else "toy_confounded")
    out = HERE / "data"
    out.mkdir(exist_ok=True)
    df = generate(args.n, args.seed, args.randomized)
    df.to_csv(out / f"{name}.csv", index=False)
    key = exact_credits(args.randomized)
    truth = dict(
        model=dict(covariates={k: ROLES[k] for k in COVARIATES}, treatment="A", outcome="Y",
                   covariate_distribution="C, Z, P independent Bernoulli(1/2)",
                   propensity="0.4" if args.randomized else "0.1 + 0.3 C + 0.3 Z",
                   outcome_mean_untreated="C + 0.7 P", treatment_effect="0.5 for every unit",
                   noise="Normal(0, 0.5^2)"),
        sample=dict(n=args.n, seed=args.seed, randomized=args.randomized),
        exact=dict(crude_contrast=key["crude"], ate=key["ate"], crude_minus_ate=key["crude_minus_ate"],
                   global_game=dict(zip(["{}", "{C}", "{Z}", "{C,Z}", "{P}", "{C,P}", "{Z,P}", "{C,Z,P}"], key["game"])),
                   shapley_credits=key["credits"]),
        reading="The credits sum to the crude-minus-ATE gap. Z's credit is negative: adjusting for the treatment-only variable first amplifies the bias that C still carries. P's credit is exactly zero.",
    )
    (out / f"{name}_truth.json").write_text(json.dumps(truth, indent=1), encoding="utf-8")
    print(f"wrote {out / (name + '.csv')} ({len(df)} rows) and {name}_truth.json")
    print("exact credits:", {k: round(v, 6) for k, v in key["credits"].items()}, "| crude - ATE =", round(key["crude_minus_ate"], 6))
    print("sample: P(A=1) =", round(df.A.mean(), 4), "| crude contrast =", round(df.loc[df.A == 1, "Y"].mean() - df.loc[df.A == 0, "Y"].mean(), 4))


if __name__ == "__main__":
    main()
