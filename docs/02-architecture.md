---
id: ARC-001
title: MIOS System Architecture
document: 02-architecture.md
version: 1.0.0
status: Approved
owner: MIOS Architecture
last_updated: 2026-07-28
---

# 1. Executive Summary

MIOS is a layered, event-driven market intelligence platform. Raw market data enters the system through a single, well-defined data layer, is normalized into a shared market store, and is then distributed to a set of independent analysis engines through an event bus. Each engine has a single responsibility and produces a discrete, evidence-backed piece of intelligence. These outputs are reconciled, checked for contradictions, and synthesized into a final decision-support view that is explained in plain language and presented to the trader.

Every component in this architecture has a single responsibility and communicates through well-defined boundaries. No component performs the work of another. This separation exists to preserve the product's core commitment, defined in [01-product.md](01-product.md): explainability is more important than prediction. The architecture is designed so that every piece of intelligence surfaced to the trader can be traced backward, engine by engine, to the raw market data that produced it.

This document defines the structural design of MIOS: its layers, components, data flow, execution order, and the architectural principles that govern how the system may grow. It does not define implementation, code, APIs, or data schemas — those are addressed in subsequent architecture and engineering documents, in accordance with the [Documentation Standard](DOCUMENTATION_STANDARD.md).

---

# 2. Architecture Principles

| Principle | Explanation |
|---|---|
| Modular | Every capability of MIOS is built as a distinct module with a clearly bounded responsibility. Modules can be understood, reviewed, and modified in isolation. |
| Event Driven | Components communicate by producing and consuming events rather than calling one another directly. This decouples producers of intelligence from consumers of intelligence. |
| Explainable | Every module must produce output that is traceable to observable evidence. No module may produce an output that cannot be explained in terms of its inputs. |
| Deterministic | Given the same market data as input, a module must produce the same output. Behavior must not depend on hidden state, randomness, or unexplained variation. |
| Scalable | The architecture must support the addition of new intelligence capabilities without requiring changes to existing, unrelated components. |
| Independent Engines | Each analysis engine operates on its own domain of market intelligence and does not depend on the internal logic of other engines. |
| Single Responsibility | Every component does exactly one job. A component that is responsible for more than one concern must be split. |
| Low Coupling | Components depend on shared, stable contracts (the market store and the event bus), not on each other's internals. |
| High Cohesion | The logic within a single component is closely related and focused on a single domain of intelligence. |

---

# Architecture Constraints

The following architectural rules are mandatory and cannot be violated without creating a new Architecture Decision Record (ADR).

| Rule ID | Constraint |
|---------|------------|
| ARC-001 | Only the Data Layer may communicate with external market data providers. |
| ARC-002 | Only the Market Store may act as the authoritative source of market state. |
| ARC-003 | Analysis Engines must never call each other directly. |
| ARC-004 | All inter-component communication must occur through the Event Bus. |
| ARC-005 | The Dashboard must never perform analysis. |
| ARC-006 | The AI Explanation Engine must never create intelligence; it may only explain intelligence produced by the Decision Engine. |
| ARC-007 | Every intelligence output must be traceable back to observable market evidence. |
| ARC-008 | No module may introduce prediction or trade signals. |

---

# 3. High-Level System Diagram

```
                        Market Data
                             │
                             ▼
                        Data Layer
                             │
                             ▼
                       Market Store
                             │
                             ▼
                        Event Bus
                             │
              ┌──────────────┼──────────────┬──────────────┬──────────────┐
              ▼              ▼              ▼              ▼              ▼
        Price Engine   Liquidity Engine  Options Engine  Momentum Engine  Context Engine
              │              │              │              │              │
              └──────────────┴──────────────┴──────────────┴──────────────┘
                                            │
                                            ▼
                                Contradiction Engine
                                            │
                                            ▼
                                   Decision Engine
                                            │
                                            ▼
                              AI Explanation Engine
                                            │
                                            ▼
                                       Dashboard
```

---

# 4. System Layers

