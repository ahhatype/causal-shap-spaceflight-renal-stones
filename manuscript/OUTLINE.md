# Manuscript outline (2026-08-30, with the 2026-09-04 addendum)

> Moved into the tracked manuscript folder on 2026-09-04 (ADR 009). Gated LumaWarp block detail removed; everything else as written.


**Status:** draft outline, 2026-08-30. Not circulated.
**Target journal:** npj Microgravity (decided 2026-08-30).
**Circulation gate:** Section 8 describes outputs derived from the Lucidity
Sciences LumaWarp runtime. Nothing in this document goes to coauthors or
reviewers until Lucidity answers the six questions in
`LUMAWARP_EXPLAIN_GUIDE.md` section 7. Sections 1 through 7, 9, and 10 contain
no proprietary material and can be drafted and reviewed now.

**Working title:** Predictive attribution does not locate intervention targets:
a known-truth study on a renal-stone topology.

---

## The argument in one paragraph

On a causal graph, a mediator can screen off its ancestors for prediction while
still carrying their intervention effects. A predictive attribution method will
therefore concentrate credit near the outcome, sometimes on a node whose total
effect is zero. We test this where the answer key exists: synthetic data from a
DAG whose structural equations we wrote. Three results follow. Ordinary SHAP
puts most of its credit on a zero-effect proxy. Constraining feature order to
the DAG does not repair this, and the paired bootstrap intervals for that
comparison include zero. Propagating interventions through the structural system
does repair it. We then show what the repaired ranking is actually for: an
affordable action, selected under a budget, not another importance score.

---

## Positioning (decided 2026-08-30, rebalanced 2026-08-30)

Lead with the problem, not the estimation theory. Long-duration spaceflight
poses an epidemiology without trials: renal stone risk shifts under altered
gravity, cohorts are tiny, and countermeasure decisions must be argued from
mechanism, observational structure, and simulation. The paper's contribution
is an instrument for making that argument honestly: a single guided pipeline
that walks from data to an affordable countermeasure with the assumptions
visible at every step, exercised on testbeds whose answer keys we wrote and
on a NASA-aligned renal topology.

The scientific spine is the proximity-bias failure and its repair. A node
caused by the outcome (a clinic visit, a late biomarker) can dominate
predictive attribution while carrying zero intervention effect; that is a
live hazard in spaceflight biomarker work, where outcome-adjacent measures
are the easiest to collect. The pipeline shows the failure on a graph small
enough to check by hand, then shows the repair: the graph, not the model,
governs which nodes can receive causal credit and which can be priced as
levers. Expert adjudication (DISCOVERED to RECOVERED, with a ledger) is a
first-class step, not a preprocessing footnote.

One paragraph, not more, on estimation stance: the pipeline deliberately
spans both poles of the structure-versus-target tradition. The causal
Shapley survey trusts the full fitted system to map where credit can live;
the intervention stage then asks one narrow question per surviving lever, a
shift contrast that is a modified treatment policy parameter (Diaz Munoz and
van der Laan 2012; Haneuse and Rotnitzky 2013; Diaz et al. 2023), estimable
with minimal trust from the lever's adjustment set (the semiparametric arm),
or simulated through the calibrated system (the DoWhy-GCM pole, Blobaum et
al. 2024). Cite Marschak (1953) and Heckman (2010) for the economy-of-trust
framing and do-Shapley (Jung et al. 2022) as the published bridge on the
attribution side, and move on.

Related routes are considerations the pipeline can stage, never rivals:
DoWhy and Ananke for single-estimand identification; policy learning (Athey
and Wager 2021), causal bandits (Lattimore et al. 2016; Lee and Bareinboim
2018), and causal Bayesian optimization (Aglietti et al. 2020) for
constrained where-to-intervene. Do not write "no tool does cost-aware
selection": causal Bayesian optimization and budgeted bandits do. The honest
niche is itemized cost sheets over shift parameters inside one
discovery-to-pricing chain, applied end to end to a spaceflight problem.
The hub's Methods tab carries the verified reference list; mirror it in the
submission.

---

## Section 1. Problem

**Claim.** The question "what did the model listen to?" and the question "where
are the system's levers?" have different answers, and the gap is structural
rather than a defect of any one estimator.

**Content.** Renal stone risk during spaceflight, using the NASA SA-07566
topology. Say **NASA-topology simulation** throughout. Never say NASA effect.
State once, early, that the graph topology is source-aligned while every
coefficient is a simulation parameter we chose.

