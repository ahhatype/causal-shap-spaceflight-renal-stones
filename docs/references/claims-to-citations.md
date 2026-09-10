# Claims to citations: the reframed argument

**Status:** literature check, 2026-09-03. Every reference below was verified
against a publisher, proceedings, PubMed, arXiv, or author page that displays
the citation. Details that could not be confirmed are flagged inline and
again in the closing list. This complements the annotated references in
[`../full_dag/PROVENANCE_AND_REFERENCES.md`](../full_dag/PROVENANCE_AND_REFERENCES.md),
which cover the attribution-method lineage; the claims here are the ones the
1 September 2026 reframing adds ([framing memo](../framing/prediction-vs-intervention.md)).

## Claim 1. Prediction and intervention are distinct modeling goals with distinct playbooks

- Shmueli, G. (2010). To Explain or to Predict? *Statistical Science* 25(3):289-310. <https://doi.org/10.1214/10-STS330>
  Explanatory and predictive modeling differ at every step; explanatory power does not imply predictive power or the reverse.
- Hernán, M.A., Hsu, J., Healy, B. (2019). A Second Chance to Get Causal Inference Right: A Classification of Data Science Tasks. *CHANCE* 32(1):42-49. <https://doi.org/10.1080/09332480.2019.1579578>
  Description, prediction, and causal inference as three distinct tasks; prediction does not answer "what if we intervene."
- Harrell, F.E. Jr. (2015). *Regression Modeling Strategies*, 2nd ed. Springer. <https://doi.org/10.1007/978-3-319-19425-7>
  Section 1.1 "Hypothesis Testing, Estimation, and Prediction" lays out the three purposes. Section 4.12 "Summary: Possible Modeling Strategies" gives separate recipes: 4.12.1 predictive models, 4.12.2 effect estimation, 4.12.3 hypothesis testing. Supporting citation, not the argument's anchor. Numbering confirmed against the book's table of contents and Harrell's online course notes (<https://hbiostat.org/rmsc/intro>, <https://hbiostat.org/rmsc/multivar>).
- Breiman, L. (2001). Statistical Modeling: The Two Cultures. *Statistical Science* 16(3):199-231. <https://doi.org/10.1214/ss/1009213726>
  The data-model versus algorithmic-model split; frames SHAP-on-black-box as the predictive culture. It is about prediction versus data models, not about causal inference; do not overstate.

## Claim 2. Total effects are products of path coefficients; deep effects attenuate and need more precision

Product of coefficients:

- Wright, S. (1921). Correlation and Causation. *Journal of Agricultural Research* 20:557-585. (No DOI.) Origin of path coefficients and tracing rules.
- Wright, S. (1934). The Method of Path Coefficients. *Annals of Mathematical Statistics* 5(3):161-215. <https://doi.org/10.1214/aoms/1177732676>
  Each path's contribution is the product of the elementary coefficients along it.
- Bollen, K.A. (1987). Total, Direct, and Indirect Effects in Structural Equation Models. *Sociological Methodology* 17:37-69. Reprinted in Bollen (1989), *Structural Equations with Latent Variables*, Wiley.
  Indirect effect as the sum of products along directed paths; matrix-power formulation.
- Sobel, M.E. (1987). Direct and Indirect Effects in Linear Structural Equation Models. *Sociological Methods and Research* 16(1):155-176. <https://doi.org/10.1177/0049124187016001006>
  Same decomposition plus delta-method standard errors for products, which is where the precision loss shows up.
- Pearl, J. (2009). *Causality*, 2nd ed. Cambridge University Press. Chapter 5, especially 5.3, on identification in linear models.

Power to detect chained effects:

- Fritz, M.S., MacKinnon, D.P. (2007). Required Sample Size to Detect the Mediated Effect. *Psychological Science* 18(3):233-239. <https://doi.org/10.1111/j.1467-9280.2007.01882.x>
  Sample size for a single-mediator product rises sharply as either path shrinks.
- MacKinnon, D.P., Lockwood, C.M., Hoffman, J.M., West, S.G., Sheets, V. (2002). A Comparison of Methods to Test Mediation and Other Intervening Variable Effects. *Psychological Methods* 7(1):83-104. <https://doi.org/10.1037/1082-989X.7.1.83>
  Low power of causal-steps tests for indirect effects.
