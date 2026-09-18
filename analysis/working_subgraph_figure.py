"""Draw the 14-node study model with audited source-to-model edge categories.

Build: python analysis/working_subgraph_figure.py
Use --refresh-drawio only when deliberately replacing the editable diagram.
The figure styles show structural provenance, never effect size or strength.
"""
from __future__ import annotations
import argparse
import csv
import textwrap
import yaml
from source_graph_figure import REPO, export

STYLE = {
    "retained_direct": {"color":"#202020","style":"solid","penwidth":"1.5"},
    "collapsed_source_path": {"color":"#2166a0","style":"dashed","penwidth":"1.5"},
    "study_added": {"color":"#717171","style":"dotted","penwidth":"1.5"},
}


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--refresh-drawio",action="store_true"); args=ap.parse_args()
    spec=yaml.safe_load((REPO/"config/dag_spec.yaml").read_text(encoding="utf-8"))
    mapping=list(csv.DictReader((REPO/"docs/technical/working-graph-edge-map.csv").open(encoding="utf-8-sig")))
    categories={(e['working_from'],e['working_to']):e['classification'] for e in mapping}
    edges={(e['from'],e['to']) for e in spec['edges']}
    assert len(spec['nodes'])==14 and len(edges)==21
    assert len(mapping)==len(categories)==21 and edges==set(categories)
    graph={"directed":True,"graphAttributes":{"rankdir":"LR","ranksep":"0.65","nodesep":"0.35","splines":"spline","outputorder":"edgesfirst","pad":"0.14","bgcolor":"white"},"nodeAttributes":{"shape":"box","style":"rounded,filled","fillcolor":"#ffffff","color":"#555555","fontname":"Arial","fontsize":"15","margin":"0.14,0.10","penwidth":"0.8"},"edgeAttributes":{"arrowsize":"0.7"},"nodes":[],"edges":[]}
    labels={"history_of_nephrolithiasis":"Personal/family\nstone history","hypercalciuria_predisposition":"Hypercalciuria\npredisposition","vitamin_d_inflight":"In-flight\nvitamin D","nutrients_risk":"Nutrients (risk)","hydration_fluid_intake":"Hydration /\nfluid intake"}
    for n in spec['nodes']:
        label=labels.get(n['id'],"\n".join(textwrap.wrap(n['label'].split(' (')[0],18,break_long_words=False)))
        attrs={"label":label}
        if n['id']=="nephrolithiasis": attrs.update(fillcolor="#eaf0f5",penwidth="1.6")
        graph['nodes'].append({"name":n['id'],"attributes":attrs})
    for e in spec['edges']:
        attrs=dict(STYLE[categories[e['from'],e['to']]])
        # Interactions are equation properties; they do not override provenance.
        graph['edges'].append({"tail":e['from'],"head":e['to'],"attributes":attrs})
    export(graph,"dot","working_subgraph_dag",args.refresh_drawio,legend=[
        ("Retained source edge", "#202020", ""),
        ("Collapsed source pathway", "#2166a0", "5 3"),
        ("Study-added or adapted", "#717171", "1 3"),
    ])


if __name__=="__main__": main()
