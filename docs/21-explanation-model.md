---
id: EXPLANATION-MODEL-001
title: MIOS Explanation Model Specification
document: 21-explanation-model.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the canonical representation of every Explanation produced by the AI Explanation Engine, defined in [14-ai-explanation-engine.md](14-ai-explanation-engine.md). It builds upon the Intelligence Domain aggregates introduced in [17-domain-model.md](17-domain-model.md), the canonical Market Model defined in [18-market-model.md](18-market-model.md), the canonical Analysis Model defined in [19-analysis-model.md](19-analysis-model.md), and the canonical Decision Model defined in [20-decision-model.md](20-decision-model.md).

Every Explanation originates from exactly one Decision. Explanations exist to improve human understanding of an already-produced Decision without modifying its meaning.

This document becomes the single source of truth for every explanation generated within MIOS. It does not define prompts, LLM implementations, APIs, events, persistence, or implementation classes. It remains entirely at the canonical model level.

---

# 2. Scope

This document covers the canonical representation of:

- Decision Explanations
- Evidence Explanations
- Confidence Explanations
- Contradiction Explanations
- Context Explanations
- Summary Explanations
- Traceability
- Explainability

---

# 3. Design Principles

| Principle | Description |
|---|---|
| Faithfulness | An Explanation accurately represents the meaning of the Decision it describes, without distortion. |
| No Hallucination | An Explanation never introduces reasoning, evidence, or conclusions absent from the Decision it describes. |
| Evidence First | Every statement in an Explanation traces back to the evidence referenced by the underlying Decision. |
| Deterministic Meaning | The same Decision produces an Explanation with the same meaning every time it is explained. |
| Human Readability | An Explanation is expressed in language understandable to the trader, without sacrificing accuracy. |
| Complete Traceability | An Explanation preserves the full evidence chain back to the Decision, its Supporting Assessments, and their evidence. |
| No Hidden Reasoning | Every claim in an Explanation is visible and attributable to a specific part of the Decision it describes. |
| No New Facts | An Explanation never asserts a fact about the market that is not already present in the Decision it describes. |
| Technology Independence | The canonical Explanation structure is independent of any specific generation technology or method. |
| Canonical Consistency | Every Explanation conforms to the same canonical structure, regardless of which Decision it describes. |

---

# 4. Explanation Philosophy

- Explanation ≠ Prediction. An Explanation never forecasts future market behaviour.
- Explanation ≠ Recommendation. An Explanation never advises the trader to take a specific action.
- Explanation ≠ Advice. An Explanation never offers personalized guidance.
- Explanation ≠ New Analysis. An Explanation never introduces market observations beyond those already present in the Decision it describes.
- Explanation = Human-readable interpretation of an existing Decision.

Explanations communicate meaning but never alter meaning. An Explanation is a faithful translation layer over an already-produced, evidence-backed Decision, consistent with the "Explain Everything" and "No Black Box Decisions" principles defined in [01-product.md](01-product.md).

---

# 5. Canonical Explanation Object

| Attribute | Description |
|---|---|
| Explanation Identifier | A unique identifier for the Explanation instance. |
| Decision Identifier | A reference to the single Decision this Explanation describes, per [20-decision-model.md](20-decision-model.md). |
| Instrument | The Instrument the Explanation pertains to, inherited from the referenced Decision. |
| Market | The Market the Explanation pertains to, inherited from the referenced Decision. |
| Time Window | The Time Window described by the referenced Decision. |
| Evidence References | Pointers to the evidence referenced by the underlying Decision and its Supporting Assessments. |
| Referenced Assessments | The Supporting Assessments and Contradiction Assessment referenced by the underlying Decision. |
| Confidence | The Confidence inherited from the underlying Decision, per Section 9. |
| Narrative | The structured, human-readable body of the Explanation, per Section 6. |
| Summary | A concise restatement of the Decision's Summary in plain language. |
| Generated Timestamp | The point in time the Explanation was produced. |
| Engine Version | The version of the AI Explanation Engine's generation logic, for traceability. |
| Language | The language in which the Explanation is expressed. |
| Status | The current Explanation State, per Section 11. |
| Metadata | Supporting descriptive information relevant to interpreting the Explanation. |
| Validation Rules | The Explanation must satisfy the Validation Rules defined in Section 13 before being considered Valid. |

---

# 6. Explanation Structure

