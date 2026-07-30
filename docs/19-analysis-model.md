---
id: ANALYSIS-MODEL-001
title: MIOS Analysis Model Specification
document: 19-analysis-model.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the canonical representation of every Analysis produced by MIOS. It builds upon the Intelligence Domain aggregates introduced in [17-domain-model.md](17-domain-model.md) and the canonical Market Domain objects defined in [18-market-model.md](18-market-model.md), giving every Assessment and Explanation a precise, shared shape.

This document becomes the single source of truth for every Analysis Engine, the Contradiction Engine, the Decision Engine, and the AI Explanation Engine, defined in [07-price-engine.md](07-price-engine.md) through [14-ai-explanation-engine.md](14-ai-explanation-engine.md).

This document does not define algorithms, APIs, events, persistence, or implementation classes. It defines the canonical model that future Technical Design documents must implement.

---

# 2. Scope

This document covers the canonical representation of:

- Liquidity Assessment
- Options Assessment
- Momentum Assessment
- Context Assessment
- Contradiction Assessment
- Decision Assessment
- Explanation

It also defines the shared Evidence Model, Confidence Model, Observation Model, and lifecycle rules that apply uniformly to every Analysis above.

---

# 3. Design Principles

| Principle | Description |
|---|---|
| Single Source of Truth | Every engine references the same canonical definition of an Analysis and its shared structure. |
| Evidence First | No Analysis is considered valid without a reference to the evidence that supports it, consistent with [01-product.md](01-product.md). |
| Immutable Once Published | A published Analysis is never modified; a change in market conditions produces a new Analysis. |
| Explainability by Construction | The canonical shape of an Analysis inherently carries the information needed to explain it, consistent with [02-architecture.md](02-architecture.md). |
| Cross-Engine Uniformity | Every Analysis Engine, regardless of domain, produces output conforming to the same canonical structure. |
| No Instruction Content | No Analysis may contain a buy, sell, or hold instruction, consistent with [01-product.md](01-product.md). |
| Traceable Confidence | Confidence is always expressed in a way that can be traced back to the evidence and observations that produced it. |
| Deterministic Identity | Every Analysis has an identity that can be derived consistently and does not change once assigned. |

---

# 4. Analysis Taxonomy

## 4.1 Liquidity Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents a structured, evidence-backed observation about liquidity conditions. |
| Identity | A unique Assessment Identifier, associated with an Instrument and a Time Window. |
| Owner | The Liquidity Engine, defined in [08-liquidity-engine.md](08-liquidity-engine.md). |
| Inputs | Volume, Open Interest, and related market data drawn from the canonical Market Model. |
| Outputs | Structured observations about liquidity, participation, and related conditions. |
| Evidence Requirements | Must reference the specific volume and participation data supporting each observation. |
| Confidence | Expressed using the Confidence Model defined in Section 7. |
| Lifecycle | Follows the Assessment Lifecycle defined in Section 9. |
| Validation | Must satisfy the Validation Rules defined in Section 13. |

## 4.2 Options Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents a structured, evidence-backed observation about options positioning and activity. |
| Identity | A unique Assessment Identifier, associated with an Instrument and a Time Window. |
| Owner | The Options Engine, defined in [09-options-engine.md](09-options-engine.md). |
| Inputs | Options chain data, open interest, strike, and expiry data drawn from the canonical Market Model. |
| Outputs | Structured observations about open interest, strike activity, and positioning. |
| Evidence Requirements | Must reference the specific derivatives data supporting each observation. |
| Confidence | Expressed using the Confidence Model defined in Section 7. |
| Lifecycle | Follows the Assessment Lifecycle defined in Section 9. |
| Validation | Must satisfy the Validation Rules defined in Section 13. |

