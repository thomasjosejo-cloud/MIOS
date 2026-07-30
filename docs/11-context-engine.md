---
id: CONTEXT-001
title: MIOS Context Engine Specification
document: 11-context-engine.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Context Engine transforms normalized market state into structured contextual intelligence. It is one of the independent Analysis Engines defined in [02-architecture.md](02-architecture.md).

Contextual intelligence provides surrounding environmental understanding that helps interpret observations produced by other Analysis Engines. It describes the broader market environment and contextual state that surrounds market behaviour, rather than analysing any single domain such as price, liquidity, options, or momentum.

The Context Engine consumes data exclusively from the Event Bus and Market Store. It never communicates with external providers, consistent with the Data Layer's role as the sole gateway for external market data, defined in [04-data-layer.md](04-data-layer.md).

The Context Engine produces observations rather than predictions. It never recommends trades.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Analyse Market Context | Examine market state to describe the broader environment surrounding current market behaviour. |
| Monitor Market Environment | Observe conditions that characterize the overall environment in which the market is currently operating. |
| Identify Regime Characteristics | Identify the general character of the current market regime. |
| Identify Session Context | Identify contextual factors relevant to the current trading session. |
| Identify Instrument Context | Identify contextual factors specific to the instrument being observed. |
| Generate Context Intelligence | Produce structured, evidence-backed observations about market context. |
| Publish Intelligence Events | Publish generated context intelligence as events on the Event Bus, per [06-event-bus.md](06-event-bus.md). |
| Maintain Explainability | Ensure every observation produced can be explained in terms of the contextual evidence that supports it. |
| Provide Supporting Evidence | Attach the specific observable contextual evidence that supports each observation. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No External Connectivity | The Context Engine does not communicate with external market data providers. |
| No Price Structure Analysis | The Context Engine does not analyse price structure, trend, or swing behaviour; that is the responsibility of the Price Engine. |
| No Liquidity Analysis | The Context Engine does not analyse volume or liquidity conditions; that is the responsibility of the Liquidity Engine. |
| No Options Analysis | The Context Engine does not analyse options positioning data; that is the responsibility of the Options Engine. |
| No Momentum Analysis | The Context Engine does not analyse the rate or quality of price movement; that is the responsibility of the Momentum Engine. |
| No Decision Making | The Context Engine does not synthesize a final decision-support view; that is the responsibility of the Decision Engine. |
| No Contradiction Resolution | The Context Engine does not compare or reconcile outputs from multiple Analysis Engines; that is the responsibility of the Contradiction Engine. |
| No AI Explanation | The Context Engine does not translate intelligence into plain-language explanation; that is the responsibility of the AI Explanation Engine. |
| No Trading Signals | The Context Engine never produces a buy/sell/hold signal. |
| No Trade Recommendations | The Context Engine never recommends a specific trade or action. |
| No Order Execution | The Context Engine has no role in trade execution or order routing of any kind. |

---

# 4. Inputs

The Context Engine consumes only normalized market information. Its inputs include:

- Market State
- Session Information
- Calendar Information
- Instrument Metadata
- Price History
- Volume History
- Historical Snapshots
- Market Store Context
- Event Bus Events

All inputs originate through the Event Bus and Market Store, as defined in [05-market-store.md](05-market-store.md) and [06-event-bus.md](06-event-bus.md). The Context Engine never receives data directly from an external provider.

---

# 5. Outputs

The Context Engine produces the following conceptual categories of output. This section describes categories only; it does not define payloads.

- Context Intelligence
- Regime Events
- Environment Events
- Session Events
- Supporting Evidence
- Confidence Information
- Health Information

---

# 6. Scope of Analysis

The Context Engine's intelligence domain covers:

- Market Environment
- Trading Session Context
- Instrument Context
- Regime Characteristics
- Historical Context
- Current Context
- Environmental Conditions
- State Consistency

The Context Engine observes the surrounding market environment only. It does not predict future market behaviour.

---

# 7. Evidence Philosophy

Every conclusion produced by the Context Engine must be supported by observable market evidence, consistent with the "Explain Everything" and "Evidence-Based Intelligence" principles defined in [01-product.md](01-product.md).

- No unexplained conclusions.
- No black-box reasoning.
- Every observation must be reproducible.
- Every observation must reference supporting evidence.

---

# 8. Intelligence Principles

| Principle | Description |
|---|---|
| Deterministic | Given the same market state, the Context Engine produces the same observations. |
| Evidence Based | Every observation is grounded in observable market and session data. |
| Reproducible | An observation can be independently verified by examining the same underlying contextual evidence. |
| Explainable | Every observation can be explained in terms of the evidence that produced it. |
| Provider Independent | Analysis is performed on normalized market data, independent of the originating external provider. |
| Time Consistent | The same contextual condition, occurring at different times, is analysed and represented the same way. |
| State Aware | Analysis takes into account the relevant current and historical market state held in the Market Store. |

