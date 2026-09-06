# Tutorial redesign: scope and figure provenance

This implementation follows the [page review](tutorial-page-review-2026-09-05.md).
It changes presentation, not research results. It requires neither LumaWarp nor
the research runtime, credentials, participant-level data or a new simulation.

- The opening diagrams illustrate the same unconfounded, fully mediated
  three-node chain as the existing equations. They contain no invented SHAP bars.
  Both goals remain visible without animation or JavaScript.
- The attenuation bars show the existing example's `0.6 ** depth`, rounded for
  display. The detection plot reads the checked-in
  `results/figures/depth_washout.csv`; it does not run the generator. It shows
  depths 1, 3 and 5, with all three identified, on a logarithmic sample-size axis.
  The original five-depth figure remains available from the page.
- Detection in this teaching example is the fraction of 400 replicates passing
  the original approximate 5% marginal-slope test (absolute t statistic > 1.96).
  It is not causal-discovery accuracy. The plot does not establish an E1–E3
  research result or the performance of the proposed detector.
- The seven page steps are grouped into three phases. They describe this
  project's workflow, not a requirement to fit a predictive model before every
  causal analysis. Their protocol mapping stays in the playbook.
- Recorded teaching, 14-node and 51-node results retain their identities.
  The full-DAG ordering comparison remains a null finding; structural
  propagation remains a 32×32×32 prototype. The working-subgraph expert loop
  remains explicitly a scripted heuristic in rounds two and three.
- The detector/filter, E1–E3, nonlinear-generator sweep and decision layer retain
  their unevaluated status. No private vendor technology is exposed or invoked.

Regenerate the small static diagram assets and detection chart with
`python3 site/build_tutorial_figures.py`, using only the Python standard library.
The original scientific figure and result summaries remain unchanged.

## Local validation

- Quarto rendered the tutorial and the existing archive successfully.
- Browser checks passed at widths 1440, 390 and 320 pixels: no horizontal page
  overflow, all images loaded, no page JavaScript errors, and the algebra
  disclosure opens and closes. Both goal diagrams stay visible with reduced
  motion; the status column has full opacity and no Bootstrap placeholder class.
- Main reading-path text is approximately 905 words with algebra collapsed,
  down from approximately 1,895. At the inspected desktop width, page height
  fell from 7,925 to 5,304 pixels; at 390 pixels wide, from 14,567 to 8,412.
- SVG assets parse successfully and regenerate deterministically from the saved
  summary. No simulation, LumaWarp invocation, or research-result changes occurred.
- Gemini reviewed only the revised page text and returned no remaining
  actionable issues. This is an editorial check, not scientific validation.

Claude also reviewed the revised screenshots. Its actionable typography and
spacing suggestions were incorporated. A header-overlap observation was traced
to section screenshot capture, not page layout. The muted text/background pair
has a calculated contrast ratio of 5.68:1. Mobile evidence labels were enlarged.

The initial implementation was reviewed locally before the user requested publication.

## Optional motion and the assumption sketch

The accepted follow-up adds user-triggered motion, with pause/resume and replay.
There is no autoplay. One pulse follows the intervention chain; it represents a
path, not an effect magnitude. A second replay reveals depth 1 through 5 and their
existing effect values. The static scene, no-JavaScript view and reduced-motion
view retain both goals and the complete depth example. A preference change during
playback cancels motion and restores the static view.

A small diagram beside the structure phase contrasts an unresolved edge with an
explicitly assumed direction. Its example records “A precedes B” and states that
time order constrains direction without proving a causal link. It is a generic
illustration of recording an assumption, not a depiction of completed human review.

The motion follow-up passed browser checks for no autoplay, replay, pause/resume,
completion, preference changes during playback, and no-JavaScript fallback.
The final Quarto build includes the existing archive; the root redirect and
all research results remain unchanged.