**Non-claim to state in this section.** We do not claim a new definition of
Causal SHAP. Heskes et al., Frye et al., and Janzing et al. define the
estimators we compare.

---

## Section 2. Known truth as the instrument

**Claim.** Synthetic outcomes are the experimental design, not a limitation of
it. Because we wrote the structural equations, the total effect of every node on
the outcome is computable in closed form. That is the only reason any claim
below can be checked rather than argued.

**Content.**

- Reynolds handoff, 2026-07-13: renal stone DAG with 53 nodes and 83 directed
  edges; SANS DAG with 50 nodes and 89 edges. Raw DAGitty text preserved at
  `references/robert-reynolds-2026-07-13/`.
- Concordance against the existing SA-07566 reference (51 nodes, 75 edges):
  strict label comparison gives Cohen's kappa 0.638 with SHD 56. On the
  48 shared nodes after semantic projection, kappa is 0.978, precision 1.000,
  recall 0.958, SHD 3, with 69 of 72 shared-node edges matched.
- Read that pair of numbers honestly. The simulator matches the 51-node
  reference exactly (kappa 1.000, zero edge discrepancies). Reynolds's expanded
  graph is a **candidate source revision**, not the graph the current results
  were generated from.
- Clean simulation: 10,000 records, 28 pre-outcome ancestors of
  `Nephrolithiasis`, event fraction 9.57%.
- Frozen intervention truth: 50,000 common-random-number draws, contrasting
  do(X = 1) against do(X = 0) for binary nodes and do(X = Q75) against
  do(X = Q25) for continuous ones.

**Figure 1.** The sealed world: source DAG, structural equations, frozen truth
table. Everything downstream is scored against that table.

---

## Section 3. The failure, on a graph small enough to check by hand

**Claim.** Predictive credit pools near the outcome, and the node that collects
the most can have zero total effect.

**Content.** Five-node teaching DAG: `Diet -> Hydration -> Y`, `Climate` forking
into both, and `ClinicVisit` caused by `Diet` and `Y`.

| Variable | Ordinary SHAP | Known intervention truth |
| --- | ---: | ---: |
| Diet | 8.8% | 27.6% |
| Climate | 15.4% | 37.9% |
| Hydration | 30.2% | 34.5% |
| **ClinicVisit** | **45.6%** | **0.0%** |

`ClinicVisit` is a descendant of the outcome. Intervening on it moves nothing.
It still takes the largest share of predictive credit.

**Content, flagship.** The same pattern on the renal topology, where it is less
theatrical and more useful. Seven of the 28 ancestors receive exactly zero
TreeSHAP importance under all three predictive arms. The clearest single case is
`medical_prevention_capability`: rank 4 of 28 in the frozen truth, and tied-zero
credit (rank 24.5) under every predictive estimator. Predictive ceiling for
context: the true structural risk probability reaches AUC 0.701 and the fitted
XGBoost reaches 0.684 on 2,002 held-out records with 174 events, so the model is
not broken. It is answering a different question.

---

## Section 4. DISCOVERED

**Claim.** A discovery algorithm returns an equivalence class, and what a
DAG-only tool consumes is one representative of it.

**Content.**

- PC, GES, and DirectLiNGAM return a CPDAG in which some edges stay undirected.
- The graph shown to downstream tools is one **deterministic representative
  consistent extension** (Dor-Tarsi sink removal, lexicographic tie-breaking).
  It preserves the skeleton and every compelled arrow and introduces no new
  unshielded collider. The construction is reproducible. It is not identified.
- The pairs that were undirected travel with the graph rather than being
  discarded, because they are the input to the honesty metric in Section 5.
- Algorithms disagree with each other on the same sample. Report the
  disagreement as a measurement, not as noise to be averaged away.

**Non-claim, stated explicitly and repeated in the discussion.** We do not
orient undirected edges from data, and we do not present a discovered graph as
the causal truth. Where an edge direction is not identified, we quantify what
survives the ambiguity instead of choosing and moving on quietly.

---

## Section 5. RECOVERED

**Claim.** Expert adjudication can buy usable validity even where global
edge-recovery scores barely move, and a better-looking graph can still fail the
thing you need it for.

