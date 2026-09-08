# Educator guide and answer key

Prerequisites: regression, conditional expectation and basic causal graphs.
Open the downloaded kit's `index.html` for the offline interactive lesson.
Run `python lab.py --check` from the extracted kit, or
`python docs/classroom/lab.py --check` from the repository root.

## Session plan

| Minutes | Activity | Teaching purpose |
| --- | --- | --- |
| 0–5 | Ask learners which variable the predictor should credit, without revealing effects | Elicit a prediction before the explanation |
| 5–15 | Work worksheet 1–2 and reveal model-interventional credit | Separate an unused predictor input from a non-cause |
| 15–25 | Switch to structural credit; work questions 3–4 | Define the coalition game and distinguish attribution from intervention effect |
| 25–35 | Run zero/negative-edge and nonlinear cases | Make assumptions and intervention ranges concrete |
| 35–45 | Compare the two Gaussian directions; inspect research status | Separate identification, precision, and prototype evidence |
| 45–50 | Exit ticket and discuss a next experiment | Check transfer rather than memorization |

For 90 minutes, add 20 minutes modifying `lab.py` and 20 minutes reading one frozen renal result and its generating script. Installation is unnecessary for the analytic lab; do not spend the introductory session setting up the full research stack.

## Answer key

1. No extra predictive information under the specified chain and exact M; yes, X remains a cause if ab≠0. The conditions matter. Measurement error or another unblocked path can change the screening-off statement.
2. Coalition values: 0, 0, 0.48, 0.48. Predictive φX=0, φM=0.48. These sum to f(x,m)−E[f]=0.48; E[f]=0 because the population disturbances and X have mean zero.
3. Structural v(X)=0.36; other coalition values stay as above. Symmetric Shapley averaging gives φX=0.18 and φM=0.30, still summing to 0.48. Jointly setting X and M blocks further propagation into the already-set M.
4. The population intervention contrast is 0.36. It is not 0.18. A Shapley attribution averages marginal contributions over coalitions; a specified intervention contrast asks a different question. Neither signed local credit nor global mean absolute credit is automatically an achievable benefit.
5. At a=0, X has no pathway effect and both games assign it zero. At a=−0.6, intervention effect is −0.36 and structural φX=−0.18; φM=−0.06 for eM=0.2. Signs change, arrows do not. The chart reports signed values, not importance magnitudes.
6. For Y=X²+eY with mean-zero eY, changing X from −1 to 1 gives contrast 0; changing it from 0 to 2 gives contrast 4. X directly causes Y nonlinearly; a symmetric contrast can be zero despite a causal relationship. A local tangent approximation is range-dependent and fails at a stationary point for large shifts.
7. Both models have unit marginal variances and covariance 0.6 with independent Gaussian disturbances. The joint observational distribution is identical. The do(X) effect is 0.6 in A and zero in B. Linearity alone cannot choose a direction.
8. 0.6 and 0.07776. Parallel paths can add, opposing paths can cancel, and coefficients above one can amplify. This is a conditional attenuation lesson, not a universal ordering rule.
9. Examples: repeated data/training seeds; more evaluation/background/permutation samples; graph misspecification; nonlinear generator; held-out or genuinely independent expert review; outcome-scale and intervention-range sensitivity. Scripted graph edits are not human validation.

## Assessment

Use the full-DAG structural-propagation prototype as the default research result for the exit ticket: what information did it receive, and what should be varied in a replication?

Score each exit ticket 0–2 on four dimensions (8 points total): distinguishes prediction from intervention; names the assumptions; distinguishes φX from do(X) effect; proposes a relevant validation test. Award full credit for a correct alternative counterexample with explicit assumptions.

## Accessibility and scope

The browser lesson has keyboard-operable controls, text tables duplicating bars, no autoplay, and no external dependencies. The worksheet works on paper; lab.py gives a text-only route. Numbers are exact examples, not noisy fitted estimates. The classroom model excludes confounding except in the separate directional-identification example and never recommends an action for a person.

For path products, the exact recorded detection rule and spline context, see
the repository [technical note](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/technical/path-length-and-response-shape.md).

## Reading

- Heskes et al. (2020), causal coalition values: https://proceedings.neurips.cc/paper_files/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html
- Shimizu et al. (2006), assumptions for LiNGAM: https://jmlr.org/papers/v7/shimizu06a.html
- Wang et al. (2021), edge attribution: https://proceedings.mlr.press/v130/wang21b.html
- [Comparison inputs and information supplied](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/playbook/central-workflow.md#what-information-each-comparison-receives)
- [Full-DAG research record](https://github.com/ahhatype/causal-shap-spaceflight-renal-stones/blob/main/docs/full_dag/RESEARCH_RECORD.md)
- Current project companion: https://github.com/ahhatype/causal-shap-spaceflight-renal-stones

These readings motivate distinctions; the lab's analytic derivations are provided above. Do not describe the symmetric two-player toy as an implementation of all variants in these papers.