## 4.3 Momentum Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents a structured, evidence-backed observation about market movement. |
| Identity | A unique Assessment Identifier, associated with an Instrument and a Time Window. |
| Owner | The Momentum Engine, defined in [10-momentum-engine.md](10-momentum-engine.md). |
| Inputs | Price and volume movement data drawn from the canonical Market Model. |
| Outputs | Structured observations about strength, weakness, acceleration, and deceleration. |
| Evidence Requirements | Must reference the specific movement data supporting each observation. |
| Confidence | Expressed using the Confidence Model defined in Section 7. |
| Lifecycle | Follows the Assessment Lifecycle defined in Section 9. |
| Validation | Must satisfy the Validation Rules defined in Section 13. |

## 4.4 Context Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents a structured, evidence-backed observation about the broader market environment. |
| Identity | A unique Assessment Identifier, associated with a Market or Instrument and a Time Window. |
| Owner | The Context Engine, defined in [11-context-engine.md](11-context-engine.md). |
| Inputs | Market state, session, and calendar data drawn from the canonical Market Model. |
| Outputs | Structured observations about market environment, regime, and session context. |
| Evidence Requirements | Must reference the specific contextual data supporting each observation. |
| Confidence | Expressed using the Confidence Model defined in Section 7. |
| Lifecycle | Follows the Assessment Lifecycle defined in Section 9. |
| Validation | Must satisfy the Validation Rules defined in Section 13. |

## 4.5 Contradiction Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents the evaluated relationship (agreement, contradiction, ambiguity, or evidence gap) between two or more upstream Assessments. |
| Identity | A unique Assessment Identifier, associated with the set of Assessments it evaluates. |
| Owner | The Contradiction Engine, defined in [12-contradiction-engine.md](12-contradiction-engine.md). |
| Inputs | Liquidity, Options, Momentum, and Context Assessments. |
| Outputs | Structured relationships describing agreement, conflict, ambiguity, or missing evidence among upstream Assessments. |
| Evidence Requirements | Must reference the specific upstream Assessments being compared. |
| Confidence | Expressed using the Confidence Model defined in Section 7. |
| Lifecycle | Follows the Assessment Lifecycle defined in Section 9. |
| Validation | Must satisfy the Validation Rules defined in Section 13; must reference at least two upstream Assessments. |

## 4.6 Decision Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents the synthesized decision-support view combining upstream Assessments and the Contradiction Assessment. |
| Identity | A unique Assessment Identifier, associated with an Instrument or Market and a point in time. |
| Owner | The Decision Engine, defined in [13-decision-engine.md](13-decision-engine.md). |
| Inputs | Liquidity, Options, Momentum, and Context Assessments, and the corresponding Contradiction Assessment. |
| Outputs | A synthesized, structured decision-support assessment. |
| Evidence Requirements | Must reference every upstream Assessment and Contradiction Assessment it synthesizes. |
| Confidence | Expressed using the Confidence Model defined in Section 7. |
| Lifecycle | Follows the Assessment Lifecycle defined in Section 9. |
| Validation | Must satisfy the Validation Rules defined in Section 13; must never contain a buy, sell, or hold instruction. |

## 4.7 Explanation

| Attribute | Description |
|---|---|
| Purpose | Represents the human-readable narrative describing a Decision Assessment. |
| Identity | A unique Explanation Identifier, associated with exactly one Decision Assessment. |
| Owner | The AI Explanation Engine, defined in [14-ai-explanation-engine.md](14-ai-explanation-engine.md). |
| Inputs | A single Decision Assessment and its referenced evidence. |
| Outputs | A faithful, plain-language explanation of the Decision Assessment. |
| Evidence Requirements | Must reference the Decision Assessment and its underlying evidence; introduces no new evidence. |
| Confidence | Expressed using the Confidence Model defined in Section 7, inherited from the explained Decision Assessment. |
| Lifecycle | Follows the Assessment Lifecycle defined in Section 9. |
| Validation | Must satisfy the Validation Rules defined in Section 13; must never introduce meaning absent from the Decision Assessment it explains. |

---

# 5. Canonical Analysis Object

Every Analysis in the taxonomy above shares the following canonical structure.