| Layer | Purpose | Consumes | Produces |
|---|---|---|---|
| Data Layer | Ingests raw market data from external sources and normalizes it into a consistent internal format. | Raw market data (price, volume, open interest, and related derivatives data). | Normalized market data. |
| Market Store | Maintains the current and historical state of normalized market data as the single shared source of truth. | Normalized market data from the Data Layer. | A queryable, consistent market state available to all downstream components. |
| Event Bus | Distributes market state changes and intelligence outputs to all interested components without direct coupling between them. | Updates from the Market Store and outputs from Analysis Engines. | Events consumed by Analysis Engines, the Contradiction Engine, and the Decision Layer. |
| Analysis Engines | Independently analyze market state within a specific domain (price, liquidity, options, momentum, context) and produce evidence-backed intelligence. | Events from the Event Bus. | Domain-specific intelligence outputs, published back to the Event Bus. |
| Decision Layer | Reconciles intelligence from all Analysis Engines, identifies contradictions, and synthesizes a coherent decision-support view. | Intelligence outputs from all Analysis Engines. | A unified, contradiction-checked intelligence summary. |
| Presentation Layer | Explains and displays the synthesized intelligence to the trader in a clear, evidence-linked format. | The unified intelligence summary from the Decision Layer. | A human-readable, explainable presentation of market intelligence. |

---

# 5. Component Responsibilities

| Component | Responsibility |
|---|---|
| Data Layer | Ingest raw market data from external sources and normalize it into a consistent internal format for downstream use. |
| Market Store | Hold the authoritative current and historical state of normalized market data, accessible to all components that need it. |
| Event Bus | Carry events between components without requiring any component to know about the internal implementation of another. |
| Price Engine | Analyze raw price action and produce evidence-based observations about price behavior. |
| Liquidity Engine | Analyze volume and liquidity-related data to produce evidence-based observations about market liquidity conditions. |
| Options Engine | Analyze options-specific data (including open interest and put-call activity) to produce evidence-based observations about options positioning. |
| Momentum Engine | Analyze the rate and quality of price movement to produce evidence-based observations about market momentum. |
| Context Engine | Analyze structural and historical context (such as key levels and prior behavior) to produce evidence-based observations about the current market context. |
| Contradiction Engine | Compare outputs from all Analysis Engines to identify agreement, disagreement, or contradiction between them. |
| Decision Engine | Synthesize the outputs of the Analysis Engines and the Contradiction Engine into a single, coherent intelligence summary. |
| AI Explanation Engine | Translate the synthesized intelligence summary into clear, plain-language explanations, each traceable to its underlying evidence. |
| Dashboard | Present the explained intelligence to the trader in a structured, scannable, professional interface. |

---

# 6. Data Flow

The following sequence describes how a single unit of market data moves through MIOS, from ingestion to presentation.

```
 Market Data Source
        │
        │  1. Raw data received
        ▼
   Data Layer  ─────────────────────────────► Normalizes raw data
        │
        │  2. Normalized data written
        ▼
  Market Store  ────────────────────────────► Updates authoritative market state
        │
        │  3. State change event published
        ▼
   Event Bus  ─────────────────────────────► Broadcasts event to subscribed engines
        │
        ├──────────────┬──────────────┬──────────────┬──────────────┐
        ▼              ▼              ▼              ▼              ▼
  Price Engine   Liquidity Eng.  Options Engine  Momentum Eng.  Context Engine
        │              │              │              │              │
        │  4. Each engine independently analyzes relevant market state
        │  5. Each engine publishes evidence-backed intelligence to the Event Bus
        └──────────────┴──────────────┴──────────────┴──────────────┘
                                    │
                                    ▼
                        Contradiction Engine
                                    │
                                    │  6. Compares engine outputs for agreement/conflict
                                    ▼
                           Decision Engine
                                    │
                                    │  7. Synthesizes a unified intelligence summary
                                    ▼
                       AI Explanation Engine
                                    │
                                    │  8. Produces plain-language, evidence-linked explanation
                                    ▼
                              Dashboard
                                    │
                                    │  9. Presents intelligence to the trader
                                    ▼
                                 Trader
```

At every step, the data produced carries a traceable link back to the market state that generated it, preserving end-to-end explainability.

---

# 7. Engine Execution Order

MIOS executes its components in the following fixed order:

