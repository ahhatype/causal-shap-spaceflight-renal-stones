# Playbook schematic

The flowchart for the manuscript's Discussion playbook: how a Space SHAP
analysis moves from its question to a graph, a causal game and an attribution,
and the rules that govern each phase. The figure lives in the Overleaf project
"Space Shap Playbook v1" beside the manuscript; this folder holds the LaTeX
sources so it can be rebuilt and revised here.

| File | What it is |
| --- | --- |
| `Playbook flow 1.1.tex`, `.pdf` | The current proposal (version 1.1, 8 October 2026). It starts from Aimee Harrison's 6 October schematic and keeps her layout, box sizes, phase labels and dagger convention. Only wording a reviewer would reject changed, each change with a reason and a citation. Eleven references. |
| `playbook-schematic.tex`, `.pdf` | An earlier full rewrite, renumbered to the manuscript's Steps 0 to 6, with longer boxes and twenty-nine citations. Kept for reference; it is not the proposal. |
| `references.bib` | One bibliography that compiles both files. |

Build either file with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.

## The question that drove the revision

Does it make a DAG more valid when two causal discovery algorithms converge on
the same graph? No. Both algorithms see the same sample, the same measured
variables, the same selection and the same measurement error, so their
agreement cannot speak to any of those. Under Markov and faithfulness,
observational discovery identifies at most an equivalence class, so agreement
on a CPDAG settles neither orientation nor the assumptions. Benchmark success
can come from a shared artifact such as variance ordering (Reisach, Seiler and
Weichwald 2021). A rule that keeps only the edges both methods support is an
intersection: it can only remove edges, so it trades recall for precision and
never adds validity.

The concession both outside reviewers made: when methods have different and
imperfectly correlated errors, agreement can be limited robustness evidence, in
the triangulation sense of Lawlor, Tilling and Davey Smith (2016). The
schematic therefore says that agreement between methods on the same data is a
robustness check rather than validation. What does support validity: testing
the graph's implied independencies, with rejection as the informative outcome;
evidence about edges from outside the dataset; and the sensitivity of the
target to the alternatives still open.

## What changed in version 1.1

Seven boxes, one scope sentence, one footnote sentence and seven of the eight
rules have wording changes. The ones that mattered most:

1. Rule 1 keeps the pairing sentence and says that agreement can raise
   confidence when the methods have different sources of error, and that
   agreement alone does not validate the DAG.
2. The discovery box asks for at least two suitable methods and retains their
   candidate graphs and unresolved orientations; the intersection rule is gone,
   and intersection is named as a stated precision-over-recall choice, never
   the default.
3. In Phase 4 an intervention question goes to identification and estimation
   with attribution optional; causal attribution declares its game and is
   checked against a reference for the same allocation; the undefined labels
   "Causal Interventional SHAP" and "Causal Predictive SHAP" are gone; on the
   prediction branch the causal comparison is optional.
4. The review box judges each result against its own target, with the support
   that target requires.
5. Rule 3 says a passing implication test is not confirmation and cannot
   support a present edge; rejection is the informative outcome; reusing the
   discovery data needs post-selection handling.

Phase numbers are local to this schematic and differ from the manuscript's
Steps 0 to 6; the figure's footnote says so. The change-by-change ledger and
the outside reviews that settled each wording are kept with the coauthor
review records, not in this public folder.