- Kenny, D.A., Judd, C.M. (2014). Power Anomalies in Testing Mediation. *Psychological Science* 25(2):334-339. <https://doi.org/10.1177/0956797613502676>
  Caveat: the indirect-effect test can sometimes be more powerful than the total-effect test. Cite as a caveat, not as support.

Measurement error and attenuation:

- Spearman, C. (1904). The Proof and Measurement of Association between Two Things. *American Journal of Psychology* 15:72-101. <https://pubmed.ncbi.nlm.nih.gov/21051364/>
- Hutcheon, J.A., Chiolero, A., Hanley, J.A. (2010). Random measurement error and regression dilution bias. *BMJ* 340:c2289. <https://doi.org/10.1136/bmj.c2289>
- VanderWeele, T.J., Valeri, L., Ogburn, E.L. (2012). The Role of Measurement Error and Misclassification in Mediation Analysis. *Epidemiology* 23(4):561-564. <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3367328/>
  Error in the mediator biases the indirect effect toward the null and the direct effect away from it.

No paper states "effects attenuate geometrically with depth" as a theorem. Derive it from the product rule with standardized coefficients below one in magnitude, and cite Fritz and MacKinnon for the power cost.

## Claim 3. Constraint-based discovery degrades with depth, degree, and conditioning-set size

- Spirtes, P., Glymour, C., Scheines, R. (2000). *Causation, Prediction, and Search*, 2nd ed. MIT Press. PC algorithm, faithfulness, dependence of orientation on skeleton correctness.
- Kalisch, M., Bühlmann, P. (2007). Estimating High-Dimensional Directed Acyclic Graphs with the PC-Algorithm. *JMLR* 8:613-636. <https://www.jmlr.org/papers/v8/kalisch07a.html>
  Consistency needs sparsity and a lower bound on nonzero partial correlations; edges below the bound are not recoverable. The bound is in the paper's assumptions (A4 in the arXiv version), not the abstract; check before quoting.
- Colombo, D., Maathuis, M.H. (2014). Order-Independent Constraint-Based Causal Structure Learning. *JMLR* 15:3921-3962. <https://jmlr.org/papers/v15/colombo14a.html>
  PC-stable; order dependence comes from early conditional-independence errors altering later conditioning sets.
- Zhang, J., Spirtes, P. (2003). Strong Faithfulness and Uniform Consistency in Causal Inference. *UAI 2003*. <https://arxiv.org/abs/1212.2506>
  Uniform consistency needs a floor on dependence strength; weak edges are indistinguishable from absent ones at finite n.
- Uhler, C., Raskutti, G., Bühlmann, P., Yu, B. (2013). Geometry of the faithfulness assumption in causal inference. *Annals of Statistics* 41(2):436-463. <https://arxiv.org/abs/1207.0547>
  The set of non-strong-faithful distributions has non-trivial measure and grows with graph size and density.
- Ramsey, J., Zhang, J., Spirtes, P. (2006). Adjacency-Faithfulness and Conservative Causal Inference. *UAI 2006*, 401-408. <https://dl.acm.org/doi/10.5555/3020419.3020468>
- Zhang, J., Spirtes, P. (2008). Detection of Unfaithfulness and Robust Causal Inference. *Minds and Machines* 18:239-271. <https://doi.org/10.1007/s11023-008-9096-4>
- Faltenbacher, S., Wahl, J., Herman, R., Runge, J. (2025). How PC-based Methods Err. arXiv:2502.14719. <https://arxiv.org/abs/2502.14719> Preprint. How local test errors propagate through the output graph in small samples.
- Averin, P., Moysiadis, T., Katakis, I. (2026). Conditional Independence Tests for Constraint-Based Causal Discovery: A Survey. arXiv:2608.11156. <https://arxiv.org/abs/2608.11156> Preprint. Power decay with conditioning-set size and its consequences for skeleton and v-structure errors.
- Sedgewick, A.J., Shi, I., Donovan, R.M., Benos, P.V. (2016). Learning mixed graphical models with separate sparsity parameters and stability-based model selection. *BMC Bioinformatics* 17(Suppl 5):175.
  The MGM skeleton step of CausalMGM: an undirected graph over mixed continuous and discrete variables, with stability-based sparsity selection.
