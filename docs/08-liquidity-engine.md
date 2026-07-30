---
id: LIQUIDITY-001
title: MIOS Liquidity Engine Specification
document: 08-liquidity-engine.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Liquidity Engine is responsible for transforming normalized market activity into structured liquidity intelligence. It is one of the independent Analysis Engines defined in [02-architecture.md](02-architecture.md).

The Liquidity Engine consumes market data exclusively from the Event Bus and Market Store. It never communicates with external providers, consistent with the Data Layer's role as the sole gateway for external market data, defined in [04-data-layer.md](04-data-layer.md).

The Liquidity Engine produces observations rather than predictions. It describes what has occurred in liquidity and participation behaviour, backed by observable evidence. It never produces trading signals or execution recommendations.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Analyse Liquidity Conditions | Examine market activity to assess the current liquidity conditions of an instrument. |
| Identify Liquidity Structure | Identify how liquidity is organized and distributed across the market. |
| Monitor Volume Behaviour | Observe how traded volume behaves relative to its own recent history. |
| Monitor Participation Behaviour | Observe how market participation changes over time. |
| Generate Liquidity Intelligence | Produce structured, evidence-backed observations about liquidity. |
| Publish Intelligence Events | Publish generated liquidity intelligence as events on the Event Bus, per [06-event-bus.md](06-event-bus.md). |
| Maintain Explainability | Ensure every observation produced can be explained in terms of the liquidity evidence that supports it. |
| Provide Supporting Evidence | Attach the specific observable liquidity evidence that supports each observation. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No External Connectivity | The Liquidity Engine does not communicate with external market data providers. |
| No Price Structure Analysis | The Liquidity Engine does not analyse price structure, trend, or swing behaviour; that is the responsibility of the Price Engine. |
| No Options Analysis | The Liquidity Engine does not analyse options positioning data; that is the responsibility of the Options Engine. |
| No Momentum Analysis | The Liquidity Engine does not analyse the rate or quality of price movement; that is the responsibility of the Momentum Engine. |
| No Decision Making | The Liquidity Engine does not synthesize a final decision-support view; that is the responsibility of the Decision Engine. |
| No AI Explanation | The Liquidity Engine does not translate intelligence into plain-language explanation; that is the responsibility of the AI Explanation Engine. |
| No Trading Signals | The Liquidity Engine never produces a buy/sell/hold signal. |
| No Trade Recommendations | The Liquidity Engine never recommends a specific trade or action. |
| No Order Execution | The Liquidity Engine has no role in trade execution or order routing of any kind. |

---

# 4. Inputs

The Liquidity Engine consumes only normalized market information. Its inputs include:

- Volume History
- Open Interest History
- Price History
- OHLC
- Session Information
- Instrument Metadata
- Market State Events
- Historical Snapshots

All inputs originate through the Event Bus and Market Store, as defined in [05-market-store.md](05-market-store.md) and [06-event-bus.md](06-event-bus.md). The Liquidity Engine never receives data directly from an external provider.

---

# 5. Outputs

The Liquidity Engine produces the following conceptual categories of output. This section describes categories only; it does not define payloads.

- Liquidity Intelligence
- Liquidity Events
- Participation Events
- Supporting Evidence
- Confidence Information
- Health Information

---

# 6. Scope of Analysis

The Liquidity Engine's intelligence domain covers:

- Liquidity Conditions
- Participation Levels
- Volume Behaviour
- Open Interest Behaviour
- Accumulation Behaviour
- Distribution Behaviour
- Liquidity Imbalance
- Liquidity Context

The Liquidity Engine observes historical and current liquidity behaviour only. It never predicts future liquidity.

---

# 7. Evidence Philosophy

Every conclusion produced by the Liquidity Engine must be supported by observable market evidence, consistent with the "Explain Everything" and "Evidence-Based Intelligence" principles defined in [01-product.md](01-product.md).

- No unexplained conclusions.
- No black-box reasoning.
- Every observation must be reproducible.
- Every observation must reference supporting evidence.

---

# 8. Intelligence Principles

| Principle | Description |
|---|---|
| Deterministic | Given the same liquidity data, the Liquidity Engine produces the same observations. |
| Evidence Based | Every observation is grounded in observable volume and participation data. |
| Reproducible | An observation can be independently verified by examining the same underlying liquidity evidence. |
| Explainable | Every observation can be explained in terms of the evidence that produced it. |
| Provider Independent | Analysis is performed on normalized market data, independent of the originating external provider. |
| Time Consistent | The same liquidity condition, occurring at different times, is analysed and represented the same way. |
| State Aware | Analysis takes into account the relevant current and historical market state held in the Market Store. |

---

# 9. Engine Lifecycle