| Component | Role |
|---|---|
| Executive Summary | States, in the fewest words possible, what the underlying Decision communicates. |
| Supporting Evidence | Describes the specific evidence that supports the Decision, in plain language. |
| Contradictions | Describes any agreement, conflict, or ambiguity identified by the Contradiction Assessment referenced by the Decision. |
| Context | Describes the relevant Decision Context surrounding the Decision, per [20-decision-model.md](20-decision-model.md). |
| Confidence Statement | Describes, in plain language, the Confidence Level associated with the Decision and why it was assigned. |
| Decision Summary | Restates the Decision's Summary in accessible language, without adding or removing meaning. |
| Limitations | Describes any Missing Evidence or Evidence Completeness gaps identified in the underlying Decision. |
| Closing Statement | Reaffirms that the Explanation is descriptive, not prescriptive, and that the trader retains full decision-making authority. |

---

# 7. Explanation Context

| Context Element | Description |
|---|---|
| Market Context | The relevant Context Assessment content described in plain language. |
| Session Context | The Trading Session during which the underlying Decision was generated. |
| Liquidity Context | The relevant Liquidity Assessment content described in plain language. |
| Momentum Context | The relevant Momentum Assessment content described in plain language. |
| Options Context | The relevant Options Assessment content described in plain language. |
| Contradiction Context | The relevant Contradiction Assessment content described in plain language. |
| Temporal Context | The Time Window of the Decision and its relationship to recent prior Decisions. |
| Historical Context | Relevant historical Assessments referenced by the underlying Decision's Context. |

---

# 8. Evidence Mapping

| Link | Description |
|---|---|
| Decision → Assessments | The Explanation preserves the Decision's references to its Supporting Assessments. |
| Assessments → Evidence | The Explanation preserves each Supporting Assessment's references to its underlying evidence, per [19-analysis-model.md](19-analysis-model.md). |
| Evidence → Market Facts | The Explanation preserves the evidence's ultimate origin in canonical Market Model data, per [18-market-model.md](18-market-model.md). |
| Explanation → Entire Evidence Chain | The Explanation itself references the full chain from Decision through Assessments to underlying evidence. |
| Evidence Completeness | The Explanation reflects the same Evidence Completeness assessment already present in the underlying Decision. |
| Evidence Integrity | The Explanation does not alter or reinterpret the referenced evidence. |
| Evidence Provenance | The Explanation preserves the traceable origin of every piece of evidence it describes. |

---

# 9. Explanation Fidelity

An Explanation must satisfy the following fidelity requirements:

- No invented information.
- No omitted critical evidence.
- No altered confidence.
- No altered contradiction.
- No altered conclusion.
- No unsupported wording.
- Semantic equivalence with the underlying Decision: the Explanation's meaning, once translated back into structured terms, matches the Decision it describes.

---

# 10. Explanation Lifecycle

| Stage | Description |
|---|---|
| Created | The AI Explanation Engine has produced an Explanation instance but has not yet confirmed it satisfies all Validation Rules. |
| Validated | The Explanation has been confirmed to satisfy all Validation Rules defined in Section 13. |
| Published | The validated Explanation has been made available to downstream consumers and is now immutable. |
| Superseded | A newer Explanation describing a subsequent Decision for the same Instrument or Market has since been published. |
| Archived | The Explanation is retained for historical reference but is no longer the subject of active downstream consumption. |

---

# 11. Explanation States

| State | Description |
|---|---|
| Draft | The Explanation has been created but not yet validated. |
| Valid | The Explanation has satisfied all Validation Rules. |
| Published | The Explanation has been made available to downstream consumers and is immutable. |
| Deprecated | The Explanation remains published but describes a Decision that has since been superseded. |
| Archived | The Explanation is retained for historical or audit purposes only. |

---

# 12. Explainability Rules

Every statement must trace to evidence.

Every conclusion must trace to the Decision.

Every confidence statement must trace to Decision Confidence.

Every contradiction statement must trace to the Contradiction Assessment.

No hidden reasoning.

---

# 13. Validation Rules

| Rule | Description |
|---|---|
| Decision Required | Every Explanation must reference exactly one Decision. |
| Evidence Required | Every Explanation must carry Evidence References consistent with its referenced Decision. |
| Traceability Complete | Every statement in the Explanation's Narrative must be traceable to the Decision, its Supporting Assessments, or their evidence. |
| Narrative Consistent | The Explanation's Narrative and Summary must not contradict one another. |
| Confidence Consistent | The Explanation's Confidence Statement must match the Confidence Level of the referenced Decision. |
| Immutable After Publication | An Explanation in the Published state is never modified. |
| Unique Identity | Every Explanation must carry a unique Explanation Identifier that does not change over its lifecycle. |
| Chronological Validity | An Explanation's Generated Timestamp must be later than that of the Decision it describes. |

