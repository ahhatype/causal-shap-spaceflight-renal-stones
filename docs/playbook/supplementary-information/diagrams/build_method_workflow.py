"""Export the current native workflow; never rewrite its editable source.

Requires ReportLab and optionally pdftoppm. This renderer supports the native
boxes, text and connected arrows used here. For arbitrary new draw.io shapes,
export directly from draw.io. The article's normal build does not run this file.
"""
from pathlib import Path
from html.parser import HTMLParser
import math
import shutil
import subprocess
import xml.etree.ElementTree as ET
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'method-workflow.drawio'
OUT=HERE.parent/'figures'

def properties(value):
    return dict(p.split('=',1) for p in value.split(';') if '=' in p)

class Blocks(HTMLParser):
    def __init__(self,size,color,bold=False):
        super().__init__(convert_charrefs=True)
        self.default=(size,color,bold); self.format=self.default
        self.blocks=[]; self.current=[]
    def flush(self):
        if self.current:
            self.blocks.append((''.join(self.current),*self.format)); self.current=[]
    def handle_starttag(self,tag,attrs):
        if tag=='br':self.current.append('\n')
        if tag=='div':
            self.flush()
            css=dict(p.strip().split(':',1) for p in dict(attrs).get('style','').split(';') if ':' in p)
            self.format=(float(css.get('font-size',str(self.default[0])).replace('px','')),
                         css.get('color',self.default[1]),css.get('font-weight','')=='bold')
    def handle_endtag(self,tag):
        if tag=='div':self.flush();self.format=self.default
    def handle_data(self,data):self.current.append(data)

def wrap(value,width,size,font):
    result=[]
    for paragraph in value.split('\n'):
        line=''
        for word in paragraph.split():
            proposed=(line+' '+word).strip()
            if line and stringWidth(proposed,font,size)>width:result.append(line);line=word
            else:line=proposed
        result.append(line)
    return result

def main():
    before=SOURCE.read_bytes(); tree=ET.fromstring(before); model=tree.find('.//mxGraphModel')
    width,height=(float(model.get(k)) for k in ('pageWidth','pageHeight'))
    drawing=Drawing(width,height)
    cells=model.findall('./root/mxCell');by_id={c.get('id'):c for c in cells}
    assert len(by_id)==len(cells),'Duplicate IDs'
    boxes={}
    for cell in cells:
        if cell.get('vertex')!='1':continue
        g=cell.find('mxGeometry');x,y,w,h=(float(g.get(k)) for k in ('x','y','width','height'))
        assert min(x,y)>=0 and x+w<=width and y+h<=height,cell.get('id')
        boxes[cell.get('id')]=(x,y,w,h)
    def point(id,rx,ry):
        x,y,w,h=boxes[id];return x+rx*w,y+ry*h
    for cell in cells:
        if cell.get('edge')!='1':continue
        s=properties(cell.get('style',''));source,target=cell.get('source'),cell.get('target')
        assert source in boxes and target in boxes,cell.get('id')
        route=[point(source,float(s.get('exitX','.5')),float(s.get('exitY','1')))]
        route += [(float(p.get('x')),float(p.get('y'))) for p in cell.findall('./mxGeometry/Array/mxPoint')]
        route += [point(target,float(s.get('entryX','.5')),float(s.get('entryY','0')))]
        color=colors.HexColor(s.get('strokeColor','#586873'))
        for (x1,y1),(x2,y2) in zip(route,route[1:]):
            assert 0<=x1<=width and 0<=y1<=height and 0<=x2<=width and 0<=y2<=height,cell.get('id')
            drawing.add(Line(x1,height-y1,x2,height-y2,strokeColor=color,strokeWidth=float(s.get('strokeWidth','1.3')),
                             strokeDashArray=[4,3] if s.get('dashed')=='1' else None))
        if s.get('endArrow','block')!='none':
            (x1,y1),(x2,y2)=route[-2:];a=math.atan2(y2-y1,x2-x1)
            pts=[x2,height-y2,x2-7*math.cos(a)+3*math.sin(a),height-(y2-7*math.sin(a)-3*math.cos(a)),
                 x2-7*math.cos(a)-3*math.sin(a),height-(y2-7*math.sin(a)+3*math.cos(a))]
            drawing.add(Polygon(pts,fillColor=color,strokeColor=color))
    for cell in cells:
        if cell.get('vertex')!='1':continue
        id=cell.get('id');x,y,w,h=boxes[id];s=properties(cell.get('style',''));is_box=s.get('strokeColor','none')!='none'
        if is_box:
            drawing.add(Rect(x,height-y-h,w,h,rx=7,ry=7,fillColor=colors.HexColor(s.get('fillColor','#f0f5f6')),
                             strokeColor=colors.HexColor(s.get('strokeColor','#27647b')),strokeWidth=float(s.get('strokeWidth','1.2'))))
        parser=Blocks(float(s.get('fontSize','13')),s.get('fontColor','#203647'),s.get('fontStyle')=='1')
        parser.feed(cell.get('value',''));parser.flush();parts=[]
        for value,size,color,bold in parser.blocks:
            font='Helvetica-Bold' if bold else 'Helvetica';lines=wrap(value,w-(20 if is_box else 0),size,font)
            parts.append((lines,size,color,font))
        total=sum(len(lines)*size*1.22 for lines,size,_,_ in parts)+6*max(0,len(parts)-1)
        assert total<=h-(10 if is_box else 0)+.1,(id,total,h)
        cursor=y+(h-total)/2
        for lines,size,color,font in parts:
            for line in lines:
                drawing.add(String(x+w/2,height-cursor-size,line,fontName=font,fontSize=size,
                                   fillColor=colors.HexColor(color),textAnchor='middle'))
                cursor+=size*1.22
            cursor+=6
    OUT.mkdir(exist_ok=True)
    renderPDF.drawToFile(drawing,str(OUT/'method-workflow.pdf'))
    renderSVG.drawToFile(drawing,str(OUT/'method-workflow.svg'))
    if shutil.which('pdftoppm'):
        subprocess.run(['pdftoppm','-scale-to','1800','-png','-singlefile',str(OUT/'method-workflow.pdf'),str(OUT/'method-workflow')],check=True)
    assert SOURCE.read_bytes()==before,'Source changed unexpectedly'
    print('Workflow XML, IDs, endpoints, geometry and text fit verified; PDF/SVG/PNG exports refreshed. Native source unchanged.')

if __name__=='__main__':main()