- Sedgewick, A.J., et al. (2019). Mixed graphical models for integrative causal analysis with application to chronic lung disease diagnosis and prognosis. *Bioinformatics* 35(7):1204-1212. <https://academic.oup.com/bioinformatics/article/35/7/1204/5091182>
  MGM followed by PC-Stable or CPC-Stable over the learned skeleton; the "MGM PC-Stable" the whiteboard names. R package `causalMGM` (CRAN, `pc_stable()`); method note at arXiv:1704.02621.
- Reisach, A., Seiler, C., Weichwald, S. (2021). Beware of the Simulated DAG! *NeurIPS 34*. <https://proceedings.neurips.cc/paper/2021/hash/e987eff4a7c7b7e580d659feb6f60c1a-Abstract.html>
  Varsortability in simulated additive-noise DAGs; standardization matters for synthetic benchmarks like ours.

Support for "hub nodes and depth" is indirect: degree-bounded test counts, power decay with conditioning-set size, error propagation. No paper isolates depth from the outcome as the driver.

## Claim 4. Linear direct effects as a working assumption

- Shimizu, S., Hoyer, P.O., Hyvärinen, A., Kerminen, A. (2006). A Linear Non-Gaussian Acyclic Model for Causal Discovery. *JMLR* 7:2003-2030. <https://jmlr.org/papers/v7/shimizu06a.html>
  Full identifiability under linearity with non-Gaussian noise.
- Hoyer, P.O., Janzing, D., Mooij, J.M., Peters, J., Schölkopf, B. (2009). Nonlinear causal discovery with additive noise models. *NIPS 21*. <https://proceedings.neurips.cc/paper/2008/hash/f7664060cc52bc6f3d620bcedc94a4b6-Abstract.html>
  The nonlinear contrast; linear-Gaussian is the one case where direction is not identifiable.
- Peters, J., Janzing, D., Schölkopf, B. (2017). *Elements of Causal Inference*. MIT Press (open access). Chapters 4 and 7.
- Bühlmann, P., Peters, J., Ernest, J. (2014). CAM: Causal additive models. *Annals of Statistics* 42(6):2526-2556. <https://doi.org/10.1214/14-AOS1260>
- Peters, J., Bühlmann, P. (2014). Identifiability of Gaussian structural equation models with equal error variances. *Biometrika* 101(1):219-228. <https://doi.org/10.1093/biomet/ast043>

No citable source was found arguing that direct mechanisms in epidemiology are approximately linear. Present linearity as a modeling choice justified by identifiability and computability, not as a fact about nature.

## Claim 5. Predictive attribution credits proximal features and is not causal

- Lundberg, S.M., Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions. *NIPS 30*. <https://papers.nips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions>
- Kumar, I.E., Venkatasubramanian, S., Scheidegger, C., Friedler, S. (2020). Problems with Shapley-value-based explanations as feature importance measures. *ICML*, PMLR 119:5491-5500. <https://proceedings.mlr.press/v119/kumar20e.html>
- Janzing, D., Minorics, L., Blöbaum, P. (2020). Feature relevance quantification in explainable AI: A causal problem. *AISTATS*, PMLR 108:2907-2916. <https://proceedings.mlr.press/v108/janzing20a.html>
- Aas, K., Jullum, M., Løland, A. (2021). Explaining individual predictions when features are dependent. *Artificial Intelligence* 298:103502. <https://doi.org/10.1016/j.artint.2021.103502>
- Frye, C., Rowat, C., Feige, I. (2020). Asymmetric Shapley values. *NeurIPS 33*. <https://proceedings.neurips.cc/paper/2020/hash/0d770c496aa3da6d2c3f2bd19e7b9d6b-Abstract.html>
- Heskes, T., Sijben, E., Bucur, I.G., Claassen, T. (2020). Causal Shapley Values. *NeurIPS 33*. <https://papers.nips.cc/paper/2020/hash/32e54441e6382a7fbacbbbaf3c450059-Abstract.html>
  The closest published statement that standard SHAP conflates a root cause's effect with its mediators'.
- Wang, J., Wiens, J., Lundberg, S.M. (2021). Shapley Flow. *AISTATS*, PMLR 130:721-729. <https://proceedings.mlr.press/v130/wang21b.html>
- Jung, Y., Kasiviswanathan, S., Tian, J., Janzing, D., Blöbaum, P., Bareinboim, E. (2022). On Measuring Causal Contributions via do-interventions. *ICML*, PMLR 162. <https://proceedings.mlr.press/v162/jung22a.html>
  Jung et al. characterize allocation of a joint intervention contrast,
  give a sufficient identification criterion and develop discrete-variable
  estimators. This supports specifying the attribution target; it does not
  make do-Shapley equal to an individual intervention effect or establish a
  universal proximity bias. See the [math tutorial](../technical/do-shapley.md).
