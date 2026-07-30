---
id: AIEXPLAIN-001
title: MIOS AI Explanation Engine Specification
document: 14-ai-explanation-engine.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The AI Explanation Engine is the presentation intelligence layer of MIOS, positioned after the Decision Engine and before the Dashboard in the architecture defined in [02-architecture.md](02-architecture.md).

It consumes Decision Intelligence, Supporting Evidence, Confidence Information, and Decision Metadata. It converts this structured intelligence into understandable human explanations.

The AI Explanation Engine never performs analysis. It never performs synthesis. It never modifies upstream intelligence. Every explanation it produces must remain faithful to the originating evidence.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Receive Decision Intelligence | Receive the synthesized decision-support assessment published by the Decision Engine. |
| Interpret Structured Intelligence | Interpret the structured intelligence it receives in order to produce a faithful explanation. |
| Generate Human Readable Explanation | Produce a plain-language explanation of the received intelligence. |
| Preserve Explainability | Ensure every explanation remains consistent with the meaning of the intelligence it explains. |
| Preserve Traceability | Ensure every explanation can be traced back to the specific upstream intelligence and evidence it is based on. |
| Reference Supporting Evidence | Attach references to the supporting evidence underlying each explanation. |
| Publish Explanation Events | Publish generated explanations as events on the Event Bus, per [06-event-bus.md](06-event-bus.md). |
| Support Multiple Presentation Channels | Produce explanations suitable for use across different presentation contexts within MIOS. |
| Maintain Explanation Consistency | Ensure the same underlying intelligence is explained consistently whenever it recurs. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No Price Analysis | The AI Explanation Engine does not analyse price structure, trend, or swing behaviour; that is the responsibility of the Price Engine. |
| No Liquidity Analysis | The AI Explanation Engine does not analyse volume or liquidity conditions; that is the responsibility of the Liquidity Engine. |
| No Options Analysis | The AI Explanation Engine does not analyse options positioning data; that is the responsibility of the Options Engine. |
| No Momentum Analysis | The AI Explanation Engine does not analyse the rate or quality of price movement; that is the responsibility of the Momentum Engine. |
| No Context Analysis | The AI Explanation Engine does not analyse the broader market environment; that is the responsibility of the Context Engine. |
| No Contradiction Detection | The AI Explanation Engine does not compare or reconcile outputs from multiple Analysis Engines; that is the responsibility of the Contradiction Engine. |
| No Decision Synthesis | The AI Explanation Engine does not synthesize a decision-support assessment; that is the responsibility of the Decision Engine. |
| No Trade Execution | The AI Explanation Engine has no role in trade execution or order routing of any kind. |
| No Broker Connectivity | The AI Explanation Engine does not communicate with brokers or execution venues. |
| No Intelligence Modification | The AI Explanation Engine does not alter the meaning or content of the intelligence it explains. |
| No External Connectivity | The AI Explanation Engine does not communicate with external market data providers. |

---

# 4. Inputs

The AI Explanation Engine consumes only previously generated intelligence. Its inputs include:

- Decision Intelligence
- Supporting Evidence
- Confidence Information
- Decision Metadata
- Market Store Context
- Event Bus Events

---

# 5. Outputs

The AI Explanation Engine produces the following conceptual categories of output. This section describes categories only; it does not define payloads.

- Human Readable Explanation
- Summary Explanation
- Evidence References
- Confidence Explanation
- Decision Narrative
- Presentation Metadata
- Health Information

---

# 6. Scope of Responsibility

The AI Explanation Engine's scope covers:

- Explanation Generation
- Evidence Referencing
- Natural Language Presentation
- Decision Interpretation
- Confidence Interpretation
- Narrative Consistency
- Presentation Readiness

The AI Explanation Engine transforms intelligence into explanations only. It never creates new intelligence.

---

# 7. Explanation Philosophy

Every explanation must reference evidence.

Every explanation must preserve meaning.

No invented reasoning.

No hidden reasoning.

No hallucinated conclusions.

Every explanation must be reproducible.

---

# 8. Explanation Principles

| Principle | Description |
|---|---|
| Faithful | An explanation accurately represents the meaning of the intelligence it is based on, without distortion. |
| Deterministic | Given the same upstream intelligence, the AI Explanation Engine produces a consistent explanation. |
| Evidence Based | Every explanation is grounded in the supporting evidence attached to the upstream intelligence. |
| Transparent | The reasoning behind an explanation is visible and traceable, not hidden. |
| Explainable | Every explanation can itself be explained in terms of the upstream intelligence it describes. |
| Traceable | An explanation can always be traced back to the specific decision intelligence and evidence it is based on. |
| Presentation Independent | The explanation itself is independent of any specific presentation channel or format. |

---

# 9. Engine Lifecycle

| Stage | Description |
|---|---|
| Receive Intelligence | The AI Explanation Engine receives decision intelligence events from the Decision Engine via the Event Bus. |
| Retrieve Context | The AI Explanation Engine retrieves any additional relevant market state from the Market Store needed to produce a faithful explanation. |
| Interpret | The AI Explanation Engine interprets the received intelligence in preparation for explanation. |
| Generate Explanation | The AI Explanation Engine produces a human-readable explanation faithful to the interpreted intelligence. |
| Validate | The AI Explanation Engine confirms that the generated explanation remains faithful, evidence-based, and traceable before publication. |
| Publish | The AI Explanation Engine publishes the generated explanation as an event on the Event Bus. |
| Wait | The AI Explanation Engine returns to an idle state until the next relevant intelligence is received. |