**Content.** The recovered graph is the discovered graph plus a versioned ledger
of forbidden and required edges from domain review. The ledger records, per
entry, whether the constraint entered the search or was applied to the output
graph afterwards. Those are different epistemic acts and the record should not
blur them.

Reynolds's own classification of renal edges gives the review its categories:
definitional or identity edges, engineered by-design control, biological or
behavioral, measurement or detection, and decision or treatment response.

Evaluate along two axes rather than one.

| Metric | What it asks |
| --- | --- |
| M1 concordance | Precision, recall, F1 (directed and skeleton) and SHD against the sealed graph |
| M2 target pathway | Correct, reversed, spurious, missed, restricted to edges on exposure-to-outcome paths |
| M3 sufficiency transfer | Derive the minimal adjustment set from the learned graph; test whether it stays valid in the sealed truth |
| M4 parameter fidelity | Estimate the effect adjusting for that set; report bias against the frozen do-truth in outcome units |
| M5 identification honesty | Enumerate consistent extensions of the CPDAG; report the fraction under which the adjustment set stays valid |

M5 is the section's load-bearing metric. It prices overclaiming from an
equivalence class. When the orientation space is larger than the enumeration
cap, the reported figure is labeled a capped Monte Carlo estimate rather than an
exhaustive count.

**Terminology decision to make before drafting.** "Recovered DAG" is not
currently a defined term in this literature or in our own record, where it
appears three times informally. Either define it explicitly on first use as the
post-adjudication graph, or keep the existing notation for the plausible graph
after review round r. Do not let both float.

**Open item.** The study guide sets the exposure as cumulative mission duration.
The clean v3 simulation has no mission-duration variable and currently uses
`altered_gravity`. Resolve this before drafting, and make every document agree.

---

## Section 6. Ordering alone does not fix it

**Claim.** Supplying a causal order to the attribution method is not what
produces the improvement.

**Content.** This is the null result, and it belongs in the main text.

| Method | Kendall tau | Top-5 recovery | PBI | Mass within 2 hops |
| --- | ---: | ---: | ---: | ---: |
| Exact TreeSHAP | 0.522 | 0.60 | 1.082 | 83.1% |
| Matched ordinary interventional SHAP | 0.506 | 0.60 | 1.051 | 81.6% |
| DAG-asymmetric ordering | 0.528 | 0.60 | 1.051 | 81.2% |

Paired bootstrap over 2,000 draws: the difference in Kendall tau between matched
ordinary and DAG-asymmetric SHAP is 0.008 with interval [-0.011, 0.027]. The
intervals for PBI, POA, and proximal mass also include zero. Top-5 recovery is
identical in 99.9% of draws.

Restricting feature order to the DAG therefore does not support a causal
recovery claim on its own. Say so plainly. A reader who finds this buried in an
appendix will not trust Section 7.

---

## Section 7. Propagation is what moves the result

**Claim.** Changing the coalition value function to propagate interventions
through the structural system recovers the upstream targets.

**Content.** The value function is the expected model output under
do(X_S = x_S): background observations are abducted to exogenous draws, each
coalition intervention is propagated to descendants, and the model is scored on
the result.

| Metric | Structural prototype | Ordering-only |
| --- | ---: | ---: |
| Kendall tau | 0.794 | 0.528 |
| Spearman rho | 0.932 | 0.652 |
| Top-5 recovery | 1.00 | 0.60 |
| PBI | -0.113 | 1.051 |
| POA | -0.023 | 0.210 |
| Mass within 2 hops | 38.1% | 81.2% |

The frozen truth places 42.1% of importance within two hops, so the structural
prototype's 38.1% sits near the truth while the ordering-only arm's 81.2% sits
near the outcome.

**Label this a prototype and mean it.** The run is 32 evaluation rows by 32
background draws by 32 permutations, with no paired-bootstrap uncertainty and no
repeated-seed replication of the full pipeline. State the convergence work the
result still needs.

---

## Section 8. A per-node depth diagnostic

**Circulation gated on Lucidity sign-off. Draft, do not circulate.**

**Claim.** A predictive model's internal per-feature geometry carries a signal
about which nodes deserve a second look, and that signal is close to orthogonal
to predictive importance.

**Content.** [Withheld pending sign-off; see docs/lumawarp/README.md section 2.]

