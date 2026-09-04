"""Space SHAP manuscript schematics: FIG. 1 spine + FIG. 2 sufficiency transfer.

Drawn 2026-08-11 for the manuscript; ported into the hub 2026-09-04. Writes
PNG and PDF for both figures into docs/images/ (the manuscript and the
playbook read them from there).

    python analysis/make_spine_figs.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

INK = "#111111"; AMBER = "#b45309"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK})


def mk(figsize, xlim, ylim):
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.axis("off"); ax.set_aspect("equal")
    return fig, ax


def box(ax, x, y, w, h, num, title, sub=None, double=False, dashed=False, tfs=8.4, sfs=6.6):
    kw = dict(fill=False, edgecolor=INK, lw=1.3)
    if dashed:
        kw["linestyle"] = (0, (5, 3))
    ax.add_patch(Rectangle((x, y), w, h, **kw))
    if double:
        ax.add_patch(Rectangle((x + .5, y + .5), w - 1, h - 1, fill=False, edgecolor=INK, lw=.7))
    if sub:
        ax.text(x + w/2, y + h - 1.2, title, ha="center", va="top", fontsize=tfs,
                fontweight="bold", linespacing=1.15)
        ax.text(x + w/2, y + 1.3, sub, ha="center", va="bottom", fontsize=sfs, linespacing=1.3)
    else:
        ax.text(x + w/2, y + h/2, title, ha="center", va="center", fontsize=tfs,
                fontweight="bold", linespacing=1.15)
    if num:
        ax.text(x + w - .7, y + .5, num, ha="right", va="bottom", fontsize=7, style="italic")
    return (x, y, w, h)


def arrow(ax, p1, p2, dashed=False):
    style = dict(arrowstyle="-|>", color=INK, lw=1.1, shrinkA=2, shrinkB=2, mutation_scale=10)
    if dashed:
        style["linestyle"] = (0, (4, 3))
    ax.annotate("", xy=p2, xytext=p1, arrowprops=style, zorder=2)


def line(ax, p1, p2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=INK, lw=1.1, zorder=2)


def lab(ax, x, y, t, fs=6.6, ha="center"):
    ax.text(x, y, t, ha=ha, va="center", fontsize=fs, style="italic",
            bbox=dict(fc="white", ec="none", pad=.5), zorder=3)


def E(b, s):
    x, y, w, h = b
    return {"l": (x, y+h/2), "r": (x+w, y+h/2), "t": (x+w/2, y+h), "b": (x+w/2, y)}[s]


# ============================ FIG. 1 — the spine ============================
fig, ax = mk((13.4, 8.6), (0, 100), (0, 64))

# Phase 0 strip
ax.add_patch(Rectangle((1.5, 48), 97, 13.5, fill=False, edgecolor=INK, lw=.8,
                       linestyle=(0, (2, 2))))
ax.text(3, 59.8, "(0)  THE KNOWN WORLD — SEALED BEFORE ANY LEARNING", fontsize=8, fontweight="bold")
b_dag = box(ax, 5, 50, 24, 7.5, "0a", "LOCKED CAUSAL GRAPH G", "NASA SA-07566 renal stone\n(Reynolds handoff)", double=True)
b_gen = box(ax, 38, 50, 24, 7.5, "0b", "STRUCTURAL GENERATOR", "simcausal; coefficients =\nsimulation parameters")
b_tru = box(ax, 71, 50, 24, 7.5, "0c", "FROZEN do()-TRUTH", "50,000-draw total effects\nfor every ancestor of Y", double=True)
arrow(ax, E(b_dag, "r"), E(b_gen, "l")); arrow(ax, E(b_gen, "r"), E(b_tru, "l"))

# main flow
b_data = box(ax, 3, 33, 14, 9, "1", "OBSERVATIONAL\nDATA", "structure\nwithheld")
b_disc = box(ax, 22, 33, 17, 9, "2", "CAUSAL\nDISCOVERY", "PC · GES · LiNGAM\n· NOTEARS")
b_cpd  = box(ax, 44, 33, 17, 9, "3", "CPDAG\nENSEMBLE", "undirected edges;\nalgorithms disagree")
b_exp  = box(ax, 66, 33, 15, 9, "4", "EXPERT +\nLEDGER", "3 cited rounds\n(+ complexity flags)", double=True)
b_gp   = box(ax, 86, 33, 11, 9, "5", "PLAUSIBLE\nDAG G′", None)

arrow(ax, (50, 50), (10, 42))            # generator -> data
lab(ax, 26, 46.5, "draws only — the graph never leaves the vault")
arrow(ax, E(b_data, "r"), E(b_disc, "l"))
arrow(ax, E(b_disc, "r"), E(b_cpd, "l"))
arrow(ax, E(b_cpd, "r"), E(b_exp, "l"))
arrow(ax, E(b_exp, "r"), E(b_gp, "l"))
# expert loop-back
line(ax, (73.5, 33), (73.5, 30.2)); line(ax, (73.5, 30.2), (52.5, 30.2))
arrow(ax, (52.5, 30.2), (52.5, 33), dashed=True)
lab(ax, 63, 29.2, "re-run under revised constraints")

# dual evaluation
b_eval = box(ax, 22, 8, 42, 15, "6", "DUAL EVALUATION — LEARNED vs KNOWN", " ", tfs=8.8)
ax.text(24, 18.6, "concordance axis", fontsize=6.8, style="italic")
ax.text(24, 16.4, "M1  edge precision / recall / F1 · SHD", fontsize=6.6)
ax.text(24, 14.6, "M2  target-pathway scorecard (D→…→Y)", fontsize=6.6)
ax.text(43.5, 18.6, "structural-importance axis", fontsize=6.8, style="italic", color=AMBER)
ax.text(43.5, 16.4, "M3  sufficiency transfer of Z′ (Fig. 2)", fontsize=6.6, color=AMBER)
ax.text(43.5, 14.6, "M4  parameter fidelity — bias in D→Y", fontsize=6.6, color=AMBER)
ax.text(43.5, 12.8, "M5  identification honesty (CPDAGs)", fontsize=6.6, color=AMBER)
ax.text(24, 10.6, "reported per algorithm × expert round r = 0, 1, 2, 3", fontsize=6.4, style="italic")

arrow(ax, E(b_gp, "b"), (60, 23))                       # G' -> eval
line(ax, (83, 50), (83, 28))                             # truth -> eval (elbow)
arrow(ax, (83, 28), (63.5, 23.5))
lab(ax, 81.6, 45.2, "the sealed answer key", fs=6.4, ha="right")

# attribution downstream
b_att = box(ax, 72, 8, 25, 15, "7", "ATTRIBUTION UNDER\nG vs G′", "ordinary + causal SHAP;\nstructure error priced\nin attribution error")
arrow(ax, E(b_eval, "r"), E(b_att, "l"))
ax.text(50, 1.2, "FIG. 1", ha="center", fontsize=10.5, fontweight="bold")
fig.savefig(OUT / "fig1_space_shap_spine.png", dpi=220, bbox_inches="tight", facecolor="white")
fig.savefig(OUT / "fig1_space_shap_spine.pdf", bbox_inches="tight", facecolor="white")
plt.close(fig)

# ==================== FIG. 2 — sufficiency transfer =========================
fig, ax = mk((12.6, 7.2), (0, 100), (0, 56))

def mini_dag(ax, cx, cy, reversed_edge=False, zfill=True):
    """Abstract 5-node motif: C confounder, D exposure, M mediator, Y outcome, P proxy."""
    P = {"C": (cx, cy+9), "D": (cx-9, cy+2), "M": (cx, cy-2), "Y": (cx+9, cy+2), "Px": (cx+2, cy-9)}
    def a(u, v, dashed=False, rev=False):
        (x1, y1), (x2, y2) = P[u], P[v]
        dx, dy = x2-x1, y2-y1; L = (dx*dx+dy*dy) ** .5
        s = (x1+dx/L*2.6, y1+dy/L*2.6); e = (x2-dx/L*2.6, y2-dy/L*2.6)
        if rev:
            s, e = e, s
        st = dict(arrowstyle="-|>", color=INK, lw=1.05, mutation_scale=8)
        if dashed:
            st["linestyle"] = (0, (3, 2)); st["color"] = AMBER
        ax.annotate("", xy=e, xytext=s, arrowprops=st)
    a("C", "D"); a("C", "Y"); a("D", "M", rev=reversed_edge, dashed=reversed_edge)
    a("M", "Y"); a("Y", "Px")
    for n, (x, y) in P.items():
        fc = AMBER if (zfill and n == "C") else "white"
        ax.add_patch(Circle((x, y), 2.4, facecolor=fc, edgecolor=INK, lw=1.2, zorder=3,
                            alpha=.55 if fc == AMBER else 1))
        ax.text(x, y, {"Px": "P"}.get(n, n), ha="center", va="center", fontsize=7.4,
                zorder=4, fontweight="bold")

bL = box(ax, 4, 16, 34, 33, "i", "LEARNED GRAPH G′", " ", tfs=8.6)
mini_dag(ax, 21, 33, reversed_edge=True)
ax.text(21, 20.5, "one pathway edge wrong (D–M reversed)", fontsize=6.4, ha="center",
        style="italic", color=AMBER)
ax.text(21, 18.2, "derive minimal adjustment set  Z′ = {C}  for (D, Y)", fontsize=6.9, ha="center")

bR = box(ax, 62, 16, 34, 33, "ii", "TRUE GRAPH G — SEALED", " ", tfs=8.6, double=True)
mini_dag(ax, 79, 33, reversed_edge=False)
ax.text(79, 20.5, "backdoor test of Z′ in G (Shrier–Platt):", fontsize=6.9, ha="center")
ax.text(79, 18.2, "Z′ = {C}  →  VALID", fontsize=7.4, ha="center", fontweight="bold")

arrow(ax, (38, 32.5), (62, 32.5))
lab(ax, 50, 34.6, "M3 — SUFFICIENCY TRANSFER", fs=7.2)
lab(ax, 50, 30.6, "carry Z′ across; G′ never sees the verdict", fs=6.2)

ax.add_patch(Rectangle((4, 3.5), 92, 9, fill=False, edgecolor=INK, lw=.9))
ax.text(6, 10.2, "M4 — PARAMETER FIDELITY", fontsize=7, fontweight="bold")
ax.text(6, 7.2, "estimate E[Y | do(D)] on the synthetic data adjusting for Z′;\nreport bias and RMSE against the frozen truth (0c)", fontsize=6.5, va="center")
ax.text(53, 10.2, "M5 — IDENTIFICATION HONESTY", fontsize=7, fontweight="bold")
ax.text(53, 7.2, "if G′ is a CPDAG, enumerate its consistent DAG extensions;\nreport the fraction under which Z′ remains valid", fontsize=6.5, va="center")

ax.text(50, .4, "FIG. 2 — topological error and functional failure are different events: G′ is wrong about the pathway yet sufficient for the target parameter",
        ha="center", fontsize=7, style="italic")
fig.savefig(OUT / "fig2_sufficiency_transfer.png", dpi=220, bbox_inches="tight", facecolor="white")
fig.savefig(OUT / "fig2_sufficiency_transfer.pdf", bbox_inches="tight", facecolor="white")
print("written")
