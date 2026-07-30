---
id: PRICE-001
title: MIOS Price Engine Specification
document: 07-price-engine.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Price Engine is responsible for transforming raw price history into structured price intelligence. It is one of the independent Analysis Engines defined in [02-architecture.md](02-architecture.md).

The Price Engine consumes market data exclusively from the Event Bus and Market Store. It never communicates with external providers, consistent with the Data Layer's role as the sole gateway for external market data, defined in [04-data-layer.md](04-data-layer.md).

The Price Engine produces observations, not predictions. It describes what has occurred in price behaviour, backed by observable evidence. It never produces trading signals, and it never recommends a trade.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Analyse Price Structure | Examine price history to identify how price has organized itself over time. |
| Identify Swing Structure | Identify the sequence of swing highs and lows present in price history. |
| Identify Trend Structure | Identify the prevailing directional structure of price over a given period. |
| Monitor Price Behaviour | Observe how price behaves in relation to its own recent history. |
| Generate Price Intelligence | Produce structured, evidence-backed observations about price. |
| Publish Intelligence Events | Publish generated price intelligence as events on the Event Bus, per [06-event-bus.md](06-event-bus.md). |
| Maintain Explainability | Ensure every observation produced can be explained in terms of the price evidence that supports it. |
| Provide Evidence | Attach the specific observable price evidence that supports each observation. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No External Connectivity | The Price Engine does not communicate with external market data providers. |
| No Liquidity Analysis | The Price Engine does not analyse volume or liquidity conditions; that is the responsibility of the Liquidity Engine. |
| No Options Analysis | The Price Engine does not analyse options positioning data; that is the responsibility of the Options Engine. |
| No Momentum Analysis | The Price Engine does not analyse the rate or quality of price movement; that is the responsibility of the Momentum Engine. |
| No Decision Making | The Price Engine does not synthesize a final decision-support view; that is the responsibility of the Decision Engine. |
| No AI Explanation | The Price Engine does not translate intelligence into plain-language explanation; that is the responsibility of the AI Explanation Engine. |
| No Trading Signals | The Price Engine never produces a buy/sell/hold signal. |
| No Trade Recommendations | The Price Engine never recommends a specific trade or action. |
| No Order Execution | The Price Engine has no role in trade execution or order routing of any kind. |

---

# 4. Inputs

The Price Engine consumes only normalized market information. Its inputs include:

- Price History
- OHLC
- Session Information
- Instrument Metadata
- Market State Events
- Historical Snapshots

All inputs originate through the Event Bus and Market Store, as defined in [05-market-store.md](05-market-store.md) and [06-event-bus.md](06-event-bus.md). The Price Engine never receives data directly from an external provider.

---

# 5. Outputs

The Price Engine produces the following conceptual categories of output. This section describes categories only; it does not define payloads.

- Price Intelligence
- Structure Events
- Trend Events
- Supporting Evidence
- Confidence Information
- Health Information

---

# 6. Scope of Analysis

The Price Engine's intelligence domain covers:

- Trend
- Swing Structure
- Support
- Resistance
- Breakout Behaviour
- Range Behaviour
- Volatility Context
- Price Behaviour

The Price Engine observes what has happened in price. It does not forecast what will happen next.

---

# 7. Evidence Philosophy

Every conclusion produced by the Price Engine must be supported by observable market evidence, consistent with the "Explain Everything" and "Evidence-Based Intelligence" principles defined in [01-product.md](01-product.md).

- No unexplained conclusions.
- No black-box reasoning.
- Every observation must be reproducible.
- Every observation must reference supporting evidence.

---

# 8. Intelligence Principles

| Principle | Description |
|---|---|
| Deterministic | Given the same price history, the Price Engine produces the same observations. |
| Evidence Based | Every observation is grounded in observable price data. |
| Reproducible | An observation can be independently verified by examining the same underlying price evidence. |
| Explainable | Every observation can be explained in terms of the evidence that produced it. |
| Provider Independent | Analysis is performed on normalized market data, independent of the originating external provider. |
| Time Consistent | The same price condition, occurring at different times, is analysed and represented the same way. |
| State Aware | Analysis takes into account the relevant current and historical market state held in the Market Store. |

---

# 9. Engine Lifecycle

