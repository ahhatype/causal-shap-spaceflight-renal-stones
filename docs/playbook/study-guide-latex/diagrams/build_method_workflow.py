"""Build editable method-specific schematics and their matching vector exports.

Requires ReportLab; PNG export additionally uses pdftoppm when available.
The draw.io documents use editable nodes and source/target-connected edges.
Running this script overwrites only method-workflow and graph-surgery outputs.
"""
from pathlib import Path
from html import escape
import math
import shutil
import subprocess
import xml.etree.ElementTree as ET

from reportlab.graphics.shapes import Drawing, Rect, Circle, String, Line, Polygon
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parent/'figures'
INK, BLUE, TEAL = '#203647', '#27647b', '#397b71'
PALE, MUTED, RED = '#f0f5f6', '#586873', '#a1473c'


class Schematic:
    def __init__(self, stem, width, height):
        self.stem, self.width, self.height = stem, width, height
        self.drawing = Drawing(width, height)
        self.nodes = {}
        self.file = ET.Element('mxfile', host='app.diagrams.net', type='device', version='26.0.0')
        page = ET.SubElement(self.file, 'diagram', id=stem, name=stem.replace('-', ' ').title())
        model = ET.SubElement(page, 'mxGraphModel', grid='1', gridSize='10', guides='1', connect='1',
                              arrows='1', page='1', pageScale='1', pageWidth=str(width), pageHeight=str(height), math='0')
        self.root = ET.SubElement(model, 'root')
        ET.SubElement(self.root, 'mxCell', id='0')
        ET.SubElement(self.root, 'mxCell', id='1', parent='0')

    def _lines(self, value, width, size, bold=False):
        font = 'Helvetica-Bold' if bold else 'Helvetica'
        result = []
        for para in value.split('\n'):
            line = ''
            for word in para.split():
                candidate = f'{line} {word}'.strip()
                if stringWidth(candidate, font, size) > width and line:
                    result.append(line); line = word
                else:
                    line = candidate
            result.append(line)
        return result

    def text(self, id, x, y, w, h, value, size=12.5, color=INK, bold=False, align='center'):
        lines = self._lines(value, w, size, bold)
        leading = size*1.22
        assert leading*len(lines) <= h+1, (id, lines, h)
        top = y+(h-leading*len(lines))/2+size
        for i, line in enumerate(lines):
            self.drawing.add(String(x+w/2 if align=='center' else x, self.height-top-i*leading,
                                    line, fontName='Helvetica-Bold' if bold else 'Helvetica', fontSize=size,
                                    fillColor=colors.HexColor(color), textAnchor='middle' if align=='center' else 'start'))
        label = '<br>'.join(escape(line) for line in lines)
        style = ('text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;spacing=0;'
                 f'fontFamily=Helvetica;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};'
                 f'align={align};verticalAlign=middle;')
        c = ET.SubElement(self.root, 'mxCell', id=id, value=label, vertex='1', parent='1', style=style)
        ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), attrib={'as':'geometry'})

    def box(self, id, x, y, w, h, title, body='', foot='', color=BLUE, size=12.5, title_size=14):
        self.nodes[id] = (x,y,w,h)
        self.drawing.add(Rect(x, self.height-y-h, w,h,rx=7,ry=7,
                             fillColor=colors.HexColor(PALE),strokeColor=colors.HexColor(color),strokeWidth=1.2))
        tl = self._lines(title,w-20,title_size,True)
        bl = self._lines(body,w-20,size) if body else []
        fl = self._lines(foot,w-20,10.7) if foot else []
        th,bh,fh = len(tl)*title_size*1.18, len(bl)*size*1.22, len(fl)*13
        total = th+(5+bh if bl else 0)+(5+fh if fl else 0)
        assert total <= h-10, (id,total,h)
        cursor = y+(h-total)/2
        for lines,font_size,bold,text_color,gap in ((tl,title_size,True,color,0),(bl,size,False,INK,5),(fl,10.7,False,MUTED,5)):
            if not lines: continue
            cursor += gap
            for line in lines:
                self.drawing.add(String(x+w/2,self.height-cursor-font_size,line,
                    fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=font_size,
                    fillColor=colors.HexColor(text_color),textAnchor='middle'))
                cursor += font_size*(1.18 if bold else 1.22)
        label = f'<div style="font-size:{title_size}px;font-weight:bold;color:{color};">'+ '<br>'.join(map(escape,tl))+'</div>'
        if bl: label += f'<div style="font-size:{size}px;margin-top:5px;color:{INK};">'+'<br>'.join(map(escape,bl))+'</div>'
        if fl: label += f'<div style="font-size:10.7px;margin-top:5px;color:{MUTED};">'+'<br>'.join(map(escape,fl))+'</div>'
        style = (f'rounded=1;arcSize=10;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;'
                 f'fontFamily=Helvetica;strokeColor={color};fillColor={PALE};strokeWidth=1.2;spacing=5;')
        c = ET.SubElement(self.root,'mxCell',id=id,value=label,style=style,vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})

    def circle(self,id,cx,cy,label,color=BLUE):
        r=22
        self.nodes[id]=(cx-r,cy-r,2*r,2*r)
        self.drawing.add(Circle(cx,self.height-cy,r,fillColor=colors.HexColor(PALE),strokeColor=colors.HexColor(color),strokeWidth=1.3))
        self.drawing.add(String(cx,self.height-cy-5,label,fontName='Helvetica-Bold',fontSize=17,fillColor=colors.HexColor(color),textAnchor='middle'))
        c=ET.SubElement(self.root,'mxCell',id=id,value=label,vertex='1',parent='1',
                        style=f'ellipse;html=1;fillColor={PALE};strokeColor={color};fontFamily=Helvetica;fontSize=17;fontStyle=1;fontColor={color};')
        ET.SubElement(c,'mxGeometry',x=str(cx-r),y=str(cy-r),width=str(2*r),height=str(2*r),attrib={'as':'geometry'})

    def edge(self,id,source,target,exit=(.5,1),entry=(.5,0),points=(),color=MUTED,dashed=False,arrow=True):
        def port(node,relative):
            x,y,w,h=self.nodes[node]
            return x+relative[0]*w,y+relative[1]*h
        route=[port(source,exit),*points,port(target,entry)]
        for (x1,y1),(x2,y2) in zip(route,route[1:]):
            self.drawing.add(Line(x1,self.height-y1,x2,self.height-y2,strokeColor=colors.HexColor(color),strokeWidth=1.3,strokeDashArray=[4,3] if dashed else None))
        if arrow:
            (x1,y1),(x2,y2)=route[-2:]
            angle=math.atan2(y2-y1,x2-x1)
            pts=[x2,self.height-y2,x2-7*math.cos(angle)+3*math.sin(angle),self.height-(y2-7*math.sin(angle)-3*math.cos(angle)),x2-7*math.cos(angle)-3*math.sin(angle),self.height-(y2-7*math.sin(angle)+3*math.cos(angle))]
            self.drawing.add(Polygon(pts,fillColor=colors.HexColor(color),strokeColor=colors.HexColor(color)))
        style=(f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor={color};strokeWidth=1.3;'
               f'endArrow={"block" if arrow else "none"};endFill=1;endSize=7;'
               f'exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;'
               +('dashed=1;dashPattern=4 3;' if dashed else ''))
        c=ET.SubElement(self.root,'mxCell',id=id,edge='1',parent='1',source=source,target=target,style=style)
        g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
        if points:
            a=ET.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in points: ET.SubElement(a,'mxPoint',x=str(x),y=str(y))

    def save(self):
        FIGURES.mkdir(exist_ok=True)
        cells=self.root.findall('mxCell'); ids={c.get('id') for c in cells}
        assert len(ids)==len(cells), 'Duplicate cell ID'
        for c in cells:
            if c.get('vertex')=='1':
                g=c.find('mxGeometry');x,y,w,h=(float(g.get(k)) for k in ('x','y','width','height'))
                assert 0<=x and 0<=y and x+w<=self.width and y+h<=self.height,c.get('id')
            if c.get('edge')=='1':
                assert c.get('source') in ids and c.get('target') in ids,c.get('id')
        ET.indent(self.file,space='  ')
        path=HERE/(self.stem+'.drawio')
        ET.ElementTree(self.file).write(path,encoding='utf-8',xml_declaration=True)
        ET.parse(path)
        renderPDF.drawToFile(self.drawing,str(FIGURES/(self.stem+'.pdf')))
        renderSVG.drawToFile(self.drawing,str(FIGURES/(self.stem+'.svg')))
        if shutil.which('pdftoppm'):
            subprocess.run(['pdftoppm','-scale-to','1800','-png','-singlefile',str(FIGURES/(self.stem+'.pdf')),str(FIGURES/self.stem)],check=True)
        print(f'{self.stem}: XML, endpoint, page-bound and text-fit checks passed; PDF/SVG exported.')


