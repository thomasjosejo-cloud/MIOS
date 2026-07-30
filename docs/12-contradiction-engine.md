---
id: CONTRADICTION-001
title: MIOS Contradiction Engine Specification
document: 12-contradiction-engine.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Contradiction Engine is responsible for evaluating relationships between intelligence produced by independent Analysis Engines. It is the first orchestration component in the architecture defined in [02-architecture.md](02-architecture.md), positioned after the Analysis Engines and before the Decision Engine.

The Contradiction Engine consumes intelligence events from the Price Engine, Liquidity Engine, Options Engine, Momentum Engine, and Context Engine. It never performs domain analysis itself; it does not analyse price, liquidity, options, momentum, or context directly.

The Contradiction Engine identifies agreement, contradiction, uncertainty, and missing evidence across the intelligence it receives, and produces structured contradiction intelligence describing these relationships. It never recommends trades and never produces buy/sell/hold decisions.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Collect Engine Intelligence | Receive intelligence events published by the Price, Liquidity, Options, Momentum, and Context Engines. |
| Compare Independent Observations | Compare observations produced independently by different Analysis Engines. |
| Identify Agreements | Identify where multiple engines' observations are consistent with one another. |
| Identify Contradictions | Identify where multiple engines' observations conflict with one another. |
| Identify Missing Evidence | Identify where expected supporting evidence is absent or incomplete. |
| Identify Ambiguity | Identify where the relationship between engine observations is unclear or inconclusive. |
| Generate Contradiction Intelligence | Produce structured, evidence-backed intelligence describing the relationships found among engine outputs. |
| Publish Contradiction Events | Publish generated contradiction intelligence as events on the Event Bus, per [06-event-bus.md](06-event-bus.md). |
| Maintain Explainability | Ensure every relationship identified can be explained in terms of the specific engine observations involved. |
| Provide Supporting Evidence | Attach the specific engine observations that support each identified relationship. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No Price Analysis | The Contradiction Engine does not analyse price structure, trend, or swing behaviour; that is the responsibility of the Price Engine. |
| No Liquidity Analysis | The Contradiction Engine does not analyse volume or liquidity conditions; that is the responsibility of the Liquidity Engine. |
| No Options Analysis | The Contradiction Engine does not analyse options positioning data; that is the responsibility of the Options Engine. |
| No Momentum Analysis | The Contradiction Engine does not analyse the rate or quality of price movement; that is the responsibility of the Momentum Engine. |
| No Context Analysis | The Contradiction Engine does not analyse the broader market environment; that is the responsibility of the Context Engine. |
| No Decision Making | The Contradiction Engine does not synthesize a final decision-support view; that is the responsibility of the Decision Engine. |
| No Trade Recommendations | The Contradiction Engine never recommends a specific trade or action. |
| No AI Explanation | The Contradiction Engine does not translate intelligence into plain-language explanation; that is the responsibility of the AI Explanation Engine. |
| No Order Execution | The Contradiction Engine has no role in trade execution or order routing of any kind. |
| No External Connectivity | The Contradiction Engine does not communicate with external market data providers. |

---

# 4. Inputs

The Contradiction Engine consumes only intelligence already produced by independent engines. Its inputs include:

- Price Intelligence
- Liquidity Intelligence
- Options Intelligence
- Momentum Intelligence
- Context Intelligence
- Market Store Context
- Event Bus Events

---

# 5. Outputs

The Contradiction Engine produces the following conceptual categories of output. This section describes categories only; it does not define payloads.

- Contradiction Intelligence
- Agreement Events
- Conflict Events
- Evidence Gap Events
- Confidence Information
- Supporting Evidence
- Health Information

---

# 6. Scope of Analysis

The Contradiction Engine's scope covers:

- Agreement Detection
- Conflict Detection
- Evidence Consistency
- Evidence Completeness
- Cross Engine Relationships
- Cross Engine Alignment
- Cross Engine Ambiguity
- Cross Engine Confidence

The Contradiction Engine evaluates relationships between intelligence already produced by the Analysis Engines. It never generates new market intelligence itself.

---

# 7. Evidence Philosophy

Every contradiction must be explainable.

Every agreement must be explainable.

Every conclusion must reference supporting observations.

No hidden reasoning.

No black-box conclusions.

Every result must be reproducible.

---

# 8. Intelligence Principles

| Principle | Description |
|---|---|
| Deterministic | Given the same set of engine intelligence, the Contradiction Engine produces the same relationships. |
| Evidence Based | Every identified relationship is grounded in the specific observations it compares. |
| Explainable | Every relationship can be explained in terms of the engine outputs that produced it. |
| Transparent | The reasoning behind every agreement, contradiction, or gap is visible rather than hidden. |
| Reproducible | A relationship can be independently verified by examining the same underlying engine intelligence. |
| Engine Independent | The Contradiction Engine does not favour or depend on the internal logic of any single Analysis Engine. |
| State Aware | Analysis takes into account relevant current and historical market state held in the Market Store. |

---

# 9. Engine Lifecycle

| Stage | Description |
|---|---|
| Receive Intelligence | The Contradiction Engine receives intelligence events from the Analysis Engines via the Event Bus. |
| Retrieve Context | The Contradiction Engine retrieves any additional relevant market state from the Market Store needed to evaluate relationships. |
| Compare | The Contradiction Engine compares the observations received from independent Analysis Engines. |
| Evaluate | The Contradiction Engine evaluates the compared observations for agreement, contradiction, ambiguity, or missing evidence. |
| Generate Contradiction Intelligence | The Contradiction Engine produces structured, evidence-backed contradiction intelligence. |
| Validate | The Contradiction Engine confirms that generated intelligence conforms to its evidence and explainability principles before publication. |
| Publish | The Contradiction Engine publishes the generated intelligence as an event on the Event Bus. |
| Wait | The Contradiction Engine returns to an idle state until the next relevant intelligence is received. |

