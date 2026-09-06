# Tutorial page: editorial, visual and logic review

Review only; no page edits or publishing. Scope: the current `site/index.qmd`,
rendered locally with the existing Quarto theme. Claude reviewed page screenshots,
text and opening-figure markup. Gemini 3.1 Pro, through Antigravity, reviewed the
page text and opening-figure markup. Codex inspected the render, checked their
findings against local sources, and made the judgments below. Raw agent reports
and screenshots remain in the ignored `.scratch/agent-delegation/page-review/`.
The agents did not receive supporting research documents in this review.

## Recommendation

Keep the editorial character and the prediction/intervention contrast. Shorten
the main reading path substantially and make the figures do more explanatory
work. The current page combines a tutorial, protocol index, research status report,
and article positioning. A reader should first understand the problem, then the
approach, then the evidence and its limits.

The local render contains approximately 1,895 words in the main page. At a
1440×1000 viewport it is 7,925 pixels tall; the seven-step section alone is
2,381 pixels and about 705 words. At 390×844 the page is 14,567 pixels tall.
These are diagnostic measurements, not usability thresholds. An editorial target
of 900–1,200 words for the main reading path is reasonable; retain the detailed
protocol, provenance and results in linked documentation.

## Proposed reading order

1. **A prediction ranking does not tell us where to intervene.** One short hero.
2. **Same chain, two questions.** A complete visual comparison with a short
   explanation; optional algebra immediately beneath it.
3. **Upstream causes can be easy to miss.** Separate screening-off from
   attenuation and finite-sample uncertainty, using one compact depth example.
4. **What an intervention analysis needs.** Keep the seven steps available, but
   group them into three readable phases: understand the data and predictive
   ranking; establish and challenge the causal structure; attribute and evaluate
   candidate actions. Introduce the goal before either route and label this as
   the project's workflow, not a universal requirement to fit SHAP first.
5. **What the simulations show.** Visually separate the teaching case, the
   14-node working subgraph, and the 51-node source DAG. Preserve null results.
6. **What remains untested.** A short, legible status block and one sources row.

Suggested hero:

> **A prediction ranking does not tell us where to intervene.**
> A model can predict an outcome using a measured mediator while giving an
> upstream cause little credit. Changing that cause can still change the outcome.
> Follow a simple example, then see what a NASA-topology simulation reveals—and
> what remains untested.

The existing “Your roadmap should follow your goal” can remain as a supporting
line. It is elegant, but the proposed heading tells a new reader the actual issue.

## Cut, move, retain

| Current material | Recommended treatment |
| --- | --- |
| Journal/article positioning in the hero and footer | Remove. It does not explain the causal problem or establish the simulation's validity. |
| Hero lineage row and repeated archive/project links | Consolidate in one quiet footer sources row. |
| Long hero premise repeated in Two Goals | Replace with the short hero; explain the mechanism once beside the figure. |
| Citation triplet and “the split is standard” opening | Replace with one unobtrusive link to the supporting explanation. Keep attribution accessible. |
| Causal Roadmap resemblance, protocol numbering and code paths | Move to the playbook. Readers currently have to translate between seven page steps, older six-rung framing and numbered protocol steps. |
| Step 4 collaborator credit, vendor sign-off and before/after-expert design discussion | Move to acknowledgments or design documentation as appropriate. Retain a visible “Proposed; not evaluated” label. |
| “The picture has one more link…” | Fix the mismatch and delete the explanation. Prefer simplifying the figure to three nodes. |
| “Scaffolded and outside the article's scope” | Replace with the reader-relevant status: “Decision layer: not evaluated here.” |
| NASA topology, chosen coefficients, testbed identity, single-seed/prototype limits | Retain beside the relevant evidence. These change how a result should be read. |
| Scripted expert stand-in and attribution/action distinction | Retain. Shorten the wording, not the distinction. |

## Visual recommendations

### 1. Redesign the opening comparison; keep the graph vocabulary

The restrained nodes, arrows, blue/orange contrast and black outcome node work.
The 12-second alternating display makes readers remember one state while waiting
for the other. Display **both states simultaneously**: side by side on desktop,
stacked on mobile, using the same three-node `X → M → Y` chain as the equations.

Label the questions “What does the predictor use?” and “What changes if we set X?”
On the left, show a predictor that uses M in the explicitly stated clean-chain
example. On the right, show a controlled change to X propagating through M to Y.
In the linear example, label the total-effect derivative `ab`. Do not put a
“restored credit” bar beside that derivative: it would conflate effect and
attribution. Explain structural credit allocation later, or in a separate inset.

Current bars are hand-set in SVG keyframes, not linked to calculated attribution:
the prediction phase gives X a 4% track height and A 22% while the text says X's
credit goes to zero. Remove decorative quantities or label a schematic explicitly;
use computed values whenever comparing attribution magnitudes.

Static presentation must contain the whole comparison. Currently the
`prefers-reduced-motion` rule hides the intervention phase. Make a short optional
propagation pulse an enhancement, with a pause/replay control if motion remains.
Keep substantial labels in responsive HTML rather than shrinking them inside SVG.

### 2. Redesign the depth figure for a web reader

Retain its scientific content and the full plot in the research documentation.
The current chart is usable for close desktop inspection but has tiny axes,
legend and footnote at phone width. It visually competes with a long paragraph
and another long caption.