def workflow():
    d=Schematic('method-workflow',700,760)
    d.box('stage-0',180,15,500,66,'0  Specify the goal and population',
          'Prediction, intervention effect, or causal allocation?\nName the outcome, horizon, contrast and target population.')
    d.box('stage-1',180,99,500,82,'1  Prepare the DAG and data; fit a reference model',
          'Plausible DAG + observed data or simulation\nPredictive model and ordinary SHAP reference', 'Manuscript Steps 1-4')
    d.box('stage-2',180,199,500,82,'2  OPTIONAL: learn candidate causal structure',
          'PC / PC-stable; context-dependent alternatives:\nGES, LiNGAM, NOTEARS, mixed-data tests', 'Ng PC + IDA route: Step 6; structure checks: Step 8',TEAL)
    d.box('stage-3',180,299,500,82,'3  Review the graph and estimate mechanisms',
          'Expert review + temporal constraints; assess identification\nRetain uncertain arrows and alternative graphs', 'Manuscript Steps 2 and 6',TEAL)
    d.box('stage-4',180,399,500,98,'4  Define the causal game and graph surgery',
          'do: set coalition nodes, remove their incoming arrows,\nthen propagate through the remaining mechanisms.\nOrdering- and edge-based games use their own rules.', 'Manuscript Step 6',TEAL)
    d.box('stage-5',180,509,500,82,'5  Compute causal attributions, if requested',
          'Heskes / do-Shapley; Ng PC + IDA;\nasymmetric Shapley values (ASV); Shapley Flow', 'Methods allocate different quantities; match the target (Step 6).',TEAL)
    d.box('stage-6',180,622,500,96,'6  Compare and validate on a shared degradation path',
          'Clean -> smaller sample / selection / measurement noise\nMatch causal targets and computational budgets.\nReport uncertainty, failures and sensitivity.', 'Manuscript Steps 8-11')
    for i in range(6): d.edge(f'next-{i}',f'stage-{i}',f'stage-{i+1}',color=BLUE if i<1 or i==5 else TEAL)
    d.edge('prediction-only','stage-1','stage-6',exit=(0,.32),entry=(0,.5),points=((5,125.24),(5,670)),color=BLUE)
    d.text('prediction-label',13,201,133,68,'Prediction only:\nskip the causal route\nand go to validation.',12.3,BLUE)
    d.edge('supplied-dag','stage-1','stage-3',exit=(0,.75),entry=(0,.5),points=((158,160.5),(158,340)),color=TEAL)
    d.text('supplied-label',17,292,128,70,'Supplied DAG:\nbypass discovery;\nreview assumptions.',12.3,TEAL)
    d.box('optional-detector',18,421,126,137,'Optional\ndetector / filter',
          'Separate branch\n(Steps 5 and 7)\nUnevaluated',color=MUTED,size=12.3,title_size=13)
    d.edge('feedback','stage-6','stage-3',exit=(1,.5),entry=(1,.5),points=((693,670),(693,340)),color=MUTED,dashed=True)
    d.text('feedback-label',16,584,135,70,'Failed checks:\nrevisit the graph,\nmechanisms, data\nor target.',12.3,MUTED)
    d.text('caption',10,731,680,23,'Method families are alternatives, not a mandatory ensemble or an exhaustive comparison.',12,MUTED)
    d.save()


