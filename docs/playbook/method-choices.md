# Method choices and bounded comparisons

This methods appendix follows the manuscript-aligned [study guide](study-guide.pdf): prepare the predictive reference, optionally discover structure, review the graph and mechanisms, define a causal game, calculate attributions, and evaluate them as data conditions change. The seven stages group the manuscript's 13-step protocol; they do not replace its numbering.

The table gives an **established comparator** and a **conditional choice**, rather than a universal recommendation or an unverified “most-cited” ranking. The proposed comparisons below are not new renal results. Fuller algorithms and sensitivity settings belong in the supplement; the complete grid of methods and data-generating settings is outside this study.

## The method sequence

| Stage | Established comparator | Conditional choice and concrete output |
| --- | --- | --- |
| **0. Set the goal** | A prediction or predictive-attribution question with a specified outcome and population. | Distinguish predicted risk, an individual intervention contrast, and allocation of a joint causal contrast. Record population, timing, exposure settings, outcome scale and intended interpretation. |
| **1. Prepare data and the predictive reference** | The study's ordinary SHAP pairings: random forest and XGBoost TreeExplainer, logistic-regression LinearExplainer, and KernelExplainer or PermutationExplainer for XGBoost. | Generate a declared plausible system and fit the reference predictors. State each explainer's background, dependence treatment, output scale and global aggregation. Prefer a common output scale for a new comparison; retain labels on existing differing scales. |
| **2. Discover candidate structures (optional)** | PC, including the discovery component of Ng et al.'s Causal SHAP. | Start a focused comparison with PC-stable and a conditional-independence test suitable for the mixed data; consider GES, LiNGAM or NOTEARS when their assumptions fit. Retain unresolved directions. A supplied graph bypasses discovery and enters Stage 3. |
| **3. Review the graph and estimate mechanisms** | The unrevised discovered or supplied graph, with the downstream method fixed. | Record domain and temporal evidence for each revision, retain alternative graphs, and estimate the conditional mechanisms required downstream. Distinguish fitted mechanisms from supplied simulation mechanisms. |
| **4. Define the causal game and graph surgery** | The declared predictive coalition construction from Stage 1. | For an identified do-game, replace intervened assignment mechanisms, retain the others, and estimate or propagate the resulting distribution. Declare players, baseline, intervention values and whether the output is an outcome or a fitted prediction. |
| **5. Calculate causal attributions** | Ordinary SHAP from Stage 1, with its predictive target visible. | Compare selected causal Shapley/do-Shapley, asymmetric Shapley, discovery-based Causal SHAP and Shapley Flow constructions. Choose according to available information and the desired node, ordering or edge attribution; these are not interchangeable estimators. |
| **6. Compare under data degradation** | The clean-data analysis with its stated uncertainty. | Repeat selected comparisons under smaller samples, selection, measurement error, missingness or population/mechanism shift. Separate prediction performance, graph recovery, matched-game attribution accuracy and individual-intervention ranking agreement. |

The prediction route goes from Stage 1 to predictive evaluation in Stage 6. An intervention-effect analysis needs appropriate causal assumptions and an effect calculation, but can omit Shapley allocation. Ordinary SHAP is a study comparator, not a prerequisite for causal inference.

