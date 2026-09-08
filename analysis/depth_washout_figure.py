"""E3 figure: deeper nodes wash out sooner as sampling variance grows.

A standardized linear chain X_D -> ... -> X_1 -> Y with the same coefficient
on every edge. The total effect of the node at depth d is beta**d, so effects
shrink geometrically with depth (Wright 1934; Bollen 1987). For each sample
size n and each depth, R replicate datasets are drawn and the marginal
regression of Y on X_d uses |t| > 1.96, an approximate 5% rule. In a chain with no
confounding that marginal slope is an unbiased estimate of the total effect,
so the fraction of replicates that reject is the power to detect the node at
all. Plotted against the sampling standard error (1/sqrt(n)), the deeper
curves fall first: that is the washout, and it is driven by sampling variance
alone, before any measurement noise is added.

Writes:
  site/assets/depth_washout.svg      (the site figure)
  docs/images/depth_washout.png      (for the docs)
  results/figures/depth_washout.csv  (the curves)

    python analysis/depth_washout_figure.py
"""

from __future__ import annotations

from pathlib import Path
import argparse

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams['svg.hashsalt'] = 'space-shap-depth-20260904'
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SEED = 20260904  # continues the dated-integer seed register
BETA = 0.6
DEPTHS = (1, 2, 3, 4, 5)
SAMPLE_SIZES = np.unique(np.round(np.logspace(np.log10(25), np.log10(4000), 18)).astype(int))
REPLICATES = 400
ALPHA_T = 1.96  # Frozen approximate 5% cutoff, not the finite-sample t critical value.

INK, MUTE, PAPER = "#1a1814", "#6b6258", "#fbf7ef"
DEPTH_COLORS = {1: "#00897b", 2: "#0077a8", 3: "#1c9ed3", 4: "#e07020", 5: "#c96018"}


def simulate_chain(n: int, depth_max: int, rng: np.random.Generator) -> tuple[dict[int, np.ndarray], np.ndarray]:
    """Standardized chain: each node has unit variance; its parent explains beta**2 of it."""
    resid_sd = np.sqrt(1.0 - BETA**2)
    x = rng.standard_normal(n)
    nodes = {depth_max: x}
    for depth in range(depth_max - 1, 0, -1):
        x = BETA * x + resid_sd * rng.standard_normal(n)
        nodes[depth] = x
    y = BETA * x + resid_sd * rng.standard_normal(n)
    return nodes, y


def detection_rates() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    for n in SAMPLE_SIZES:
        hits = {d: 0 for d in DEPTHS}
        for _ in range(REPLICATES):
            nodes, y = simulate_chain(int(n), max(DEPTHS), rng)
            yc = y - y.mean()
            for d in DEPTHS:
                xc = nodes[d] - nodes[d].mean()
                r = float(xc @ yc / np.sqrt((xc @ xc) * (yc @ yc)))
                t = r * np.sqrt(n - 2) / np.sqrt(max(1e-12, 1.0 - r * r))
                hits[d] += abs(t) > ALPHA_T
        for d in DEPTHS:
            rows.append(
                {
                    "n": int(n),
                    "sampling_se": 1.0 / np.sqrt(n),
                    "depth": d,
                    "true_total_effect": BETA**d,
                    "detection_rate": hits[d] / REPLICATES,
                }
            )
    return pd.DataFrame(rows)


def draw(curves: pd.DataFrame) -> plt.Figure:
    fig, (left, right) = plt.subplots(
        1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1, 1.9]}, facecolor=PAPER
    )
    for ax in (left, right):
        ax.set_facecolor(PAPER)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=MUTE, labelsize=9)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(MUTE)

    effects = [BETA**d for d in DEPTHS]
    left.bar(DEPTHS, effects, color=[DEPTH_COLORS[d] for d in DEPTHS], width=0.7)
    for d, e in zip(DEPTHS, effects):
        left.text(d, e + 0.015, f"{e:.2f}", ha="center", fontsize=8.5, color=INK)
    left.set_xticks(list(DEPTHS))
    left.set_xlabel("depth (hops to Y)", color=INK, fontsize=9.5)
    left.set_ylabel(f"true total effect  (= {BETA}^depth)", color=INK, fontsize=9.5)
    left.set_title("Effects shrink with depth", color=INK, fontsize=11, loc="left")
    left.set_ylim(0, 0.72)

    for d in DEPTHS:
        sub = curves[curves["depth"] == d].sort_values("sampling_se")
        right.plot(sub["sampling_se"], sub["detection_rate"], color=DEPTH_COLORS[d], lw=2.4, label=f"depth {d}")
        last = sub.iloc[-1]
    right.axhline(0.8, color=MUTE, lw=1, ls=(0, (4, 4)))
    right.text(curves["sampling_se"].min(), 0.815, "80% power", color=MUTE, fontsize=8.5)
    right.set_xlabel("sample-size scale  (1 / √n, larger = smaller sample)", color=INK, fontsize=9.5)
    right.set_ylabel("fraction of marginal-slope tests detected", color=INK, fontsize=9.5)
    right.set_title("Deeper nodes wash out first as sampling variance grows", color=INK, fontsize=11, loc="left")
    right.set_ylim(0, 1.02)
    right.set_xlim(curves["sampling_se"].min() * 0.95, curves["sampling_se"].max() * 1.02)
    ticks = [1 / np.sqrt(n) for n in (4000, 1000, 250, 100, 50, 25)]
    right.set_xticks(ticks)
    right.set_xticklabels([f"n={n}" for n in (4000, 1000, 250, 100, 50, 25)])
    right.legend(frameon=False, fontsize=8.5, loc="lower left", title="node depth", title_fontsize=8.5)
    fig.text(
        0.005, 0.01,
        f"Standardized chain, edge {BETA}; {REPLICATES} replicates; marginal-slope |t| > {ALPHA_T} (approximate 5% rule). Seed {SEED}.",
        fontsize=7.5, color=MUTE,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--verify-recorded', action='store_true', help='Recompute and compare the frozen CSV, without writing outputs.')
    mode.add_argument('--render-recorded', action='store_true', help='Redraw from the frozen CSV without running simulations.')
    args = parser.parse_args()
    out_csv = REPO / "results" / "figures" / "depth_washout.csv"
    if args.verify_recorded:
        recorded = pd.read_csv(out_csv)
        actual = detection_rates()
        pd.testing.assert_frame_equal(actual, recorded, check_exact=False, rtol=1e-12, atol=1e-14)
        print(f'PASS: all {len(recorded)} frozen depth rows reproduced; no outputs written.')
        return
    curves = pd.read_csv(out_csv) if args.render_recorded else detection_rates()
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if not args.render_recorded:
        curves.to_csv(out_csv, index=False)
    fig = draw(curves)
    svg = REPO / "site" / "assets" / "depth_washout.svg"
    png = REPO / "docs" / "images" / "depth_washout.png"
    svg.parent.mkdir(parents=True, exist_ok=True)
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(svg, format="svg", facecolor=PAPER, metadata={'Date': None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines()) + '\n', encoding='utf-8')
    fig.savefig(png, dpi=160, facecolor=PAPER)
    summary = curves[curves["detection_rate"] >= 0.8].groupby("depth")["n"].min()
    print("smallest n reaching 80% power, by depth:")
    print(summary.to_string())
    print(f"wrote {svg}, {png}")
    print(f"{'read frozen' if args.render_recorded else 'wrote'} {out_csv}")


if __name__ == "__main__":
    main()