1. Data Layer
2. Market Store
3. Event Bus
4. Price Engine
5. Liquidity Engine
6. Options Engine
7. Momentum Engine
8. Context Engine
9. Contradiction Engine
10. Decision Engine
11. AI Explanation Engine
12. Dashboard

## 7.1 Rationale for This Order

- **Data Layer before Market Store**: Data must be normalized before it can be trusted as authoritative state. Writing unnormalized data into the Market Store would corrupt the single source of truth used by every downstream component.
- **Market Store before Event Bus**: An event describing a market state change is only meaningful once that state has actually been committed to the Market Store. Publishing an event before the state exists would create inconsistency between what is announced and what is available to be queried.
- **Event Bus before the Analysis Engines**: The Analysis Engines are consumers of events. They cannot begin analysis until the Event Bus has data to distribute.
- **Price, Liquidity, Options, Momentum, and Context Engines run independently of one another, but all before the Contradiction Engine**: These engines analyze different domains of the same market state and do not depend on each other's outputs. The Contradiction Engine requires all of their outputs to exist before it can compare them.
- **Contradiction Engine before Decision Engine**: The Decision Engine synthesizes a coherent summary. It requires the Contradiction Engine's comparison of agreement and conflict in order to represent that synthesis honestly, rather than silently ignoring disagreement between engines.
- **Decision Engine before AI Explanation Engine**: The Explanation Engine translates a finished, synthesized intelligence summary into plain language. It cannot explain a summary that does not yet exist.
- **AI Explanation Engine before Dashboard**: The Dashboard presents explained intelligence. It does not perform its own analysis or synthesis, so the explanation must exist before it can be displayed.

This fixed order guarantees that every stage operates on complete, consistent inputs from the stage before it, which is a precondition for end-to-end explainability.

---

# 8. Module Independence

Every Analysis Engine (Price, Liquidity, Options, Momentum, Context) must operate independently. An engine's internal logic must not be aware of, or dependent on, the internal logic of any other engine.

## 8.1 Allowed Dependencies

- An engine may depend on the Market Store as its source of market state.
- An engine may depend on the Event Bus to receive input events and publish its own output.
- An engine may depend on shared, stable conventions defined by the architecture (such as event and evidence structure), as opposed to the implementation of another engine.

## 8.2 Forbidden Dependencies

- An engine must not call another engine directly.
- An engine must not read another engine's internal state.
- An engine must not depend on the presence, absence, or output of another specific engine in order to function.
- An engine must not depend on the Decision Engine, Contradiction Engine, AI Explanation Engine, or Dashboard for its own analysis.
- The Contradiction Engine, Decision Engine, AI Explanation Engine, and Dashboard must not perform their own independent market analysis; they operate strictly on the outputs already produced by the Analysis Engines.

---

# 9. Error Handling Philosophy

| Principle | Description |
|---|---|
| Fail Fast | When a component receives invalid, incomplete, or inconsistent input, it must fail immediately and visibly rather than continuing with unreliable data. |
| Graceful Degradation | When a non-critical component fails, the rest of the system should continue operating and clearly indicate which intelligence is unavailable, rather than failing entirely. |
| Never Fabricate Data | No component may substitute assumed, estimated, or invented data for missing or failed data. Absence of data must be represented as absence, never disguised as a real observation. |
| Timestamp Everything | Every piece of data and every derived output must carry a timestamp indicating when it was produced, so that its freshness and sequence can always be verified. |
| Transparent Failures | Failures must be surfaced clearly to the trader through the Presentation Layer, rather than hidden or silently absorbed. |

---

# 10. Scalability Strategy

MIOS is designed so that new intelligence capabilities can be added without modifying existing engines. This is achieved by treating each Analysis Engine as an independent subscriber to, and publisher on, the Event Bus.

To add a new engine:

1. The new engine subscribes to the relevant events already published by the Market Store and Event Bus.
2. The new engine performs its own independent analysis, following the same architectural principles as existing engines (Section 2).
3. The new engine publishes its evidence-backed output to the Event Bus in the same manner as existing engines.
4. The Contradiction Engine and Decision Engine incorporate the new engine's output as an additional input, without requiring changes to any existing engine.

