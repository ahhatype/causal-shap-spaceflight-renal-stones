# For coauthors: where everything is

Written 2026-09-04 for Aimee Harrison and Lexi Pasi; Robert Reynolds is
welcome to the same page. Five minutes covers it.

## The one idea

Your roadmap should follow your goal. Prediction is often the default
playbook, and it is fine for prediction. The goal of intervention is to
identify intervenable levers, which motivates casting a wider net and
retaining deeper nodes in the graph. The paper tests one path from data to a
candidate intervention on NASA's renal-stone DAG, with data simulated from
that topology under coefficients we chose, so every method is scored against
a known answer.

The path has seven steps: Data; Predict and explain (the prediction recipe
stops here); Discover; Cast wider, then filter; Resolve the graph; Propagate;
Price. It consolidates Aimee's 13-step protocol, Andy's August schematic, and
the ACIC five-step workflow; the cross-map is in the playbook, linked below.

## Where to read, in order

| | What | Where |
| --- | --- | --- |
| 1 | The argument on one page, with the animation | <https://andystats.github.io/causal-shap-target-dags/> |
| 2 | The current manuscript draft (PDF) | Box: `Causal SHAP Target DAGs - Robert Reynolds Lexi Pasi/from-github-2026-09-04/Space SHAP manuscript draft 2026-09-04.pdf` |
| 3 | The repository front page and the seven-step table | <https://github.com/ahhatype/causal-shap-spaceflight-renal-stones> |
| 4 | Start-here guide: where everything is, what is done, what is next | [`ORIENTATION.md`](../ORIENTATION.md) |
| 5 | The playbook: each step's inputs, tools, guards, and the "one flow, five tellings" table | [`docs/playbook/README.md`](playbook/README.md) |
| 6 | The framing memo behind the reframing, with citations | [`docs/framing/prediction-vs-intervention.md`](framing/prediction-vs-intervention.md) |
| 7 | Results so far | [`docs/step04_results.md`](step04_results.md), [`docs/step06_results.md`](step06_results.md), [`docs/full_dag/RESEARCH_RECORD.md`](full_dag/RESEARCH_RECORD.md) |
| 8 | Decisions, numbered | [`docs/decisions/`](decisions/) (007 consolidation, 008 LumaWarp gate, 009 one home) |

The manuscript source (LaTeX) lives in the repository but is not published
yet; coauthors receive dated PDF exports in the Box folder above. The old
`causal-shap-target-dags` repository is frozen and only serves the site.

## What we would like from you

**Aimee.** The introduction in the PDF is the human-written text from your
August draft, reproduced verbatim; anything in blue in the PDF is an LLM
draft awaiting a human rewrite, anything in red is an open item. Please check
(a) that the seven-step path and the "one flow, five tellings" table
represent your 13-step protocol fairly, and (b) the motivating outline: does
the premise above carry the paper's opening the way you intended?

**Lexi.** Three things sit with you, all recorded in
[`docs/lumawarp/README.md`](lumawarp/README.md) and question 3 and 4 of the
framing memo: (a) the dichromatic sensitivity gating rule and which two
channels it pairs; (b) whether the filter runs before the expert edits the
graph, to propose candidates, or after, to audit it (the site currently
shows before); (c) the six sign-off questions for Lucidity, section 8 of
that file, so that anything LumaWarp-specific can enter the paper.

## How to comment

- Comments on the PDF in Box, or an email, both work. If you prefer GitHub,
  open an issue on the hub repository.
- Please do not edit the Box copies of the Word drafts; they are the
  archived August originals. The working draft is the LaTeX in the repository
  and Andy will carry changes across.

## Three conventions

- Say "NASA-topology simulation", never "NASA effect". NASA supplied the
  graph, not the coefficients or the effects.
- Rounds two and three of the step 6 expert loop were a scripted heuristic
  standing in for a reviewer, and every number from them says so.
- Nothing about LumaWarp's internals, binaries, or block-level results goes
  on GitHub until Lucidity signs off. The public repository holds the
  interface contract and placeholders only.
