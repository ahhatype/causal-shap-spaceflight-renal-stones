# From a plausible DAG to causal attribution

The [study guide PDF](study-guide.pdf) is built from the editable [LaTeX article](study-guide-latex/main.tex), with [references](study-guide-latex/references.bib) and [editable schematics](study-guide-latex/diagrams/README.md).

![Method workflow](study-guide-latex/figures/method-workflow.png)

The seven stages group the manuscript's existing protocol:

0. Specify the question, target population and intended claim.
1. Prepare the DAG and data; fit the predictive reference and ordinary SHAP comparator.
2. Optionally discover candidate structure with PC or a justified alternative. A supplied graph bypasses discovery.
3. Review the graph and estimate the mechanisms required downstream.
4. Define the causal game and interventions; perform do-graph surgery where applicable.
5. Calculate the selected causal attributions, keeping each method's target explicit.
6. Compare and validate under a common sequence of data constraints.

Prediction can proceed from the reference model to predictive validation. An intervention-effect question can omit Shapley allocation. Graph review and do-intervention surgery are separate operations.

The article gives the manuscript crosswalk, the two routes, concrete method choices and the proposed data-degradation comparison. The [method appendix](method-choices.md) expands the alternatives within each stage; the [evidence map](central-workflow.md) records completed results and remaining work. The [selection note](../technical/selection-mechanism.md) develops the illustrative population extension.

For editing and compilation, see the [working-folder instructions](study-guide-latex/README.md). The LaTeX file is the editing source; this page is an entry point.
