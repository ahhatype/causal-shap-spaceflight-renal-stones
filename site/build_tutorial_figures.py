"""Redraw tutorial assets from recorded summaries; never run a simulation."""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'site/assets'
INK, BLUE, ORANGE = '#1a1814', '#0077a8', '#bb541a'


def chain(intervention):
    color = ORANGE if intervention else BLUE
    title = 'Set X: change travels through M to Y' if intervention else 'Predict Y: a clean mediator M can screen off X'
    edges = color if intervention else '#b9b0a1'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 150" role="img" aria-labelledby="title desc"><title id="title">{title}</title>',
             '<desc id="desc">A three-node causal chain X to M to Y. Edge coefficients are a and b. No attribution magnitudes are depicted.</desc>',
             f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="{edges}"/></marker></defs>',
             f'<g font-family="Arial, sans-serif" text-anchor="middle" fill="{INK}">']
    for x in [70, 240]:
        parts.append(f'<path d="M{x+32} 85H{x+132}" stroke="{edges}" stroke-width="2.5" marker-end="url(#arrow)"/>')
    for x, label in [(70,'X'),(240,'M'),(410,'Y')]:
        active = label == ('X' if intervention else 'M')
        fill = INK if label=='Y' else ('#fbe6d9' if intervention else '#e0f1f7') if active else '#ffffff'
        stroke = color if active else INK if label=='Y' else '#b9b0a1'
        parts.append(f'<circle cx="{x}" cy="85" r="31" fill="{fill}" stroke="{stroke}" stroke-width="2"/><text x="{x}" y="95" font-size="28" fill="{"#ffffff" if label=="Y" else INK}">{label}</text>')
    parts.append('<text x="155" y="67" font-size="22" font-style="italic">a</text><text x="325" y="67" font-size="22" font-style="italic">b</text>')
    if intervention:
        parts.append(f'<text x="70" y="29" font-size="19" fill="{color}">set X</text><path d="M70 37V47" stroke="{color}" stroke-width="2"/>')
    parts.append('</g></svg>')
    return '\n'.join(parts)


def detection(rows):
    x = lambda n: 48 + math.log(n / 25) / math.log(4000 / 25) * 396
    y = lambda rate: 246 - rate * 216
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 310" role="img" aria-labelledby="title desc">',
             '<title id="title">Larger samples help detect weaker effects</title>',
             '<desc id="desc">Recorded teaching simulation, depths 1, 3 and 5. At n=25 detection rates are 92.75%, 19%, and 8%. At n=4000 all reach 100% in these recorded replicates. Sample size uses a logarithmic axis. Detection is a marginal-slope test, not discovery accuracy.</desc>',
             '<g font-family="Arial, sans-serif" font-size="20" fill="#625b52">']
    for rate in [0, .5, 1]:
        parts.append(f'<path d="M48 {y(rate):.1f}H444" stroke="#ded7ca"/><text x="38" y="{y(rate)+5:.1f}" text-anchor="end">{int(rate*100)}</text>')
    for n in [25,100,500,4000]:
        parts.append(f'<text x="{x(n):.1f}" y="270" text-anchor="middle">{n:,}</text>')
    parts.append('<text x="48" y="17" fill="#1a1814">Detected (%)</text><text x="246" y="300" text-anchor="middle" fill="#1a1814">Sample size (log scale)</text>')
    for depth, color, dash, label_n in [(1,BLUE,'',60),(3,'#4b7468','7 4',120),(5,ORANGE,'2 5',400)]:
        values = sorted((r for r in rows if int(r['depth'])==depth),key=lambda r:int(r['n']))
        points=' '.join(f"{x(int(r['n'])):.2f},{y(float(r['detection_rate'])):.2f}" for r in values)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}" stroke-linecap="round"/>')
        label = min(values,key=lambda r:abs(int(r['n'])-label_n))
        ly=y(float(label['detection_rate'])) + (24 if depth==1 else -10)
        parts.append(f'<text x="{x(int(label["n"])):.1f}" y="{ly:.1f}" fill="{color}" font-size="22" font-weight="bold" stroke="#fbf9f5" stroke-width="4" paint-order="stroke">Depth {depth}</text>')
    parts.append('</g></svg>')
    return '\n'.join(parts)


if __name__ == '__main__':
    with (ROOT/'results/figures/depth_washout.csv').open() as source:
        rows=list(csv.DictReader(source))
    for name, content in [('prediction-chain.svg',chain(False)),('intervention-chain.svg',chain(True)),('depth-detection.svg',detection(rows))]:
        (ASSETS/name).write_text(content+'\n')
        print('Wrote',name)
