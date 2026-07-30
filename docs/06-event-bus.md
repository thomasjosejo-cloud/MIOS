---
id: EVENT-001
title: MIOS Event Bus Specification
document: 06-event-bus.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Event Bus is the communication backbone of MIOS. Every module in the system communicates through events rather than through direct calls to one another, in accordance with the event-driven architecture defined in [02-architecture.md](02-architecture.md).

The Event Bus enables loose coupling between components: a publisher of an event has no knowledge of which components, if any, consume it, and a consumer of an event has no knowledge of the internal logic that produced it. This separation is what allows the Data Layer, the Market Store, every Analysis Engine, the Contradiction Engine, the Decision Engine, the AI Explanation Engine, and the Dashboard to evolve independently of one another.

The Event Bus performs no business logic, no analysis, and no decision making. Its sole responsibility is to carry events reliably, in order, from publishers to subscribers.

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Receive Published Events | Accept events published by any authorized component within MIOS. |
| Distribute Events | Deliver published events to every component subscribed to receive them. |
| Maintain Delivery Order | Preserve the order in which events were published when delivering them to subscribers. |
| Support Multiple Subscribers | Allow more than one component to subscribe to and receive the same event independently. |
| Provide Event Isolation | Ensure that the processing of an event by one subscriber does not affect its delivery to, or processing by, another subscriber. |
| Support Independent Processing | Allow each subscriber to process delivered events at its own pace, without being blocked by other subscribers. |
| Support Scalable Communication | Allow new publishers and subscribers to be introduced without requiring changes to existing ones. |
| Maintain Event Traceability | Preserve the ability to trace a delivered event back to its original publication. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No Analysis | The Event Bus does not interpret or evaluate the content of any event. |
| No Market Intelligence | The Event Bus does not produce market intelligence of any kind. |
| No Business Logic | The Event Bus applies no business or trading logic to the events it carries. |
| No Persistence | The Event Bus is not responsible for the authoritative storage of market data; that responsibility belongs to the Market Store, defined in [05-market-store.md](05-market-store.md). |
| No Dashboard Logic | The Event Bus has no awareness of how events are ultimately presented to the trader. |
| No AI | The Event Bus applies no machine learning or explanatory logic to events. |
| No Trading Decisions | The Event Bus has no role in trade execution or trading decisions of any kind. |
| No Event Modification | The Event Bus does not alter the content of an event between publication and delivery. |

---

# 4. Event Philosophy

Events describe facts that have already occurred. An event is a record of something that happened — a market update, a piece of intelligence produced by an engine, or a change in system state — not a statement about what will happen next.

Events are immutable. Once an event has been published, its content does not change. Events represent historical truth: they are the permanent record of what the system observed or produced at a given moment. Events never predict future behaviour.

Event immutability is critical because every downstream component in MIOS — every Analysis Engine, the Contradiction Engine, the Decision Engine, and the AI Explanation Engine — relies on the events it consumes being a faithful, unaltered record of what actually occurred. If an event could be modified after publication, no downstream component could trust that its analysis was based on the same facts observed by any other component, undermining the explainability and determinism principles defined in [02-architecture.md](02-architecture.md).

---

# 5. Event Categories

The Event Bus carries the following conceptual categories of events. This section describes categories only; it does not define payloads.

- Market Data Events
- Market State Events
- Analysis Events
- Decision Events
- AI Explanation Events
- System Events
- Monitoring Events

---

# 6. Publishers

| Publisher | Published Events |
|---|---|
| Data Layer | Normalized market data events, as defined in [04-data-layer.md](04-data-layer.md). |
| Market Store | Market state events reflecting changes to the authoritative market record. |
| Price Engine | Price-related intelligence events. |
| Liquidity Engine | Liquidity-related intelligence events. |
| Options Engine | Options-related intelligence events. |
| Momentum Engine | Momentum-related intelligence events. |
| Context Engine | Context-related intelligence events. |
| Contradiction Engine | Events describing agreement or conflict among Analysis Engine outputs. |
| Decision Engine | Events carrying the synthesized intelligence summary. |
| AI Explanation Engine | Events carrying plain-language explanations of synthesized intelligence. |

Publishers know nothing about subscribers. A publisher's responsibility ends once it has published an event to the Event Bus.

---

# 7. Subscribers

| Subscriber | Consumes |
|---|---|
| Market Store | Normalized market data events published by the Data Layer. |
| Price Engine | Market state events relevant to price analysis. |
| Liquidity Engine | Market state events relevant to liquidity analysis. |
| Options Engine | Market state events relevant to options analysis. |
| Momentum Engine | Market state events relevant to momentum analysis. |
| Context Engine | Market state events relevant to context analysis. |
| Contradiction Engine | Intelligence events published by all Analysis Engines. |
| Decision Engine | Events published by the Contradiction Engine. |
| AI Explanation Engine | Events published by the Decision Engine. |
| Dashboard | Events published by the AI Explanation Engine. |

Subscribers never communicate directly with publishers. All communication passes through the Event Bus.

---

# 8. Event Lifecycle

| Stage | Description |
|---|---|
| Created | A component produces an event describing a fact that has occurred. |
| Published | The event is submitted to the Event Bus for distribution. |
| Delivered | The Event Bus makes the event available to every subscribed component. |
| Consumed | A subscriber receives and begins processing the event. |
| Completed | A subscriber finishes processing the event. |
| Archived (if applicable) | The event is retained in accordance with applicable retention policy after it is no longer actively needed. |

---

# 9. Event Delivery Rules