---

# 10. Reliability Requirements

| Requirement | Description |
|---|---|
| Deterministic Processing | The same upstream intelligence produces a consistent explanation. |
| Repeatable Results | Reprocessing the same historical decision intelligence produces a consistent explanation. |
| Faithful Representation | The generated explanation accurately reflects the meaning of the upstream intelligence without distortion. |
| Transparent Failures | Failures within the AI Explanation Engine are surfaced clearly rather than silently absorbed, consistent with [02-architecture.md](02-architecture.md). |
| Independent Operation | The AI Explanation Engine operates without depending on the internal logic of any upstream engine beyond the intelligence it receives. |
| Recovery | The AI Explanation Engine resumes normal operation following a disruption without requiring manual reconstruction of missed explanations. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| No Market Analysis | The AI Explanation Engine does not perform its own analysis of price, liquidity, options, momentum, or context. |
| No Decision Making | The AI Explanation Engine does not synthesize a decision-support assessment. |
| No Contradiction Detection | The AI Explanation Engine does not compare or reconcile upstream intelligence outputs. |
| No Intelligence Modification | The AI Explanation Engine does not alter the content or meaning of the intelligence it explains. |
| No Hallucination | The AI Explanation Engine does not introduce reasoning, evidence, or conclusions not present in the upstream intelligence. |
| No External Calls | The AI Explanation Engine does not communicate with external systems or data providers. |
| No Self Learning | The AI Explanation Engine's explanation logic does not adapt itself based on past outcomes. |
| No Trade Execution | The AI Explanation Engine has no role in trade execution or order placement. |

---

# 12. AI Explanation Engine Governance

The AI Explanation Engine is responsible only for explanation.

It never replaces the Decision Engine.

It never replaces the Analysis Engines.

It never modifies intelligence.

It never changes evidence.

It never generates new conclusions.

Its responsibility ends after publishing explainable narratives.

---

# 13. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Deterministic
- [ ] Evidence Based
- [ ] Faithful
- [ ] Explainable
- [ ] Architecture Compliant
- [ ] Ready for implementation

---

# 14. ADR-001

**Decision:**
Human explanation shall be isolated into an independent presentation engine.

**Reason:**
Isolating the generation of human-readable explanations into its own component preserves the single responsibility and separation of analysis and presentation principles defined in [02-architecture.md](02-architecture.md). It ensures that explanation remains a faithful translation of already-produced, evidence-backed intelligence, rather than a source of new or altered reasoning, consistent with the "Explain Everything" and "No Black Box Decisions" principles defined in [01-product.md](01-product.md).

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Explanation inside Decision Engine | Would conflate the responsibility of synthesizing a decision-support assessment with the responsibility of explaining it in plain language, violating single responsibility and making it harder to audit each function independently. |
| Frontend-generated explanations | Would place interpretive responsibility inside the Presentation Layer, violating the architecture's separation of analysis and presentation defined in [02-architecture.md](02-architecture.md), and risk inconsistent explanations across presentation channels. |
| Analysis Engine explanations | Would require every Analysis Engine to independently produce human-readable explanations, duplicating explanation logic and risking inconsistency across engines. |

**Consequences:**

- The Dashboard can rely on receiving already-explained, human-readable intelligence rather than performing its own interpretation.
- Any change to how intelligence is explained in plain language is scoped entirely to the AI Explanation Engine.
- Explanations remain consistently faithful to the upstream evidence across every presentation channel.

---

# 15. Document Dependencies

This AI Explanation Engine Specification depends on:

- 01-product.md
- 02-architecture.md
- 06-event-bus.md
- 13-decision-engine.md

This document is referenced by:

- 15-api-specification.md
- 16-frontend.md

---

# 16. Glossary

| Term | Meaning |
|------|---------|
| Explanation | A human-readable description of already-produced intelligence, faithful to its underlying evidence. |
| Decision Narrative | A plain-language description of a synthesized decision-support assessment. |
| Supporting Evidence | The specific observable data referenced to justify an explanation. |
| Confidence Explanation | A plain-language description of how strongly available evidence supports an assessment. |
| Traceability | The ability to trace an explanation back to the intelligence and evidence it is based on. |
| Faithful Representation | An explanation that accurately reflects the meaning of the intelligence it describes, without distortion. |
| Presentation Metadata | Supporting information describing how and when an explanation was produced. |
| Human Readable Intelligence | Structured intelligence translated into a form understandable by the trader. |

---

# 17. AI Explanation Engine Freeze

This specification becomes authoritative after approval.

The AI Explanation Engine shall remain a presentation engine.

It shall never become an Analysis Engine.

It shall never become an Orchestration Engine.

Its responsibilities may not expand into market analysis, decision synthesis, or intelligence generation.

Any change requires an approved Architecture Decision Record (ADR).

---

# 18. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial AI Explanation Engine Specification for MIOS. |
