# DAG Harvest Protocol

> Ported from the Box project folder on 2026-09-04 (Andy Wilson's July 2026 notes). Paths and links inside refer to the Target DAGs repository as it stood then; the canonical implementations now live under `analysis/` and `apps/` in this hub.

**Version:** 1.0 (2026-02-23)
**Project:** Tao of RWD — DAG Builder Module

---

## Purpose

This protocol guides the systematic extraction of causal DAG (directed acyclic graph) primitives from published literature. Each harvester works independently on papers from their domain, then individual harvests are combined into a shared protocol and edge library.

**Goal:** Turn unstructured causal reasoning in the literature into structured data — nodes, edges, and structural assumptions — that can be imported into the Tao of RWD DAG builder.

Think of it as a **REVMAN for causal structure**: instead of extracting effect estimates for meta-analysis, we extract causal assumptions for DAG construction.

---

## Step 1: Rate the Paper (CSER Scale)

Before attempting extraction, score the paper on the **Causal Structure Explicitness Rating** (CSER) scale. This determines how much structure you can expect to harvest and how much effort is warranted.

| Score | Label | What it means | What you can extract |
|-------|-------|---------------|---------------------|
| **5** | Explicit DAG | Paper includes DAG figure(s) with nodes and directed edges. Causal assumptions are formally encoded. | Direct transcription of nodes, edges, and types. High-fidelity harvest. |
| **4** | Near-explicit | Causal framework language, partial diagrams, references DAG methodology. | Nodes and most edges recoverable; some edges need inference from text. |
| **3** | Strongly implied | Clear causal language, systematic confounder reasoning, dose-response or temporality arguments. A DAG could be reconstructed from the prose. | Core exposure-outcome path clear; confounder set identifiable; edge directions inferable. |
| **2** | Weakly implied | Causal intent in design (e.g., propensity scores, "treatment effects") but no causal model specified. Variable selection is empirical, not theory-driven. | Exposure and outcome identifiable; confounder vs. mediator vs. collider roles ambiguous. |
| **1** | No causal structure | Purely descriptive or associational. No exposure-outcome framing, no adjustment rationale. | Minimal: at best, candidate nodes for future DAGs. No edges extractable. |

### Decision tree

```
Does the paper include a DAG figure?
├── YES → Is it complete (all key variables + directed edges)?
│   ├── YES → Score 5
│   └── NO (partial/illustrative only) → Score 4
└── NO
    ├── Does it reference DAG/causal-diagram methodology? → Score 4
    ├── Does it use causal language + systematic confounder reasoning? → Score 3
    ├── Does it have causal intent but empirical/atheoretical variable selection? → Score 2
    └── Is it purely descriptive with no causal framing? → Score 1
```

**Triage guidance:** For CSER 1-2 papers, extraction yield is low. Consider whether the paper is worth a full harvest or just a brief note identifying the exposure, outcome, and variable list.

---

## Step 1b: Classify the Paper Type

Before harvesting, also classify the paper's **type**. This determines whether you extract DAG structure or follow references to primary studies — just like in a systematic review, where you extract data from primary studies, not from reviews.

| Type | SR analogy | What to do |
|------|-----------|------------|
| **Primary study** | Original research | Full harvest. This is the main target. Extract nodes, edges, structure, and evidence metrics. |
| **Methodological/teaching** | Review/commentary | Do NOT harvest as a primary source. Extract the **methodological lesson** (e.g., "colliders exist," "confounding by indication matters") and **follow the references** to the primary studies it discusses. Harvest *those* instead. |
| **Methodological + reanalysis** | Pooled analysis | Partial harvest. The paper reanalyzes primary data to make a methodological point. Harvest the structural insight but flag that the DAG was constructed to teach, not to comprehensively model the domain. Link to the companion primary study. |

### Why this matters

The most famous "DAG papers" (Hernan 2002, Greenland/Pearl/Robins 1999, etc.) are methodological — they use applied examples to illustrate methodology, not to answer a causal question. Harvesting them as if they're primary studies is a trap:
- The DAG is simplified to make a teaching point, not to be comprehensive
- The authors aren't trying to model the full causal structure of the domain
- Following their references to the actual primary studies yields richer, more complete harvests

**Record the Paper Type in the metadata table** alongside the CSER score.

---

## Step 2: Extract Nodes

For each variable the paper discusses, create a node entry:

| Field | Description | Maps to |
|-------|-------------|---------|
| **ID** | Short identifier (E, D, C1, U1, etc.) | `DagNode.label` |
| **Label** | Descriptive name | `DagNode.label` |
| **Type** | EXPOSURE, OUTCOME, REGULAR, ADJUSTED, or LATENT | `DagNode.nodeType` |
| **Description** | What the variable represents | `DagNode.description` |
| **Measured?** | Yes / Partially / No | (metadata) |

### Node types to look for

- **Exposure (E/W)**: Primary treatment, intervention, or exposure of interest
- **Outcome (D/Y)**: Primary endpoint or disease outcome
- **Confounders**: Common causes of exposure and outcome → Type: ADJUSTED (if the paper adjusts for them) or REGULAR
- **Mediators**: Variables on the causal pathway between exposure and outcome → Type: REGULAR
- **Colliders**: Variables that are common *effects* of two or more causes → Type: REGULAR (with a note about collider role)
- **Latent/unmeasured variables**: Acknowledged but unmeasured common causes → Type: LATENT
- **Effect modifiers / Instruments**: Variables that modify the effect or serve as instruments → Type: REGULAR (with a note)

### Tips

- For CSER 5 papers: nodes are usually directly transcribable from figures
- For CSER 3-4 papers: extract from the confounding discussion, adjustment sets, and Methods section
- For CSER 2 papers: the variable list is available but roles (confounder vs. mediator vs. collider) are ambiguous — flag this uncertainty
- Always look for **unmeasured variables** the authors acknowledge. These are critical for structural completeness.

---

## Step 3: Extract Edges

For each relationship between nodes, record:

| Field | Values | Maps to |
|-------|--------|---------|
| **From → To** | Node IDs | `DagEdge.sourceNode` → `DagEdge.targetNode` |
| **Direction** | DIRECTED or BIDIRECTED | `DagEdge.edgeType` |
| **Confidence** | HIGH / MED_HIGH / MEDIUM / LOW_MED / LOW | `DagEdge.confidence` |
| **Origin** | LITERATURE / EXPERT / MECHANISTIC / DATA_DRIVEN / UNKNOWN | `DagEdge.origin` |
| **Evidence** | META_ANALYSIS / SYSTEMATIC_REVIEW / RCT / COHORT / CASE_CONTROL / CROSS_SECTIONAL / EXPERT_OPINION / MECHANISTIC / NOT_SPECIFIED | `DagEdge.strongestEvidence` |
| **Certainty** | CERTAIN / PROBABLE / UNCERTAIN | `DagEdge.directionCertainty` |
| **Justification** | Free text: why does this edge exist? Cite specific evidence. | `DagEdge.justification` |

### Tips

- **Direction matters.** An edge A → B means "A is a direct cause of B" (possibly through mechanisms not represented in the DAG). Getting direction wrong changes the entire structural interpretation.
- **Absence of an edge is also a claim.** If two variables in your DAG have no edge between them, you're claiming they are conditionally independent given their parents. Make sure missing edges are deliberate.
- **Bidirected edges** (A ↔ B) represent an unmeasured common cause. Use these when you believe both variables share a latent parent but don't want to add the latent node explicitly.
- **Record justifications from the paper**, not just your own reasoning. Quote or cite the section where the authors defend the relationship.

---

## Step 4: Assess Structure

After extracting nodes and edges, evaluate the DAG as a whole:

- [ ] **Completeness** — Are all relevant paths between exposure and outcome represented?
- [ ] **Backdoor paths** — Can all non-causal paths be blocked by conditioning? What is the correct adjustment set?
- [ ] **Collider identification** — Are any variables common *effects* of two causes? Would conditioning on them open non-causal paths?
- [ ] **Testable implications** — Does the DAG generate conditional independencies that could be checked in data?
- [ ] **Missing edges** — Are there plausible relationships the paper doesn't discuss?
- [ ] **Adjustment validity** — Does the paper's actual adjustment strategy match what the DAG would recommend?
- [ ] **Harvester vs. paper** — Clearly note which structural claims come directly from the paper and which are your interpretation.

---

## Step 5: Record Evidence Metrics (per edge)

Where the paper (or its cited references) reports quantitative estimates for an edge:

| Field | Description | Maps to |
|-------|-------------|---------|
| **Edge** | Which edge | `DagEdgeCitationMetric` |
| **Measure** | OR, HR, RR, RD, etc. | `DagEdgeCitationMetric.metricName` |
| **Value** | Point estimate + CI | `DagEdgeCitationMetric.metricValue` |
| **Population** | Study population | (citation metadata) |
| **Source** | Citation | `DagEdgeCitation` |

---

## Output Format

### File naming

```
harvests/{cser_score}-{first_author_lastname}-{year}.md
```

### Required sections

Each harvest file should include:
1. **Paper Metadata** (title, authors, journal, year, DOI/PMID, study design, **Paper Type**, CSER score)
2. **CSER Justification** (why this score)
3. **Research Question**
4. **Nodes** (table)
5. **Edges** (table)
6. **Key Structural Insight** (the most important causal reasoning in the paper)
7. **Adjustment Set** (DAG-guided recommendation)
8. **Evidence Metrics** (table, where available)
9. **Structural Assessment** (checklist from Step 4)

### Reference example: A paired harvest

The protocol includes a **paired example** showing how primary studies and methodological papers work together:

#### Primary study (the harvest target)

[`harvests/3-hernandez-diaz-2000.md`](harvests/3-hernandez-diaz-2000.md) — **CSER 3, Primary study**

> Hernandez-Diaz S, Werler MM, Walker AM, Mitchell AA. Folic acid antagonists during pregnancy and the risk of birth defects. *N Engl J Med.* 2000;343(22):1608-1614.

A multicenter case-control study from the Slone Birth Defects Study. Strong causal reasoning (confounding by indication, mechanistic hypothesis testing via effect modification) but **no formal DAG**. The harvest reconstructs the causal structure from the study design and adjustment strategy — this is where the protocol adds the most value.

Key structural features: confounding by indication (infection → drug use → birth defects), effect modification as a mechanistic test (folic acid blocks DHFRI but not AED pathway), and selection bias via malformation-based controls.

#### Methodological companion (not a harvest target)

[`harvests/5-hernan-2002.md`](harvests/5-hernan-2002.md) — **CSER 5, Methodological + reanalysis**

> Hernan MA, Hernandez-Diaz S, Werler MM, Mitchell AA. Causal Knowledge as a Prerequisite for Confounding Evaluation. *Am J Epidemiol.* 2002;155(2):176-184.

The same research group's methodological paper, using the same Slone data. Demonstrates that statistical confounding criteria can misidentify colliders as confounders, biasing estimates toward the null. This paper is classified as **Methodological + reanalysis** — it teaches the lesson, but the primary data lives in the companion study.

#### What the pairing demonstrates

1. **The harvest adds the most value for CSER 2-3 papers**, where causal reasoning exists but hasn't been formalized as a DAG.
2. **Methodological papers are references, not harvest targets** — like reviews in a systematic review, they point you to primary studies.
3. **Following references from famous methods papers leads to rich primary harvests** that are more comprehensive than the simplified teaching examples.

---

## Combining Harvests Across Domains

Each team member should harvest papers from their own domain independently. When combining:

1. **Use consistent node naming.** If two harvests refer to the same concept (e.g., "SES", "socioeconomic status", "education level"), agree on a canonical label.
2. **Flag overlapping edges.** When two papers discuss the same causal relationship, record both and note agreements/disagreements in confidence and direction.
3. **Preserve CSER scores.** The CSER score reflects the source paper's explicitness, not the harvester's confidence. A CSER-3 harvest with careful reconstruction is valuable but carries more uncertainty than a CSER-5 transcription.
4. **Document inter-harvester disagreements.** When two people harvest the same paper and produce different DAGs (especially for CSER 3), this is expected — document both versions and discuss.

### Merging into the edge library

Harvested edges become candidates for the Tao of RWD edge library. Each edge carries:
- Its source citation (the harvested paper)
- The CSER score of that source
- The confidence, evidence type, and direction certainty from the harvest
- Any quantitative metrics

Multiple harvests of the same edge strengthen confidence; conflicting harvests flag areas needing further review.

---

## Quick Reference: Common Pitfalls

| Pitfall | Why it matters | How to avoid |
|---------|---------------|--------------|
| **Treating a collider as a confounder** | Adjusting for a collider opens a non-causal path, introducing bias | Always check: is this variable a common *cause* (confounder) or common *effect* (collider) of other variables? |
| **Ignoring unmeasured variables** | Omitting latent common causes hides confounding | Explicitly list variables the authors acknowledge as unmeasured |
| **Confusing the paper's claims with your interpretation** | Mixes transcription with reconstruction | Label each structural claim as "from paper" or "harvester interpretation" |
| **Orphaned nodes** | A node with no edges adds noise, not structure | Every node should connect to at least one edge. If not, either add the edge or remove the node. |
| **Missing edges as oversights** | An absent edge claims conditional independence — make this deliberate | Review every pair of nodes and ask: "Is there really no direct causal relationship here?" |
| **Harvesting a methods paper as a primary study** | The DAG was built to teach, not to model the domain comprehensively — it's deliberately simplified | Check Paper Type first. If the paper's goal is to demonstrate methodology, follow its references to the primary studies and harvest *those* |

---

## Methodological References

- Hernan MA, Robins JM. *Causal Inference: What If.* Chapman & Hall/CRC, 2020. [Free access](https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/) — Chapters 6-8 cover DAGs, confounding, and selection bias.
- Greenland S, Pearl J, Robins JM. Causal diagrams for epidemiologic research. *Epidemiology.* 1999;10(1):37-48. — The foundational paper bringing DAGs to epidemiology.
- Pearl J. *Causality: Models, Reasoning, and Inference.* Cambridge University Press, 2000. — The theoretical foundation.
- Hernan MA et al. Causal Knowledge as a Prerequisite for Confounding Evaluation. *Am J Epidemiol.* 2002;155(2):176-184. — The reference example for this protocol.
