---
id: OPTIONS-001
title: MIOS Options Engine Specification
document: 09-options-engine.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Options Engine is responsible for transforming normalized derivatives market information into structured options intelligence. It is one of the independent Analysis Engines defined in [02-architecture.md](02-architecture.md).

The Options Engine consumes market data exclusively from the Event Bus and Market Store. It never communicates with external providers, consistent with the Data Layer's role as the sole gateway for external market data, defined in [04-data-layer.md](04-data-layer.md).

The Options Engine produces observations rather than predictions. It describes what has occurred in options positioning and activity, backed by observable evidence. It never produces trading signals or execution recommendations.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Analyse Options Market Structure | Examine derivatives market data to assess how the options market is currently structured. |
| Monitor Open Interest Behaviour | Observe how open interest changes across strikes and expiries over time. |
| Monitor Options Participation | Observe the level of activity across the options market. |
| Analyse Strike Activity | Examine activity concentrated at specific strikes. |
| Analyse Expiry Context | Examine how activity and positioning vary across different expiries. |
| Generate Options Intelligence | Produce structured, evidence-backed observations about options positioning and activity. |
| Publish Intelligence Events | Publish generated options intelligence as events on the Event Bus, per [06-event-bus.md](06-event-bus.md). |
| Maintain Explainability | Ensure every observation produced can be explained in terms of the derivatives evidence that supports it. |
| Provide Supporting Evidence | Attach the specific observable derivatives evidence that supports each observation. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No External Connectivity | The Options Engine does not communicate with external market data providers. |
| No Price Structure Analysis | The Options Engine does not analyse price structure, trend, or swing behaviour; that is the responsibility of the Price Engine. |
| No Liquidity Analysis | The Options Engine does not analyse general market volume or liquidity conditions; that is the responsibility of the Liquidity Engine. |
| No Momentum Analysis | The Options Engine does not analyse the rate or quality of price movement; that is the responsibility of the Momentum Engine. |
| No Decision Making | The Options Engine does not synthesize a final decision-support view; that is the responsibility of the Decision Engine. |
| No AI Explanation | The Options Engine does not translate intelligence into plain-language explanation; that is the responsibility of the AI Explanation Engine. |
| No Trading Signals | The Options Engine never produces a buy/sell/hold signal. |
| No Trade Recommendations | The Options Engine never recommends a specific trade or action. |
| No Order Execution | The Options Engine has no role in trade execution or order routing of any kind. |

---

# 4. Inputs

The Options Engine consumes only normalized market information. Its inputs include:

- Options Chain Data
- Open Interest History
- Strike Metadata
- Expiry Metadata
- Price History
- OHLC
- Session Information
- Instrument Metadata
- Market State Events
- Historical Snapshots

All inputs originate through the Event Bus and Market Store, as defined in [05-market-store.md](05-market-store.md) and [06-event-bus.md](06-event-bus.md). The Options Engine never receives data directly from an external provider.

---

# 5. Outputs

The Options Engine produces the following conceptual categories of output. This section describes categories only; it does not define payloads.

- Options Intelligence
- Open Interest Events
- Strike Activity Events
- Expiry Context Events
- Supporting Evidence
- Confidence Information
- Health Information

---

# 6. Scope of Analysis

The Options Engine's intelligence domain covers:

- Open Interest Behaviour
- Strike Activity
- Call and Put Positioning
- Expiry Structure
- Options Participation
- Position Build-up Behaviour
- Position Unwinding Behaviour
- Derivatives Context

The Options Engine observes historical and current derivatives behaviour only. It never predicts future market direction.

---

# 7. Evidence Philosophy

Every conclusion produced by the Options Engine must be supported by observable market evidence, consistent with the "Explain Everything" and "Evidence-Based Intelligence" principles defined in [01-product.md](01-product.md).

- No unexplained conclusions.
- No black-box reasoning.
- Every observation must be reproducible.
- Every observation must reference supporting evidence.

---

# 8. Intelligence Principles

| Principle | Description |
|---|---|
| Deterministic | Given the same derivatives data, the Options Engine produces the same observations. |
| Evidence Based | Every observation is grounded in observable options market data. |
| Reproducible | An observation can be independently verified by examining the same underlying derivatives evidence. |
| Explainable | Every observation can be explained in terms of the evidence that produced it. |
| Provider Independent | Analysis is performed on normalized market data, independent of the originating external provider. |
| Time Consistent | The same derivatives condition, occurring at different times, is analysed and represented the same way. |
| State Aware | Analysis takes into account the relevant current and historical market state held in the Market Store. |