- Ng, W.Y., Wang, L.R., Liu, S., Fan, X. (2025). Causal SHAP: Feature Attribution with Dependency Awareness through Causal Discovery. *IJCNN 2025*. arXiv:2509.00846, <https://arxiv.org/abs/2509.00846>. IEEE Xplore record 11228295; the IEEE DOI was not retrieved.

No paper proves a general proximity bias. Heskes et al. and Wang et al. are the cleanest published statements; the proximity-bias index and the mediator-inversion tables in this repository are the paper's own evidence.

## Claim 6. Small, selected spaceflight cohorts

- Reynolds, R.J., Day, S.M. (2019). Mortality Among International Astronauts. *Aerospace Medicine and Human Performance* 90(7):647-651. <https://pubmed.ncbi.nlm.nih.gov/31227040/>
- Reynolds, R.J., Day, S.M. (2019). Mortality of US astronauts: comparisons with professional athletes. *Occupational and Environmental Medicine* 76(2):114-117. <https://pubmed.ncbi.nlm.nih.gov/30514748/>
- Reynolds, R.J., Day, S.M., Kanikkannan, L. (2023). Viability of internal comparisons for epidemiological research in the US astronaut corps. *npj Microgravity* 9:36. <https://doi.org/10.1038/s41526-023-00278-z>
- Reynolds, R.J., et al. (2022). Validating Causal Diagrams of Human Health Risks for Spaceflight: An Example Using Bone Data from Rodents. *Biomedicines* 10(9):2187. <https://doi.org/10.3390/biomedicines10092187>
- Antonsen, E., Reynolds, R.J., Charvat, J., et al. (2024). Causal diagramming for assessing human system risk in spaceflight. *npj Microgravity* 10:32. <https://doi.org/10.1038/s41526-024-00375-7>
- Goodenow-Messman, D.A., Gokoglu, S.A., Kassemi, M., Myers, J.G. Jr. (2022). Numerical characterization of astronaut CaOx renal stone incidence rates to quantify in-flight and post-flight relative risk. *npj Microgravity* 8:2. <https://doi.org/10.1038/s41526-021-00187-z>
  First author is Goodenow-Messman. `config/dag_spec.yaml` and the methods draft cite this as "Goodenow et al."; correct before submission.

## Claim 7. Sensitivity gating and two-stage screening

- Fan, J., Lv, J. (2008). Sure independence screening for ultrahigh dimensional feature space. *JRSS-B* 70(5):849-911. <https://doi.org/10.1111/j.1467-9868.2008.00674.x>
- Barber, R.F., Candès, E.J. (2015). Controlling the false discovery rate via knockoffs. *Annals of Statistics* 43(5):2055-2085. <https://doi.org/10.1214/15-AOS1337>
- Barber, R.F., Candès, E.J. (2019). A knockoff filter for high-dimensional selective inference. *Annals of Statistics* 47(5):2504-2537. <https://projecteuclid.org/euclid.aos/1564797855>

Nothing was found on two-channel or "dichromatic" detection inside causal discovery. Cite the screening and knockoff analogs only; present the filter as new.

## Weak or missing support

1. Geometric attenuation with depth: derived, not cited (Claim 2).
2. Kenny and Judd (2014) cuts partly against "deeper is weaker"; cite as a caveat.
3. Depth and hub nodes in PC: indirect support only (Claim 3).
4. Kalisch and Bühlmann's partial-correlation floor: check the assumption label before quoting.
5. "Direct mechanisms are approximately linear": no citation; state as a choice (Claim 4).
6. General proximity bias of SHAP: no proof in the literature; our own evidence (Claim 5).
7. Ng et al. (2025) IEEE DOI not retrieved.
8. Two-channel detection: no literature (Claim 7).
9. Averin et al. (2026) and Faltenbacher et al. (2025) are preprints.
10. "Goodenow et al." was corrected to "Goodenow-Messman et al." in `config/dag_spec.yaml` and the methods draft on 2026-09-03; check the paper's reference list too.