Harrell's three uses of models are **hypothesis testing, estimation and prediction**. Modeling serves all three. The routing here also uses Hernán, Hsu and Healy's distinction between description, prediction and counterfactual prediction. An adjusted regression coefficient is not automatically a causal effect. [Harrell, RMS chapter 1](https://hbiostat.org/rmsc/intro.html), [Hernán et al., 2019](https://doi.org/10.1080/09332480.2019.1579578)

## Stage 1: establish a reproducible reference

Keep the 14-node working subgraph and 51-node source DAG separate. NASA supplies plausible topology; the simulated coefficients and response forms are study assumptions. In a blinded discovery comparison, withhold the generating graph and mechanisms from the algorithms. Record separately any method receiving an ordering, a graph, estimated mechanisms or the generating mechanisms.

A prespecified regression with supported nonlinear terms is a useful predictive reference. Flexible learners are alternatives whose complexity and tuning need to fit the available sample size. Predictive importance is assessed for the fitted model, rather than presumed to be a ranking of preventive opportunities. Record training/evaluation splits and repeat the entire fitted pipeline when estimating training-sample uncertainty. [Harrell, RMS model validation](https://hbiostat.org/rmsc/validate.html)

The existing random-forest TreeSHAP result uses probabilities; other reported pairings use log odds. Ranking comparisons do not make their magnitudes commensurate. Harmonizing a future comparison requires recomputing explanations for the chosen output; a nonlinear conversion of an existing additive decomposition does not generally preserve that decomposition.

## Stage 2: concrete discovery choices

| Method | Operation and justified use | Limit to retain |
| --- | --- | --- |
| **PC** | Deletes edges using conditional-independence tests and orients those justified by its rules. The study's concrete reference; generally returns a CPDAG representing an equivalence class. | Its usual causal interpretation requires acyclicity, causal sufficiency, Markov and faithfulness assumptions, suitable tests and an appropriate sampling model. An isolated outcome remains a diagnostic result. |
| **PC-stable** | Makes skeleton estimation independent of variable order. Useful for checking whether the PC result depends on column order. | Skeleton stability does not make every orientation unique or correct, and does not remove statistical or causal assumptions. |
| **MGM plus PC-stable with mixed-data tests** | Learns an undirected mixed graphical model as a starting skeleton and uses mixed-variable regression-based independence tests with PC-stable. A concrete candidate for continuous renal variables and a binary outcome. | The selected test's regression assumptions and sparse cells still matter. MGM preprocessing can exclude edges before orientation; it is not a correction for unmeasured confounding or selection bias. |
| **GES** | Searches over equivalence classes using a score. Useful as a score-based comparison when the chosen score and variable models are appropriate. | Its large-sample guarantees do not establish correct recovery in a sparse, selected, mixed-variable cohort. Record the score and penalty, not just the algorithm name. |
| **LiNGAM** | Uses a linear acyclic structural model with independent non-Gaussian disturbances to help identify direction. | The binary-logit renal outcome is not a continuous linear LiNGAM mechanism. Use an explicitly compatible subproblem or label the mismatch; do not treat it as a universal renal default. |
| **NOTEARS** | Encodes acyclicity as a smooth constraint and learns a weighted structure through continuous optimization. | Specify the exact loss and model class. The original linear least-squares formulation is not automatically suitable for a binary outcome; optimization and acyclicity alone do not establish causal identification. |

Primary sources: [Kalisch et al., 2012 (PC/pcalg)](https://doi.org/10.18637/jss.v047.i11), [Colombo and Maathuis, 2014 (PC-stable)](https://jmlr.org/papers/v15/colombo14a.html), [Sedgewick et al., 2019 (mixed-data discovery)](https://doi.org/10.1093/bioinformatics/bty769), [Chickering, 2002 (GES)](https://jmlr.org/papers/v3/chickering02b.html), [Shimizu et al., 2006 (LiNGAM)](https://jmlr.org/papers/v7/shimizu06a.html), [Zheng et al., 2018 (NOTEARS)](https://proceedings.neurips.cc/paper_files/paper/2018/hash/e347c51419ffb23ca3fd5050202f9c3d-Abstract.html).

A focused first comparison would separate the change from PC to PC-stable from the change in independence test, so an improvement is not assigned to the wrong component. Supply the same observations and prior information, record tuning choices, and evaluate both structural recovery and consequences for the target. A supplied-graph route remains legitimate when the study asks about attribution conditional on that graph; it does not claim to recover structure from data.

## Stages 3–4: graph review is distinct from an intervention

**Graph review** revises a hypothesis about the observational system. An edge may be added, removed or oriented using documented timing and subject-matter evidence. The comparison is unrevised versus revised graph under the same downstream method. If observations leave directions unresolved, retain the relevant alternatives and examine whether they imply different adjustment sets or intervention effects. The existing working-subgraph revision rounds two and three are scripted heuristics; human expert review remains pending.

**Graph surgery** represents an intervention within a specified causal model. For `do(M=m)` in `X → M → Y`, replace the assignment equation for `M` by the constant `m` and remove `X → M`; retain `M → Y` and its mechanism. This operation neither discovers nor verifies the graph. [Hernán and Robins, *Causal Inference: What If*](https://miguelhernan.org/whatifbook)

For coalition C, distinguish:

- **Outcome game:** `v_Y(C) = E[Y | do(X_C=x_C)]`.
- **Model-output game:** `v_f(C) = E[f(X) | do(X_C=x_C)]`.

These need not agree. A DAG by itself does not provide the needed coefficients, response forms or all interventional distributions. Fitting node conditionals for propagation requires the causal and identification assumptions of the chosen method; predictive fit alone does not establish them. Identification, measurement and support must justify estimation from observed data. Under an appropriate model, standardization or another identified estimator can replace explicit forward simulation. Doubly robust estimation does not fix an unidentified target, absent support or an incorrect graph.

The full-DAG propagation prototype scores a fitted prediction model after propagating interventions with supplied simulation mechanisms. It also uses graph-respecting orders. It is not the same estimand or information setting as symmetric, outcome-based do-Shapley estimated from observations.

## Stage 5: allocation rules and causal information

| Family | What is being computed | What must be fixed for a valid comparison |
| --- | --- | --- |
| **Causal Shapley / do-Shapley** | Shapley increments of specified interventional coalition values. Heskes et al. precede Jung et al.; Jung's outcome-based formulation develops identification and estimation as well as axiomatic properties. | Outcome versus model output, player set, intervention values, baseline, scale and permutation weights. |
| **Ng et al. Causal SHAP** | PC-derived structure and IDA causal-strength information enter a weighted, normalized attribution construction. | The discovery, strength-estimation and normalization choices. Do not relabel its result as a symmetric outcome do-Shapley estimator. |
| **Asymmetric Shapley values (ASV)** | Changes the weights assigned to variable orders to incorporate causal precedence. | The order distribution and underlying coalition game. Causal ordering alone does not specify intervention propagation through mechanisms. |
| **Shapley Flow** | Attributes model prediction credit to edges relative to a stated explanation boundary. | The graph, boundary and edge-level target. Any conversion into node rankings needs an explicit aggregation rule. |

Sources: [Heskes et al., 2020](https://proceedings.neurips.cc/paper_files/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html), [Jung et al., 2022](https://proceedings.mlr.press/v162/jung22a.html), [Ng et al., 2025](https://arxiv.org/abs/2509.00846), [Frye et al., 2020](https://proceedings.neurips.cc/paper/2020/hash/0d770c496aa3da6d2c3f2bd19e7b9d6b-Abstract.html), [Wang et al., 2021](https://proceedings.mlr.press/v130/wang21b.html).

The [do-Shapley tutorial](../technical/do-shapley.md) gives the exact example and definitions. Allocating a joint intervention contrast is different from estimating the effect of intervening on one variable. Jung's estimator development focuses on discrete variables under its stated identification and estimation assumptions; extending it to the renal setting requires additional work. No renal matched-game oracle or DML estimator is reported as completed.

## Stage 6: bounded comparisons along a common degradation path

Use a fixed target and a declared starting system, then rerun selected comparisons as data conditions change. A change in selected population can change the true target itself, so recompute the appropriate simulated reference rather than counting that change as estimator error. Missingness, measurement error and smaller samples are distinct mechanisms.

| Stage being examined | One bounded comparison | Main assessment |
| --- | --- | --- |
| **0: target definition** | Report a risk forecast and a specified intervention contrast for the same example. | Whether each output answers its declared question; this is not an accuracy contest between different targets. |
| **1: predictive reference** | Compare a prespecified regression with one selected flexible predictor using matched training and evaluation data. | Calibration, prediction error and attribution stability, with output scale and explanation game controlled. |
| **2: discovery** | Compare PC and PC-stable using the same valid test; separately examine a mixed-data test or MGM starting skeleton. | Edge and orientation recovery, unresolved structure, target-pathway recovery and adjustment-set consequences. |
| **3: graph/mechanism review** | Compare unrevised and documented revised inputs under the same attribution method and budget. | Whether changes affect identification and estimates. Report simulated-truth-assisted revisions separately from blinded human review. |
| **4: causal game** | In a small specified system, contrast the predictive and do-interventional coalition values; check each against its own exact calculation. | Implementation correctness and differences between targets, not universal superiority of one game. |
| **5: allocation** | Hold the game fixed and compare symmetric with restricted-order allocation, or compare estimators of one fixed game against its matching oracle. | Separate a changed allocation rule from estimation error. Edge-based methods require an edge-based reference. |
| **6: degradation** | Reduce sample size first; then introduce one prespecified selection, measurement or missingness mechanism before considering combinations. | Repeated full-pipeline uncertainty, failures and target-specific degradation. Add population/mechanism shift as a separately declared scenario. |

Record the generator, estimand, training repetitions, evaluation records, tuning and computation budgets, supplied causal information and failure criteria before running each comparison. An evaluation-record bootstrap for one fitted model does not replace repeated training runs. Preserve null and diagnostic outcomes.

Report four separate quantities: predictive performance; structural recovery; attribution error against a matching game and allocation rule; and ranking agreement with individual intervention effects. Comparing all methods against symmetric do-Shapley is a target-agreement exercise when their estimands differ. Kendall's tau against individual effects is a screening-agreement diagnostic, not interchangeable with attribution accuracy.

The broader degradation comparison remains proposed. The optional detector/filter branch remains unevaluated and should not determine which causal variables are retained without independent evidence. A separate planted mediation case could test a future detector; it would not establish universal upstream suppression. The existing [selection extension](../technical/selection-mechanism.md) is illustrative and supplies no new renal benchmark result.

These comparisons do not establish a universally preferred full pipeline. Interactions between method choices and data conditions remain outside the bounded comparisons, and unsupported identification or support should lead to a narrower claim or additional data rather than a forced attribution.
