"""Recreate the editable selection overlay using only Python's standard library.

The .drawio files are the editing sources. Running this script resets manual
diagram edits; it is provided as an optional reproducible starting point.
"""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
INK, BLUE, TEAL, PALE, MUTED = '#203647', '#27647b', '#397b71', '#f0f5f6', '#586873'


class Diagram:
    def __init__(self, name, width, height):
        self.file = ET.Element('mxfile', host='app.diagrams.net', type='device', version='26.0.0')
        page = ET.SubElement(self.file, 'diagram', id=name, name=name)
        model = ET.SubElement(page, 'mxGraphModel', dx=str(width), dy=str(height), grid='1', gridSize='10',
                              guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1',
                              pageScale='1', pageWidth=str(width), pageHeight=str(height), math='0', shadow='0')
        self.root = ET.SubElement(model, 'root')
        ET.SubElement(self.root, 'mxCell', id='0')
        ET.SubElement(self.root, 'mxCell', id='1', parent='0')
        self.height = height

    def node(self, id, x, y, w, h, title, body='', color=BLUE):
        label = f'<div style="font-size:14px;font-weight:bold;color:{color};">{escape(title)}</div>'
        if body:
            label += f'<div style="font-size:12.8px;color:{INK};margin-top:8px;">{escape(body).replace(chr(10), "<br>")}</div>'
        style = ('rounded=1;arcSize=10;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;'
                 f'fontFamily=Helvetica;fontColor={INK};strokeColor={color};fillColor={PALE};'
                 'strokeWidth=1.2;spacing=5;')
        c = ET.SubElement(self.root, 'mxCell', id=id, value=label, style=style, vertex='1', parent='1')
        ET.SubElement(c, 'mxGeometry', x=str(x), y=str(self.height-y-h), width=str(w), height=str(h), attrib={'as': 'geometry'})

    def label(self, id, x, y, w, h, text, size=13, color=INK, bold=False, align='center', connectable=False):
        style = ('text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;'
                 f'align={align};verticalAlign=middle;fontFamily=Helvetica;fontSize={size};'
                 f'fontColor={color};fontStyle={1 if bold else 0};spacing=0;')
        c = ET.SubElement(self.root, 'mxCell', id=id, value=escape(text).replace('\n', '<br>'),
                          style=style, vertex='1', parent='1', connectable='1' if connectable else '0')
        ET.SubElement(c, 'mxGeometry', x=str(x), y=str(self.height-y-h), width=str(w), height=str(h), attrib={'as': 'geometry'})

    def edge(self, id, source, target, color=MUTED, dashed=False, exit=(.5,1), entry=(.5,0), points=()):
        style = ('edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;'
                 f'strokeColor={color};strokeWidth=1.2;endArrow=block;endFill=1;endSize=7;'
                 f'exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;'
                 f'entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;'
                 + ('dashed=1;dashPattern=4 3;' if dashed else ''))
        c = ET.SubElement(self.root, 'mxCell', id=id, style=style, edge='1', parent='1', source=source, target=target)
        g = ET.SubElement(c, 'mxGeometry', relative='1', attrib={'as': 'geometry'})
        if points:
            a = ET.SubElement(g, 'Array', attrib={'as': 'points'})
            for x, y in points:
                ET.SubElement(a, 'mxPoint', x=str(x), y=str(self.height-y))

    def save(self, path):
        ET.indent(self.file, space='  ')
        ET.ElementTree(self.file).write(path, encoding='utf-8', xml_declaration=True)


def selection():
    d = Diagram('Renal selection overlay', 720, 340)
    d.label('title', 0, 311, 720, 28, 'Renal pathway subset with a proposed selection overlay', 16, INK, True)
    d.node('history', 10, 245, 180, 60, 'Stone history H', 'Pre-flight information')
    d.node('eligibility', 280, 245, 160, 60, 'Eligibility E=1', color=TEAL)
    d.node('screening', 525, 245, 180, 60, 'Baseline screening B', 'e.g. fitness', TEAL)
    d.node('assignment', 280, 149, 160, 60, 'Assignment G=1', color=TEAL)
    d.label('observed', 525, 152, 180, 52, 'Observed crew:\nE=1 and G=1', 12.5, TEAL)
    d.node('hydration', 10, 40, 175, 62, 'Hydration strategy A', 'After selection')
    d.node('urine', 275, 40, 170, 62, 'Urine chemistry', 'Existing mediator')
    d.node('outcome', 530, 40, 175, 62, 'Nephrolithiasis Y', 'Outcome')
    d.edge('history-eligibility', 'history', 'eligibility', TEAL, True, (1,.5), (0,.5))
    d.edge('screening-eligibility', 'screening', 'eligibility', TEAL, True, (0,.5), (1,.5))
    d.edge('eligibility-assignment', 'eligibility', 'assignment', TEAL, True)
    d.edge('hydration-urine', 'hydration', 'urine', exit=(1,.5), entry=(0,.5))
    d.edge('urine-outcome', 'urine', 'outcome', exit=(1,.5), entry=(0,.5))
    d.edge('history-urine', 'history', 'urine', points=((100,123),(360,123)))
    d.edge('hydration-outcome', 'hydration', 'outcome', entry=(.5,1), points=((97.5,18),(617.5,18)))
    d.save(HERE/'renal-selection-overlay.drawio')


def validate(path):
    root = ET.parse(path).getroot()
    cells = root.findall('.//mxCell')
    ids = {c.get('id') for c in cells}
    assert len(ids) == len(cells), f'Duplicate IDs: {path}'
    model = root.find('.//mxGraphModel')
    width, height = float(model.get('pageWidth')), float(model.get('pageHeight'))
    for c in cells:
        g = c.find('mxGeometry')
        if c.get('vertex') == '1':
            x, y, w, h = (float(g.get(k)) for k in ('x','y','width','height'))
            assert x >= 0 and y >= 0 and x+w <= width and y+h <= height, c.get('id')
        if c.get('edge') == '1':
            assert c.get('source') in ids and c.get('target') in ids, c.get('id')
    vertices = sum(c.get('vertex') == '1' for c in cells)
    edges = sum(c.get('edge') == '1' for c in cells)
    print(f'{path.name}: valid XML; {vertices} editable nodes/labels; {edges} connected edges; geometry within page.')


if __name__ == '__main__':
    selection()
    validate(HERE/'renal-selection-overlay.drawio')