---

# 9. Engine Lifecycle

| Stage | Description |
|---|---|
| Receive Event | The Context Engine receives a relevant event from the Event Bus. |
| Retrieve Context | The Context Engine retrieves any additional relevant market state from the Market Store needed to perform its analysis. |
| Analyse | The Context Engine examines the available environmental data within its defined scope of analysis. |
| Generate Intelligence | The Context Engine produces structured, evidence-backed context intelligence. |
| Validate | The Context Engine confirms that generated intelligence conforms to its evidence and explainability principles before publication. |
| Publish | The Context Engine publishes the generated intelligence as an event on the Event Bus. |
| Wait | The Context Engine returns to an idle state until the next relevant event is received. |

---

# 10. Reliability Requirements

| Requirement | Description |
|---|---|
| Deterministic Processing | The same input data always produces the same output intelligence. |
| Repeatable Results | Reprocessing the same historical data produces the same observations. |
| Fault Isolation | A failure within the Context Engine does not affect the operation of other Analysis Engines. |
| Transparent Failures | Failures within the Context Engine are surfaced clearly rather than silently absorbed, consistent with [02-architecture.md](02-architecture.md). |
| Independent Operation | The Context Engine operates without depending on the internal state or availability of any other Analysis Engine. |
| Recovery | The Context Engine resumes normal operation following a disruption without requiring manual reconstruction of missed analysis. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| No Predictions | The Context Engine does not forecast future market behaviour. |
| No Trade Signals | The Context Engine does not produce buy/sell/hold signals. |
| No Decision Making | The Context Engine does not synthesize a final decision-support view. |
| No Contradiction Resolution | The Context Engine does not compare or reconcile outputs from multiple Analysis Engines. |
| No External Calls | The Context Engine does not communicate with external systems or data providers. |
| No Provider Awareness | The Context Engine has no knowledge of which external provider originated the data it analyses. |
| No AI | The Context Engine does not apply machine learning or generative explanation logic. |
| No Self Learning | The Context Engine's analysis logic does not adapt itself based on past outcomes. |
| No Market Orders | The Context Engine has no role in trade execution or order placement. |

---

# 12. Context Engine Governance

The Context Engine is responsible only for contextual intelligence.

It shall never evaluate price structure.

It shall never evaluate liquidity.

It shall never evaluate options.

It shall never evaluate momentum.

It shall never resolve contradictions.

It shall never combine intelligence from multiple engines into a decision.

Those responsibilities belong to the Contradiction Engine and the Decision Engine.

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
Context intelligence shall be produced by an independent, dedicated engine.

**Reason:**
Isolating contextual analysis into its own engine preserves the single responsibility and high cohesion principles defined in [02-architecture.md](02-architecture.md), and allows contextual intelligence to be developed, reasoned about, and validated independently of price, liquidity, options, and momentum analysis. This separation also enables the Contradiction Engine to meaningfully compare the Context Engine's output against other domains of intelligence, rather than having contextual framing embedded inside another engine's analysis.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Single combined engine | Would merge multiple, distinct intelligence domains into one component, violating single responsibility and making it harder to isolate faults or reason about any one domain of intelligence. |
| Dashboard analysis | Would place analytical responsibility inside the Presentation Layer, violating the architecture's separation of analysis and presentation defined in [02-architecture.md](02-architecture.md). |
| Decision Engine analysis | Would require the Decision Engine to perform domain-specific analysis in addition to synthesis, violating its role as a synthesizer of already-produced intelligence, not a producer of it. |

**Consequences:**

- Context intelligence remains isolated from, and independently verifiable against, the outputs of other Analysis Engines.
- Any change to how market context is analysed is scoped entirely to the Context Engine and does not require changes to other engines.
- The Contradiction Engine can rely on receiving context intelligence as a distinct, independent input.

---

# 15. Document Dependencies

This Context Engine Specification depends on:

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
| Context Intelligence | Structured, evidence-backed observations about the broader market environment. |
| Market Context | Relevant surrounding market state used to inform analysis. |
| Market Environment | The overall conditions in which current market behaviour is occurring. |
| Market Regime | The general character of market behaviour over a given period. |
| Trading Session | A defined period of market activity. |
| Observation | A statement about market context that has already occurred. |
| Evidence | Observable contextual data supporting an observation. |
| Confidence | An indication of how strongly available evidence supports an observation. |
| Explainability | The property of an observation being traceable to its supporting evidence. |

---

# 17. Context Engine Freeze

This specification becomes authoritative after approval.

The Context Engine shall remain an independent analysis engine.

Its responsibilities may not be expanded into other intelligence domains.

Any change requires an approved Architecture Decision Record (ADR).

---

# 18. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Context Engine Specification for MIOS. |
