# JAN SUTRA — Citizen Sentiment & Governance Decision Intelligence

> **From citizen signal to evidence-backed governance action.**

JAN SUTRA is a **decision-support prototype** that demonstrates how fragmented citizen feedback can be converted into structured governance insights, prioritised interventions, and field-validation plans.

It is designed as an analytical workflow rather than a political persuasion, voter-targeting, or profiling system.

---

## Why JAN SUTRA?

Citizen feedback is often fragmented across complaints, surveys, service experiences, and administrative records. A useful governance analysis should answer more than:

> **"What are people saying?"**

It should help answer:

1. **What changed?**
2. **Where is the change concentrated?**
3. **What are the plausible drivers?**
4. **What evidence supports each hypothesis?**
5. **What remains untested?**
6. **Which issue should be prioritised?**
7. **What should be verified in the field before action?**
8. **What administrative intervention could be evaluated?**

JAN SUTRA structures this process as:

**Signal → Trend → MECE Drivers → Competing Hypotheses → Evidence → Priority → Field Validation → Administrative Action**

---

## Core Capabilities

### 1. Data-Quality Audit

The pipeline performs deterministic quality checks before analysis, including:

- duplicate detection
- date validation
- district validation
- sentiment standardisation
- missing-value handling
- derived analytical fields
- quality scoring
- explicit audit reporting

The goal is to make the analytical starting point visible rather than treating the input dataset as automatically reliable.

---

### 2. Trend & Anomaly Analysis

JAN SUTRA analyses monthly issue-level patterns using:

- negative-sentiment rates
- feedback volume
- satisfaction trends
- historical mean and standard deviation
- z-score based screening
- month-on-month change

Issues are classified into states such as:

- **Escalating**
- **Improving**
- **Stable**
- **Normal fluctuation**
- **Insufficient history**

The anomaly logic is intended as a **screening mechanism**, not a statistically validated forecasting model.

---

### 3. MECE Governance Issue Trees

For major governance issues, the platform uses analyst-designed **MECE driver trees** to structure possible explanations.

For example, a Public Transport issue can be decomposed into areas such as:

- Availability & Coverage
- Reliability & Scheduling
- Capacity & Safety
- Affordability & Access

These trees are deliberately treated as **hypothesis structures**, not machine-discovered causal explanations.

---

### 4. Competing Hypotheses & Evidence Triangulation

JAN SUTRA separates:

**Observed signal**

from

**Possible explanation**

and from

**Evidence required to validate the explanation.**

The evidence layer combines available feedback patterns with district-level service indicators where appropriate.

Evidence is explicitly labelled as:

- descriptive evidence
- directional association
- evidence gap
- field validation requirement

The system does **not** convert correlation into causation.

---

### 5. Transparent Priority Scoring

Issues are ranked using a transparent multi-factor priority framework.

The score considers:

- issue prevalence
- negative sentiment
- trend behaviour
- population exposure
- evidence availability

Each component is visible rather than hidden inside an opaque model.

The resulting score should be interpreted as a **decision-prioritisation heuristic**, not an objectively calibrated measure of governance importance.

---

### 6. Intervention Mapping

Potential interventions are structured around:

- **Lever**
- **Proposed action**
- **Accountable owner**
- **Validation data**
- **Success metric**

This creates a direct connection between:

**Evidence → Intervention → Measurement**

rather than generating generic recommendations.

---

### 7. Field Verification Workflow

Before an analytical hypothesis is translated into action, JAN SUTRA defines what should be verified through fieldwork and administrative records.

A typical workflow is:

**Hypothesis → Field verification → Administrative cross-check → Contradictory evidence check → Decision**

If field evidence contradicts the leading hypothesis, the hypothesis should be revised rather than forcing the evidence to support the original recommendation.

---

### 8. Executive Governance Brief

The platform can generate an executive PDF containing:

- key issue
- priority assessment
- trend
- supporting evidence
- evidence gaps
- proposed action
- accountable owner
- validation data
- success metric
- analytical caveats

---

## Architecture

```text
Citizen Feedback
       │
       ▼
Data-Quality Audit
       │
       ▼
Sentiment / Issue Structure
       │
       ▼
Trend Detection
       │
       ▼
MECE Driver Tree
       │
       ▼
Competing Hypotheses
       │
       ▼
Evidence Triangulation
       │
       ▼
Priority Scoring
       │
       ▼
Field Validation Plan
       │
       ▼
Governance Action
       │
       ▼
Executive Brief