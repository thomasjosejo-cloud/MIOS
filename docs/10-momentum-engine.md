---
id: MOMENTUM-001
title: MIOS Momentum Engine Specification
document: 10-momentum-engine.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Momentum Engine is responsible for transforming normalized market movement into structured momentum intelligence. It is one of the independent Analysis Engines defined in [02-architecture.md](02-architecture.md).

The Momentum Engine consumes market data exclusively from the Event Bus and Market Store. It never communicates with external providers, consistent with the Data Layer's role as the sole gateway for external market data, defined in [04-data-layer.md](04-data-layer.md).

The Momentum Engine produces observations rather than predictions. It describes what has occurred in market movement, backed by observable evidence. It never produces trading signals or execution recommendations.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Analyse Momentum Behaviour | Examine market movement to assess how momentum has behaved over time. |
| Monitor Market Strength | Observe conditions indicating strength in current market movement. |
| Monitor Market Weakness | Observe conditions indicating weakness in current market movement. |
| Identify Acceleration Behaviour | Identify periods where market movement has been accelerating. |
| Identify Deceleration Behaviour | Identify periods where market movement has been decelerating. |
| Generate Momentum Intelligence | Produce structured, evidence-backed observations about momentum. |
| Publish Intelligence Events | Publish generated momentum intelligence as events on the Event Bus, per [06-event-bus.md](06-event-bus.md). |
| Maintain Explainability | Ensure every observation produced can be explained in terms of the movement evidence that supports it. |
| Provide Supporting Evidence | Attach the specific observable movement evidence that supports each observation. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No External Connectivity | The Momentum Engine does not communicate with external market data providers. |
| No Price Structure Analysis | The Momentum Engine does not analyse price structure, trend, or swing behaviour; that is the responsibility of the Price Engine. |
| No Liquidity Analysis | The Momentum Engine does not analyse volume or liquidity conditions; that is the responsibility of the Liquidity Engine. |
| No Options Analysis | The Momentum Engine does not analyse options positioning data; that is the responsibility of the Options Engine. |
| No Decision Making | The Momentum Engine does not synthesize a final decision-support view; that is the responsibility of the Decision Engine. |
| No AI Explanation | The Momentum Engine does not translate intelligence into plain-language explanation; that is the responsibility of the AI Explanation Engine. |
| No Trading Signals | The Momentum Engine never produces a buy/sell/hold signal. |
| No Trade Recommendations | The Momentum Engine never recommends a specific trade or action. |
| No Order Execution | The Momentum Engine has no role in trade execution or order routing of any kind. |

---

# 4. Inputs

The Momentum Engine consumes only normalized market information. Its inputs include:

- Price History
- OHLC
- Volume History
- Session Information
- Instrument Metadata
- Market State Events
- Historical Snapshots

All inputs originate through the Event Bus and Market Store, as defined in [05-market-store.md](05-market-store.md) and [06-event-bus.md](06-event-bus.md). The Momentum Engine never receives data directly from an external provider.

---

# 5. Outputs

The Momentum Engine produces the following conceptual categories of output. This section describes categories only; it does not define payloads.

- Momentum Intelligence
- Strength Events
- Weakness Events
- Momentum Context Events
- Supporting Evidence
- Confidence Information
- Health Information

---

# 6. Scope of Analysis

The Momentum Engine's intelligence domain covers:

- Momentum Behaviour
- Strength
- Weakness
- Acceleration
- Deceleration
- Persistence
- Momentum Context
- Market Energy

The Momentum Engine observes historical and current market movement only. It never predicts future momentum or price direction.

---

# 7. Evidence Philosophy

Every conclusion produced by the Momentum Engine must be supported by observable market evidence, consistent with the "Explain Everything" and "Evidence-Based Intelligence" principles defined in [01-product.md](01-product.md).

- No unexplained conclusions.
- No black-box reasoning.
- Every observation must be reproducible.
- Every observation must reference supporting evidence.

---

# 8. Intelligence Principles

| Principle | Description |
|---|---|
| Deterministic | Given the same movement data, the Momentum Engine produces the same observations. |
| Evidence Based | Every observation is grounded in observable price and volume movement. |
| Reproducible | An observation can be independently verified by examining the same underlying movement evidence. |
| Explainable | Every observation can be explained in terms of the evidence that produced it. |
| Provider Independent | Analysis is performed on normalized market data, independent of the originating external provider. |
| Time Consistent | The same momentum condition, occurring at different times, is analysed and represented the same way. |
| State Aware | Analysis takes into account the relevant current and historical market state held in the Market Store. |

---