| Rule | Description |
|---|---|
| Immutable Events | An event's content does not change after it has been published. |
| Ordered Delivery | Events are delivered to each subscriber in the order they were published. |
| No Modification | No component, including the Event Bus itself, may alter an event after publication. |
| Independent Consumption | Each subscriber consumes and processes events independently of other subscribers. |
| Publisher Independence | A publisher's operation does not depend on the presence or state of any subscriber. |
| Subscriber Independence | A subscriber's operation does not depend on the presence or state of any other subscriber. |
| Retry Behaviour | Delivery of an event may be retried in the event of a transient failure, without altering the event's content. |
| Duplicate Protection | The same event is not processed by a subscriber more than once as a result of a redelivery. |
| Traceability | Every delivered event can be traced back to its original publication. |

---

# 10. Event Ordering

Deterministic ordering matters because MIOS's architecture depends on every component processing the same sequence of facts in the same order, in order to remain explainable and reproducible.

| Principle | Description |
|---|---|
| Chronological Order | Events are delivered in the order the facts they describe actually occurred. |
| Same Input → Same Processing | Given the same ordered sequence of events, a component's processing must produce the same result, consistent with the deterministic principle in [02-architecture.md](02-architecture.md). |
| Consistent Replay | Replaying the same sequence of events must produce the same outcome as the original processing. |
| Deterministic Execution | Components must not depend on event arrival timing beyond the guaranteed order, avoiding non-deterministic behaviour. |

---

# 11. Reliability Principles

| Principle | Description |
|---|---|
| Reliable Delivery | Published events are delivered to all subscribed components. |
| Fault Isolation | A failure in one subscriber's processing does not affect delivery to, or processing by, other subscribers. |
| Independent Failures | The failure of one publisher or subscriber does not cascade into the failure of unrelated components. |
| Retry Strategy | Transient delivery failures are retried without duplicating or altering event content. |
| Error Visibility | Delivery and processing failures are made visible rather than silently absorbed, consistent with the transparent failure principle in [02-architecture.md](02-architecture.md). |
| Monitoring | The health and throughput of event delivery can be observed. |
| Recovery | The Event Bus can resume normal operation following a disruption without requiring manual reconstruction of missed events. |

These principles are described conceptually; specific reliability mechanisms are outside the scope of this specification.

---

# 12. Constraints

| Constraint | Description |
|---|---|
| No Business Logic | The Event Bus applies no business or trading logic to events. |
| No Intelligence | The Event Bus does not generate market intelligence. |
| No Event Mutation | The Event Bus does not alter event content between publication and delivery. |
| No Direct Engine Calls | The Event Bus does not permit or facilitate direct calls between engines. |
| No Provider Awareness | The Event Bus has no knowledge of external market data providers. |
| No Storage Decisions | The Event Bus does not determine how or where market data is persisted. |
| No Trading Decisions | The Event Bus has no role in trade execution or trading decisions of any kind. |

---

# 13. Event Bus Governance

Every inter-module communication inside MIOS must occur through the Event Bus unless explicitly defined otherwise in Architecture ADRs.

Publishers cannot know subscribers.

Subscribers cannot depend on publishers.

Events are immutable.

Event ordering must remain deterministic.

Every event must be traceable.

---

# 14. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Architecture compliant
- [ ] Deterministic
- [ ] Loosely coupled
- [ ] Traceable
- [ ] Ready for implementation

---

# 15. ADR-001

**Decision:**
MIOS shall use an event-driven architecture for inter-module communication.

**Reason:**
An event-driven architecture allows every component in MIOS to remain independently understandable, testable, and replaceable, consistent with the modularity, low coupling, and single responsibility principles defined in [02-architecture.md](02-architecture.md). By requiring all communication to pass through the Event Bus rather than direct calls, no component is required to know about the internal implementation of another, and new components can be introduced without modifying existing ones, consistent with the scalability strategy in [02-architecture.md](02-architecture.md).

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Direct engine calls | Would create tight coupling between components, requiring each engine to know about the interfaces of every other engine it calls, directly violating the Module Independence requirements in [02-architecture.md](02-architecture.md). |
| Shared memory | Would allow components to read or modify shared state without a traceable record of how or when that state changed, undermining event immutability and traceability. |
| Polling architecture | Would introduce unnecessary latency and unpredictable processing delays, and would make deterministic, ordered processing of market facts significantly harder to guarantee. |

**Consequences:**

- All new components must integrate with MIOS exclusively through the Event Bus.
- Any exception to event-driven communication must be documented through a new, approved Architecture Decision Record.
- Component design must assume that publishers and subscribers may be added or changed independently over time.

---

# 16. Document Dependencies

This Event Bus Specification depends on:

- 01-product.md
- 02-architecture.md
- 04-data-layer.md
- 05-market-store.md

This document is referenced by:

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

---

# 17. Glossary

| Term | Meaning |
|------|---------|
| Event | A published record of a fact that has already occurred within MIOS. |
| Publisher | A component that produces and publishes events to the Event Bus. |
| Subscriber | A component that receives and processes events from the Event Bus. |
| Immutable Event | An event whose content cannot be changed once published. |
| Delivery | The act of making a published event available to a subscriber. |
| Consumption | The act of a subscriber receiving and processing a delivered event. |
| Replay | The act of reprocessing a previously published sequence of events. |
| Ordering | The guarantee that events are delivered in the sequence they were published. |
| Traceability | The ability to trace a delivered event back to its original publication. |
| Loose Coupling | A design property in which components interact without depending on one another's internal implementation. |

---

# 18. Event Bus Freeze

This specification becomes authoritative after approval.

Future messaging technologies may change.

The architectural role of the Event Bus may not change.

Events shall remain immutable.

Inter-module communication shall remain event-driven unless superseded by an approved Architecture Decision Record (ADR).

---

# 19. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Event Bus Specification for MIOS. |
