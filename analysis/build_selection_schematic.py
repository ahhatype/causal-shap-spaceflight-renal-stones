"""Rebuild the supplementary selection schematic (ReportLab required)."""
from pathlib import Path
import math
import shutil
import subprocess

from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/images'
INK = colors.HexColor('#203647')
BLUE = colors.HexColor('#27647b')
TEAL = colors.HexColor('#397b71')
PALE = colors.HexColor('#f0f5f6')
MUTED = colors.HexColor('#586873')


def text(d, x, y, lines, size=14, color=INK, bold=False, anchor='middle', leading=None):
    for i, line in enumerate(lines.split('\n')):
        d.add(String(x, y - i * (leading or size * 1.35), line,
                     fontName='Helvetica-Bold' if bold else 'Helvetica',
                     fontSize=size, fillColor=color, textAnchor=anchor))


def box(d, x, y, w, h, title, body='', color=BLUE):
    d.add(Rect(x, y, w, h, rx=7, ry=7, fillColor=PALE, strokeColor=color, strokeWidth=1.2))
    text(d, x+w/2, y+h-22, title, 14, color, True)
    if body:
        text(d, x+w/2, y+h-43, body, 12.8)


def arrow(d, x1, y1, x2, y2, color=MUTED, dashed=False):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.2,
               strokeDashArray=[4, 3] if dashed else None))
    angle = math.atan2(y2-y1, x2-x1)
    pts = [x2, y2,
           x2-7*math.cos(angle)+3*math.sin(angle), y2-7*math.sin(angle)-3*math.cos(angle),
           x2-7*math.cos(angle)-3*math.sin(angle), y2-7*math.sin(angle)+3*math.cos(angle)]
    d.add(Polygon(pts, fillColor=color, strokeColor=color))


def selection():
    d = Drawing(720, 340)
    # A displayed subset of existing renal edges; screening is a separate overlay.
    box(d, 10, 245, 180, 60, 'Stone history H', 'Pre-flight information')
    box(d, 280, 245, 160, 60, 'Eligibility E=1', '', TEAL)
    box(d, 525, 245, 180, 60, 'Baseline screening B', 'e.g. fitness', TEAL)
    arrow(d, 190, 275, 280, 275, TEAL, True)
    arrow(d, 525, 275, 440, 275, TEAL, True)
    box(d, 280, 149, 160, 60, 'Assignment G=1', '', TEAL)
    arrow(d, 360, 245, 360, 209, TEAL, True)
    text(d, 610, 183, 'Observed crew:\nE=1 and G=1', 12.5, TEAL)
    box(d, 10, 40, 175, 62, 'Hydration strategy A', 'After selection')
    box(d, 275, 40, 170, 62, 'Urine chemistry', 'Existing mediator')
    box(d, 530, 40, 175, 62, 'Nephrolithiasis Y', 'Outcome')
    arrow(d, 185, 70, 275, 70)
    arrow(d, 445, 70, 530, 70)
    # History -> urine chemistry is an existing working-graph edge.
    d.add(Line(100, 245, 100, 123, strokeColor=MUTED, strokeWidth=1.2))
    d.add(Line(100, 123, 360, 123, strokeColor=MUTED, strokeWidth=1.2))
    arrow(d, 360, 123, 360, 102)
    # The direct hydration -> outcome edge is retained, routed beneath the nodes.
    d.add(Line(100, 40, 100, 18, strokeColor=MUTED, strokeWidth=1.2))
    d.add(Line(100, 18, 615, 18, strokeColor=MUTED, strokeWidth=1.2))
    arrow(d, 615, 18, 615, 40)
    text(d, 360, 324, 'Renal pathway subset with a proposed selection overlay', 16, INK, True)
    return d



def main():
    OUT.mkdir(exist_ok=True)
    diagram = selection()
    stem = OUT / 'renal-selection-overlay'
    renderSVG.drawToFile(diagram, str(stem.with_suffix('.svg')))
    renderPDF.drawToFile(diagram, str(stem.with_suffix('.pdf')))
    if shutil.which('pdftoppm'):
        subprocess.run(['pdftoppm', '-scale-to', '1600', '-png', '-singlefile',
                        str(stem.with_suffix('.pdf')), str(stem)], check=True)

if __name__ == '__main__':
    main()
