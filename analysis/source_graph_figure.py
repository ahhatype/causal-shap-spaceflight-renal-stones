"""Export the complete supplied renal DAG, with neutral edge styling.

Run with Python (svglib/reportlab installed), Poppler pdftoppm, and the
bundled @viz-js/viz runtime (or set VIZ_JS_MODULE to its dist/viz.cjs).
--refresh-drawio deliberately replaces the editable diagram; a normal
build preserves it. To publish manual draw.io edits, export that file
directly to PDF/SVG instead of rerunning this source-based layout.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import textwrap
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs/images"
SOURCE = REPO / "analysis/output/dag_sources"


def layout(graph: dict, engine: str) -> dict:
    """Use Graphviz's JSON geometry, through the available Viz.js bundle."""
    runtime = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node"
    module = Path(os.environ.get("VIZ_JS_MODULE", runtime / "node_modules/@viz-js/viz/dist/viz.cjs"))
    node = shutil.which("node") or str(runtime / "bin/node.exe")
    if not module.is_file():
        raise RuntimeError("Set VIZ_JS_MODULE to the installed @viz-js/viz/dist/viz.cjs")
    code = "const fs=require('fs'); const v=require(process.argv[1]); v.instance().then(x=>{ const g=JSON.parse(fs.readFileSync(0,'utf8')); process.stdout.write(JSON.stringify({svg:x.renderString(g,{engine:process.argv[2],format:'svg'}),geometry:x.renderJSON(g,{engine:process.argv[2]})})); });"
    result = subprocess.run([node, "-e", code, str(module), engine], input=json.dumps(graph), text=True, encoding="utf-8", capture_output=True, check=True)
    return json.loads(result.stdout)


def native_drawio(geom: dict, path: Path, title: str, legend: list | None = None) -> None:
    """Separate editable nodes, labels and attached arrow connectors."""
    _, _, width, height = map(float, geom["bb"].split(","))
    doc = ET.Element("mxfile", host="app.diagrams.net", agent="source_graph_figure.py", version="24.7.17")
    diagram = ET.SubElement(doc, "diagram", id=path.stem, name=title)
    model = ET.SubElement(diagram, "mxGraphModel", dx=str(width), dy=str(height), grid="1", gridSize="10", page="1", pageScale="1", pageWidth=str(round(width+40)), pageHeight=str(round(height+40)))
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    for n in geom["objects"]:
        x,y = map(float,n["pos"].split(",")); w,h=float(n["width"])*72,float(n["height"])*72
        value=n.get("label", n["name"]).replace("\\n", "\n")
        style=f"rounded=1;whiteSpace=wrap;html=0;arcSize=12;fillColor={n.get('fillcolor','#ffffff')};strokeColor={n.get('color','#555555')};fontColor={n.get('fontcolor','#202020')};fontFamily=Arial;fontSize={n.get('fontsize','12')};spacing=5;"
        cell=ET.SubElement(root,"mxCell",id=f"n{n['_gvid']}",value=value,style=style,vertex="1",parent="1")
        ET.SubElement(cell,"mxGeometry",x=str(x-w/2+20),y=str(height-y-h/2+20),width=str(w),height=str(h),attrib={"as":"geometry"})
    for i,e in enumerate(geom["edges"]):
        dash = "dashed=1;dashPattern=5 3;" if e.get("style")=="dashed" else "dashed=1;dashPattern=1 3;" if e.get("style")=="dotted" else ""
        cell=ET.SubElement(root,"mxCell",id=f"e{i}",edge="1",parent="1",source=f"n{e['tail']}",target=f"n{e['head']}",style=f"edgeStyle=none;curved=1;rounded=1;html=0;endArrow=block;endFill=1;strokeColor={e.get('color','#555555')};strokeWidth=1.2;{dash}")
        geo=ET.SubElement(cell,"mxGeometry",relative="1",attrib={"as":"geometry"})
        points=next((d["points"] for d in e.get("_draw_",[]) if d["op"]=="b"),[])
        if len(points)>2:
            arr=ET.SubElement(geo,"Array",attrib={"as":"points"})
            for x,y in points[1:-1]:
                ET.SubElement(arr,"mxPoint",x=str(x+20),y=str(height-y+20))
    for i,(label,color,dash) in enumerate(legend or []):
        x=20+i*width/3; y=height+45
        line=ET.SubElement(root,"mxCell",id=f"legend-line-{i}",edge="1",parent="1",style=f"endArrow=none;strokeColor={color};strokeWidth=1.5;"+("dashed=1;dashPattern="+dash+";" if dash else ""))
        geo=ET.SubElement(line,"mxGeometry",relative="1",attrib={"as":"geometry"})
        ET.SubElement(geo,"mxPoint",x=str(x),y=str(y),attrib={"as":"sourcePoint"}); ET.SubElement(geo,"mxPoint",x=str(x+35),y=str(y),attrib={"as":"targetPoint"})
        cell=ET.SubElement(root,"mxCell",id=f"legend-text-{i}",vertex="1",parent="1",value=label,style="text;html=0;align=left;verticalAlign=middle;fontFamily=Arial;fontSize=12;")
        ET.SubElement(cell,"mxGeometry",x=str(x+40),y=str(y-12),width=str(width/3-40),height="24",attrib={"as":"geometry"})
    if legend: model.set("pageHeight",str(round(height+90)))
    ET.indent(doc)
    path.write_text(ET.tostring(doc,encoding="unicode"),encoding="utf-8")


