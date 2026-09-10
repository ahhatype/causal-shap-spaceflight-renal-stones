# Path length, response shape and causal credit

This is the technical companion to the [central workflow](../playbook/central-workflow.md)
and [classroom lesson](../classroom/README.md). The propositions below are
conditional mathematical statements, not additional renal findings. The
[do-Shapley tutorial](do-shapley.md) defines the attribution games, their
baselines and the difference from individual intervention effects.

## 1. A cause can receive zero predictive credit

Let $M=aX+\varepsilon_M$ and $Y=bM+\varepsilon_Y$, with independent,
mean-zero disturbances, independent of X, and M measured exactly. Then
$E[Y\mid X,M]=bM$. A predictor $f(X,M)=bM$ does not use X, so a
model-interventional Shapley game assigns X zero credit. Conditional SHAP
need not: it can use the association between X and M. Meanwhile,

$$E[Y\mid do(X=x_1)]-E[Y\mid do(X=x_0)]=ab(x_1-x_0).$$

Full mediation, exact measurement and the chosen attribution game matter.
For the four-node animation, the corresponding effect slope is $abc$.
This distinguishes a model explanation from an intervention contrast;
it does not establish a universal upstream bias.

For the [two-player lab](../classroom/lab.py), $a=b=0.6$, $x=1$ and
$\varepsilon_M=0.2$, giving $m=0.8$ and $f=0.48$. The predictive coalition
values for $\varnothing,X,M,XM$ are $(0,0,0.48,0.48)$. In the specified
structural game they are $(0,0.36,0.48,0.48)$: jointly intervening on M
holds it fixed, even when X is also set. Therefore

$$\phi_X=\tfrac12(0.36-0)+\tfrac12(0.48-0.48)=0.18,$$
$$\phi_M=\tfrac12(0.48-0)+\tfrac12(0.48-0.36)=0.30.$$