| Attribute | Description |
|---|---|
| Identifier | A unique identifier for the Analysis instance. |
| Analysis Type | The taxonomy category the Analysis belongs to (Section 4). |
| Instrument | The Instrument the Analysis pertains to, where applicable, per the canonical Market Model in [18-market-model.md](18-market-model.md). |
| Market | The Market the Analysis pertains to, where applicable. |
| Time Window | The point or span of time the Analysis describes. |
| Evidence References | Pointers to the specific market data or upstream Assessments supporting the Analysis. |
| Confidence Level | The Confidence associated with the Analysis, per the Confidence Model in Section 7. |
| Supporting Observations | The individual Observations that compose the Analysis, per the Observation Model in Section 8. |
| Generated Timestamp | The point in time the Analysis was produced. |
| Engine | The owning engine that produced the Analysis. |
| Version | The version of the producing engine's analysis logic, for traceability. |
| Status | The current Assessment State, per Section 10. |
| Metadata | Supporting descriptive information relevant to interpreting the Analysis. |
| Validation Rules | The Analysis must satisfy the Validation Rules defined in Section 13 before being considered Valid. |

---

# 6. Evidence Model

| Concept | Description |
|---|---|
| Direct Evidence | Evidence drawn directly from canonical Market Model data (such as a Tick, Candle, or Order Book Snapshot). |
| Derived Evidence | Evidence drawn from another Assessment already produced by an Analysis Engine. |
| Supporting Evidence | Additional evidence that reinforces an Analysis without being strictly required for it to be valid. |
| Evidence References | The specific pointers within an Analysis that identify its Direct, Derived, and Supporting Evidence. |
| Evidence Completeness | The degree to which an Analysis's Evidence References fully account for the observations it makes. |
| Evidence Integrity | The property that referenced evidence has not been altered since the Analysis was produced. |
| Evidence Provenance | The traceable origin of a piece of evidence, back to the canonical Market Model or an upstream Assessment. |

---

# 7. Confidence Model

| Concept | Description |
|---|---|
| Confidence Levels | A qualitative scale (for example, Low, Moderate, High) indicating how strongly available evidence supports an Analysis. |
| Confidence Meaning | Confidence describes the strength of the evidence behind an observation; it never describes the likelihood of a future market outcome. |
| Confidence Boundaries | Confidence is always bounded to a defined, qualitative set of levels; it is never expressed as an unbounded or precise numerical score. |
| Unknown Confidence | A state indicating that insufficient information exists to assign a Confidence Level. |
| Unsupported Confidence | A state indicating that an Analysis's claimed Confidence Level cannot be reconciled with its Evidence References, and which must be rejected under the Validation Rules in Section 13. |
| Confidence Governance | Every Confidence Level assigned to an Analysis must be traceable to the specific evidence and observations that justify it. |

Numerical scoring methodologies are outside the scope of this specification.

---

# 8. Observation Model

| Concept | Description |
|---|---|
| Observation | A single, discrete statement about something that has been observed in the market, grounded directly in evidence. |
| Finding | A grouping of related Observations that together describe a coherent pattern or condition. |
| Assessment | A complete Analysis instance, composed of one or more Findings, evidence, and a Confidence Level, per Section 5. |
| Conclusion | The overall statement an Assessment makes once its Findings and evidence have been considered together. |

An Observation is the smallest unit of evidence-backed fact; a Finding groups Observations; an Assessment is the published, canonical unit of Analysis; a Conclusion is the top-level statement the Assessment communicates. A Conclusion is never a trading instruction.

---

# 9. Assessment Lifecycle

| Stage | Description |
|---|---|
| Created | The owning engine has produced an Analysis instance but has not yet confirmed it satisfies all Validation Rules. |
| Validated | The Analysis has been confirmed to satisfy all Validation Rules defined in Section 13. |
| Published | The validated Analysis has been made available to downstream consumers and is now immutable. |
| Superseded | A newer Analysis of the same type, for the same Instrument or Market and a later Time Window, has since been published. |
| Archived | The Analysis is retained for historical reference but is no longer the subject of active downstream consumption. |