def surgery():
    d=Schematic('graph-surgery',700,330)
    d.text('title',10,5,680,29,'Graph surgery for a node intervention',18,INK,True)
    d.text('observational-title',20,52,315,25,'Observational system',15,BLUE,True)
    d.text('intervention-title',365,52,315,25,'Intervened system: do(M = m)',15,TEAL,True)
    for prefix,offset,color in [('obs',0,BLUE),('do',345,TEAL)]:
        for label,cx in [('X',70),('M',177),('Y',284)]: d.circle(prefix+'-'+label,cx+offset,123,label,color)
        d.edge(prefix+'-M-Y',prefix+'-M',prefix+'-Y',exit=(1,.5),entry=(0,.5),color=color)
    d.edge('obs-X-M','obs-X','obs-M',exit=(1,.5),entry=(0,.5),color=BLUE)
    d.edge('removed-X-M','do-X','do-M',exit=(1,.5),entry=(0,.5),color=RED,dashed=True,arrow=False)
    d.text('removed-cross',453,105,30,33,'x',22,RED,True)
    d.text('removed-label',430,153,78,25,'removed',11.5,RED)
    d.text('obs-equation',20,189,315,48,'M = f_M(X, U_M)\nY = f_Y(M, U_Y)',14,INK)
    d.text('do-equation',365,189,315,48,'M = m\nY = f_Y(M, U_Y)  (unchanged)',14,INK)
    d.text('explanation',20,263,660,53,'Replace only the equation for M with a constant.\nRemove X -> M; keep M -> Y and propagate the intervention downstream.',13.5,INK)
    d.save()


if __name__=='__main__':
    workflow()
    surgery()
