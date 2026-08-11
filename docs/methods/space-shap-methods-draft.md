> Snapshot converted from "Space SHAP: Intro & Methods Drafts.docx" on 2026-08-11.
> This is a working draft, not the source of truth. Update this copy when the
> original document changes.

[This is human written with an LLM editor providing revision
suggestions. Let's make sure we don't ever let an LLM rewrite it -
Nature explicitly restricts that. Use LLM to guide revisions, but make
sure a human is always rewriting this.]{.mark}

[-- TO REVIEW: I had Claude add citations where I was going off the book
-- I need to check all citations.]{.mark}

Understanding the complex, interrelated pathways between spaceflight
environmental hazards and multiple mission-level outcomes is a critical
need to support future deep space travel (Reynolds et al., 2022; NASA,
2022). Spaceflight data sets present unique challenges for
epidemiological research and risk assessment modeling due in part to
their sparseness and inherent selection bias (Reynolds & Day, 2019;
Reynolds et al., 2023); recent innovations in predictive and statistical
methods provide promising remedies to these limitations (Li et al.,
2023; Sanders et al., 2023; Scott et al., 2023). However, application of
novel methods without well-informed, causal reasoning may lead to naive
calculations that are confidently backed by data but not by realistic
mechanisms (Hooker & Mentch, 2019; Reisach et al., 2021); this is
particularly true when the methods employ machine learning (ML).

In support of causally motivated research, the Human System Risk Board
(HSRB) team at the National Aeronautics and Space Administration (NASA)
maintains expert-driven directed acyclic graphs (DAGs) for the
approximately 30 known spaceflight risks (Antonsen et al., 2024). In
addition to providing justifiable, foundational models that are easily
communicated between researchers, DAGs also codify causal relationships
in a manner that is interpretable to machines; they are used as baseline
data for many causal packages and predictive models (Kalisch et al.,
2012; Textor et al., 2016; Sharma & Kiciman, 2020). The lifecycle of
these DAGs includes human review as well as data-driven validation;
explicitly defined metrics and evaluation procedures weight evidence
from multiple sources to evaluate effect strength and to affirm and
refine the edges in NASA\'s maintained DAGs (Reynolds et al., 2022;
Antonsen et al., 2023; Ward et al., 2024).

Explainable AI (XAI) has emerged to make the behavior of otherwise
opaque ML models transparent, offering methods applied after a model is
trained, which quantify how individual input features contribute to its
predictions (Barredo Arrieta et al., 2020; Vilone & Longo, 2021). Based
on Shapley values, a cooperative game-theory method for fairly
distributing a payout among the players who produce it, SHAP treats each
input feature as a player and assigns it the marginal contribution it
makes to a given prediction, yielding additive and locally accurate
feature attributions (Lundberg & Lee, 2017; Shapley, 1953). Out of the
box SHAP and similar algorithms derive feature importance without a
causal framework; epidemiology teams increasingly interpret these
outputs to inform causal pathways and to guide study design and
statistical analyses (Lundberg et al., 2020; Annals of Epidemiology,
2025). XAI algorithms, such as SHAP, offer a data-driven approach to
validate and enhance these diagrams.

However, out of the box SHAP does not see causal structures and thus can
identify spurious relationships and underweights downstream effects in
favor of features proximate to the outcome (\[your ACIC / Tao of RWD
Causal SHAP poster\]; Janzing et al., 2020; Aas et al., 2021; Kumar et
al., 2020; Ng et al., 2025). Because these attributions carry the errors
noted above, their interpretation risks incorrect causal conclusions
unless paired with critical human oversight. Causally informed SHAP, by
contrast, is aware of the causal structure, which provides opportunities
for capturing feature importance and effect strength with higher
fidelity (Ng et al., 2025).

[{To do: I need to write the paragraph on what causally informed SHAP is
and overview each individual method and dependency on DAG}.]{.mark}

To our knowledge, no prior work has applied causal feature-attribution
methods to human spaceflight epidemiology, nor systematically
benchmarked out-of-the-box SHAP against causally informed variants under
the data constraints characteristic of astronaut cohorts. This gap is
one the architects of NASA\'s DAG program have themselves flagged;
machine learning has been named as a priority future direction for
populating and refining the risk DAGs (Reynolds et al., 2022; Sanders et
al., 2023). By evaluating how well a validated ground-truth DAG can be
recovered under both full and partial specification, as well as under
progressive degradation toward realistic spaceflight data conditions,
this work directly addresses that need and offers a reusable template
for causally faithful attribution in sparse, highly selected cohorts.

[This paper offers a systematic evaluation of the results of out of the
box SHAP versus causally informed SHAP variants, evaluated against a
ground truth. Using synthetic data, seeded with DAGs from NASA\'s
maintained library, we will consider how well multiple frameworks and
multiple engines can recover a DAG with either full or partial initial
specification. \[\[To do: Once we finalize the full scope of this
article, finalize to encompass all the work we do.\]\]]{.mark}

Methods (optimistic draft)

[It is unlikely all of this will remain in scope for the article, but
preserving as a goal and future direction. This is LLM generated text
based on my direction and planning based on our conversation July 2026,
and existing work done. Should not be used for the article text - but
rewritten by human when scope determined.]{.mark}

## Overview and study design

We evaluate whether causally informed feature-attribution methods
recover the true intervention-relevant importance of upstream risk
factors more faithfully than standard, causality-blind attribution, and
whether iterative human expert revision of the underlying causal
structure improves that recovery as data are degraded toward the
constraints characteristic of spaceflight epidemiology. The study is
conducted on synthetic data generated from a known causal structure, so
that ground-truth feature importance is defined by construction and
every attribution method can be scored against it. The primary case
study is the NASA Human System Risk Board (HSRB) Risk of Renal Stone
Formation directed acyclic graph (DAG), source identifier SA-07566, with
nephrolithiasis as the confirmed outcome.

All numerical edge coefficients used in data generation are simulation
design parameters informed by the published literature; they are not
empirical NASA effect estimates and are not interpreted as such. Graph
topology is source-aligned to the published NASA DAG; the coefficients
are subject to domain-expert review and are used here solely to define a
ground truth against which attribution methods are compared.

The pipeline is organized into a sequence of numbered steps. Steps 1
through 8 and 10 constitute the core analysis. Steps 9 and 11 are
robustness and generalization extensions that may be reported in
compressed form or deferred to subsequent work depending on space; step
12 is identified as future work; and step 13 is scoped out of the
present paper. Each step is described in turn below.

## Step 1: Exposure and outcome specification

The exposure is cumulative mission duration, operationalized as total
days in microgravity. This continuous framing is preferred over a binary
flown/unflown indicator or a categorical mission-era classification
because it preserves the dose-response relationship that is central to
the underlying physiological mechanism: microgravity-induced bone
resorption elevates circulating and urinary calcium in proportion to
exposure, which in turn drives urinary supersaturation and stone risk.

The outcome is nephrolithiasis, consistent with the target node of the
published NASA DAG. Because symptomatic stone events in the astronaut
corps are rare, and because the richest quantitative evidence attaches
to the upstream supersaturation step rather than to incidence,
calcium-oxalate relative supersaturation (an immediate precursor of
stone formation) is additionally modeled as a continuous secondary
outcome. Nephrolithiasis incidence serves as the clinically anchored
primary target; supersaturation serves as the better-populated
continuous proxy used in sensitivity analyses.

## Step 2: Causal graph construction and expert-guided augmentation