Show the standardized chain and its effect sizes prominently:
`0.60 → 0.36 → 0.22 → 0.13 → 0.08` for depths 1–5. State “0.6 per edge; teaching
simulation.” Provide a second panel, stacked on phones, showing how detection
changes with sample size. Directly label curves, enlarge type, and use sample
size as the main reader-facing axis. Define detection as the marginal-slope test
used by this simulation; it is not a causal-discovery success rate.

Keep the approximately 60× sample-size observation as an explicitly approximate
equal-power comparison under the stated model, not a universal depth rule.
An optional sample-size control could be useful later, but it is not needed for
the first simplification. Do not replace probability curves with a deterministic
“noise floor” that makes detection look all-or-nothing.

### 3. Add one compact workflow illustration

Use a fork for the goals and a short causal-analysis lane. Reuse one small graph:
uncertain edges → documented assumptions → propagation → separately evaluated
actions. Dashed outlines mean proposed or unresolved, with text labels as well.
Keep seven short step labels beneath the larger phases; link each to details.
This should replace several paragraphs, not sit above an unchanged long list.
Avoid astronaut or kidney ornament that adds atmosphere without teaching a step.

### 4. Make the evidence easier to compare without overstating it

Group rows by testbed and name every metric. The bare value 0.0059 does little
for a newcomer without a scale or comparison; lead with the pattern and put the
exact attribution table behind a link. Use stacked evidence entries on phones:
testbed, observation, result, limitation. The current three-column table becomes
extremely tall, with narrow sentence fragments.

If adding a results chart later, keep the matched ordinary/ordering comparison
together and place the structural prototype in a clearly separate panel. Do not
turn 0.506, 0.528 and 0.794 into an apparently matched three-arm efficacy chart.
Use uncertainty from recorded results only; never invent error bars for the
32×32×32 prototype. A well-grouped table is sufficient for the first pass.

## Logic to tighten before rewriting

- **Screening-off is conditional.** The clean fully mediated chain illustrates
  why an ideal predictor can ignore X once M is known. The hero currently
  generalizes from this to measured mediators in general. Additional paths,
  measurement error and fitted-model behavior matter; the page's own working-
  subgraph result shows that credit can shift in the opposite direction.
- **Depth is a separate mechanism.** Attenuating coefficients can shrink total
  effects; measurement error and sampling uncertainty concern their recovery.
  Do not merge these with the reason a clean mediator screens off X.
- **Discovery does not share a predictor's screening-off “blindness.”** In a
  chain, conditional independence helps remove the non-edge X–Y while retaining
  X–M and M–Y. A long chain need not require larger conditioning sets. State
  discovery difficulty in terms of assumptions, weak dependencies, data types,
  sample size and graph connectivity, and keep the observed PC failure local
  to its tested configuration. PC targets a skeleton/equivalence class under its
  assumptions; see [Kalisch and Bühlmann](https://www.jmlr.org/papers/v8/kalisch07a.html).
- **A workflow is not an identification guarantee.** Causal discovery need not
  orient every edge, and linearity alone does not identify a causal graph.
  “Linear mechanisms make this simulation and its effects easier to compute” is
  cleaner than implying that linearity settles identification. Mark unresolved
  assumptions and the scripted reviewer explicitly.
- **Propagation and action evaluation are distinct.** Structural attribution
  can use intervention-based coalition expectations; the resulting Shapley value
  is still not the benefit of a particular feasible action. This distinction is
  consistent with [Heskes et al.](https://proceedings.neurips.cc/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html)
  and the repository's documented coalition value. Rename “Price” to “Evaluate
  candidate actions”: benefit, uncertainty, feasibility and cost all belong there.
- **Use “no detected difference,” not “tie.”** Preserve the matched comparison's
  null finding without suggesting an equivalence test established equality.

## Verified presentation defects and first-pass priorities

1. **Placeholder class collision.** Quarto emits both the heading and its enclosing
   section with class `placeholder`. Bootstrap defines that class with
   `background-color: currentcolor`, `opacity: .5` and `cursor: wait`. This makes
   the status column grey and difficult to read. Rename the custom class, e.g.
   `claim-placeholder`, and update the theme selector. It is not a scroll-animation
   artifact.
2. **Reduced-motion loses the point.** Correct the opening figure's fallback.
3. **Mobile figures shrink their text.** Use responsive arrangements, not merely
   width:100% on a dense fixed-layout image.
4. **The opening delays the example.** At the inspected phone size, almost the
   entire first viewport is heading and centered prose. Shorten first; left-align
   the longer introductory text if any remains.
5. **Keep the good foundations.** Retain the serif headings, restrained palette,
   clear numbering and generous spacing. The issue is the amount and order of
   explanation, not a need for a new brand or a visual on every paragraph.

## What the collaboration contributed

Claude usefully identified the hidden intervention fallback, mobile figure/table
problems and grey status column. Its replacement hero still overgeneralized
mediator behavior, and its suggested intervention-side credit bar would preserve
an ambiguity we should remove. Its claim that mobile body text generally needs
left alignment was too broad; the main issue is the long centered hero.

Gemini usefully proposed moving depth before the path and cutting metadata.
Reject its suggestion that discovery fails for the same screening-off reason as
prediction. Also reject its blanket statement that structural attribution does
not estimate intervention expectations: those can be its coalition values.
Gemini did not inspect rendered figures, so its praise of their legibility is
not evidence. Neither agent's output is an automatic scientific sign-off.

Next implementation pass: fix the two verified display issues, cut project
commentary, revise the hero and section order, then redesign the opening figure
and mobile evidence layout. Retain prototype and placeholder status at each
relevant result. Review the revised page before adding further visuals.
