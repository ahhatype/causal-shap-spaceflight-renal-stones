# Prediction credit, causal contributions and intervention effects

Shapley averaging can allocate different quantities. The scientific question
is determined by the coalition value function: what does it mean to include
a variable, and what happens to the variables not included?

## Three questions

For a fitted predictor f, a record v and feature indices N, common games are:

| Question | Coalition value | What happens to the other variables? |
| --- | --- | --- |
| Which observed inputs explain this prediction? | $v_{cond}(S)=E[f(V)\mid V_S=v_S]$ | Their distribution is conditioned on the observed inputs. |
| Which model inputs contribute when replaced against a background? | $v_{model}(S)=E[f(v_S,V_{-S})]$ | They retain their joint marginal background distribution; changes are not propagated along causal arrows. |
| How much outcome change should be allocated to each part of a joint intervention? | $v_{do}(S)=E[Y\mid do(V_S=v_S)]$ | Unfixed variables respond according to the causal system. |

The second is commonly called *interventional SHAP* in model-explanation
software. The third defines the *do-Shapley* game. The two can coincide under
appropriate causal and outcome-model assumptions, such as a correctly
specified outcome model with no causal effects among its input features and
no unmeasured input–outcome confounding. The word “interventional” alone does
not specify which question is being answered.

[Heskes et al. (2020)](https://proceedings.neurips.cc/paper_files/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html)
develop causal Shapley values for prediction explanations.
[Jung et al. (2022), Sections 2–5](https://proceedings.mlr.press/v162/jung22a/jung22a.pdf)
use the same interventional equation and extend its treatment to outcomes
whose generating model is inaccessible, with axioms, identification results
and observational-data estimators. Their uniqueness result holds under their
specified axioms; it does not select the appropriate causal question for an
application.

## The allocation and its baseline

For any specified game v, symmetric Shapley credit is

$$\phi_i(v)=\sum_{S\subseteq N\setminus\{i\}}
\frac{|S|!(n-|S|-1)!}{n!}\,[v(S\cup\{i\})-v(S)].$$

Equivalently, average the contribution made when i joins over all uniformly
weighted variable orders. Each order telescopes from the empty coalition to
the full coalition, so

$$\sum_i\phi_i(v_{do})=E[Y\mid do(V=v)]-E[Y].$$

Jung et al. center the outcome so that E[Y]=0. With an uncentered outcome,
the baseline subtraction must remain explicit.

**A share of a joint intervention is a different target from an individual
intervention effect.** For example,

$$\Delta_i(h,l)=E[Y\mid do(V_i=h)]-E[Y\mid do(V_i=l)]$$

lets all other variables respond in both arms. Shapley credit also considers
coalitions that have already fixed some of those variables.

## Worked calculation: X → M → Y

Let M=0.6X+eM and Y=0.6M+eY, with mutually independent mean-zero X, eM and
eY. At x=1 and eM=0.2, m=0.8. The ideal predictor f=0.6M gives 0.48.

| Coalition fixed at the record's values | Model-interventional game | do-Shapley game |
| --- | ---: | ---: |
| None | 0 | 0 |
| X=1 | 0 | 0.36 |
| M=0.8 | 0.48 | 0.48 |
| X=1, M=0.8 | 0.48 | 0.48 |

Fixing X changes the expected mediator to 0.6 and hence the expected outcome
to 0.36. Fixing M overrides its equation, including its response to X.
Therefore,

$$\phi_X=\tfrac12(0.36-0)+\tfrac12(0.48-0.48)=0.18,$$
$$\phi_M=\tfrac12(0.48-0)+\tfrac12(0.48-0.36)=0.30.$$

The model-interventional credits are (0, 0.48). The effect of changing X
from 0 to 1 is 0.36. All three answers are correct for their stated targets.

Restricting the order to X before M gives (0.36, 0.12). This is an asymmetric
allocation of the same causal game, not the symmetric do-Shapley value.
The [Python lab](../classroom/lab.py) independently enumerates both orders
and checks them against the closed-form values:

```bash
python docs/classroom/lab.py --oracle
python docs/classroom/lab.py --check
```

This is an exact analytic oracle check, not a fitted estimator or a new renal
result. It illustrates the game on a continuous chain; it does not establish
the applicability of Jung et al.'s discrete-variable estimation theory to
continuous data.

## Identification, estimation and decisions

Jung et al. give a sufficient graphical criterion for identifying the
coalition effects, including some graphs with latent confounding. Their
estimator development focuses on discrete variables and the Markovian and
direct-cause settings. It uses inverse probability weighting, outcome
regression and double/debiased machine learning with sample splitting and
sampled permutations. Double robustness concerns specified nuisance-model
errors; it does not repair an incorrect graph or inadequate intervention
support. The general identification criterion is not a general-purpose
estimator for every graph with hidden confounding.

Our renal generators contain continuous and binary variables. Extending
these estimators requires an explicit identification and estimation design.
Choosing a feasible action additionally requires an intervention contrast,
uncertainty, timing, feasibility and cost; the allocation alone supplies no
action recommendation.

## What the renal benchmark measures

The existing renal scores compare global mean-absolute attribution rankings
with individual high-versus-low intervention-effect rankings. They measure
agreement with an intervention-screening target. They do not isolate error
in estimating the attribution method's own target: even an exact do-Shapley
allocation need not equal the individual intervention effects.

The full-DAG prototype uses known mechanisms, graph-respecting orders and
the fitted XGBoost margin as its outcome. It is not Jung et al.'s symmetric
outcome-based estimator. Changing the outcome from risk to model log-odds,
the order distribution, the player set or the global aggregation changes
the comparison. See the [comparison inputs](../playbook/central-workflow.md#what-information-each-comparison-receives).

A future renal oracle comparison should measure attribution error against
the same game's known values, then report agreement with individual effects
as a separate criterion. Match outcome scale, intervention values, player
set, order weights and sampling budgets. The two-player oracle above is
complete; a renal do-Shapley oracle or DML comparison has not been run.

## ConfoundingSHAP: attribution of adjustment bias

[Brockschmidt et al. (2026)](https://arxiv.org/abs/2605.10533v1) ask which measured
covariates account for changes in a treatment-effect estimate as adjustment is
expanded. Section 2, Table 1 and Supplement A distinguish explanations of
treatment assignment, predicted outcomes, effect heterogeneity and confounding
bias. They explicitly distinguish their bias game from causal, asymmetric and
do-Shapley attribution.

For binary treatment A, outcome Y and eligible pretreatment covariates X, define

$$\delta_S(x_S)=E[Y\mid A=1,x_S]-E[Y\mid A=0,x_S],\qquad
\tau_S(x_S)=E[\tau(X)\mid X_S=x_S].$$

Both contrasts use the same information level. Residual bias is
$b_S=\delta_S-\tau_S$. The local game is $v_x(S)=-b_S(x_S)$ and the signed
global game is $v(S)=-E[b_S(X_S)]$. Under valid full adjustment, the credits sum
to the crude-minus-adjusted ATE contrast. Each local explanation has this same
total, although its allocation varies across profiles. Global signed credit
equals average local signed credit; mean absolute local credit is different.

The method needs consistency, overlap and a sufficient full adjustment set,
even without a complete DAG. It cannot certify adjustment sufficiency or reveal
unmeasured confounding. Zero credit can reflect cancellation. Nonzero credit can
arise for proxies or instruments that amplify residual confounding. Scores do
not automatically identify graph roles.

### Relation to the proposed detector

ConfoundingSHAP supplies a treatment-specific adjustment diagnostic for Step 3,
with its game specified in Step 4 and robustness assessed in Step 6. Its output
has outcome units, such as risk difference. LumaWarp's proposed detector supplies
feature flags for graph review through a separate
[public interface](../../python/src/causal_shap_renal/lumawarp_contract.py).
Its depth, importance and complexity channels are standardized within groups;
validation remains pending. ConfoundingSHAP belongs alongside these diagnostics,
not in place of a detector channel or an edge weight. The provisional graph
complexity index in `apps/causal_shap/complexity.py` is distinct from both.

Randomized treatment can have zero ConfoundingSHAP despite strong predictors,
effect heterogeneity or complex mechanisms. A simple system can have substantial
confounding. A joint experiment should vary confounding, depth and mechanism
complexity separately and assess each output against its own target. No LumaWarp
comparison is reported here.

### Bounded renal comparison

The [comparison script](../../analysis/confoundingshap_comparison.py) uses the
existing 10,000-record, **51-node/75-edge clean simulation**. Treatment is
thiazides, outcome is nephrolithiasis, and the players are Medical Prevention
Capability, bisphosphonates, potassium citrate and water intake. Graph checks
confirm that the first alone blocks all backdoors, and adding the others
preserves sufficiency. All are treatment nondescendants. The sibling treatments
also affect the outcome; they are not pure proxies.

All 16 coalitions use saturated binary-cell outcome means and shapiq 1.7.0's exact
Shapley calculator, across five prespecified 6,000/4,000 training/evaluation
splits. This is an independent plug-in implementation of the signed game,
**not a replication of the authors' TabPFN estimator**. All training arm/covariate
cells are populated (minimum across splits: 38). The crude contrast is estimated
in training data; adjusted contrasts use the evaluation covariate distribution.
Finite-split discrepancies include nuisance error and composition variation.

| Covariate | Mean signed contribution, percentage points | Range across five splits |
| --- | ---: | ---: |
| Medical Prevention Capability | -0.413 | -0.530 to -0.327 |
| Bisphosphonates | -0.086 | -0.102 to -0.073 |
| Potassium citrate | -0.003 | -0.032 to +0.015 |
| Water intake | -0.012 | -0.035 to +0.016 |

The negative total means the crude estimate is more negative than the adjusted
estimate. Medical Prevention Capability receives the largest absolute signed
contribution in every split. These ranges describe split sensitivity, not
confidence intervals or independent simulation replications. Adjusted risk
differences range from -1.72 to -2.91 percentage points, versus -1.77 to -1.80
for the finite-sample generating-model reference. Stable attribution ordering
therefore does not establish accurate effect estimation.

The reference reconstructs expected potential outcomes under the canonical
mechanisms: thiazides changes the outcome logit through its only directed path
by $-0.70(0.60)(0.60)=-0.252$. Paired probability differences averaged over each
evaluation split supply an ATE diagnostic, not an oracle for confounding
allocation. Outputs also show conditional SHAP for the fitted control-outcome
model and CATE. Those mean-absolute summaries answer different questions; they
are not accuracy competitors or the historical TreeSHAP benchmark.

Two exact synthetic checks make the distinction concrete. Independent
Bernoulli(1/2) variables C and Z, propensity $0.1+0.3C+0.3Z$, and outcome mean $C+\tau A$ give signed credits
0.332008 for confounder C and **-0.019508 for instrument Z**. Adjusting for Z
amplifies remaining bias before C enters. Adding independent effect-modifier and
outcome-only variables separates CATE and outcome importance; randomizing
treatment makes the bias game zero while those other signals remain. These are
independently derived checks, not results reported by the paper or renal effects.

The 14-node calcium example needs a separate treatment design. Thresholding
observed continuous calcium does not define an intervention that sets calcium;
its original instrument need not satisfy exclusion for the new indicator.
Hydration's independence can imply zero **global signed** confounding credit in
the clean generator without implying zero local absolute credit. Its positive
calcium interaction changes the log-odds slope; risk-difference attenuation or
large CATE importance should not be assumed before calculation.

### Package and reproduction

The completed TabPFN-2.5 comparison uses the same five 6,000/4,000 splits and
all 16 coalitions. Mean held-out signed contributions are:

| Covariate | Cell means, percentage points | TabPFN-2.5, percentage points |
| --- | ---: | ---: |
| Medical Prevention Capability | -0.413 | -0.472 |
| Bisphosphonates | -0.086 | -0.403 |
| Potassium citrate | -0.003 | -0.284 |
| Water intake | -0.012 | -0.290 |

The largest absolute contribution under TabPFN belongs to Medical Prevention
Capability in two splits, bisphosphonates in two and water intake in one. Under
cell means, Medical Prevention Capability leads in all five. This is an
estimator-sensitivity result; there is no renal allocation oracle establishing
which credit vector is more accurate.

The average adjusted risk difference is -1.229 percentage points with TabPFN,
-2.163 with cell means and -1.786 for the generating-model reference. Across the
five splits, mean absolute ATE error is 0.615 versus 0.434 percentage points,
respectively. TabPFN estimates range from -1.889 to -0.592 percentage points.
These settings do not demonstrate improved effect estimation with TabPFN.
The comparison varies the data split and model seed together; it does not
separate their contributions or establish general estimator superiority.

Outcome and CATE importance are also saved for both estimators. They describe
conditional mean-absolute Shapley values of the population-specific,
state-averaged fitted surfaces. Signed confounding credit has a different
target and aggregation. Numerical variation between predictions for identical
states is recorded by the audit; state weighting reproduces the actual-row
population means. The full-model anchor is an estimate, not observed causal
truth, so larger total allocated bias may reflect estimation error.

The [released implementation](https://github.com/mmschlk/shapiq/blob/v1.7.0/src/shapiq_games/benchmark/causal_xai/base.py)
provides `GlobalConfoundingXAI` and `LocalConfoundingXAI` in
`shapiq_games.benchmark.causal_xai`. These hardcode TabPFN nuisance fits, without a
sklearn backend. Version 1.7.0 needs Python 3.12 or later. Select the model
version explicitly: the installed TabPFN 9.0.0 default
is model 3.5, whereas the paper used 2.5. The
[TabPFN comparison](../../analysis/confoundingshap_tabpfn.py) explicitly selects
model 2.5 in the upstream S-learner, with one ensemble member and a fixed seed
per split. It predicts all 6,000 training and 4,000 evaluation rows separately
using float32 inference. It retains both the training-population signed game
and a held-out standardization matched to the cell-mean reference. These are
documented adaptations of the released estimator, not a reproduction of every
experiment in the paper.

Use an isolated environment with the project dependencies and
`analysis/requirements-confoundingshap.txt`, then:

```bash
python analysis/confoundingshap_comparison.py
python -m pytest python/tests/test_confoundingshap_comparison.py
```

[Outputs and metadata](../../analysis/output/confoundingshap_pilot/) preserve
hashes, versions, seeds, coalition values and limitations. Checks cover Shapley
efficiency, an independent factorial calculation, exact synthetic oracles and
local/global averaging. [TabPFN outputs](../../analysis/output/confoundingshap_tabpfn/)
also retain population-specific predictions and a paired comparison. The
[audit](../../analysis/audit_confoundingshap_tabpfn.py) reconstructs these results,
checks empirical standardization and optionally repeats a model fit. Repeated
data generation and detector comparisons remain pending. In the upstream global signed game, the
supplied mean CATE is an additive constant and cancels from all Shapley marginals.
Here the anchor reuses the full fitted S-learner, so the full-set residual is
zero by construction. With a separately estimated CATE anchor, the upstream
finite-sample endpoint need not be zero. Neither endpoint verifies identification.

## References

- Jung, Y., Kasiviswanathan, S., Tian, J., Janzing, D., Blöbaum, P., and Bareinboim, E. (2022). [On Measuring Causal Contributions via do-interventions](https://proceedings.mlr.press/v162/jung22a.html). *ICML*, PMLR 162:10476–10501.
- Heskes, T., Sijben, E., Bucur, I. G., and Claassen, T. (2020). [Causal Shapley Values: Exploiting Causal Knowledge to Explain Individual Predictions of Complex Models](https://proceedings.neurips.cc/paper_files/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html). *NeurIPS* 33:4778–4789.
- [Technical BibTeX](../references/technical-companion.bib).
- Brockschmidt, M., Thies, S. M. A. R., Schröder, M., Frauen, D., Melnychuk, V., Muschalik, M., Hüllermeier, E., and Feuerriegel, S. (2026). [ConfoundingSHAP: Quantifying confounding strength in causal inference](https://arxiv.org/abs/2605.10533v1). arXiv:2605.10533v1, preprint.