| Stage | Description |
|---|---|
| Receive Event | The Price Engine receives a relevant event from the Event Bus. |
| Retrieve Context | The Price Engine retrieves any additional relevant market state from the Market Store needed to perform its analysis. |
| Analyse | The Price Engine examines the available price data within its defined scope of analysis. |
| Generate Intelligence | The Price Engine produces structured, evidence-backed price intelligence. |
| Validate | The Price Engine confirms that generated intelligence conforms to its evidence and explainability principles before publication. |
| Publish | The Price Engine publishes the generated intelligence as an event on the Event Bus. |
| Wait | The Price Engine returns to an idle state until the next relevant event is received. |

---

# 10. Reliability Requirements

| Requirement | Description |
|---|---|
| Deterministic Processing | The same input data always produces the same output intelligence. |
| Repeatable Results | Reprocessing the same historical data produces the same observations. |
| Fault Isolation | A failure within the Price Engine does not affect the operation of other Analysis Engines. |
| Transparent Failures | Failures within the Price Engine are surfaced clearly rather than silently absorbed, consistent with [02-architecture.md](02-architecture.md). |
| Independent Operation | The Price Engine operates without depending on the internal state or availability of any other Analysis Engine. |
| Recovery | The Price Engine resumes normal operation following a disruption without requiring manual reconstruction of missed analysis. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| No Predictions | The Price Engine does not forecast future price behaviour. |
| No Trade Signals | The Price Engine does not produce buy/sell/hold signals. |
| No Decision Making | The Price Engine does not synthesize a final decision-support view. |
| No External Calls | The Price Engine does not communicate with external systems or data providers. |
| No Provider Awareness | The Price Engine has no knowledge of which external provider originated the data it analyses. |
| No AI | The Price Engine does not apply machine learning or generative explanation logic. |
| No Self Learning | The Price Engine's analysis logic does not adapt itself based on past outcomes. |
| No Market Orders | The Price Engine has no role in trade execution or order placement. |

---

# 12. Price Engine Governance

The Price Engine is responsible only for price intelligence.

It shall never evaluate liquidity.

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
Price intelligence shall be produced by an independent, dedicated engine.

**Reason:**
Isolating price analysis into its own engine preserves the single responsibility and high cohesion principles defined in [02-architecture.md](02-architecture.md), and allows price intelligence to be developed, reasoned about, and validated independently of liquidity, options, momentum, and context analysis. This separation also enables the Contradiction Engine to meaningfully compare the Price Engine's output against other domains of intelligence.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Single combined engine | Would merge multiple, distinct intelligence domains into one component, violating single responsibility and making it harder to isolate faults or reason about any one domain of intelligence. |
| Dashboard analysis | Would place analytical responsibility inside the Presentation Layer, violating the architecture's separation of analysis and presentation defined in [02-architecture.md](02-architecture.md). |
| Decision Engine analysis | Would require the Decision Engine to perform domain-specific analysis in addition to synthesis, violating its role as a synthesizer of already-produced intelligence, not a producer of it. |

**Consequences:**

- Price intelligence remains isolated from, and independently verifiable against, the outputs of other Analysis Engines.
- Any change to how price is analysed is scoped entirely to the Price Engine and does not require changes to other engines.
- The Contradiction Engine can rely on receiving price intelligence as a distinct, independent input.

---

# 15. Document Dependencies

This Price Engine Specification depends on:

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
| Price Intelligence | Structured, evidence-backed observations about price behaviour. |
| Trend | The prevailing directional structure of price over a given period. |
| Swing | A directional movement in price between a identifiable high and low point. |
| Structure | The organization of price action based on swings, highs, and lows. |
| Evidence | Observable price data supporting an observation. |
| Observation | A statement about price behaviour that has already occurred. |
| Market Context | Relevant surrounding market state used to inform analysis. |
| Confidence | An indication of how strongly available evidence supports an observation. |
| Explainability | The property of an observation being traceable to its supporting evidence. |

---

# 17. Price Engine Freeze

This specification becomes authoritative after approval.

The Price Engine shall remain an independent analysis engine.

Its responsibilities may not be expanded into other intelligence domains.

Any change requires an approved Architecture Decision Record (ADR).

---

# 18. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Price Engine Specification for MIOS. |