The base causal structure is the NASA HSRB SA-07566 renal stone
formation DAG, obtained in DAGitty form through a domain-expert handoff
and reconciled against the publicly distributed source graph. After
semantic node mapping, the expert-supplied graph and the reference graph
agreed closely (Cohen\'s kappa 0.978; precision 1.000; recall 0.958;
structural Hamming distance 3), with a small number of unmatched edges
retained for expert adjudication.

For tractability and interpretability, a twelve-node working subgraph
was defined around the principal mechanistic pathway, comprising the
exposure (mission duration), demographic and behavioral confounders (age
at launch, sex), a countermeasure-era effect modifier, pre-flight and
in-flight vitamin D status, dietary nutrient intake, the two
bone-remodeling mediators (bone formation and bone resorption),
hydration status, a urine-chemistry composite, a
mineralized-renal-material (supersaturation) mediator, and the
nephrolithiasis outcome. Multi-marker nodes (bone formation, bone
resorption, urine chemistry) are represented as principal-component
composites of their constituent biomarkers.

Two structural distinctions are made explicit. First, variables that
exert genuine causal influence on the mechanism are represented as DAG
nodes with directed edges, whereas variables that restrict cohort
membership (for example, astronaut selection screening) are represented
not as nodes but as a selection mechanism applied during data generation
and stressed in Step 10. Second, vitamin D is represented at two time
points: a pre-flight instance acting as an exogenous confounder, and an
in-flight instance that is itself a child of mission duration and
therefore a mediator. This dual representation reflects the time-varying
nature of vitamin D depletion over long missions and is revisited in the
longitudinal extension (Step 12).

Candidate augmentations to the base graph, drawn from known limitations
of spaceflight epidemiology, are annotated using NASA\'s own
level-of-evidence schema so that added edges are independently
justifiable, and are reviewed by the domain expert before being admitted
to the analysis graph.

## Step 3: Synthetic data generation

Synthetic datasets are generated from the specified DAG using the
simcausal framework, which produces data from user-defined structural
equations and supports the simulation of interventions.
Structural-equation coefficients are literature-informed placeholders
pending domain-expert calibration; where the published literature
supports only the direction of an effect and not its magnitude, this is
recorded explicitly and the magnitude is treated as an assumption to be
varied in sensitivity analysis. A sample size of approximately 1,000
records is used as the default regime, chosen to approximate the order
of magnitude of NASA\'s real astronaut cohort, with larger generated
samples available where estimator stability requires them.

simcausal is the sole default generator because access to it is
guaranteed. Alternative generators and a real-data-seeded semi-synthetic
approach are considered only as robustness extensions (Step 9).

## Step 4: Baseline attribution with standard SHAP

Standard, causally uninformed SHAP attributions are computed as the
reference against which causally informed methods are compared. Expected
attribution patterns are first derived directly from the known DAG, in
the spirit of deriving testable implications from a causal structure, so
that each method\'s output can be evaluated against a structurally
motivated expectation rather than against intuition alone. In
particular, because the bone-remodeling mediators are included in the
model alongside the exposure, a causally faithful method should
attribute the mediated portion of the exposure\'s effect to the
mediators rather than double-counting it on the exposure; a method that
instead assigns the exposure a large direct attribution despite the
mediators being present is misattributing mediated effect as direct
effect. This is the specific failure mode the baseline is designed to
expose.

Attributions are computed across model classes to determine whether any
failure of standard SHAP is consistent or model-class-specific. The
tree-ensemble models (random forest and gradient-boosted trees) are
explained with the interventional tree estimator, using a held-out
background sample so that removed features are marginalized against real
reference values in a manner consistent with an interventional reading.
Linear and logistic models are explained with a closed-form linear
estimator configured with the empirical feature covariance rather than a
feature-independence assumption, because several mediators are
correlated through shared upstream causes. A stacked-ensemble learner is
treated as a black box and explained with the model-agnostic kernel and
permutation estimators.

For the kernel estimator at the default sample size, the number of
sampled coalitions follows the standard heuristic, and a
k-means-summarized background is used in place of the full sample to
keep computation tractable; attribution stability is assessed by varying
the background summary size and comparing the resulting importance
rankings. The link function is chosen to match the outcome scale
(identity for the continuous supersaturation outcome, logit for the
binary incidence outcome). For the permutation estimator, the evaluation
budget is set to a multiple of its enforced minimum given the small
feature count.

The full breadth of model-explainer combinations is carried only at this
baseline step. Subsequent steps narrow to two representative
combinations: a gradient-boosted tree explained interventionally, and a
stacked ensemble explained model-agnostically.

## Step 5: Complexity-aware reweighting

Attribution outputs from Step 4 that are amenable to complexity-aware
reweighting are re-evaluated using the collaborating complexity-scoring
tool, which assigns each feature a score reflecting its causal
entanglement or depth within the graph. The interface between this tool
and the attribution outputs, and the subset of Step 4 strategies to
which it applies, are to be specified by the tool\'s developers; the
tool is provisional at the time of writing and is not yet integrated
into the pipeline.

## Step 6: Causally informed attribution and human-in-the-loop iteration

Four causally informed attribution methods spanning the range from
full-graph-dependent to structure-discovering are compared: causal
Shapley values, which require a complete directed graph and split
attribution into direct and indirect components via the do-calculus;
Shapley Flow, which also requires a complete graph but attributes to
edges rather than nodes; asymmetric Shapley values, which require only a
causal ordering rather than full edge structure; and a discovery-based
causal SHAP method that infers a partially directed graph from data
using a constraint-based algorithm and quantifies causal strength before
computing attributions. Each method is paired with the predictive engine
used in its originating publication where identifiable (gradient-boosted
trees for causal Shapley values and Shapley Flow; a random forest for
the discovery-based method), and with the stacked-ensemble fallback
where the originating publication does not specify a single engine.
Because pairing methods with heterogeneous engines confounds method with
engine, at least one common-engine comparison is additionally run so
that observed differences can be attributed to the method rather than to
the learner.

The human-in-the-loop procedure exploits the fact that each method
admits a different kind of expert input. For the graph-dependent
methods, the expert revises edge presence, direction, and
functional-form assumptions; for the edge-attribution method, the expert
additionally critiques individual edge attributions; for the
ordering-based method, the expert revises the causal ordering; and for
the discovery-based method, the expert corrects the automatically
inferred structure by orienting undirected edges, adjusting estimated
edge strengths against known literature values, and setting the
discovery algorithm\'s significance threshold. The discovery-based
method is qualitatively distinct in that the expert corrects an
automated inference rather than supplying structure from scratch, and
this distinction is treated as a central thread of the analysis.

Each method is evaluated over three iteration rounds. The first round
uses each method\'s initial input (the working DAG, an initial ordering,
or the unrevised discovered graph, as applicable). The domain expert
then reviews the resulting attributions against the DAG-derived
expectations from Step 4 and revises the relevant input, and the method
is rerun; this is repeated for a third round. At each round, attribution
rankings are scored against the known ground-truth total effects, and
the round-over-round stability of the rankings is recorded, yielding
both a convergence trajectory and a comparison of which methods improve
under expert revision versus which plateau.

## Step 7: Complexity-aware reweighting of causally informed attributions

The complexity-aware reweighting of Step 5 is applied to the causally
informed attributions of Step 6, under the same provisional status and
pending the same interface specification.

## Step 8: Structural recovery comparison