def export(graph: dict, engine: str, stem: str, refresh_drawio: bool = False, legend: list | None = None) -> None:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    OUT.mkdir(parents=True,exist_ok=True)
    result=layout(graph,engine)
    svgtext=result["svg"]
    if legend:
        ns="http://www.w3.org/2000/svg"; ET.register_namespace("",ns)
        xml=ET.fromstring(svgtext); box=list(map(float,xml.attrib["viewBox"].split())); w,h=box[2:]
        xml.set("viewBox",f"0 0 {w} {h+42}"); xml.set("height",f"{h+42}pt")
        for i,(label,color,dash) in enumerate(legend):
            x=12+i*(w-24)/3; y=h+20
            line=ET.SubElement(xml,f"{{{ns}}}line",x1=str(x),x2=str(x+35),y1=str(y),y2=str(y),stroke=color,attrib={"stroke-width":"1.5"})
            if dash: line.set("stroke-dasharray",dash)
            text=ET.SubElement(xml,f"{{{ns}}}text",x=str(x+41),y=str(y+4),fill="#202020",attrib={"font-family":"Arial","font-size":"12"}); text.text=label
        svgtext=ET.tostring(xml,encoding="unicode")
    svg=OUT/f"{stem}.svg"; svg.write_text(svgtext,encoding="utf-8")
    drawing=svg2rlg(str(svg)); renderPDF.drawToFile(drawing,str(OUT/f"{stem}.pdf"))
    subprocess.run(["pdftoppm","-singlefile","-scale-to","2400","-png",str(OUT/f"{stem}.pdf"),str(OUT/stem)],check=True,capture_output=True)
    editable=OUT/f"{stem}.drawio"
    if refresh_drawio or not editable.exists():
        native_drawio(result["geometry"],editable,stem.replace("_"," "),legend)
    print(f"{stem}: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges; PDF/SVG/PNG; editable diagram {'refreshed' if refresh_drawio else 'preserved if present'}")


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--refresh-drawio",action="store_true"); args=ap.parse_args()
    nodes=list(csv.DictReader((SOURCE/"robert_renal_stone_20220322_nodes.csv").open(encoding="utf-8-sig")))
    edges=list(csv.DictReader((SOURCE/"robert_renal_stone_20220322_edges.csv").open(encoding="utf-8-sig")))
    assert len(nodes)==53 and len(edges)==83
    names={n['node'] for n in nodes}; assert all(e['from'] in names and e['to'] in names for e in edges)
    graph={"directed":True,"graphAttributes":{"overlap":"prism","sep":"+14","splines":"true","outputorder":"edgesfirst","pad":"0.10","bgcolor":"white"},"nodeAttributes":{"shape":"box","style":"rounded,filled","fillcolor":"#ffffff","color":"#555555","fontname":"Arial","fontsize":"18","margin":"0.08,0.05","penwidth":"0.8"},"edgeAttributes":{"color":"#555555","penwidth":"0.85","arrowsize":"0.65"},"nodes":[],"edges":[]}
    for n in nodes:
        attrs={"label":"\n".join(textwrap.wrap(n['node'],20,break_long_words=False)),"pos":f"{float(n['x'])*22},{-float(n['y'])*15}!"}
        if n['node']=="Nephrolithiasis": attrs.update(fillcolor="#eaf0f5",penwidth="1.6")
        graph['nodes'].append({"name":n['node'],"attributes":attrs})
    graph['edges']=[{"tail":e['from'],"head":e['to']} for e in edges]
    export(graph,"neato","nasa_supplied_dag",args.refresh_drawio)


if __name__=="__main__": main()