---

# 10. Assessment States

| State | Description |
|---|---|
| Draft | The Analysis has been created but not yet validated. |
| Valid | The Analysis has satisfied all Validation Rules. |
| Invalid | The Analysis has failed one or more Validation Rules and cannot be published. |
| Published | The Analysis has been made available to downstream consumers and is immutable. |
| Deprecated | The Analysis remains published but has been superseded and should no longer inform new decisions. |
| Archived | The Analysis is retained for historical or audit purposes only. |

---

# 11. Evidence Traceability

Every Analysis must preserve an unbroken chain of traceability:

- A Liquidity, Options, Momentum, or Context Assessment traces back to Direct Evidence in the canonical Market Model.
- A Contradiction Assessment traces back to the specific Liquidity, Options, Momentum, and Context Assessments it compares.
- A Decision Assessment traces back to the specific upstream Assessments and Contradiction Assessment it synthesizes.
- An Explanation traces back to the single Decision Assessment it describes, and transitively to every Assessment and evidence that Decision Assessment references.

This traceability chain must remain intact and inspectable at every stage, consistent with the "Explain Everything" principle defined in [01-product.md](01-product.md).

---

# 12. Cross-Engine Consistency

- Every Analysis Engine produces Assessments conforming to the same Canonical Analysis Object structure defined in Section 5.
- No Analysis Engine may reference the internal reasoning of another engine; it may only reference another engine's already-published Assessment.
- The Contradiction Engine relies on all upstream Analysis Engines expressing Confidence and Evidence References in the same canonical form, enabling meaningful comparison.
- The Decision Engine relies on the Contradiction Engine's output being expressed in the same canonical form as the Assessments it evaluates.

---

# 13. Validation Rules

| Rule | Description |
|---|---|
| Evidence Required | Every Analysis must carry at least one Evidence Reference. |
| Confidence Required | Every Analysis must carry a Confidence Level, which may be Unknown but not absent. |
| Immutable After Publication | An Analysis in the Published state is never modified. |
| Valid References | Every Evidence Reference and upstream Assessment reference must resolve to a concept that actually exists. |
| Chronological Consistency | An Analysis's Generated Timestamp must be consistent with the Time Window and evidence it references. |
| Engine Ownership | Every Analysis must be attributable to exactly one owning engine, per the taxonomy in Section 4. |
| Single Identity | Every Analysis must carry a unique Identifier that does not change over its lifecycle. |

---

# 14. Relationships

| From | To | Relationship |
|---|---|---|
| Assessment | Evidence | Every Assessment references one or more pieces of Evidence. |
| Assessment | Instrument | An Assessment is associated with the Instrument it pertains to, where applicable. |
| Assessment | Market | An Assessment is associated with the Market it pertains to, where applicable. |
| Assessment | Explanation | A Decision Assessment is described by exactly one Explanation. |
| Assessment | Decision | Liquidity, Options, Momentum, Context, and Contradiction Assessments are referenced by zero or more Decision Assessments. |
| Decision | Contradiction | A Decision Assessment references the Contradiction Assessment relevant to its synthesis. |
| Contradiction | Other Assessments | A Contradiction Assessment references two or more Liquidity, Options, Momentum, or Context Assessments. |

---

# 15. Domain Constraints

- No trading recommendations may appear in any Analysis.
- Evidence is mandatory for every Analysis.
- Historical Analysis instances are immutable once published.
- Explainability is mandatory: every Analysis must be traceable to its supporting evidence.
- Cross-engine independence is preserved: no Analysis Engine analyzes or depends on another engine's internal reasoning.

---

# 16. Governance

This Analysis Model is owned by MIOS Architecture and serves as the single source of truth for the canonical structure of every Analysis produced across the platform.

Any engine requiring a new Analysis category must propose it as an addition to the taxonomy in Section 4 before it is used elsewhere.