Because the discovery-based method of Step 6 already infers a graph as
its first stage, that inferred graph is reused here rather than
recomputed, and the step evaluates structural recovery accuracy in its
own right, independent of downstream attribution. One representative
algorithm is drawn from each major family of causal-discovery methods: a
constraint-based algorithm (reused from Step 6), a score-based
algorithm, a continuous-optimization algorithm, and a functional
non-Gaussian algorithm. Each is scored against the known generating
structure using structural Hamming distance and edge precision and
recall. This step functions as a diagnostic layer for Step 6: poor
structural recovery here directly explains attribution errors observed
there for the discovery-based method.

## Step 9: Robustness to the data-generating process (extension)

To distinguish findings that reflect the causal methods from findings
that reflect a particular simulator\'s idiosyncrasies, the narrowed
pipeline of Steps 4 through 8 is re-run on data produced by additional
generators. Should domain-restricted real data become available, a
real-data-seeded semi-synthetic validation approach is additionally
considered. This step is an extension and may be reported in compressed
form.

## Step 10: Robustness to spaceflight-epidemiological constraints

The narrowed pipeline is re-run under sampling regimes that emulate the
characteristic constraints of spaceflight cohorts, applied as selection
and degradation mechanisms rather than as changes to the causal
structure. These include reduced sample size, widened mission-era
ranges, selection on cardiovascular fitness, selection on a narrow age
window, and, where estimable, isolation- and environment-specific
effects. Attribution fidelity is tracked as a function of the severity
of each constraint, isolating the robustness of each method to selection
bias as distinct from its robustness to confounding.

## Step 11: Generalization to out-of-distribution populations

Reported in its own dedicated section rather than as a robustness pass,
this analysis examines how attribution and prediction behave when the
target population differs structurally from the training population; for
example, predicting for commercial-spaceflight participants when the
data derive from career astronauts, or for exploration-duration missions
when the data derive from shorter missions. Because this raises a
distinct generalization question rather than extending the
within-distribution comparison, it is a candidate for separate
treatment.

## Step 12: Longitudinal extension (future work)

The dual representation of vitamin D as both a pre-flight confounder and
an exposure-driven in-flight mediator is an instance of
treatment-confounder feedback, for which the established remedy is the
family of g-methods. Extending the static, single-time-point comparison
of this paper to a longitudinal setting, and testing whether
longitudinally aware attribution methods recover coherent importance for
such time-varying confounder-mediators, is identified as the natural
sequel and is not undertaken here.

## Step 13: Counterfactual recourse extension (out of scope)

A cost-aware counterfactual-explanation component, in which the
complexity score defines the cost of intervening on each feature, was
part of the original project framing. Because generating actionable
counterfactual recourse is a task distinct from feature attribution
rather than an extension of it, it is scoped out of the present paper
and left to be defined by its owners.

## Evaluation metrics

