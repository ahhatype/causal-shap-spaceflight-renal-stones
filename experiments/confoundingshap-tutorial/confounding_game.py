"""The ConfoundingSHAP game on a finite population of binary covariate states.

Definitions (Brockschmidt et al., 2026, arXiv:2605.10533). For a binary treatment A, an outcome Y and
pretreatment covariates X, with S a subset of the covariates and x_S a profile on S:

    delta_S(x_S) = E[Y | A = 1, X_S = x_S] - E[Y | A = 0, X_S = x_S]     the contrast adjusted for S only
    tau_S(x_S)   = E[tau(X) | X_S = x_S]                                 the fully adjusted effect, projected onto S
    b_S(x_S)     = delta_S(x_S) - tau_S(x_S)                             the residual confounding bias after adjusting for S

The signed global game is v(S) = -E[b_S(X_S)]. Its Shapley values share the crude-minus-adjusted gap
among the covariates: v(empty) = -(crude contrast - ATE), v(all covariates) = 0 under valid full
adjustment, and the credits sum to v(all) - v(empty) = crude - ATE.

Everything here is exact arithmetic on population probabilities or on empirical cell frequencies;
nothing is fitted. shapiq's ExactComputer is used as a check of the factorial Shapley formula when
it is installed. No environment variables are read.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

COVARIATES = ["C", "Z", "P"]
TREATMENT = "A"
OUTCOME = "Y"
ROLES = {"C": "confounder (C -> A and C -> Y)", "Z": "treatment-only (Z -> A)", "P": "outcome-only (P -> Y)"}


def masks(p: int) -> np.ndarray:
    """All 2**p coalitions as boolean rows; row k has member j when bit j of k is set."""
    return np.array([[bool(k & (1 << j)) for j in range(p)] for k in range(2 ** p)])


def exact_shapley(values: np.ndarray) -> np.ndarray:
    """Shapley values from one game value per coalition (factorial formula)."""
    p = int(round(math.log2(len(values))))
    if len(values) != 2 ** p:
        raise ValueError("expected one value per coalition, 2**p of them")
    out = np.zeros(p)
    for j in range(p):
        for s in range(2 ** p):
            if not s & (1 << j):
                k = bin(s).count("1")
                w = math.factorial(k) * math.factorial(p - k - 1) / math.factorial(p)
                out[j] += w * (values[s | (1 << j)] - values[s])
    return out


def shapiq_shapley(values: np.ndarray) -> np.ndarray | None:
    """The same Shapley values through shapiq's exact computer, or None when shapiq is not installed."""
    try:
        from shapiq import ExactComputer
    except ImportError:
        return None
    p = int(round(math.log2(len(values))))

    def game(coalitions):
        index = np.asarray(coalitions, dtype=int) @ (1 << np.arange(p))
        return values[index]

    sv = ExactComputer(n_players=p, game=game)(index="SV", order=1)
    return np.array([sv[(j,)] for j in range(p)])


def projection(states: np.ndarray, weights: np.ndarray, values: np.ndarray, subset: np.ndarray) -> np.ndarray:
    """E[values | X_S = x_S] for every state row, on a weighted finite population of states."""
    result = np.empty(len(states))
    for i, row in enumerate(states):
        same = np.all(states[:, subset] == row[subset], axis=1)
        result[i] = np.average(values[same], weights=weights[same])
    return result