---

# 9. Engine Lifecycle

| Stage | Description |
|---|---|
| Receive Event | The Options Engine receives a relevant event from the Event Bus. |
| Retrieve Context | The Options Engine retrieves any additional relevant market state from the Market Store needed to perform its analysis. |
| Analyse | The Options Engine examines the available derivatives data within its defined scope of analysis. |
| Generate Intelligence | The Options Engine produces structured, evidence-backed options intelligence. |
| Validate | The Options Engine confirms that generated intelligence conforms to its evidence and explainability principles before publication. |
| Publish | The Options Engine publishes the generated intelligence as an event on the Event Bus. |
| Wait | The Options Engine returns to an idle state until the next relevant event is received. |

---

# 10. Reliability Requirements

| Requirement | Description |
|---|---|
| Deterministic Processing | The same input data always produces the same output intelligence. |
| Repeatable Results | Reprocessing the same historical data produces the same observations. |
| Fault Isolation | A failure within the Options Engine does not affect the operation of other Analysis Engines. |
| Transparent Failures | Failures within the Options Engine are surfaced clearly rather than silently absorbed, consistent with [02-architecture.md](02-architecture.md). |
| Independent Operation | The Options Engine operates without depending on the internal state or availability of any other Analysis Engine. |
| Recovery | The Options Engine resumes normal operation following a disruption without requiring manual reconstruction of missed analysis. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| No Predictions | The Options Engine does not forecast future market direction. |
| No Trade Signals | The Options Engine does not produce buy/sell/hold signals. |
| No Decision Making | The Options Engine does not synthesize a final decision-support view. |
| No External Calls | The Options Engine does not communicate with external systems or data providers. |
| No Provider Awareness | The Options Engine has no knowledge of which external provider originated the data it analyses. |
| No AI | The Options Engine does not apply machine learning or generative explanation logic. |
| No Self Learning | The Options Engine's analysis logic does not adapt itself based on past outcomes. |
| No Market Orders | The Options Engine has no role in trade execution or order placement. |

---

# 12. Options Engine Governance

The Options Engine is responsible only for options intelligence.

It shall never evaluate price structure.

It shall never evaluate liquidity.

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
Options intelligence shall be produced by an independent, dedicated engine.

**Reason:**
Isolating options analysis into its own engine preserves the single responsibility and high cohesion principles defined in [02-architecture.md](02-architecture.md), and allows options intelligence to be developed, reasoned about, and validated independently of price, liquidity, momentum, and context analysis. This separation also enables the Contradiction Engine to meaningfully compare the Options Engine's output against other domains of intelligence.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Single combined engine | Would merge multiple, distinct intelligence domains into one component, violating single responsibility and making it harder to isolate faults or reason about any one domain of intelligence. |
| Dashboard analysis | Would place analytical responsibility inside the Presentation Layer, violating the architecture's separation of analysis and presentation defined in [02-architecture.md](02-architecture.md). |
| Decision Engine analysis | Would require the Decision Engine to perform domain-specific analysis in addition to synthesis, violating its role as a synthesizer of already-produced intelligence, not a producer of it. |

**Consequences:**

- Options intelligence remains isolated from, and independently verifiable against, the outputs of other Analysis Engines.
- Any change to how options data is analysed is scoped entirely to the Options Engine and does not require changes to other engines.
- The Contradiction Engine can rely on receiving options intelligence as a distinct, independent input.

---

# 15. Document Dependencies

This Options Engine Specification depends on:

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
| Options Intelligence | Structured, evidence-backed observations about options positioning and activity. |
| Open Interest | The total number of outstanding derivative contracts for an instrument. |
| Strike | A specific price level at which an options contract can be exercised. |
| Expiry | The date on which an options contract ceases to be valid. |
| Position Build-up | An observed increase in open positions at a given strike or expiry. |
| Position Unwinding | An observed decrease in open positions at a given strike or expiry. |
| Observation | A statement about options behaviour that has already occurred. |
| Evidence | Observable derivatives data supporting an observation. |
| Confidence | An indication of how strongly available evidence supports an observation. |
| Explainability | The property of an observation being traceable to its supporting evidence. |

---

# 17. Options Engine Freeze

This specification becomes authoritative after approval.

The Options Engine shall remain an independent analysis engine.

Its responsibilities may not be expanded into other intelligence domains.

Any change requires an approved Architecture Decision Record (ADR).

---

# 18. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Options Engine Specification for MIOS. |