Attribution methods are scored against the known ground-truth total
effects using rank-agreement measures (Kendall\'s tau, Spearman\'s rho),
top-k recovery, and a normalized discounted cumulative gain at k,
supplemented by measures of proximity bias that quantify a method\'s
tendency to over-credit features near the outcome. Structural recovery
(Step 8) is scored using structural Hamming distance and edge precision
and recall. Where a locked comparison is reported, uncertainty is
quantified by paired bootstrap resampling over evaluation records.

## Reproducibility and provenance

All datasets are synthetic and contain no astronaut, patient, or
participant records. Graph topology is source-aligned to the published
NASA DAG; all coefficients are simulation design parameters rather than
empirical estimates and are flagged as requiring domain-expert
calibration before any substantive interpretation. Data generation,
attribution, structural recovery, and evaluation are implemented as a
scripted, version-controlled pipeline with frozen output artifacts, and
the ground-truth total effects are computed before and independently of
the attribution comparison to prevent leakage.

Claude working notebook on the methods

# NASA HSRB Renal Stone Risk DAG --- Human SHAP Methods: Working Notes

**Status:** Living document, in progress. All effect sizes marked
PLACEHOLDER are literature-informed starting points, not final, pending
Robert Reynolds\'s review.

**NOTE: Andy to supply proper DAG as supplied by Robert for the paper.**

**Base DAG:** NASA\'s public SA-07566 \"Risk of Renal Stone Formation\"
DAG, supplied to Andy Wilson and Lexi Pasi by Robert Reynolds (DAGitty
source, 2026-07-13 handoff; 53 nodes/83 edges per Robert\'s version, 51
nodes/75 edges in the prior source-aligned reference, Cohen\'s kappa
0.978 after semantic mapping). Public sources: [[DAG narrative
(PDF)]{.underline}](https://www.nasa.gov/wp-content/uploads/2025/09/renal-stone-risk-dag-narrative.pdf);
[[DAG code, DAGitty
(TXT)]{.underline}](https://www.nasa.gov/wp-content/uploads/2025/09/renal-stone-dag-code-sa-07566.txt);
[[NASA risk
page]{.underline}](https://www.nasa.gov/directorates/esdmd/hhp/risk-of-renal-stone-formation/);
[[2017 HRP evidence
report]{.underline}](https://humanresearchroadmap.nasa.gov/evidence/reports/Renal.pdf).
Andy\'s implementation:
[[andystats/causal-shap-target-dags]{.underline}](https://github.com/andystats/causal-shap-target-dags).

**Superseded direction:** bone fracture (via Reynolds, Scott, Turner,
Iwaniec, Bouxsein, Sanders & Antonsen, 2022, *Biomedicines* 10(9), 2187)
was the original primary track, dropped in favor of renal stone. It\'s
not wasted work: the Bone Formation/Bone Resorption mediator nodes carry
over directly, Bone Remodeling sits immediately upstream of the renal
pathway in NASA\'s own reference graph. The bone-specific outcome
measures (FRAX, F.Load, HR-pQCT) are no longer used.

## 1. Exposure

**Cumulative mission duration (days).** Chosen over binary flown/unflown
or era/vehicle-class framing to preserve the dose-response relationship
central to the unloading mechanism.

## 2. DAG structure and node definitions

**Confirmed mechanism (NASA narrative, direct basis):** exposure to
microgravity induces bone loss which increases circulating calcium,
impacting renal stone risk. Excess blood calcium from Bone Remodeling
feeds Urine Chemistry; Urine Chemistry determines whether Mineralized
Renal Material precipitates; this determines Nephrolithiasis (kidney
stone) risk, the outcome. Andy\'s repo confirms Nephrolithiasis as the
target, with 28 pre-outcome ancestors in the full 51-node source graph
--- scoped down to 12 nodes below for tractability, matching the same
rigor previously applied to bone.

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **\#**      **Node**           **Type**                    **Measure(s)**       **Composite/split   **Source**
                                                                                  decision**          
  ----------- ------------------ --------------------------- -------------------- ------------------- ------------------------------------------------------------------------------------------------------
  1           Duration           Exposure                    Cumulative mission   Single measure      NASA narrative; [[Gabel et al. 2021]{.underline}](https://pubmed.ncbi.nlm.nih.gov/33597120/)
                                                             days                                     

  2           Age at launch      Confounder, direction TBD   Age in years         Single measure,     ---
                                                                                  **not NASA-named**  
                                                                                  --- narrative uses  
                                                                                  \"Individual        
                                                                                  Factors\... genetic 
                                                                                  predispositions\"   
                                                                                  without decomposing 
                                                                                  further; included   
                                                                                  by analogy, flag to 
                                                                                  Robert              

  3           Sex                Confounder                  Male/female          Single measure ---  [[Numerical characterization of astronaut CaOx renal stone risk, npj Microgravity
                                                                                  **stronger evidence 2022]{.underline}](https://www.nature.com/articles/s41526-021-00187-z)
                                                                                  here than for       
                                                                                  bone**: male        
                                                                                  astronauts and male 
                                                                                  analog cohorts show 
                                                                                  greater             
                                                                                  susceptibility to   
                                                                                  elevated urinary    
                                                                                  CaOx                
                                                                                  supersaturation     
                                                                                  than females        

  4           Era /              Effect modifier, **weaker   Binary: pre/post     Single measure      Note below: high-load resistive exercise \"appears to have only a marginal effect\" on renal stone
              countermeasure     than in bone**              ARED, or KCit                            risk specifically, unlike its strong effect on bone
              protocol                                       availability                             

  5a          Vitamin D          Exogenous confounder        Serum 25(OH)D₃,      Split from          [[Smith et al. 2012,
              (pre-flight)                                   baseline             \"Nutrients\";      JBMR]{.underline}](https://academic.oup.com/jbmr/article-abstract/27/9/1896/7598261)
                                                                                  appears 2x in DAG   

  5b          Vitamin D          Mediator, child of          Serum 25(OH)D₃,      Same split          [[J. Nutrition, Mir
              (in-flight)        Duration, feeds Urine       in-flight/post                           cohort]{.underline}](https://jn.nutrition.org/article/S0022-3166(22)10077-5/fulltext) --- 32--36%
                                 Chemistry via calcium                                                decline during long missions
                                 absorption                                                           

  6           Nutrients (Risk)   Confounder/countermeasure   Dietary oxalate,     Single composite    NASA narrative: \"Nutrients affect Urine Chemistry through the intake of\... oxalate, calcium,
                                                             calcium, magnesium   measure             magnesium\"
                                                             intake (broader than                     
                                                             bone\'s calcium-only                     
                                                             node, since                              
                                                             oxalate/magnesium                        
                                                             matter specifically                      
                                                             for stone chemistry)                     

  7           Bone formation     Mediator                    P1NP, BSAP,          PCA composite       [[Gabel et al., Sci Adv 2024]{.underline}](https://www.science.org/doi/10.1126/sciadv.adq3632)
                                                             osteocalcin          (carried over from  
                                                                                  bone track)         

  8           Bone resorption    Mediator, **primary driver  NTX, CTX             PCA composite       \"Bone resorption brought on by spaceflight elevates urinary calcium and the risk of renal stone
                                 of this pathway**                                                    formation\" --- [[Bone metabolism and renal stone risk during ISS missions,
                                                                                                      ScienceDirect]{.underline}](https://www.sciencedirect.com/science/article/abs/pii/S8756328215003658)

  9           Hydration status   Mediator/countermeasure     24-hr urine volume,  Single measure      NASA narrative + [[OCHMO-MTB-003]{.underline}](https://www.nasa.gov/ochmo-mtb-003-urinary-health-2/):
                                                             fluid intake                             \"increased fluid intake\... potentially effective countermeasure\"

  10          Urine Chemistry    Mediator                    PCA composite:       PCA composite       NASA narrative and [[OCHMO-MTB-003]{.underline}](https://www.nasa.gov/ochmo-mtb-003-urinary-health-2/)
                                                             calcium, citrate,                        monitoring panel (calcium oxalate, uric acid, citrate, pH, sodium, sulfate, phosphorus, magnesium,
                                                             oxalate, pH                              potassium)

  11          Mineralized Renal  Mediator                    Relative             Single measure      25% of astronauts show elevated CaOx supersaturation pre-flight vs. 46% post-flight --- [[Goodenow et
              Material (CaOx                                 supersaturation                          al., npj Microgravity 2022]{.underline}](https://www.nature.com/articles/s41526-021-00187-z)
              supersaturation)                               (RSS) score                              

  12          Nephrolithiasis    Outcome                     Kidney stone         Single measure      NASA narrative and Andy\'s repo confirm as target; kidney stone is the **2nd most likely reason for
                                                             presence/incidence                       ISS emergency medical evacuation** per NASA\'s Integrated Medical Model ---
                                                                                                      [[OCHMO-MTB-003]{.underline}](https://www.nasa.gov/ochmo-mtb-003-urinary-health-2/)
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Note on Astronaut Selection:** the NASA narrative names it directly
(\"individuals with a high risk of renal stones would not be selected
into the Astronaut Corps\"). Per our earlier structural distinction
(§4), this is a selection mechanism, not a causal DAG node, so it
belongs in step 10\'s sampling constraints, not this table.

## 3. PLACEHOLDER edge effect sizes --- pending Robert\'s review

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Edge**                      **Placeholder           **Source**
                                magnitude**             
  ----------------------------- ----------------------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Duration → Resorption         \~2× baseline           [[Gabel et al.
                                resorption markers,     preprint]{.underline}](https://www.researchgate.net/publication/387274968_Tracking_of_spaceflight-induced_bone_remodeling_reveals_a_limited_time_frame_for_recovery_of_resorption_sites_in_humans)
                                sustained through 6-mo  
                                missions (carried over  
                                from bone track, same   
                                mechanism)              

  Duration → Formation          Near-zero to mildly     [[Smith, NASA NTRS review]{.underline}](https://ntrs.nasa.gov/api/citations/20100030546/downloads/20100030546.pdf)
                                decreased               

  Resorption → Urine Chemistry  Directional only, no    [[Bone metabolism and renal stone risk, ISS missions]{.underline}](https://www.sciencedirect.com/science/article/abs/pii/S8756328215003658)
  (calcium)                     magnitude found yet:    
                                \"bone resorption\...   
                                elevates urinary        
                                calcium and the risk of 
                                renal stone formation\" 

  Duration → Mineralized Renal  Prevalence of elevated  [[Goodenow et al., npj Microgravity 2022]{.underline}](https://www.nature.com/articles/s41526-021-00187-z)
  Material (CaOx                CaOx supersaturation:   
  supersaturation)              25% pre-flight → 46%    
                                post-flight             

  Sex → Mineralized Renal       Directional: males more [[Goodenow et al.]{.underline}](https://www.nature.com/articles/s41526-021-00187-z)
  Material                      susceptible to elevated 
                                CaOx supersaturation    
                                than females; astronaut 
                                cohorts are heavily     
                                male-skewed (29M/1F in  
                                the KCit trial below),  
                                limiting power          

  Era (KCit availability) ×     KCit-treated crew       [[NASA NTRS, KCit trial]{.underline}](https://ntrs.nasa.gov/citations/20080046171)
  Resorption → Urine Chemistry  showed decreased        
                                urinary calcium         
                                excretion and           
                                maintained preflight    
                                CaOx supersaturation    
                                risk level (vs.         
                                untreated controls\'    
                                increase); N=30         
                                (29M/1F)                

  Era (ARED) × Duration →       **Contrast with bone:** [[Goodenow et al.]{.underline}](https://www.nature.com/articles/s41526-021-00187-z)
  Mineralized Renal Material    high-load resistive     
                                exercise \"appears to   
                                have only a marginal    
                                effect as a renal stone 
                                occurrence              
                                countermeasure,\"       
                                unlike its strong       
                                effect on bone mass     

  Hydration → Urine Chemistry / Directional only:       NASA narrative; [[OCHMO-MTB-003]{.underline}](https://www.nasa.gov/ochmo-mtb-003-urinary-health-2/)
  Mineralized Renal Material    increased fluid         
                                intake/urine volume is  
                                a \"potentially         
                                effective               
                                countermeasure,\"       
                                operationally           
                                constrained by mission  
                                resource limits         

  Vitamin D → Urine Chemistry   General                 Mendelian randomization study, modifiable risk factors for kidney stones (PMC10116718)
  (calcium)                     (non-spaceflight)       
                                literature: OR 1.55 per 
                                SD increase in serum    
                                25(OH)D for kidney      
                                stone risk, via         
                                increased intestinal    
                                calcium absorption      

  Nutrients                     Directional only, NASA  NASA narrative
  (oxalate/calcium/magnesium) → narrative names the     
  Urine Chemistry               pathway without         
                                magnitude               
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Honest gap:** several edges here are directional-only (no magnitude
found), more so than the bone track. This DAG\'s downstream chain (Urine
Chemistry → Mineralized Renal Material → Nephrolithiasis) has real
quantitative anchors at the Mineralized Renal Material step (25%→46%)
but not yet at Urine Chemistry\'s individual solute-level edges or the
final Nephrolithiasis incidence step. Worth prioritizing with Robert.

## 4. Open decisions log

-   **Age arrow:** unresolved for renal stone (unlike bone, where the
    2007 BMD-loss-rate study gave a clear answer). NASA\'s narrative
    doesn\'t decompose \"Individual Factors\" by age specifically ---
    needs Robert\'s input on direction and whether it modifies the
    Duration pathway or acts on baseline risk directly.

-   **Sex:** kept as a direct effect (not Sex × Era interaction, unlike
    the bone track) given the more specific supporting evidence (male
    susceptibility to CaOx supersaturation). Revisit if Robert\'s DAG
    handles it differently.

-   **Astronaut Selection:** confirmed as a step-10 sampling constraint,
    not a DAG node (NASA\'s own narrative frames it as a selection
    mechanism, consistent with our earlier structural distinction).

-   **Outcome measure:** Nephrolithiasis as binary incidence, vs.
    Mineralized Renal Material\'s continuous CaOx supersaturation score
    as a proxy outcome --- Andy\'s repo uses Nephrolithiasis as the
    target; open whether we follow that or use the earlier, more
    data-rich supersaturation measure given it has better-populated
    evidence (25%/46% figures) than incidence itself.

## 4b. What Andy has already completed (per andystats/causal-shap-target-dags, repo review)

This is existing work in the repo, distinct from what remains to be
built. Sourced from the repo\'s README, docs/METHODS.md,
docs/DATA_PROVENANCE.md, and the ROBERT_REYNOLDS_DAGS_2026-07-13.md
handoff. Maps onto our step numbers below.

**Done / substantially built:**

-   **DAG ingestion and validation (our step 2):** Robert\'s two DAGitty
    files (Renal Stone, 53 nodes/83 edges; SANS, 50 nodes/89 edges)
    ingested via analysis/10_ingest_robert_dags.R, with lossless
    round-trip checks. Renal graph reconciled against the prior SA-07566
    reference: Cohen\'s kappa 0.978, precision 1.000, recall 0.958,
    structural Hamming distance 3 after semantic mapping. Three
    unmatched edges flagged for Robert\'s adjudication.

-   **simcausal data generation (our step 3):** working simulator
    (renal_stone_source_aligned_simcausal.R), locked parent structure at
    Cohen\'s kappa 1.000 vs. source graph. Two regimes exist:
    source_aligned_clean_v3 (10,000 records) and
    source_aligned_nasa_like_v4 (adds astronaut selection + informative
    measurement, i.e. an early version of our step-10 selection
    constraints).

-   **Frozen interventional ground truth (our baseline for step 4):**
    06_compute_interventional_truth.R computes standardized absolute
    total risk difference for all 28 ancestors via 50,000
    common-random-number simulations. This is the equivalent of our
    DAG-derived baseline.

-   **Out-of-box + asymmetric SHAP (our steps 4 + partial 6):** exact
    TreeSHAP, interventional SHAP (128 background, 128 permutations),
    and DAG-constrained asymmetric SHAP (ASV), all on a shared XGBoost
    model (held-out AUC 0.684 vs. structural-truth ceiling 0.701).

-   **Structural Causal SHAP prototype (our step 6, Ng-et-al.-style):**
    structural_value.py implements an intervention-propagating value
    function (do(X_S), propagate through descendants, score fixed
    model). Currently at 32 evaluation records / 32 background / 32
    permutations --- explicitly a milestone, not a locked result.

-   **Complexity score / LumaWarp precursor (our step 5):** PSCI v0
    (complexity.py), provisional, plugged into a registry seam for
    Lexi\'s final score.

-   **Evaluation harness (our step 6 evaluation):** Kendall\'s τ,
    Spearman\'s ρ, top-5 recovery, NDCG@5, mean directed distance to
    outcome, proximal mass, PBI, POA. Locked comparison uses 2,000
    paired bootstrap draws.

**Headline results already obtained (renal DAG):** ordinary TreeSHAP τ =
0.522 vs. truth; DAG-asymmetric SHAP τ = 0.528 (statistically tied --- a
deliberate null); structural prototype τ = 0.794 with 100% top-5
recovery. On teaching DAGs, ordinary SHAP is *negatively* correlated
with causal truth (τ ≈ −0.33), which the structural method flips
positive.

**Not yet done (gaps that are our contribution to build):**

-   Human-in-the-loop iteration rounds (our step 6): repo has
    single-pass results, not the 3-round Robert-revision design.

-   Full 4-method comparison (our step 6): repo has TreeSHAP + ASV +
    structural prototype, but **not** Heskes Causal Shapley Values or
    Shapley Flow.

-   DAG-discovery comparison (our step 8): repo uses the known graph;
    PC/GES/LiNGAM/NOTEARS recovery comparison not present (NOTEARS
    exists only as an optional build path).

-   Multi-simulator robustness (our step 9): only simcausal; no
    simDAG/DagSim/dagsampler/Credence.

-   Space-epi constraint stress tests (our step 10): only the single
    nasa_like_v4 selection regime, not the full
    small-N/era/selection-bias sweep.

-   Out-of-distribution generalization (our step 11): absent.

-   Effect-size calibration: repo is explicit that all coefficients are
    simulation parameters, **not** NASA estimates, and require domain
    review --- exactly our §3 open item with Robert.

-   SANS DAG: ingested and validated but no data/coefficients/results
    --- a possible second case study, currently out of scope.

**Bottom line:** Andy has built a working end-to-end single-pass
pipeline (ingest → simulate → frozen truth → attribution → evaluation)
on the renal DAG, with a promising structural-prototype result. The
paper\'s distinct contributions are the human-in-the-loop iteration
design, the full multi-method comparison, and the
robustness/generalization sweeps --- none of which exist yet.

**Step 12 --- Longitudinal causal SHAP.** The Vitamin D node\'s dual
role (pre-flight confounder + in-flight mediator, caused by Duration
itself) is a textbook case of treatment-confounder feedback. Standard
adjustment risks bias; the established fix is g-methods (g-formula,
marginal structural models via IPW). Canonical reference: Robins, Hernán
& Brumback, \"Marginal Structural Models and Causal Inference in
Epidemiology,\" *Epidemiology* 11(5), 2000.

On the SHAP side specifically, longitudinal-aware variants exist and are
worth testing against the static single-timepoint DAG used in this
paper:

-   **WindowSHAP** (Nayebi et al.) --- model-agnostic, validated on
    longitudinal clinical/EHR time series, closest match to this data
    type

-   **SurvSHAP(t)** --- time-dependent explanations for survival models,
    matches a fracture-risk-over-time outcome shape directly

-   **TimeSHAP** (Bento et al.) --- built for recurrent/sequential
    models, event/feature/cell-level attribution

Natural sequel paper: does a longitudinal SHAP approach recover causally
coherent importance for time-varying confounder-mediators like Vitamin D
better than the static DAG comparison in this paper\'s main analysis?

## 6. Methods steps overview (cross-reference to full braindump)

1.  Exposure/outcome selection --- **done**, see §1

2.  DAG node review + human-limitation additions --- **done**, see §2.
    Renal-stone DAG is now the sole primary track (bone fracture dropped
    as a separate direction; its Formation/Resorption mediator nodes
    carry over since they sit directly upstream in NASA\'s renal
    reference graph)

3.  Simulated data generation via simcausal --- **pending**, effect
    sizes need Robert\'s sign-off (§3). Andy\'s July 20 CSV
    (renal_stone_source_aligned_clean_v3.csv) is his simcausal output
    from this same NASA SA-07566 DAG, potentially usable as a starting
    point once effect sizes are reconciled with Robert.

4.  Out-of-box SHAP --- **in progress**, full spec in §7

5.  LumaWarp pass on applicable step-4 strategies --- **partially
    resolved, updated**: confirmed as Lucidity Sciences\' \"Luma Warp\"
    tool (Lexi Pasi). Per Andy\'s current GitHub repo
    (andystats/causal-shap-target-dags), it\'s now formalized as a
    \"complexity score (PSCI v0),\" explicitly provisional, feeding a
    \"registry seam for the authors\' final score.\" Still not
    integrated into the pipeline; interface details for this paper still
    pending.

6.  Causal SHAP (4-method comparison: Heskes, Shapley Flow, ASV, Ng et
    al.) --- **spec fully defined**, see §9. **Note:** Robert\'s
    original ask (relayed by Andy, June 22) also included a
    \"cost-sensitive DiCE\" (counterfactual explanations) angle, not
    incorporated anywhere in this plan yet --- worth raising before
    finalizing step 6\'s scope.

7.  LumaWarp reassessment of step 6 --- same LumaWarp status as step 5.

8.  DAG recovery comparison: PC, GES, LiNGAM, NOTEARS --- **spec fully
    defined**, see §11. PC reused from step 6\'s Causal SHAP run.

9.  Reassess with simDAG, DagSim, dagsampler, and --- **iff NASA data
    access is granted** --- Credence (Parikh, Hong & Boyd, \"Validating
    Causal Inference Methods,\" ICML 2022; a real-data-seeded
    semi-synthetic validation framework, confirmed via Andy\'s repo,
    built \"in the spirit of Credence\"). simcausal remains the
    unconditional default throughout this paper since we have guaranteed
    access to it; Credence is preserved as a stretch goal only, not a
    dependency. --- pending

10. Reassess under space-epi constraints: small N, era range, cardio/age
    selection bias --- pending

11. Generalization to out-of-distribution populations (commercial
    spaceflight, Mars-duration) --- **flagged as its own dedicated
    section**, not folded into the reassessment sequence. Distinct
    enough in contribution (novel generalization question, not just
    another robustness pass) to warrant standalone treatment rather than
    being step-numbered alongside the reassessment steps.

12. Longitudinal causal SHAP --- future work, see §5

13. Cost-aware manifold warping for cost-sensitive DiCE --- **TODO, out
    of scope for this paper, for Andy/Lexi to define.** See §15 for what
    DiCE is and why it\'s flagged separately rather than specced here.

**Structural note:** bone fracture is no longer a separate track (see
title-page note). The Bone Formation/Bone Resorption mediator nodes
carry over into the renal-stone DAG (§2) since Robert\'s own DAG source
splits \"Bone Remodeling\" into exactly those two nodes, and NASA\'s
public renal-stone narrative states the mechanism directly: unloading →
Bone Remodeling → increased blood/urine calcium → Nephrolithiasis.

## 7. Step 4 spec: out-of-box SHAP

**Baseline evaluation approach:** derive expected feature-attribution
patterns directly from the specified DAG (§2), analogous to Reynolds et
al.\'s marginal-correlation/conditional-independence testable
implications, applied to attribution instead of correlation. Key open
design choice: whether mediator nodes (Formation, Resorption, etc.) are
included alongside Duration in the model. If included, a causally
faithful method should show Duration\'s direct attribution shrink toward
zero (fully mediated); if excluded, Duration should absorb the
mediators\' share. Decide and state explicitly per model spec.

**Explainer × model pairings:**

  -----------------------------------------------------------------------------------------
  **Explainer**           **Model**               **Treatment**
  ----------------------- ----------------------- -----------------------------------------
  TreeExplainer           Random Forest           feature_perturbation=\"interventional\"

  TreeExplainer           XGBoost                 feature_perturbation=\"interventional\"

  LinearExplainer         Linear/logistic         masker = feature covariance matrix (not
                          regression (per outcome independence)
                          type)                   

  KernelExplainer         SuperLearner            treated as black box

  PermutationExplainer    SuperLearner            treated as black box
  -----------------------------------------------------------------------------------------

**Scope narrowing:** full breadth (all 5 above) carried through step 4
only, as a standalone baseline contribution (does out-of-box SHAP fail
consistently across model classes, or is it model-class-specific?).
Steps 5--10 narrow to two representative combinations:
TreeExplainer+XGBoost and KernelExplainer+SuperLearner.

**KernelExplainer specs (assuming N≈1000):**

-   nsamples: auto default = 2×M + 2048 (≈2064--2068 for \~8--10
    features)

-   Background: k-means summary recommended over full sample. Full
    N=1000 background × auto nsamples × 1000 explained instances ≈ 2B
    model evaluations (intractable); k=50 background reduces to ≈103M
    (tractable, in line with published KernelExplainer deployment
    examples)

-   Link function: identity for continuous outcome; logit if outcome is
    binary/probability-based

-   Sensitivity test: rerun across background sizes (k=10, 50, 100, 250,
    full N) and compare attribution rank correlation / mean absolute
    difference to identify convergence point

**PermutationExplainer specs:**

-   max_evals: hard minimum 2×M + 1 (≈17--21 for \~8--10 features); use
    several multiples of this floor for stability, cheap given low
    feature count

-   Each cycle costs 2×(M+1) model evaluations per background row

**Outcome translation note:** unlike bone (where the rodent source
measured strength via direct mechanical testing), the renal-stone DAG\'s
outcome, Nephrolithiasis, is directly observable in humans without a
translational proxy: kidney stone incidence is diagnosed clinically
(ultrasound, CT) and is what NASA\'s own DAG targets natively. The
nearer-term mediator, Mineralized Renal Material (CaOx supersaturation),
has the richest quantitative evidence (25%→46% pre/post-flight
prevalence) and may be worth using as a secondary, better-populated
outcome alongside Nephrolithiasis incidence itself (see §4 open
decision).

**Mediator inclusion decision:** Mediators (Formation, Resorption, Bone
mass, Trabecular architecture) ARE included alongside Duration in the
fitted model. Methods-text framing: per Heskes et al. (2020), when
mediators are included alongside an upstream cause, a causally faithful
attribution method should split that cause\'s total effect into a direct
component and an indirect (mediated) component, with the indirect
portion attributed to the mediators rather than double-counted on the
upstream feature. A method assigning Duration a large \"direct\"
attribution despite Formation/Resorption being in the model is
misattributing mediated effect as direct effect. This is the specific
failure mode the DAG-derived baseline (step 4) is designed to detect.

## 8. Step 5 spec: LumaWarp pass

**STATUS: TODO --- details to be filled out by Lexi/Andy.**

## 9. Step 6 spec: Causal SHAP comparison

**Design:** full-breadth comparison, same structure as step 4,
cost-aware (see below).

  -----------------------------------------------------------------------------------------------------------------------------------
  **Method**        **Citation**         **Package**                                                                **DAG
                                                                                                                    requirement**
  ----------------- -------------------- -------------------------------------------------------------------------- -----------------
  Causal Shapley    Heskes et al.,       shapr (R/Python) --- native support via confounding argument in explain()  Full DAG required
  Values            NeurIPS 2020         (superseded earlier note about an unmerged patch)                          

  Shapley Flow      Wang, Wiens &        [[shapflow]{.underline}](https://github.com/nathanwang000/Shapley-Flow),   Full DAG required
                    Lundberg, AISTATS    also on PyPI                                                               
                    2021                                                                                            

  Asymmetric        Frye, Rowat & Feige, shapr, via asymmetric + causal_ordering arguments                          Partial: causal
  Shapley Values    NeurIPS 2020                                                                                    ordering only
  (ASV)                                                                                                             

  Causal SHAP       Ng, Wang, Liu & Fan, No public repo found; implementable from paper\'s Algorithm 1 using pcalg  None --- PC
                    IJCNN 2025           (R) / causal-learn (Python) for PC + pcalg::ida() for IDA                  discovers CPDAG
                    (arXiv:2509.00846)                                                                              from data
  -----------------------------------------------------------------------------------------------------------------------------------

**Cost note (from Ng et al.\'s own benchmarks):** on their 31-feature
IBS dataset, Causal SHAP computation took 366s vs. 0.26s (PC) and 1.56s
(IDA) --- Monte Carlo sampling is the bottleneck, not causal discovery.
Our DAG has \~9-10 features vs. their 31, should scale down, but budget
accordingly across 4 methods × 3 human-in-the-loop iterations (below).

**Human-in-the-loop mapping:**

  -----------------------------------------------------------------------
  **Method**              **Requires to run**     **Revised between
                                                  iterations**
  ----------------------- ----------------------- -----------------------
  Causal Shapley Values   Full directed DAG       Edge
                                                  presence/direction,
                                                  functional form
                                                  assumptions --- maps
                                                  directly onto existing
                                                  Robert DAG-review
                                                  workflow

  Shapley Flow            Full directed DAG       Same as above, plus
                                                  individual edge-level
                                                  attribution critique
                                                  (unique to this method,
                                                  attributes to edges not
                                                  nodes)

  ASV                     Causal ordering         The ordering itself /
                          (partial order)         which variables are
                                                  known ancestors

  Causal SHAP (Ng et al.) Nothing (auto-discovers Manual orientation of
                          CPDAG)                  PC\'s undirected edges,
                                                  IDA edge-weight
                                                  corrections against
                                                  literature effect
                                                  sizes, PC significance
                                                  threshold
  -----------------------------------------------------------------------

Note the last row is categorically different: correcting/constraining an
automated discovery process rather than supplying structure from
scratch. Worth framing explicitly as the paper\'s throughline.

**Iteration evaluation design:** 3 rounds per method. Round 1 = initial
input (step-2 DAG for DAG-requiring methods, initial ordering for ASV,
raw unrevised PC/CPDAG for Ng et al.\'s method) → Robert reviews
attribution against step-4 DAG-derived baseline → revises input → rerun
(round 2) → repeat (round 3). Track RMSE against simulated ground truth
per round (metric borrowed directly from Ng et al.\'s own validation
approach) plus rank-stability of attributions round over round.

**Engine per method (step 6), matched to each foundational paper\'s own
experiments:**

  -----------------------------------------------------------------------
  **Method**              **Engine**              **Source**
  ----------------------- ----------------------- -----------------------
  Causal Shapley Values   XGBoost                 NeurIPS reviewer
  (Heskes et al.)                                 commentary confirms
                                                  XGBoost used on their
                                                  bike-sharing dataset
                                                  experiment

  Shapley Flow (Wang et   XGBoost                 Reference
  al.)                                            implementation
                                                  (flow.py) uses xgboost
                                                  in case studies

  ASV (Frye et al.)       **SuperLearner          ---
                          (fallback)** --- no     
                          single model type       
                          clearly identifiable    
                          from their              
                          paper/examples          

  Causal SHAP (Ng et al.) Random Forest           Explicitly stated in
                                                  paper: \"All
                                                  experiments used the
                                                  same Random Forest
                                                  model as the black
                                                  box\"
  -----------------------------------------------------------------------

## 10. Step 7 spec

**STATUS: TODO --- details to be filled out by Lexi/Andy.**

## 11. Step 8 spec: DAG recovery comparison

**Reframing note:** since Ng et al.\'s Causal SHAP (step 6) already runs
PC as its first stage, step 8\'s PC evaluation reuses that same CPDAG
rather than recomputing it. Step 8 is a diagnostic layer on top of step
6, not a redundant parallel task: it evaluates structural recovery
accuracy (structural Hamming distance, edge precision/recall) against
known simulated ground truth, independent of feature attribution. Poor
PC recovery in step 8 directly explains any corresponding attribution
errors seen from Ng et al.\'s method in step 6.

One algorithm per category, spanning constraint-based, score-based,
continuous-optimization, and non-Gaussian/functional assumption
families:

  -------------------------------------------------------------------------
  **Category**              **Algorithm**           **Foundational
                                                    reference**
  ------------------------- ----------------------- -----------------------
  Constraint-based          PC (reused from step 6) Spirtes, Glymour &
                                                    Scheines, *Causation,
                                                    Prediction, and
                                                    Search*, MIT Press,
                                                    2000

  Score-based               GES                     Chickering, \"Optimal
                                                    Structure
                                                    Identification with
                                                    Greedy Search,\" *JMLR*
                                                    3, 2002

  Continuous optimization   NOTEARS                 Zheng, Aragam,
                                                    Ravikumar & Xing,
                                                    NeurIPS 2018

  Functional/non-Gaussian   LiNGAM                  Shimizu, Hoyer,
                                                    Hyvärinen & Kerminen,
                                                    *JMLR* 7, 2006
  -------------------------------------------------------------------------

## 12. Cost breakdown

Note on methodology: rows marked **(grounded)** cite an actual published
benchmark. All other rows are qualitative/structural estimates based on
how each method is known to scale, since no direct runtime figures exist
for our specific setup, they are directional, not measured. TBD rows are
genuinely unknown pending other decisions.

  -----------------------------------------------------------------------------------------------------------
  **Step \#**    **Step label**        **Substep / model**      **Expected       **Justification**
                                                                cost**           
  -------------- --------------------- ------------------------ ---------------- ----------------------------
  3              Simulated data        simcausal, DAG-to-data   Low              Single-pass generation from
                 generation            (N=1000, \~10 nodes)                      specified structural
                                                                                 equations; scales linearly
                                                                                 with N and node count, no
                                                                                 iterative fitting

  4              Out-of-box SHAP       TreeExplainer + Random   Low--Medium      Exact tree-based
                                       Forest (interventional)                   computation; cost driven by
                                                                                 RF training, not the
                                                                                 explainer itself

  4              Out-of-box SHAP       TreeExplainer + XGBoost  Low--Medium      Same as above; sequential
                                       (interventional)                          boosting adds modest
                                                                                 training overhead vs. RF

  4              Out-of-box SHAP       LinearExplainer +        Very Low         Closed-form computation, no
                                       regression                                sampling required

  4              Out-of-box SHAP       KernelExplainer +        High             At N=1000, auto nsamples ≈
                                       SuperLearner             **(grounded)**   2M+2048 (\~2,064--2,068 for
                                                                                 \~8--10 features);
                                                                                 full-sample background ×
                                                                                 nsamples × 1,000 explained
                                                                                 rows ≈ 2B evaluations
                                                                                 (established earlier as
                                                                                 intractable); k=50 summary
                                                                                 reduces to ≈103M, still
                                                                                 large. SuperLearner\'s
                                                                                 cross-validated stacking
                                                                                 makes each individual
                                                                                 evaluation costlier than a
                                                                                 single model call

  4              Out-of-box SHAP       PermutationExplainer +   Medium--High     max_evals floor is 2M+1
                                       SuperLearner                              (\~17--21 for \~8--10
                                                                                 features), cheap per cycle
                                                                                 given low feature count, but
                                                                                 SuperLearner\'s per-call
                                                                                 cost and multiple cycles
                                                                                 needed for stability push
                                                                                 this up

  5              LumaWarp pass         TBD                      TBD              Pending LumaWarp interface
                                                                                 details (Lexi/Andy)

  6              Causal SHAP           Causal Shapley Values    Medium           No published runtime
                 comparison            (Heskes), XGBoost, via                    benchmark found; scales with
                                       shapr                                     background samples ×
                                                                                 features, shapr\'s
                                                                                 batching/parallelization
                                                                                 should mitigate

  6              Causal SHAP           Shapley Flow, XGBoost    Medium--High     No published benchmark
                 comparison                                                      found; edge-level
                                                                                 attribution evaluates flow
                                                                                 across the full graph rather
                                                                                 than per-node, expected to
                                                                                 exceed node-based causal
                                                                                 Shapley cost

  6              Causal SHAP           ASV, SuperLearner        Medium           Restricts permutations to
                 comparison            (fallback), via shapr                     causal-ordering-consistent
                                                                                 orderings only, a subset of
                                                                                 full permutation space,
                                                                                 reducing cost relative to
                                                                                 unconstrained
                                                                                 PermutationExplainer;
                                                                                 SuperLearner\'s per-call
                                                                                 cost still applies

  6              Causal SHAP           Causal SHAP (Ng et al.), High             Paper\'s own benchmark:
                 comparison            Random Forest            **(grounded)**   366.13s for causal SHAP
                                                                                 value computation alone
                                                                                 (Monte Carlo-dominated), 31
                                                                                 features/294 training rows,
                                                                                 AMD EPYC 7713. Our DAG has
                                                                                 fewer features (\~9--10),
                                                                                 likely reduces cost
                                                                                 somewhat, but this was the
                                                                                 single most expensive
                                                                                 component the source paper
                                                                                 measured

  6              Causal SHAP           × 3 human-in-the-loop    ×3 multiplier    Each method reruns fully per
                 comparison            iterations, all 4                         revision round; total step 6
                                       methods                                   cost ≈ 3 × (sum of the four
                                                                                 rows above)

  7              LumaWarp reassessment TBD                      TBD              Pending LumaWarp interface
                                                                                 details (Lexi/Andy); also
                                                                                 depends on step 5 cost once
                                                                                 known

  8              DAG recovery          PC (reused from step 6)  Negligible       Already computed in step 6;
                 comparison                                     **(grounded)**   Ng et al.\'s benchmark shows
                                                                                 PC at 0.26s for 31 features,
                                                                                 effectively free at reuse

  8              DAG recovery          GES                      Low--Medium      Score-based greedy search;
                 comparison                                                      standard literature
                                                                                 characterizes it as
                                                                                 comparable to or somewhat
                                                                                 slower than PC\'s
                                                                                 constraint-based pruning at
                                                                                 small feature counts

  8              DAG recovery          NOTEARS                  Medium           Continuous/gradient-based
                 comparison                                                      optimization requires
                                                                                 iterative steps rather than
                                                                                 a single combinatorial
                                                                                 search; typically slower
                                                                                 than PC/GES at small feature
                                                                                 counts, scales better at
                                                                                 high dimensions, not
                                                                                 relevant at our \~10-node
                                                                                 scale

  8              DAG recovery          LiNGAM                   Low--Medium      ICA-based, relatively
                 comparison                                                      efficient at small feature
                                                                                 counts, no iterative search
                                                                                 required

  9              Reassessment with     simDAG, DagSim,          Medium--High,    Each simulator reruns the
                 additional simulators dagsampler (+ credence   multiplicative   narrowed step 4--8 pipeline
                                       if granted)                               on newly generated data;
                                                                                 cost ≈ (number of
                                                                                 simulators) × (step 4--8
                                                                                 cumulative cost), not
                                                                                 additive

  10             Space-epi constraint  Small N / era range /    Medium--High,    Each constraint scenario
                 reassessment          cardio & age selection   multiplicative   reruns the narrowed
                                       bias / isolation effects                  2-combination pipeline (not
                                                                                 full step-4 breadth) under a
                                                                                 degraded sample; cost scales
                                                                                 with number of scenarios
                                                                                 tested

  11             Out-of-distribution   TBD, own section         TBD              Scope not yet fully
                 generalization                                                  specified; pending its own
                                                                                 methods design pass
  -----------------------------------------------------------------------------------------------------------

## 14. Archival note

Renal stone is now the primary and sole DAG track (see §2, §3, and the
title-page note). This section previously held the renal-stone build-out
as a parallel option alongside bone fracture; that content has been
merged into §2/§3 and this section is kept only as a pointer for
provenance. Andy\'s repo also reports evaluation metrics beyond what
we\'ve used so far, Kendall\'s τ, Spearman\'s ρ, top-5 recovery, NDCG@5,
mean directed distance to outcome, proximal mass, the Proximity Bias
Index (PBI), and the Proximal Over-attribution Area (POA), still worth
considering as additions to step 6\'s evaluation beyond RMSE and rank
correlation.

## 15. Step 13 spec: cost-aware manifold warping for cost-sensitive DiCE

**STATUS: TODO, out of scope for this paper. For Andy/Lexi to define and
own.**

**What DiCE is, for reference:** Diverse Counterfactual Explanations
(Mothilal, Sharma & Tan, \"Explaining Machine Learning Classifiers
through Diverse Counterfactual Explanations,\" *Proceedings of the 2020
Conference on Fairness, Accountability, and Transparency* (FAT\* \'20),
pp. 607--617). Unlike SHAP-family methods (attribution: how much did
each feature contribute), DiCE answers a recourse question: what is the
smallest set of feature changes that flips a prediction to a desired
outcome, generating a diverse set of such counterfactuals rather than
one. \"Cost-sensitive\" extensions weight the search by how feasible or
cheap each feature change actually is. Closely related: Karimi,
Schölkopf & Valera, \"Algorithmic Recourse: from Counterfactual
Explanations to Interventions,\" *FAccT* 2021, the causal extension
using a graph so a proposed change propagates consistently through
descendants (already cited in Andy\'s repo\'s method-background list).

**Why flagged separately rather than specced here:** this is a
materially different task from attribution (recourse/recommendation vs.
explanation), not a small extension of steps 4--10. Robert\'s original
framing (relayed by Andy, June 22 email) paired it with \"cost-aware
manifold warping,\" i.e., using the PSCI/LumaWarp complexity score to
define the cost function, features that are deeply causally entangled
would carry higher cost to intervene on. Both pieces need Andy and
Lexi\'s ownership before this can be scoped into a methods section.