| Stage | Description |
|---|---|
| Receive Event | The Liquidity Engine receives a relevant event from the Event Bus. |
| Retrieve Context | The Liquidity Engine retrieves any additional relevant market state from the Market Store needed to perform its analysis. |
| Analyse | The Liquidity Engine examines the available liquidity data within its defined scope of analysis. |
| Generate Intelligence | The Liquidity Engine produces structured, evidence-backed liquidity intelligence. |
| Validate | The Liquidity Engine confirms that generated intelligence conforms to its evidence and explainability principles before publication. |
| Publish | The Liquidity Engine publishes the generated intelligence as an event on the Event Bus. |
| Wait | The Liquidity Engine returns to an idle state until the next relevant event is received. |

---

# 10. Reliability Requirements

| Requirement | Description |
|---|---|
| Deterministic Processing | The same input data always produces the same output intelligence. |
| Repeatable Results | Reprocessing the same historical data produces the same observations. |
| Fault Isolation | A failure within the Liquidity Engine does not affect the operation of other Analysis Engines. |
| Transparent Failures | Failures within the Liquidity Engine are surfaced clearly rather than silently absorbed, consistent with [02-architecture.md](02-architecture.md). |
| Independent Operation | The Liquidity Engine operates without depending on the internal state or availability of any other Analysis Engine. |
| Recovery | The Liquidity Engine resumes normal operation following a disruption without requiring manual reconstruction of missed analysis. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| No Predictions | The Liquidity Engine does not forecast future liquidity behaviour. |
| No Trade Signals | The Liquidity Engine does not produce buy/sell/hold signals. |
| No Decision Making | The Liquidity Engine does not synthesize a final decision-support view. |
| No External Calls | The Liquidity Engine does not communicate with external systems or data providers. |
| No Provider Awareness | The Liquidity Engine has no knowledge of which external provider originated the data it analyses. |
| No AI | The Liquidity Engine does not apply machine learning or generative explanation logic. |
| No Self Learning | The Liquidity Engine's analysis logic does not adapt itself based on past outcomes. |
| No Market Orders | The Liquidity Engine has no role in trade execution or order placement. |

---

# 12. Liquidity Engine Governance

The Liquidity Engine is responsible only for liquidity intelligence.

It shall never evaluate price structure.

It shall never evaluate options.

It shall never evaluate momentum.

It shall never combine intelligence from multiple engines.

That responsibility belongs to the Contradiction Engine.

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
Liquidity intelligence shall be produced by an independent, dedicated engine.

**Reason:**
Isolating liquidity analysis into its own engine preserves the single responsibility and high cohesion principles defined in [02-architecture.md](02-architecture.md), and allows liquidity intelligence to be developed, reasoned about, and validated independently of price, options, momentum, and context analysis. This separation also enables the Contradiction Engine to meaningfully compare the Liquidity Engine's output against other domains of intelligence.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Single combined engine | Would merge multiple, distinct intelligence domains into one component, violating single responsibility and making it harder to isolate faults or reason about any one domain of intelligence. |
| Dashboard analysis | Would place analytical responsibility inside the Presentation Layer, violating the architecture's separation of analysis and presentation defined in [02-architecture.md](02-architecture.md). |
| Decision Engine analysis | Would require the Decision Engine to perform domain-specific analysis in addition to synthesis, violating its role as a synthesizer of already-produced intelligence, not a producer of it. |

**Consequences:**

- Liquidity intelligence remains isolated from, and independently verifiable against, the outputs of other Analysis Engines.
- Any change to how liquidity is analysed is scoped entirely to the Liquidity Engine and does not require changes to other engines.
- The Contradiction Engine can rely on receiving liquidity intelligence as a distinct, independent input.

---

# 15. Document Dependencies

This Liquidity Engine Specification depends on:

- 01-product.md
- 02-architecture.md
- 04-data-layer.md
- 05-market-store.md
- 06-event-bus.md

This document is referenced by:

- 12-contradiction-engine.md
- 13-decision-engine.md
- 14-ai-explanation-engine.md
- 15-api-specification.md
- 16-frontend.md

---

# 16. Glossary

| Term | Meaning |
|------|---------|
| Liquidity Intelligence | Structured, evidence-backed observations about liquidity and participation behaviour. |
| Liquidity | The degree to which an instrument can be traded without significantly affecting its price. |
| Participation | The level of market activity contributing to observed liquidity conditions. |
| Volume | The quantity of an instrument traded over a defined time interval. |
| Open Interest | The total number of outstanding derivative contracts for an instrument. |
| Observation | A statement about liquidity behaviour that has already occurred. |
| Evidence | Observable liquidity data supporting an observation. |
| Confidence | An indication of how strongly available evidence supports an observation. |
| Market Context | Relevant surrounding market state used to inform analysis. |
| Explainability | The property of an observation being traceable to its supporting evidence. |

---

# 17. Liquidity Engine Freeze

This specification becomes authoritative after approval.

The Liquidity Engine shall remain an independent analysis engine.

Its responsibilities may not be expanded into other intelligence domains.

Any change requires an approved Architecture Decision Record (ADR).

---

# 18. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Liquidity Engine Specification for MIOS. |
