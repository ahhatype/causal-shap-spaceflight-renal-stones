"""Generate a self-contained, offline teaching animation from retained source."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    svg = (ROOT/'docs/images/two-goals.svg').read_text(encoding='utf-8')
    svg = svg.replace('<svg ', '<svg id="chain-animation" ', 1)
    controller = (ROOT/'docs/classroom/animation-controller.js').read_text(encoding='utf-8')
    html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Predictive and structural credit — teaching companion</title>
<style>body{margin:0;background:#fbf9f5;color:#1a1814;font:18px/1.6 system-ui,sans-serif}main{max-width:960px;margin:auto;padding:30px 22px}h1{font:normal clamp(30px,5vw,48px)/1.15 Georgia,serif}a{color:#0077a8}figure{margin:24px 0;padding:16px;background:white;border:1px solid #ded7ca}figure>svg{display:block;width:100%;height:auto}.chain-controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center}.chain-controls[hidden]{display:none}button{min-height:44px;padding:8px 12px;font:inherit;background:white;border:1px solid #aaa;cursor:pointer}button:focus-visible,a:focus-visible{outline:3px solid #0077a8}figcaption{font-size:16px;margin-top:20px}#chain-status{font-size:15px}</style>
</head><body><main>
<nav><a href="index.html">Interactive calculation</a> · <a href="https://github.com/ahhatype/causal-shap-spaceflight-renal-stones">Master repository</a></nav>
<h1>A cause can receive little predictive credit</h1>
<p>In X → A → M → Y, an ideal predictor can use M alone when it is measured exactly and carries the entire pathway. Changing X can still change Y.</p>
<figure>''' + svg + '''
<div class="chain-controls" hidden><button id="chain-play" type="button">Play comparison</button><button type="button" data-chain-view="prediction">Show prediction</button><button type="button" data-chain-view="structural">Show structural credit</button><span id="chain-status" role="status">Prediction view</span></div>
<figcaption>Bars are schematic, not measured SHAP values or effect sizes. Totals are not comparable across phases. Structural credit is not an intervention effect or an action recommendation.</figcaption></figure>
<p>Under independent mean-zero disturbances, A=aX+eA, M=bA+eM and Y=cM+eY, the mean response slope for setting X is abc. Model-interventional SHAP gives unused inputs zero credit; conditional SHAP can behave differently.</p>
<p>The <a href="index.html">two-player calculation</a> combines A into the X-to-M relation and specifies every coalition value. It is separate from both renal simulations. See the repository's technical note for path products, detection power, nonlinear counterexamples and references.</p>
<noscript><p>The prediction scene above is static. The text and worksheet explain both questions without animation.</p></noscript>
</main><script>''' + controller + '</script></body></html>\n'
    (ROOT/'docs/classroom/animation.html').write_text(html, encoding='utf-8')
    print('Built self-contained docs/classroom/animation.html')


if __name__ == '__main__':
    main()
