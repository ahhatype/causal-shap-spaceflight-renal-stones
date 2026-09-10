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

## References

- Jung, Y., Kasiviswanathan, S., Tian, J., Janzing, D., Blöbaum, P., and Bareinboim, E. (2022). [On Measuring Causal Contributions via do-interventions](https://proceedings.mlr.press/v162/jung22a.html). *ICML*, PMLR 162:10476–10501.
- Heskes, T., Sijben, E., Bucur, I. G., and Claassen, T. (2020). [Causal Shapley Values: Exploiting Causal Knowledge to Explain Individual Predictions of Complex Models](https://proceedings.neurips.cc/paper_files/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html). *NeurIPS* 33:4778–4789.
- [Technical BibTeX](../references/technical-companion.bib).