Both credit vectors sum to 0.48; the effect of setting X from 0 to 1 is
0.36. [Heskes et al.](https://proceedings.neurips.cc/paper_files/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html)
provides the causal-game framework; [Jung et al. (2022)](https://proceedings.mlr.press/v162/jung22a.html)
extend the do-Shapley treatment to inaccessible outcome mechanisms. This
symmetric toy illustrates that game, separately from its discrete-variable
estimation theory and our asymmetric full-DAG prototype.

## 2. Path products explain attenuation under stated conditions

For an acyclic affine structural model $Z=BZ+\alpha+\varepsilon$, with
$B_{ji}$ the coefficient on $i\to j$, acyclicity makes B nilpotent. The
total effect between distinct nodes is

$$\tau_{j\leftarrow i}=[(I-B)^{-1}]_{ji}
=\sum_{p:i\leadsto j}\prod_{e\in p}\beta_e.$$

See [Wright (1934)](https://doi.org/10.1214/aoms/1177732676) and
[Sobel (1987)](https://doi.org/10.1177/0049124187016001006).
On a *single* standardized chain with every coefficient $\beta=0.6$,
$\tau_d=0.6^d$: 0.6, 0.36, 0.216, 0.1296 and 0.07776 at depths 1–5.
For a general DAG, path multiplicity, signs and coefficient magnitudes
can change this ordering. Even coefficients below one on every edge do
not guarantee that total effects decrease with shortest-path distance.

**Suggested callout:** A longer pathway can be harder to detect. State
the coefficients and competing paths before treating this as a prediction.

## 3. What the recorded depth experiment actually tests

![Path length and detection in the standardized teaching chain](../images/depth_washout.png)

The generator uses independent Gaussian disturbances and unit population
variance at each node: each child equals $0.6$ times its parent plus a
disturbance with SD $\sqrt{1-0.6^2}$. It draws 400 datasets at each of 18
sample sizes from 25 to 4,000, with seed 20260904. For each depth it computes
the sample correlation r and

$$t=r\sqrt{\frac{n-2}{1-r^2}},\qquad \text{detected}=\mathbf1\{|t|>1.96\}.$$

The fixed cutoff is an **approximate** two-sided 5% rule. It is not the
exact finite-sample $t_{n-2}$ critical value. The recorded CSV and figures
retain that rule; no results were retuned during consolidation. The plotted
$1/\sqrt n$ is a sample-size scale, not the actual slope standard error.
At n=25, recorded detection is 92.75%, 19% and 8% at depths 1, 3 and 5.
These are Monte Carlo proportions, not guaranteed power values. At 400
replicates their binomial standard error is $\sqrt{\hat p(1-\hat p)/400}$
(at most 0.025); observing 100% does not prove population power equals one.

For a weak standardized marginal association $\rho=\beta^d$, the rough
signal scale is $\sqrt n\,\rho$. Holding it fixed suggests
$n\propto|\beta|^{-2d}$. This is a heuristic for this chain, not an exact
sample-size formula or a mediation/discovery test. [Fritz and MacKinnon
(2007)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2843527/) study power for
mediated-effect tests, which are related but different calculations.

| Resource | Source |
| --- | --- |
| Simulation, test and original plotting code | [depth_washout_figure.py](../../analysis/depth_washout_figure.py) |
| Frozen teaching results | [depth_washout.csv](../../results/figures/depth_washout.csv) |
| Original full figure | [PNG](../images/depth_washout.png) |
| Summary figure | [SVG](../images/depth-detection.svg) |
| Simplified figure renderer | [build_tutorial_figures.py](../../site/build_tutorial_figures.py) |

```bash
python analysis/depth_washout_figure.py --verify-recorded
python analysis/depth_washout_figure.py --render-recorded
```

The first command reproduces the Monte Carlo calculations and compares them
with the frozen CSV without writing it. The second redraws from that CSV.
This experiment does not measure graph-discovery accuracy, measurement-error
bias, SHAP importance or astronaut effects. The Gaussian-PC disconnected
outcome is a separate working-subgraph diagnostic.

## 4. Direct relationships need not be straight lines

A direct arrow specifies a structural dependency. It does not specify its
response shape. For $Y=X^2+\varepsilon$, the contrast from -1 to 1 is zero
but the contrast from 0 to 2 is four. Neither erases the direct causal arrow.
For twice-differentiable g with $|g''|\le K$ over the chosen interval,

$$|g(x+\Delta)-g(x)-g'(x)\Delta|\le\tfrac12 K\Delta^2.$$

**Suggested callout:** Over a limited range, a straight line can be a useful
approximation. Whether it is adequate depends on curvature and the size of
the proposed change. The renal generator's binary-logit outcome and
interaction already depart from a wholly linear-Gaussian system.

## 5. Where Wahba and affine splines fit

An affine function has the form $a+bx$. A continuous piecewise-affine spline
joins straight segments, for example

$$g(x)=a+bx+\sum_k c_k(x-\kappa_k)_+,\qquad (u)_+=\max(u,0).$$

The knots $\kappa_k$ mark changes of slope. This is distinct from a cubic
smoothing spline. In the classical smoothing objective

$$\min_g\;\frac1n\sum_i(y_i-g(x_i))^2+\lambda\int[g''(t)]^2dt,$$

affine functions have zero curvature penalty; the fitted curve can bend
when the data support it. [Wahba (1990)](https://epubs.siam.org/doi/book/10.1137/1.9781611970128)
develops smoothing splines and their reproducing-kernel framework. For this
project that motivates a *proposed* response-shape sensitivity analysis:
keep the causal question explicit while comparing affine and flexible
mechanisms. Fitting a spline alone identifies neither causal direction nor
an intervention effect. No Wahba-based renal comparison has been run.

For example, two standardized Gaussian models can have the same observed
covariance 0.6: $M=0.6X+\sqrt{0.64}\varepsilon_M$, or
$X=0.6M+\sqrt{0.64}\varepsilon_X$. The effect of do(X) on M is 0.6 in the
first and zero in the second. [Shimizu et al. (2006)](https://jmlr.org/papers/v7/shimizu06a.html)
requires additional assumptions, including non-Gaussian independent noise
and no hidden confounders, for its linear discovery result.

Machine-readable citations: [technical-companion.bib](../references/technical-companion.bib).
Broader attribution and spaceflight references remain in the
[reference map](../references/manuscript-references.md).