def population_game(states: np.ndarray, weights: np.ndarray, propensity: np.ndarray,
                    mu0: np.ndarray, tau: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Signed local games v_x(S) = -b_S(x_S) for every state (columns) and coalition (rows), and the global game."""
    mu1 = mu0 + tau
    local = []
    for subset in masks(states.shape[1]):
        e = projection(states, weights, propensity, subset)
        delta = (projection(states, weights, propensity * mu1, subset) / e
                 - projection(states, weights, (1 - propensity) * mu0, subset) / (1 - e))
        local.append(projection(states, weights, tau, subset) - delta)
    local = np.asarray(local)
    return local @ weights, local


# ---------- the tutorial's generating model ----------

def toy_model(randomized: bool = False) -> dict:
    """Three independent Bernoulli(1/2) covariates; A ~ Bernoulli(0.1 + 0.3 C + 0.3 Z) or Bernoulli(0.4) when
    randomized; E[Y | A = 0, X] = C + 0.7 P; tau(X) = 0.5 for every unit."""
    states = masks(3).astype(int)                      # columns C, Z, P
    c, z, p = states.T
    weights = np.full(8, 1 / 8)
    propensity = np.full(8, 0.4) if randomized else 0.1 + 0.3 * c + 0.3 * z
    mu0 = c + 0.7 * p
    tau = np.full(8, 0.5)
    return dict(states=states, weights=weights, propensity=propensity, mu0=mu0, tau=tau)


def exact_credits(randomized: bool = False) -> dict:
    """The answer key: the global game, its Shapley credits, the crude contrast and the ATE, all exact."""
    m = toy_model(randomized)
    game, local = population_game(m["states"], m["weights"], m["propensity"], m["mu0"], m["tau"])
    credits = exact_shapley(game)
    check = shapiq_shapley(game)
    if check is not None:
        np.testing.assert_allclose(check, credits, atol=1e-12, rtol=0)
    e, w = m["propensity"], m["weights"]
    mu1 = m["mu0"] + m["tau"]
    crude = float((w * e * mu1).sum() / (w * e).sum() - (w * (1 - e) * m["mu0"]).sum() / (w * (1 - e)).sum())
    ate = float((w * m["tau"]).sum())
    np.testing.assert_allclose(credits.sum(), crude - ate, atol=1e-12)
    np.testing.assert_allclose(game[-1], 0.0, atol=1e-12)
    return dict(credits=dict(zip(COVARIATES, credits.tolist())), game=game.tolist(),
                crude=crude, ate=ate, crude_minus_ate=crude - ate)


# ---------- the plug-in estimate from a data set ----------

def estimate_from_sample(df: pd.DataFrame, covariates: list[str] = COVARIATES,
                         treatment: str = TREATMENT, outcome: str = OUTCOME) -> dict:
    """Saturated cell-mean plug-in of the signed global game on the empirical covariate distribution.

    For each coalition S: delta_S from the mean outcome by (treatment, X_S); tau_hat(x) from the mean outcome
    by (treatment, all covariates); tau_S as the empirical projection of tau_hat onto X_S. Every (arm, cell)
    must be populated; the function refuses to extrapolate into an empty cell.
    """
    p = len(covariates)
    states = masks(p).astype(int)
    key = df[covariates].to_numpy() @ (1 << np.arange(p))
    counts = np.bincount(key, minlength=2 ** p).astype(float)
    if (counts == 0).any():
        raise ValueError("a covariate profile has no records; the plug-in cannot evaluate every coalition")
    weights = counts / counts.sum()
    a = df[treatment].to_numpy()
    y = df[outcome].to_numpy()

    def cell_mean(arm: int, subset: np.ndarray) -> np.ndarray:
        """Mean outcome in the arm for the covariate profile of every state, keyed on the subset only."""
        sub_key = states[:, subset] @ (1 << np.arange(subset.sum())) if subset.any() else np.zeros(len(states), dtype=int)
        row_key = df[covariates].to_numpy()[:, subset] @ (1 << np.arange(subset.sum())) if subset.any() else np.zeros(len(df), dtype=int)
        out = np.empty(len(states))
        for i, k in enumerate(sub_key):
            pick = (row_key == k) & (a == arm)
            if not pick.any():
                raise ValueError(f"no records with {treatment}={arm} in a cell of {list(np.array(covariates)[subset])}")
            out[i] = y[pick].mean()
        return out

    full = np.ones(p, dtype=bool)
    tau_hat = cell_mean(1, full) - cell_mean(0, full)          # fully adjusted contrast per state
    game = np.empty(2 ** p)
    for k, subset in enumerate(masks(p)):
        delta = cell_mean(1, subset) - cell_mean(0, subset)
        tau_s = projection(states, weights, tau_hat, subset)
        game[k] = -float(weights @ (delta - tau_s))
    credits = exact_shapley(game)
    crude = float(y[a == 1].mean() - y[a == 0].mean())
    adjusted = float(weights @ tau_hat)
    np.testing.assert_allclose(game[0], -(crude - adjusted), atol=1e-12)
    np.testing.assert_allclose(game[-1], 0.0, atol=1e-12)
    np.testing.assert_allclose(credits.sum(), crude - adjusted, atol=1e-12)
    return dict(credits=dict(zip(covariates, credits.tolist())), game=game.tolist(),
                crude=crude, adjusted_ate=adjusted, crude_minus_adjusted=crude - adjusted,
                n=int(len(df)), min_cell=int(min(((key == k) & (a == arm)).sum() for k in range(2 ** p) for arm in (0, 1))))