---

# 14. Relationships

| From | To | Relationship |
|---|---|---|
| Explanation | Decision | An Explanation references exactly one Decision. |
| Explanation | Assessments | An Explanation references the Supporting Assessments and Contradiction Assessment referenced by its Decision. |
| Explanation | Evidence | An Explanation references the evidence referenced by its Decision and Supporting Assessments. |
| Explanation | Market | An Explanation is associated with the Market of its referenced Decision. |
| Explanation | Instrument | An Explanation is associated with the Instrument of its referenced Decision, where applicable. |

---

# 15. Domain Constraints

- No Buy instruction may appear in any Explanation.
- No Sell instruction may appear in any Explanation.
- No Hold instruction may appear in any Explanation.
- No prediction of future market direction may appear in any Explanation.
- No advice may appear in any Explanation.
- No hallucinated content may appear in any Explanation.
- Evidence is mandatory for every Explanation.
- Historical Explanation instances are immutable once published.

---

# 16. Governance

This Explanation Model is owned by MIOS Architecture and serves as the single source of truth for the canonical structure of every Explanation produced by the AI Explanation Engine.

Any proposed change to the Canonical Explanation Object, Explanation Structure, or Explanation Fidelity requirements requires an approved Architecture Decision Record (ADR).

Any future generation method, API, or event contract derived from this model must remain compatible with the canonical definitions in this document; where a conflict arises, this document takes precedence.

No revision to this model may weaken the fidelity requirements defined in Section 9.

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
MIOS adopts a canonical explanation model ensuring faithful, evidence-backed human-readable explanations.

**Reason:**
A canonical explanation model ensures that every Explanation produced by the AI Explanation Engine remains a strictly faithful translation of an already-produced Decision, consistent with the "Explain Everything" and "No Black Box Decisions" principles defined in [01-product.md](01-product.md). Defining fidelity, structure, and traceability requirements at the canonical level guarantees that no future generation method can introduce hallucinated content, hidden reasoning, or instruction content into an Explanation.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Allow explanations to be generated ad hoc without a canonical structure | Would risk inconsistent fidelity and traceability across explanations, making it difficult to guarantee that every Explanation remains faithful to its Decision. |
| Allow the AI Explanation Engine to introduce supplementary market commentary beyond the Decision | Would violate the "No New Facts" principle in Section 3 and risk the Explanation Engine effectively performing its own analysis, contradicting [14-ai-explanation-engine.md](14-ai-explanation-engine.md). |
| Express Explanation confidence independently of Decision Confidence | Would risk the Explanation misrepresenting the underlying Decision's evidence strength, undermining explanation fidelity. |

**Consequences:**

- The AI Explanation Engine must produce output conforming to the Canonical Explanation Object defined in Section 5.
- Any future generation method must preserve the fidelity requirements defined in Section 9.
- The Frontend and any future API or event contract exposing explanations must preserve the full traceability chain defined in Section 8.

---

# 19. Dependencies

This Explanation Model Specification depends on:

- 17-domain-model.md
- 18-market-model.md
- 19-analysis-model.md
- 20-decision-model.md

This document is referenced by:

- AI Explanation Engine
- OpenAPI
- Event Contracts
- Frontend
- Algorithms

---

# 20. Glossary

| Term | Meaning |
|------|---------|
| Explanation | The canonical, faithful human-readable translation of a Decision produced by the AI Explanation Engine. |
| Narrative | The structured, human-readable body of an Explanation. |
| Fidelity | The property of an Explanation accurately representing its underlying Decision without distortion, omission, or invention. |
| Semantic Equivalence | The property of an Explanation's meaning matching its underlying Decision when translated back into structured terms. |
| Evidence Mapping | The preserved chain of references from an Explanation back through the Decision, its Assessments, and their evidence. |
| Traceability | The property of an Explanation being consistently linked back to the Decision and evidence it describes. |
| Explainability | The property of an Explanation being fully describable in terms of the Decision and evidence that produced it. |
| Hallucination | The introduction of information, reasoning, or conclusions absent from the underlying Decision; strictly prohibited. |

---

# 21. Explanation Model Freeze

This Explanation Model becomes the authoritative canonical representation of every Explanation produced by MIOS after approval.

The AI Explanation Engine shall conform to the Canonical Explanation Object, Explanation Structure, and Explanation Fidelity requirements defined here.

No revision to this model may weaken its fidelity, traceability, or explainability requirements.

Changes to this model require an approved Architecture Decision Record (ADR).

---

# 22. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Explanation Model Specification for MIOS. |