Changes to the Canonical Analysis Object, Evidence Model, Confidence Model, or Assessment Lifecycle require an approved Architecture Decision Record (ADR).

Any future algorithm, API, or event contract derived from this model must remain compatible with the canonical definitions in this document; where a conflict arises, this document takes precedence.

---

# 17. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Canonical
- [ ] Technology Independent
- [ ] Ready for Technical Design

---

# 18. ADR-001

**Decision:**
MIOS adopts a canonical analysis model as the definitive representation of every Assessment and Explanation produced across the platform.

**Reason:**
A single canonical analysis model ensures that every Analysis Engine, the Contradiction Engine, the Decision Engine, and the AI Explanation Engine produce and consume intelligence in the same structural form, consistent with the single source of truth and explainability principles defined in [02-architecture.md](02-architecture.md) and [01-product.md](01-product.md). Without a canonical model, engines could express evidence and confidence inconsistently, undermining the Contradiction Engine's ability to meaningfully compare their outputs and the Decision Engine's ability to synthesize them.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Allow each engine to define its own analysis output structure | Would risk inconsistent representation of evidence and confidence across engines, undermining the Contradiction Engine's ability to compare Assessments meaningfully. |
| Combine evidence and confidence handling directly into the Domain Model | Would conflate the general-purpose domain concepts defined in [17-domain-model.md](17-domain-model.md) with the analysis-specific structures needed by the engines, reducing clarity for both. |
| Represent confidence as a precise numerical score | Would imply a level of predictive precision inconsistent with the "This is NOT a prediction system" principle defined in [01-product.md](01-product.md), and risk misrepresenting evidence strength as statistical certainty. |

**Consequences:**

- Every Analysis Engine, the Contradiction Engine, the Decision Engine, and the AI Explanation Engine must produce output conforming to the Canonical Analysis Object defined in Section 5.
- Any new type of Analysis must first be added to the taxonomy in Section 4.
- Future algorithm, API, and event contract designs must preserve the Evidence Model, Confidence Model, and traceability guarantees defined in this document.

---

# 19. Dependencies

This Analysis Model Specification depends on:

- 17-domain-model.md
- 18-market-model.md

This document is referenced by:

- 07-price-engine.md
- 08-liquidity-engine.md
- 09-options-engine.md
- 10-momentum-engine.md
- 11-context-engine.md
- 12-contradiction-engine.md
- 13-decision-engine.md
- 14-ai-explanation-engine.md
- Every subsequent Technical Design document defining algorithms, APIs, or event contracts.

---

# 20. Glossary

| Term | Meaning |
|------|---------|
| Analysis | The general term for any Assessment or Explanation produced by an engine within the taxonomy defined in Section 4. |
| Assessment | A complete, evidence-backed Analysis instance produced by an Analysis, Contradiction, or Decision Engine. |
| Explanation | A human-readable narrative describing a Decision Assessment, produced by the AI Explanation Engine. |
| Evidence Reference | A pointer from an Analysis to the specific market data or upstream Assessment supporting it. |
| Confidence Level | A qualitative indication of how strongly evidence supports an Analysis. |
| Observation | A single, discrete, evidence-backed statement about the market. |
| Finding | A grouping of related Observations describing a coherent pattern or condition. |
| Conclusion | The overall statement an Assessment communicates once its Findings and evidence are considered together. |
| Traceability | The property of an Analysis being consistently linked back to the evidence and upstream Assessments that produced it. |

---

# 21. Analysis Model Freeze

This Analysis Model becomes the authoritative canonical representation of every Analysis produced by MIOS after approval.

All Analysis Engines, the Contradiction Engine, the Decision Engine, and the AI Explanation Engine shall conform to the Canonical Analysis Object, Evidence Model, Confidence Model, and lifecycle defined here.

Changes to this model require an approved Architecture Decision Record (ADR).

---

# 22. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Analysis Model Specification for MIOS. |