[Block-level behavior withheld from the tracked outline pending Lucidity
Sciences' sign-off (ADR 008). The private format guide holds it.]

**Frame it as a diagnostic, at the strength the evidence supports.** This is a
pointer to nodes where the reviewer should distrust the current attribution and
iterate. It is not a causal claim and not an importance score. Three flags on
three single-seed runs is an observation worth prespecifying and testing, not a
result. State that the interpretation of the three blocks is our reading and has
not been confirmed by the vendor.

---

## Section 9. Price and dice: from a ranking to an affordable action

**Claim.** A target ranking becomes a decision only when feasibility and cost
enter, and the ranking alone can recommend something you cannot afford or cannot
move.

**Content.** Selection is a constrained optimization: maximize expected benefit
subject to a budget and to a probability-of-benefit floor. Benefit is measured
by simulating the structural model under do(a) against the same exogenous draws,
so the contrast is paired. Cost is charged on the nodes an actor directly
assigns, never on the downstream changes the model propagates.

Two screens run before any money is considered. A node must be manipulable, and
a node must be an ancestor of the outcome. The second screen removes the
zero-effect proxy from Section 3 by construction rather than by estimation.
Every exclusion is reported with the rule that caused it.

Worked result on the teaching DAG, where the total effects are exact:

| Action | Benefit | Cost | Benefit/cost |
| --- | ---: | ---: | ---: |
| Hydration +1 | 1.0 | 1.0 | 1.00 |
| Diet +1 | 0.8 | 1.3 | 0.62 |
| Climate +1 | 1.1 | 1.5 | 0.73 |
| ClinicVisit +1 | screened: not an ancestor | | |

The selected action changes with the budget: Hydration at budgets 1.2 and 1.4,
Climate at 1.5. The largest effect wins only once it is affordable.

**A methodological point worth its own paragraph.** The obvious objective,
maximize benefit divided by cost, is degenerate under linear costs: benefit and
cost both scale with the dose, so the ratio is dose-invariant and arbitrarily
small cheap actions tie for first. We report the ratio as a diagnostic and
optimize the budget-constrained problem instead. The two disagree in our worked
example at budget 1.5, which is the cleanest demonstration of why the choice
matters.

**Naming.** Call this cost-constrained causal recourse candidate generation.
Cite DiCE as the lineage the design is deliberately restricted from: there is no
model-gradient counterfactual search here and no proximity-to-manifold term.
Cite Karimi et al. for the result that recourse cannot generally be guaranteed
without the true structural equations when interventions have descendants. The
output is a recommendation candidate worth testing, not a recommendation.

---

## Section 10. The recovered graph as a Bayesian network

**Claim.** The object the pipeline produces is reusable: a directed graph with
fitted structural equations, on which further interventions can be posed and
answered without re-running discovery.

**Content.** Export contains the recovered graph and its constraint ledger, the
fitted structural equations with per-node diagnostics, the node flags, the
action ranking with its screening report, the M1 through M5 results, and the
count of undirected pairs still unresolved. That last number travels with the
export so a downstream user cannot mistake a representative extension for an
identified graph.

Close on what this does not settle: unmeasured confounding is not detectable
from the graph, the structural equations are linear and additive by assumption,
and the cost sheet in the worked example is illustrative rather than
domain-reviewed.

---

## Limitations, as a numbered section rather than a paragraph

1. All datasets are synthetic. Topologies are source-aligned; coefficients are
   simulation parameters, not NASA estimates.
2. DAG-constrained ordering and structural intervention propagation answer
   different questions and should not share one label without stating the value
   function.
3. The structural result is a 32x32x32 prototype without repeated-seed
   uncertainty over the full pipeline.
4. Discovery results are single-seed pilots. Skeleton recovery and directed
   recovery differ substantially, and the pilot placed mediators in a learned
   adjustment set.
5. The depth diagnostic is single-seed, derived from a proprietary runtime, and
   its three blocks are interpreted by us rather than defined by the vendor.
6. Intervention-target ranking is not a treatment recommendation. Safety,
   timing, reversibility, and domain constraints sit outside the current engine.
7. SANS is ingested as topology and provenance only. No coefficients, data, or
   results are claimed for it.
8. Both estimation poles trust the same unverifiable input, the DAG. A wrong
   adjustment set makes a targeted estimate confidently wrong; the Maxim buys
   reduced parametric trust, not reduced structural trust.
9. Attribution is not achievable effect. Shapley's efficiency axiom fixes the
   total to be divided, so a triage ranking by attribution must not be read as
   a ranking of feasible gains; price and dice re-measures for exactly this
   reason.
10. Shortlist-then-estimate reintroduces selection and multiplicity that
    per-parameter inference does not fix; say so where the winners are
    declared.

---

## Figures

1. The sealed world: source DAG, structural equations, frozen truth.
2. The teaching trap: ordinary credit against known truth, side by side.
3. Discovered to recovered: CPDAG with undirected edges dashed, then the
   adjudicated graph, with the constraint ledger beside it.
4. The three attribution arms against frozen truth, with the paired-bootstrap
   intervals on the ordering-only comparison drawn so the reader sees them
   crossing zero.
5. Depth flags over the recovered graph (gated).
6. Benefit against cost, with the budget line moving and the selected action
   changing as it moves.

---

## Drafting order

Sections 2, 3, 4, 6, and 7 rest entirely on frozen results and can be written
now. Section 5 needs the exposure question settled. Section 9 needs the cost
module's renal sheet, which is illustrative until domain review. Section 8 is
written last and held.

## Open questions for coauthors

**Reynolds.** Which renal and SANS edges are definitional, deterministic, or
by design? Which placeholder coefficients are implausible? Which nodes are
actionable, and at what relative cost? Is SANS acceptable as the prespecified
second topology?

**Lucidity.** The six questions in `LUMAWARP_EXPLAIN_GUIDE.md` section 7, of
which two gate this manuscript: what the three blocks measure, and what part of
the reduction and aggregate output may appear in a public paper.

**Authorship.** Order is unconfirmed. Settle it separately from the science.

---

## Addendum, 2026-09-04: the reframing, mapped onto the sections above

The 1 September whiteboard and the framing memo
(`docs/framing/prediction-vs-intervention.md`) move the article from "which
upstream node to change" to "a playbook for graph-based intervention
estimation". The sections above still stand; this is what changes in each.

| Section | Change |
| --- | --- |
| Argument paragraph | Open with two goals, two playbooks. Prediction is the default recipe and is fine for prediction; intervention casts a wider net and still prunes. Cite Shmueli 2010, Hernán et al. 2019, Harrell 2015 together and move on |
| Positioning | Lead with the playbook, exercised on the renal topology, rather than with the proximity-bias failure alone |
| 1. Problem | Add: deeper nodes wash out with depth (product rule), sampling variance (figure: `docs/images/depth_washout.png`), noise, and discovery; the core question is how to tell a deep node from a shallow one |
| 2. Known truth | Unchanged. Add the 14-node working subgraph as the primary case study alongside the full DAG |
| 3. The failure | Add the working-subgraph mediator inversions (four of five pairings on the oxalate chain) |
| 4. DISCOVERED | Add: PC pruned every edge into the binary outcome at n = 1,000; run MGM PC-Stable (CausalMGM) alongside PC |
| 5. RECOVERED | Unchanged; the "recovered DAG" terminology decision still open |
| 6. Ordering alone | Unchanged |
| 7. Propagation | Add the Heskes-style value function as the fourth Step 6 method on the working subgraph (replaces the blocked shapr path) |
| 8. Depth diagnostic (gated) | Reframe as the detector for rung 3 with the dichromatic filter as rung 4; state the problem ("deep from shallow") first; report E1 to E3 when run; still gated |
| 9. Price and dice | Unchanged; note it is rung 6 and out of scope |
| 10. Bayesian network export | Unchanged |
| Limitations | Add the linearity assumption as a stated working assumption (enforced in the generator, relaxed in estimators, priced in Step 9) |
| Figures | Add the depth-washout figure to Figure 1 or as Figure 2 |

Open items carried from the memo: which two channels the dichromatic filter
pairs; where the filter sits relative to expert review; the Goodenow-Messman
correction in the reference list.

The consolidated plan of 2026-08-10 (`Space SHAP_ Consolidated Plan v2.docx`)
organizes the same material as a spine, Phase 0 (the known world) through
Phase VI (robustness), with the M1 to M6 evaluation battery in Phase III.
The rungs of the playbook (`docs/playbook/README.md`) map onto that spine;
M1 to M5 are implemented in `apps/causal_shap/evaluation.py`, and M6 (do
detector flags coincide with true adjustment-set members or pathway
ancestors more than chance?) is the prespecified test for rung 3 once the
provider is available.
