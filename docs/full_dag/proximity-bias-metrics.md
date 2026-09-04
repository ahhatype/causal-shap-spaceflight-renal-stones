# Proposal: DAG Distance and Proximal Attribution Bias

> Ported from the Box project folder on 2026-09-04 (Andy Wilson's July 2026 notes). Paths and links inside refer to the Target DAGs repository as it stood then; the canonical implementations now live under `analysis/` and `apps/` in this hub.

Date: 2026-07-10

## Research idea

Test whether ordinary SHAP over-allocates feature importance to variables that are topologically close to the target outcome—especially direct parents and late mediators—while under-crediting upstream variables whose effects propagate through the causal system.

This should be treated as a prespecified empirical hypothesis, not an assumed result. A direct cause may genuinely be important. The relevant question is whether a method places **more importance near the outcome than is justified by known interventional truth**.

## Primary topology measure: directed target distance

For feature/node \(X_i\) and target \(Y\), define

\[
d_i(Y)=\min_{p:X_i\rightarrow\cdots\rightarrow Y}|p|,
\]

the length in edges of the shortest directed causal path from \(X_i\) to \(Y\).

- Direct parents have distance 1.
- Earlier ancestors have distances 2, 3, and so on.
- Nodes with no directed path to the outcome are non-ancestors and receive distance \(\infty\).
- The primary analysis should use prediction-time ancestors only. A separate proxy/leakage stress test can include non-ancestors or descendants and report their attribution mass explicitly.

The current SA-07566 graph provides useful distance variation:

| Target | Ancestors | Distance range | Ancestors at each distance |
| --- | ---: | ---: | --- |
| Nephrolithiasis | 28 | 1–6 | 2, 2, 7, 9, 6, 2 |
| Loss of Mission Objectives | 44 | 1–10 | 2, 3, 4, 7, 6, 4, 2, 6, 7, 3 |
| Loss of Crew Life | 41 | 1–9 | 3, 3, 7, 6, 4, 2, 6, 7, 3 |

`Nephrolithiasis` is the natural first endpoint. `Loss of Mission Objectives` is a strong secondary endpoint because it spans more of the DAG and better connects renal risk with operational intervention targets. `Loss of Crew Life` is likely too rare for the first pass.

## Importance and truth on a comparable scale

For attribution method \(m\), define global importance

\[
I_i^{(m)}=\frac{1}{n}\sum_{s=1}^{n}|\phi_{si}^{(m)}|,
\qquad
p_i^{(m)}=\frac{I_i^{(m)}}{\sum_j I_j^{(m)}}.
\]

For the simulation truth, estimate an absolute standardized total causal effect \(T_i\) for each ancestor:

- binary node: absolute risk difference under `do(X=1)` versus `do(X=0)`;
- continuous node: absolute risk difference under a prespecified support-respecting contrast, initially the 75th versus 25th percentile or a truncated one-SD shift;
- use common Monte Carlo exogenous draws for both intervention arms to reduce simulation noise.

Normalize truth as

\[
q_i=\frac{T_i}{\sum_j T_j}.
\]

These are simulation-defined structural effects, not NASA effect estimates. The intervention contrast must be frozen before looking at the SHAP results.

## Proposed primary metrics

### 1. Attribution-weighted mean target distance

\[
\bar d_m=\sum_i p_i^{(m)}d_i,
\qquad
\bar d_T=\sum_i q_i d_i.
\]

This expresses where a method places its attribution mass in units of DAG edges from the target.

Define the **Proximity Bias Index**:

\[
\mathrm{PBI}_m=\bar d_T-\bar d_m.
\]

- `PBI > 0`: attribution is concentrated closer to the outcome than causal truth.
- `PBI = 0`: correct mean causal depth.
- `PBI < 0`: attribution is too far upstream.

The prespecified comparison is

\[
\Delta\mathrm{PBI}=\mathrm{PBI}_{ordinary}-\mathrm{PBI}_{causal}.
\]

The hypothesis predicts \(\Delta\mathrm{PBI}>0\), with Causal SHAP closer to zero.

### 2. Distance-concentration curve

For hop radius \(k\), define cumulative attribution mass within \(k\) hops of the target:

\[
C_m(k)=\sum_{i:d_i\leq k}p_i^{(m)},
\qquad
C_T(k)=\sum_{i:d_i\leq k}q_i.
\]

If ordinary SHAP over-emphasizes proximal features, its curve will sit above the truth curve at small \(k\). Causal SHAP should more closely track truth.

Summarize the curve with a signed **Proximal Over-attribution Area**:

\[
\mathrm{POA}_m=\frac{1}{K-1}\sum_{k=1}^{K-1}\{C_m(k)-C_T(k)\}.
\]

Positive values indicate excess cumulative importance near the target. Report the curve itself alongside this scalar because two distributions can have the same mean distance.

### 3. Distance-specific calibration

Aggregate mass at each exact distance and calculate

\[
R_m(k)=\frac{\sum_{i:d_i=k}p_i^{(m)}+\epsilon}
{\sum_{i:d_i=k}q_i+\epsilon}.
\]

Values above 1 mean over-attribution at that causal depth. This is useful diagnostically but is secondary to PBI and the concentration curve.

### Complementary checks

- Spearman/Kendall rank correlation with total-effect truth.
- Top-k recovery and normalized discounted cumulative gain.
- Attribution mass on direct parents, mediators, actionable upstream nodes, and non-actionable nodes.
- Off-path/proxy mass when the stress-test feature set includes non-ancestors.
- Mediator inflation ratio already present in the ACIC Causal SHAP demo.

## Proposed figure

### Primary two-part figure

**Panel A: attribution maps on the ancestor DAG.** Render the same ancestor subgraph three times—interventional truth, ordinary SHAP, and Causal SHAP. Keep node locations fixed. Use node area for normalized importance and node color for directed hop distance. Do not use the label-repulsion leader segments that produced the dial-like artifacts in the first render.

**Panel B: distance-concentration curves.** Plot hop radius on the x-axis and cumulative importance mass within that radius on the y-axis. Add lines for truth, ordinary SHAP, and Causal SHAP. Shade the area where ordinary SHAP exceeds truth. Annotate each method's PBI and POA.

This plot makes the claim visually falsifiable: a proximal-bias result appears as an ordinary-SHAP curve that rises too quickly, while a calibrated method follows the truth curve.

### Optional diagnostic panel

Plot node-level over-attribution

\[
\log_2\{(p_i^{(m)}+\epsilon)/(q_i+\epsilon)\}
\]

against directed distance, with node labels for the largest residuals. A downward trend would show increasing excess attribution near the outcome after accounting for true total effect.

## Analysis sequence

1. Build a target-specific ancestor table from the canonical edge list with node name, directed distance, role, measurement status, and actionability.
2. Lock allowable prediction-time features and explicitly exclude the outcome and post-outcome descendants from the primary analysis.
3. Estimate standardized total-effect truth from the structural model using common-random-number Monte Carlo interventions.
4. Fit one prespecified prediction model and use the identical fitted model, background sample, and evaluation records for all attribution methods.
5. Compute ordinary SHAP first; use the conventional TreeSHAP configuration as the primary foil and record its exact dependence/background settings.
6. Compute DAG-constrained Causal SHAP using the existing ACIC implementation seed.
7. Calculate rank/top-k metrics, PBI, POA, and distance-specific calibration.
8. Repeat over simulation seeds and bootstrap evaluation records. Report confidence intervals for PBI, POA, and the paired ordinary-minus-causal differences.
9. Repeat on NASA-like v4 to quantify how selection and informative missingness change the comparison.
10. Add mediator-heavy and proxy-heavy regimes only after the clean primary result is frozen.

## Guardrails and interpretation

- Do not interpret shortest-path distance as effect magnitude. It is topology, not biology.
- Do not claim proximal bias from a simple negative importance-distance correlation; strong proximal causes may be genuinely important. Calibration against known total-effect truth is essential.
- Standardized interventions across binary and continuous variables require scientific review. Sensitivity analyses should compare quartile shifts, one-SD shifts, and—where meaningful—realistic intervention ranges.
- Shortest directed distance is the transparent primary measure. Mean path length, longest path, path multiplicity, temporal distance, and cost-weighted distance can be later sensitivities.
- Ordinary SHAP may perform well in some regimes. Those regimes should be reported and used to define when DAG-aware attribution adds value.
- Selection and missingness can create predictive importance for non-ancestors. Report this as off-path/proxy attribution rather than forcing those nodes into a finite causal distance.

## Minimal success criterion

On held-out clean simulations, Causal SHAP should be closer to interventional truth than ordinary SHAP on prespecified rank recovery and should have absolute PBI/POA closer to zero. The distance figure is retained whether or not the hypothesis is supported.
