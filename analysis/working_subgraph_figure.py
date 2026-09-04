"""Draw the 14-node working subgraph from config/dag_spec.yaml.

Layered layout by longest-path depth from the roots (the same rule
r/R/dag_utils.R uses), edge style by evidence status, node fill by type.
Writes PNG and PDF to docs/images/ for the manuscript and the playbook.

    python analysis/working_subgraph_figure.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import textwrap

import matplotlib.pyplot as plt
import networkx as nx
import yaml
from matplotlib.patches import FancyArrowPatch

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "images"
INK, PAPER, MUTE = "#1a1814", "#fbf7ef", "#6b6258"
FILL = {
    "exposure": "#edf8f5", "outcome": "#1a1814", "mediator": "#edf6fc",
    "mediator_countermeasure": "#edf6fc", "confounder": "#fff3e8",
    "exogenous_confounder": "#fff3e8", "confounder_countermeasure": "#fff3e8",
}
EDGE_STYLE = {
    "confirmed_mechanism": dict(color="#00897b", lw=2.4, ls="-"),
    "magnitude_estimate": dict(color=INK, lw=1.4, ls="-"),
    "directional_only": dict(color=INK, lw=1.2, ls=(0, (4, 3))),
}


def main() -> None:
    spec = yaml.safe_load((REPO / "config" / "dag_spec.yaml").read_text(encoding="utf-8"))
    g = nx.DiGraph()
    for node in spec["nodes"]:
        g.add_node(node["id"], **node)
    for edge in spec["edges"]:
        g.add_edge(edge["from"], edge["to"], status=edge.get("status", "magnitude_estimate"),
                   interaction=bool(edge.get("interacts_with")))
    depth = {}
    for node in nx.topological_sort(g):
        preds = list(g.predecessors(node))
        depth[node] = 0 if not preds else 1 + max(depth[p] for p in preds)
    layers: dict[int, list[str]] = {}
    for node, d in depth.items():
        layers.setdefault(d, []).append(node)
    pos = {}
    for d, nodes in layers.items():
        nodes = sorted(nodes)
        for i, node in enumerate(nodes):
            pos[node] = (d * 4.0, (i - (len(nodes) - 1) / 2) * 2.1)

    fig, ax = plt.subplots(figsize=(15, 7.6), facecolor=PAPER)
    ax.set_facecolor(PAPER)
    ax.axis("off")
    for src, dst, data in g.edges(data=True):
        style = dict(EDGE_STYLE[data["status"]])
        if data["interaction"]:
            style = dict(color="#e07020", lw=1.2, ls=(0, (1.5, 2.5)))
        ax.add_patch(FancyArrowPatch(pos[src], pos[dst], arrowstyle="-|>", mutation_scale=14,
                                     shrinkA=34, shrinkB=34, connectionstyle="arc3,rad=0.08", **style))
    for node, (x, y) in pos.items():
        kind = g.nodes[node]["type"]
        fill = FILL.get(kind, PAPER)
        ax.scatter([x], [y], s=3600, c=fill, edgecolors=INK, linewidths=1.4, zorder=3)
        label = g.nodes[node]["label"].split(" (")[0]
        label = "\n".join(textwrap.wrap(label, 14, break_long_words=False))
        ax.text(x, y, label, ha="center", va="center", fontsize=5.9, zorder=4,
                color=PAPER if kind == "outcome" else INK, linespacing=1.05)
    ax.set_xlim(-2.0, max(x for x, _ in pos.values()) + 2.0)
    ax.set_ylim(min(y for _, y in pos.values()) - 1.5, max(y for _, y in pos.values()) + 2.4)
    ax.text(0.0, 1.0, "The 14-node working subgraph of NASA SA-07566", transform=ax.transAxes,
            fontsize=11, color=INK, va="top")
    ax.text(0.0, 0.955,
            "green: NASA-confirmed mechanism; solid: literature-informed magnitude; dashed: direction only; "
            "orange dotted: calcium x hydration interaction. Fills: teal exposure, blue mediators, orange confounders, black outcome.",
            transform=ax.transAxes, fontsize=7.2, color=MUTE, va="top")
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "working_subgraph_dag.png", dpi=200, bbox_inches="tight", facecolor=PAPER)
    fig.savefig(OUT / "working_subgraph_dag.pdf", bbox_inches="tight", facecolor=PAPER)
    print("wrote", OUT / "working_subgraph_dag.png")


if __name__ == "__main__":
    main()