# 9. Engine Lifecycle

| Stage | Description |
|---|---|
| Receive Event | The Momentum Engine receives a relevant event from the Event Bus. |
| Retrieve Context | The Momentum Engine retrieves any additional relevant market state from the Market Store needed to perform its analysis. |
| Analyse | The Momentum Engine examines the available movement data within its defined scope of analysis. |
| Generate Intelligence | The Momentum Engine produces structured, evidence-backed momentum intelligence. |
| Validate | The Momentum Engine confirms that generated intelligence conforms to its evidence and explainability principles before publication. |
| Publish | The Momentum Engine publishes the generated intelligence as an event on the Event Bus. |
| Wait | The Momentum Engine returns to an idle state until the next relevant event is received. |

---

# 10. Reliability Requirements

| Requirement | Description |
|---|---|
| Deterministic Processing | The same input data always produces the same output intelligence. |
| Repeatable Results | Reprocessing the same historical data produces the same observations. |
| Fault Isolation | A failure within the Momentum Engine does not affect the operation of other Analysis Engines. |
| Transparent Failures | Failures within the Momentum Engine are surfaced clearly rather than silently absorbed, consistent with [02-architecture.md](02-architecture.md). |
| Independent Operation | The Momentum Engine operates without depending on the internal state or availability of any other Analysis Engine. |
| Recovery | The Momentum Engine resumes normal operation following a disruption without requiring manual reconstruction of missed analysis. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| No Predictions | The Momentum Engine does not forecast future momentum or price direction. |
| No Trade Signals | The Momentum Engine does not produce buy/sell/hold signals. |
| No Decision Making | The Momentum Engine does not synthesize a final decision-support view. |
| No External Calls | The Momentum Engine does not communicate with external systems or data providers. |
| No Provider Awareness | The Momentum Engine has no knowledge of which external provider originated the data it analyses. |
| No AI | The Momentum Engine does not apply machine learning or generative explanation logic. |
| No Self Learning | The Momentum Engine's analysis logic does not adapt itself based on past outcomes. |
| No Market Orders | The Momentum Engine has no role in trade execution or order placement. |

---

# 12. Momentum Engine Governance

The Momentum Engine is responsible only for momentum intelligence.

It shall never evaluate price structure.

It shall never evaluate liquidity.

It shall never evaluate options.

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
Momentum intelligence shall be produced by an independent, dedicated engine.

**Reason:**
Isolating momentum analysis into its own engine preserves the single responsibility and high cohesion principles defined in [02-architecture.md](02-architecture.md), and allows momentum intelligence to be developed, reasoned about, and validated independently of price, liquidity, options, and context analysis. This separation also enables the Contradiction Engine to meaningfully compare the Momentum Engine's output against other domains of intelligence.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Single combined engine | Would merge multiple, distinct intelligence domains into one component, violating single responsibility and making it harder to isolate faults or reason about any one domain of intelligence. |
| Dashboard analysis | Would place analytical responsibility inside the Presentation Layer, violating the architecture's separation of analysis and presentation defined in [02-architecture.md](02-architecture.md). |
| Decision Engine analysis | Would require the Decision Engine to perform domain-specific analysis in addition to synthesis, violating its role as a synthesizer of already-produced intelligence, not a producer of it. |

**Consequences:**

- Momentum intelligence remains isolated from, and independently verifiable against, the outputs of other Analysis Engines.
- Any change to how momentum is analysed is scoped entirely to the Momentum Engine and does not require changes to other engines.
- The Contradiction Engine can rely on receiving momentum intelligence as a distinct, independent input.

---

# 15. Document Dependencies

This Momentum Engine Specification depends on:

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
| Momentum Intelligence | Structured, evidence-backed observations about market movement. |
| Momentum | The observed rate and quality of market movement over time. |
| Strength | A condition indicating robust, sustained market movement. |
| Weakness | A condition indicating fading or unsustained market movement. |
| Acceleration | An observed increase in the rate of market movement. |
| Deceleration | An observed decrease in the rate of market movement. |
| Observation | A statement about momentum behaviour that has already occurred. |
| Evidence | Observable movement data supporting an observation. |
| Confidence | An indication of how strongly available evidence supports an observation. |
| Explainability | The property of an observation being traceable to its supporting evidence. |

---

# 17. Momentum Engine Freeze

This specification becomes authoritative after approval.

The Momentum Engine shall remain an independent analysis engine.

Its responsibilities may not be expanded into other intelligence domains.

Any change requires an approved Architecture Decision Record (ADR).

---

# 18. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Momentum Engine Specification for MIOS. |