---

# 10. Reliability Requirements

| Requirement | Description |
|---|---|
| Deterministic Processing | The same set of engine intelligence always produces the same contradiction intelligence. |
| Repeatable Results | Reprocessing the same historical engine intelligence produces the same relationships. |
| Fault Isolation | A failure within the Contradiction Engine does not affect the operation of the Analysis Engines. |
| Transparent Failures | Failures within the Contradiction Engine are surfaced clearly rather than silently absorbed, consistent with [02-architecture.md](02-architecture.md). |
| Independent Operation | The Contradiction Engine operates without depending on the internal logic of any single Analysis Engine. |
| Recovery | The Contradiction Engine resumes normal operation following a disruption without requiring manual reconstruction of missed evaluation. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| No Predictions | The Contradiction Engine does not forecast future market behaviour. |
| No Trade Signals | The Contradiction Engine does not produce buy/sell/hold signals. |
| No Decision Making | The Contradiction Engine does not synthesize a final decision-support view. |
| No Market Analysis | The Contradiction Engine does not perform its own analysis of price, liquidity, options, momentum, or context. |
| No External Calls | The Contradiction Engine does not communicate with external systems or data providers. |
| No AI | The Contradiction Engine does not apply machine learning or generative explanation logic. |
| No Self Learning | The Contradiction Engine's evaluation logic does not adapt itself based on past outcomes. |
| No Market Orders | The Contradiction Engine has no role in trade execution or order placement. |

---

# 12. Contradiction Engine Governance

The Contradiction Engine evaluates relationships between intelligence.

It never replaces the Analysis Engines.

It never modifies intelligence produced by another engine.

It never produces market analysis.

It never produces trading decisions.

Its responsibility ends after publishing contradiction intelligence.

Decision synthesis belongs exclusively to the Decision Engine.

---

# 13. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Deterministic
- [ ] Evidence Based
- [ ] Explainable
- [ ] Architecture Compliant
- [ ] Ready for implementation

---

# 14. ADR-001

**Decision:**
Contradiction analysis shall be isolated into an independent orchestration engine.

**Reason:**
Isolating the comparison of cross-engine intelligence into its own component preserves the single responsibility and module independence principles defined in [02-architecture.md](02-architecture.md). It ensures that agreement, conflict, and evidence gaps between Analysis Engines are surfaced honestly and explicitly, rather than silently absorbed or hidden inside another component's logic, which is essential to the "No Black Box Decisions" principle defined in [01-product.md](01-product.md).

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Embed contradiction detection into each Analysis Engine | Would require every engine to be aware of every other engine's output, violating the Module Independence requirements in [02-architecture.md](02-architecture.md) and duplicating comparison logic across engines. |
| Perform contradiction detection in the Decision Engine | Would conflate the responsibility of identifying relationships between intelligence with the responsibility of synthesizing a final decision-support view, violating single responsibility and obscuring how disagreement was handled in the final synthesis. |
| Dashboard comparison | Would place analytical responsibility inside the Presentation Layer, violating the architecture's separation of analysis and presentation defined in [02-architecture.md](02-architecture.md). |

**Consequences:**

- The Decision Engine can rely on receiving already-evaluated agreement and conflict information rather than performing its own comparison.
- Any change to how relationships between engine outputs are evaluated is scoped entirely to the Contradiction Engine.
- New Analysis Engines can be added without requiring changes to existing engines, since the Contradiction Engine is the single point where their outputs are compared.

---

# 15. Document Dependencies

This Contradiction Engine Specification depends on:

- 01-product.md
- 02-architecture.md
- 05-market-store.md
- 06-event-bus.md
- 07-price-engine.md
- 08-liquidity-engine.md
- 09-options-engine.md
- 10-momentum-engine.md
- 11-context-engine.md

This document is referenced by:

- 13-decision-engine.md
- 14-ai-explanation-engine.md
- 15-api-specification.md
- 16-frontend.md

---

# 16. Glossary

| Term | Meaning |
|------|---------|
| Contradiction Intelligence | Structured, evidence-backed intelligence describing relationships between the outputs of independent Analysis Engines. |
| Agreement | A relationship in which multiple engines' observations are consistent with one another. |
| Contradiction | A relationship in which multiple engines' observations conflict with one another. |
| Ambiguity | A relationship in which the alignment between engine observations is unclear or inconclusive. |
| Evidence Gap | A condition in which expected supporting evidence is absent or incomplete. |
| Confidence | An indication of how strongly available evidence supports an identified relationship. |
| Observation | A statement produced by an Analysis Engine describing something that has occurred. |
| Cross Engine Intelligence | Intelligence derived from comparing the outputs of more than one Analysis Engine. |
| Explainability | The property of a relationship being traceable to the specific engine observations that produced it. |

---

# 17. Contradiction Engine Freeze

This specification becomes authoritative after approval.

The Contradiction Engine shall remain an orchestration engine.

It shall never become an Analysis Engine.

Its responsibilities may not expand into decision making.

Any change requires an approved Architecture Decision Record (ADR).

---

# 18. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Contradiction Engine Specification for MIOS. |