Because engines do not depend on one another (Section 8), and because all communication passes through the Market Store and Event Bus rather than direct calls, existing engines remain untouched when a new engine is introduced. This allows MIOS's intelligence coverage to grow incrementally while preserving the stability of the components already in production.

---

# 11. Security Considerations

At the architecture level, MIOS observes the following considerations. Implementation-level security controls are out of scope for this document.

- **Data Integrity**: The Market Store must be treated as the authoritative state of the system; only the Data Layer may write to it, preventing unauthorized or inconsistent state changes.
- **Boundary Control**: The Data Layer is the sole boundary through which external market data enters the system, allowing all validation and normalization concerns to be handled in one place.
- **Least Privilege Between Components**: Each component should have access only to the events and data it requires to fulfill its single responsibility, consistent with the Module Independence principles in Section 8.
- **Auditability**: Because every output is timestamped and traceable to its source evidence (Sections 6 and 9), the architecture inherently supports auditing of how any piece of intelligence was derived.
- **Separation of Analysis and Presentation**: Keeping analysis (Analysis Engines, Decision Layer) architecturally separate from presentation (Dashboard) reduces the risk of presentation-layer concerns influencing analytical integrity.

---

# 12. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Ready for Implementation

---

# 13. Architecture Decision Record

## ADR-001

**Decision:**
MIOS will use a layered, event-driven architecture, composed of a Data Layer, a Market Store, an Event Bus, independent Analysis Engines, a Decision Layer, and a Presentation Layer.

**Reason:**
MIOS's core product commitment is explainability: every piece of intelligence must be traceable to observable evidence (see [01-product.md](01-product.md)). A layered, event-driven design enforces this by requiring all market state to pass through a single normalized store and a shared event bus, rather than allowing components to share state or call each other directly. This structure keeps each engine independently understandable, testable, and auditable, and ensures that the system's intelligence output can always be traced back through a well-defined sequence of stages to its originating market data.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Monolithic analysis module handling all intelligence domains in one component | Violates single responsibility and high cohesion principles; would make individual analysis domains difficult to reason about, test, or explain in isolation. |
| Direct, synchronous calls between engines instead of an event bus | Creates tight coupling between engines, directly violating the Module Independence requirements in Section 8 and making it harder to add new engines without touching existing ones. |
| A single combined "Analysis and Decision" engine instead of separate Analysis, Contradiction, and Decision stages | Would obscure disagreement between domains of intelligence and undermine the ability to explain how a final decision-support view was reached. |

**Consequences:**

- All future engines must integrate through the Market Store and Event Bus, not through direct dependencies on other engines.
- Any proposed architectural change must be evaluated against the principles in Section 2 before being adopted.
- The fixed execution order defined in Section 7 must be preserved as new components are added, unless a future ADR explicitly revises it.

---

# Document Dependencies

This Architecture Specification depends on:

- 01-product.md

This document is referenced by:

- 04-data-layer.md
- 05-market-store.md
- 06-event-bus.md
- 07-price-engine.md
- 08-liquidity-engine.md
- 09-options-engine.md
- 10-momentum-engine.md
- 11-context-engine.md
- 12-contradiction-engine.md
- 13-decision-engine.md
- 14-ai-explanation-engine.md
- 15-api-specification.md
- 16-frontend.md

This document is the authoritative source for all architectural decisions in MIOS.

---

# Glossary

| Term | Meaning |
|------|---------|
| Data Layer | The only component allowed to communicate with external market data providers. |
| Market Store | The authoritative source of market state. |
| Event Bus | The communication backbone connecting all modules. |
| Analysis Engine | A deterministic module responsible for one market intelligence domain. |
| Decision Engine | The component responsible for combining intelligence into one market story. |
| AI Explanation Engine | Converts structured intelligence into human-readable explanations without changing its meaning. |
| Dashboard | Presentation layer used by the trader. |
| Event | A published notification describing a change in market state or intelligence. |

---

# Architecture Freeze

This architecture is considered locked after approval.

No future implementation may violate this document without an approved Architecture Decision Record (ADR).

New engines may be added.

Existing responsibilities may not be changed without formal review.

Layer boundaries are immutable unless revised by a future architecture document.

---

# 14. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-28 | MIOS Architecture | Initial System Architecture Specification for MIOS. |
