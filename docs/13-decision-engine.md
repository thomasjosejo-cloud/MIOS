---
id: DECISION-001
title: MIOS Decision Engine Specification
document: 13-decision-engine.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Decision Engine is the final orchestration engine within MIOS, positioned after the Contradiction Engine and before the AI Explanation Engine in the architecture defined in [02-architecture.md](02-architecture.md).

It consumes intelligence produced by the Price Engine, Liquidity Engine, Options Engine, Momentum Engine, Context Engine, and Contradiction Engine. It synthesizes those independent intelligence outputs into a single, structured decision-support assessment.

The Decision Engine never performs market analysis itself. It never detects contradictions. Every assessment it produces must remain deterministic, explainable, and evidence-backed. The Decision Engine never executes trades.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Collect Engine Intelligence | Receive intelligence events published by the Price, Liquidity, Options, Momentum, and Context Engines. |
| Collect Contradiction Intelligence | Receive agreement, conflict, and evidence-gap intelligence published by the Contradiction Engine. |
| Evaluate Overall Evidence | Assess the combined body of evidence provided by all upstream engines. |
| Synthesize Decision Support | Combine independently produced intelligence into a single, coherent decision-support assessment. |
| Generate Decision Intelligence | Produce structured, evidence-backed decision-support intelligence. |
| Maintain Explainability | Ensure every synthesized assessment can be explained in terms of the upstream intelligence that produced it. |
| Maintain Evidence Traceability | Preserve the ability to trace the synthesized assessment back to the specific engine outputs it was derived from. |
| Publish Decision Events | Publish generated decision intelligence as events on the Event Bus, per [06-event-bus.md](06-event-bus.md). |
| Provide Supporting Evidence | Attach the specific upstream intelligence that supports the synthesized assessment. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No Price Analysis | The Decision Engine does not analyse price structure, trend, or swing behaviour; that is the responsibility of the Price Engine. |
| No Liquidity Analysis | The Decision Engine does not analyse volume or liquidity conditions; that is the responsibility of the Liquidity Engine. |
| No Options Analysis | The Decision Engine does not analyse options positioning data; that is the responsibility of the Options Engine. |
| No Momentum Analysis | The Decision Engine does not analyse the rate or quality of price movement; that is the responsibility of the Momentum Engine. |
| No Context Analysis | The Decision Engine does not analyse the broader market environment; that is the responsibility of the Context Engine. |
| No Contradiction Detection | The Decision Engine does not compare or reconcile outputs from multiple Analysis Engines; that is the responsibility of the Contradiction Engine. |
| No Trade Execution | The Decision Engine does not place, modify, or cancel trades of any kind. |
| No Broker Connectivity | The Decision Engine does not communicate with brokers or execution venues. |
| No Portfolio Management | The Decision Engine has no role in managing positions or portfolios. |
| No Risk Management | The Decision Engine does not perform position sizing or risk management. |
| No AI Explanation | The Decision Engine does not translate intelligence into plain-language explanation; that is the responsibility of the AI Explanation Engine. |
| No External Connectivity | The Decision Engine does not communicate with external market data providers. |

---

# 4. Inputs

The Decision Engine consumes only previously generated intelligence. Its inputs include:

- Price Intelligence
- Liquidity Intelligence
- Options Intelligence
- Momentum Intelligence
- Context Intelligence
- Contradiction Intelligence
- Market Store Context
- Event Bus Events

---

# 5. Outputs

The Decision Engine produces the following conceptual categories of output. This section describes categories only; it does not define payloads.

- Decision Intelligence
- Decision Support Events
- Supporting Evidence
- Confidence Information
- Decision Metadata
- Health Information

---

# 6. Scope of Responsibility

The Decision Engine's scope covers:

- Evidence Synthesis
- Cross Engine Understanding
- Decision Consistency
- Evidence Traceability
- Decision Explainability
- Confidence Assessment
- Decision Completeness

The Decision Engine synthesizes existing intelligence only. It never creates new market intelligence.

---

# 7. Evidence Philosophy

Every decision-support assessment must be explainable.

Every conclusion must reference supporting intelligence.

Every contradiction must remain visible.

No hidden reasoning.

No black-box conclusions.

Every assessment must be reproducible.

---

# 8. Decision Principles

| Principle | Description |
|---|---|
| Deterministic | Given the same set of upstream intelligence, the Decision Engine produces the same decision-support assessment. |
| Evidence Based | Every synthesized assessment is grounded in the specific intelligence it combines. |
| Transparent | The reasoning behind every synthesized assessment is visible rather than hidden. |
| Explainable | Every assessment can be explained in terms of the upstream intelligence that produced it. |
| Reproducible | An assessment can be independently verified by examining the same underlying upstream intelligence. |
| Engine Independent | The Decision Engine does not favour or depend on the internal logic of any single upstream engine. |
| State Aware | Synthesis takes into account relevant current and historical market state held in the Market Store. |

---

# 9. Engine Lifecycle

| Stage | Description |
|---|---|
| Receive Intelligence | The Decision Engine receives intelligence events from the Analysis Engines and the Contradiction Engine via the Event Bus. |
| Retrieve Context | The Decision Engine retrieves any additional relevant market state from the Market Store needed to inform synthesis. |
| Evaluate Evidence | The Decision Engine assesses the combined body of evidence provided by all upstream intelligence. |
| Synthesize | The Decision Engine combines the evaluated evidence into a single, coherent decision-support assessment. |
| Generate Decision Intelligence | The Decision Engine produces structured, evidence-backed decision intelligence. |
| Validate | The Decision Engine confirms that generated intelligence conforms to its evidence and explainability principles before publication. |
| Publish | The Decision Engine publishes the generated intelligence as an event on the Event Bus. |
| Wait | The Decision Engine returns to an idle state until the next relevant intelligence is received. |

