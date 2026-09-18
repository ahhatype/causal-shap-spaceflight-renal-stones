# Method playbook and manuscript crosswalk

The [editable LaTeX article](study-guide-latex/README.md)
([PDF](study-guide-latex/main.pdf)) follows the manuscript's method sequence.
The [central workflow](central-workflow.md) maps that sequence to the evidence;
[method choices](method-choices.md) keeps alternatives inside their relevant stage.

## Protocol crosswalk

| Playbook stage | Manuscript protocol | Main method role |
| --- | --- | --- |
| 0. Define the target | 1 and target definitions throughout | Population, timing, prediction/effect/allocation |
| 1. Prepare data and predictive reference | 2–4 | Plausible DAG, simulation mechanisms, data, fitted model and ordinary SHAP |
| 2. Discover candidate structures (optional) | Discovery in 6; broader comparison in 8 | PC and conditional alternatives; supplied-DAG bypass |
| 3. Review graph and estimate mechanisms | 2 and graph revision in 6 | Temporal/domain evidence, revision ledger, unresolved alternatives |
| 4. Define causal game and graph surgery | Value-function components of 6 | Interventions and identification; do-surgery where the game calls for it |
| 5. Calculate causal attributions | Attribution components of 6 | Heskes/Jung-style games, Ng et al., ASV and Shapley Flow with distinct semantics |
| 6. Compare under data degradation | Evaluation in 4/6/8; proposed 9–11 | Separate predictive, graph, allocation and intervention-ranking checks; repeated settings and uncertainty |

The [13-step protocol](protocol.md) retains implementation paths and status.
Its numbering identifies work packages; this playbook separates the operations
within Step 6 rather than silently changing the manuscript's step numbers.

The supplied-graph route enters review without discovery. A prediction question
can proceed from Stage 1 to predictive validation; an effect-only question can
omit Shapley allocation. Expert graph revision and do-intervention surgery are
different operations. The [DAG harvest protocol](dag-harvest-protocol.md) supports
source and evidence review.

## Optional and unfinished components

The detector and filter in protocol Steps 5 and 7 sit beside attribution and may
flag candidates for future graph review. They remain unevaluated; the
[public interface](../lumawarp/README.md) is the relevant implementation boundary.
Rounds two and three of the current expert loop are scripted heuristics.
Longitudinal methods (Step 12) and action/recourse evaluation (Step 13) remain
extensions beyond the completed analyses.

The proposed degradation path reruns selected comparisons as sample size,
selection and measurement conditions change. It is the common experimental
axis, not evidence that every causal method is more robust. Keep the 14-node and
51-node simulations distinct, preserve nulls and report each method's target,
information, budget and uncertainty. The [selection note](../technical/selection-mechanism.md)
provides the observation-process overlay and a separate hypothetical calculation.

## Supporting schematics

The article includes editable draw.io sources for the method workflow and
intervention surgery. Earlier simulation-specific schematics remain available:
[discovery benchmark](../images/fig1_space_shap_spine.png) and
[identification checks](../images/fig2_sufficiency_transfer.png). They describe a
particular analysis design, rather than a compulsory path for every question.