---

# 10. Reliability Requirements

| Requirement | Description |
|---|---|
| Deterministic Processing | The same set of upstream intelligence always produces the same decision-support assessment. |
| Repeatable Results | Reprocessing the same historical upstream intelligence produces the same assessment. |
| Fault Isolation | A failure within the Decision Engine does not affect the operation of the Analysis Engines or the Contradiction Engine. |
| Transparent Failures | Failures within the Decision Engine are surfaced clearly rather than silently absorbed, consistent with [02-architecture.md](02-architecture.md). |
| Independent Operation | The Decision Engine operates without depending on the internal logic of any single upstream engine. |
| Recovery | The Decision Engine resumes normal operation following a disruption without requiring manual reconstruction of missed synthesis. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| No Predictions Beyond Available Evidence | The Decision Engine does not extend its assessment beyond what the available upstream intelligence supports. |
| No Market Analysis | The Decision Engine does not perform its own analysis of price, liquidity, options, momentum, or context. |
| No Contradiction Detection | The Decision Engine does not independently compare or reconcile upstream intelligence outside of what the Contradiction Engine has already identified. |
| No Trade Signals | The Decision Engine does not produce buy/sell/hold signals. |
| No Trade Execution | The Decision Engine does not place, modify, or cancel trades. |
| No External Calls | The Decision Engine does not communicate with external systems or data providers. |
| No AI | The Decision Engine does not apply machine learning or generative explanation logic. |
| No Self Learning | The Decision Engine's synthesis logic does not adapt itself based on past outcomes. |

---

# 12. Decision Engine Governance

The Decision Engine is responsible only for decision-support synthesis.

It never replaces the Analysis Engines.

It never replaces the Contradiction Engine.

It never modifies intelligence produced by another engine.

It never executes trades.

It never communicates with brokers.

It never manages portfolios.

Its responsibility ends after publishing decision intelligence.

AI explanation belongs exclusively to the AI Explanation Engine.

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
Decision synthesis shall be isolated into a dedicated orchestration engine.

**Reason:**
Isolating the synthesis of upstream intelligence into its own component preserves the single responsibility and module independence principles defined in [02-architecture.md](02-architecture.md). It ensures that the final decision-support assessment is produced through one consistent, deterministic process, traceable back to the specific engine outputs and contradiction findings that informed it, consistent with the "No Black Box Decisions" and "Trader Makes Every Decision" principles defined in [01-product.md](01-product.md).

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Decision logic inside Analysis Engines | Would require each Analysis Engine to be aware of every other engine's output, violating the Module Independence requirements in [02-architecture.md](02-architecture.md) and duplicating synthesis logic across engines. |
| Decision logic inside Contradiction Engine | Would conflate the responsibility of identifying relationships between intelligence with the responsibility of synthesizing a final decision-support view, violating single responsibility and obscuring the distinction between comparison and synthesis. |
| Dashboard synthesis | Would place synthesis responsibility inside the Presentation Layer, violating the architecture's separation of analysis and presentation defined in [02-architecture.md](02-architecture.md). |

**Consequences:**

- The AI Explanation Engine can rely on receiving an already-synthesized decision-support assessment rather than performing its own synthesis.
- Any change to how upstream intelligence is synthesized is scoped entirely to the Decision Engine.
- The Decision Engine's output remains the single authoritative decision-support assessment consumed by the rest of the system.

---

# 15. Document Dependencies

This Decision Engine Specification depends on:

- 01-product.md
- 02-architecture.md
- 05-market-store.md
- 06-event-bus.md
- 07-price-engine.md
- 08-liquidity-engine.md
- 09-options-engine.md
- 10-momentum-engine.md
- 11-context-engine.md
- 12-contradiction-engine.md

This document is referenced by:

- 14-ai-explanation-engine.md
- 15-api-specification.md
- 16-frontend.md

---

# 16. Glossary

| Term | Meaning |
|------|---------|
| Decision Intelligence | Structured, evidence-backed decision-support intelligence synthesized from upstream engine outputs. |
| Decision Support | Information intended to help the trader make an informed decision, without prescribing an action. |
| Evidence Synthesis | The process of combining independently produced intelligence into a single coherent assessment. |
| Confidence | An indication of how strongly the combined evidence supports the synthesized assessment. |
| Decision Metadata | Supporting information describing how and when a decision-support assessment was produced. |
| Observation | A statement produced by an Analysis Engine describing something that has occurred. |
| Supporting Intelligence | The specific upstream intelligence used to produce a synthesized assessment. |
| Explainability | The property of an assessment being traceable to the upstream intelligence that produced it. |
| Traceability | The ability to trace a synthesized assessment back to its originating engine outputs. |

---

# 17. Decision Engine Freeze

This specification becomes authoritative after approval.

The Decision Engine shall remain an orchestration engine.

It shall never become an Analysis Engine.

Its responsibilities may not expand into trade execution, portfolio management, or broker connectivity.

Any change requires an approved Architecture Decision Record (ADR).

---

# 18. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Decision Engine Specification for MIOS. |
