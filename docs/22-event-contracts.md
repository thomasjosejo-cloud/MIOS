---
id: EVENT-CONTRACTS-001
title: MIOS Event Contracts Specification
document: 22-event-contracts.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the canonical event model used for all asynchronous communication inside MIOS. It builds upon the Domain Model defined in [17-domain-model.md](17-domain-model.md), the canonical Market Model defined in [18-market-model.md](18-market-model.md), the canonical Analysis Model defined in [19-analysis-model.md](19-analysis-model.md), the canonical Decision Model defined in [20-decision-model.md](20-decision-model.md), and the canonical Explanation Model defined in [21-explanation-model.md](21-explanation-model.md).

Every service within MIOS communicates using canonical events, consistent with the event-driven architecture defined in [02-architecture.md](02-architecture.md) and the Event Bus specification in [06-event-bus.md](06-event-bus.md).

This document is technology independent. It becomes the single source of truth for every event published and consumed within MIOS, and defines canonical event contracts only.

---

# 2. Scope

This document covers the canonical representation of:

- Market Events
- Analysis Events
- Decision Events
- Explanation Events
- Platform Events
- Event Metadata
- Event Versioning
- Event Ordering
- Event Validation

---

# 3. Event Design Principles

| Principle | Description |
|---|---|
| Canonical First | Every event conforms to the Canonical Event Object defined in Section 5, regardless of category. |
| Immutable | An event's content never changes once published, consistent with [06-event-bus.md](06-event-bus.md). |
| Technology Independent | Event contracts are defined independently of any specific messaging technology or transport. |
| Replay Safe | Events can be replayed in their original order without ambiguity or altered meaning. |
| Traceable | Every event carries information sufficient to trace it back to its origin and any event that caused it. |
| Versioned | Every event carries a version, supporting safe evolution of event contracts over time. |
| Deterministic | The same underlying fact always produces an event with the same canonical shape. |
| Evidence Preserving | Events describing Analysis, Decision, or Explanation content preserve the evidence references defined in [19-analysis-model.md](19-analysis-model.md), [20-decision-model.md](20-decision-model.md), and [21-explanation-model.md](21-explanation-model.md). |
| Idempotent | Reprocessing the same event does not change the outcome beyond its first processing. |
| Consumer Independent | An event's shape does not depend on the identity or number of its consumers. |

---

# 4. Event Philosophy

- Event = Fact. An event describes something that has already occurred.
- Event ≠ Command. An event never instructs a component to perform an action.
- Event ≠ Request. An event never asks another component to do something on the publisher's behalf.
- Event ≠ Query. An event never requests information from another component.
- Event = Immutable record that something has occurred, consistent with the Event Philosophy defined in [06-event-bus.md](06-event-bus.md).

---

# 5. Canonical Event Object

| Attribute | Description |
|---|---|
| Event Identifier | A unique identifier for the event instance. |
| Event Type | The specific category of fact the event describes, per Sections 7 through 11. |
| Aggregate Type | The domain aggregate, per [17-domain-model.md](17-domain-model.md), that the event pertains to. |
| Aggregate Identifier | The identity of the specific aggregate instance the event describes. |
| Event Timestamp | The point in time the fact described by the event occurred. |
| Producer | The component that published the event. |
| Version | The version of the event's canonical contract. |
| Correlation Identifier | A shared reference linking this event to the broader chain of activity it belongs to. |
| Causation Identifier | A reference to the specific event, if any, that directly caused this event to be produced. |
| Metadata | Supporting descriptive information relevant to interpreting the event, per Section 12. |
| Validation Rules | The event must satisfy the Validation Rules defined in Section 16 before being considered valid. |

This section defines conceptual attributes only; it does not define a serialization format.

---

# 6. Event Categories

| Category | Description |
|---|---|
| Market Events | Events describing facts observed in the Market Domain, per [18-market-model.md](18-market-model.md). |
| Analysis Events | Events describing the publication of Assessments produced by the Analysis and Contradiction Engines, per [19-analysis-model.md](19-analysis-model.md). |
| Decision Events | Events describing the publication or lifecycle transitions of Decisions, per [20-decision-model.md](20-decision-model.md). |
| Explanation Events | Events describing the publication or lifecycle transitions of Explanations, per [21-explanation-model.md](21-explanation-model.md). |
| Platform Events | Events describing facts within the Platform Domain, per [17-domain-model.md](17-domain-model.md), such as User, Configuration, Alert, and Watchlist activity. |

---

# 7. Market Events

| Event | Purpose |
|---|---|
| Market Created | Records that a new Market has been onboarded into MIOS. |
| Instrument Created | Records that a new Instrument has been listed within a Market. |
| Tick Observed | Records that a new Tick has been received and validated for an Instrument. |
| Candle Finalized | Records that a Candle's interval has closed and its OHLC values are final. |
| Order Book Snapshot Recorded | Records that a new Order Book Snapshot has been captured for an Instrument. |
| Session Started | Records that a Trading Session has begun for a Market. |
| Session Closed | Records that a Trading Session has ended for a Market. |
| Calendar Updated | Records that a Market's Trading Calendar has been revised. |

---

# 8. Analysis Events

| Event | Purpose |
|---|---|
| Liquidity Assessment Published | Records that the Liquidity Engine has published a new Liquidity Assessment. |
| Options Assessment Published | Records that the Options Engine has published a new Options Assessment. |
| Momentum Assessment Published | Records that the Momentum Engine has published a new Momentum Assessment. |
| Context Assessment Published | Records that the Context Engine has published a new Context Assessment. |
| Contradiction Assessment Published | Records that the Contradiction Engine has published a new Contradiction Assessment. |

---

# 9. Decision Events

| Event | Purpose |
|---|---|
| Decision Published | Records that the Decision Engine has published a new Decision. |
| Decision Superseded | Records that a previously published Decision has been superseded by a newer one. |
| Decision Archived | Records that a Decision has transitioned to the Archived state. |

---

# 10. Explanation Events

| Event | Purpose |
|---|---|
| Explanation Published | Records that the AI Explanation Engine has published a new Explanation. |
| Explanation Superseded | Records that a previously published Explanation has been superseded by a newer one. |
| Explanation Archived | Records that an Explanation has transitioned to the Archived state. |

---

# 11. Platform Events

| Event | Purpose |
|---|---|
| User Created | Records that a new User account has been created. |
| Configuration Updated | Records that a User's or the platform's Configuration has changed. |
| Alert Generated | Records that a new Alert has been created for a User. |
| Watchlist Updated | Records that a User's Watchlist has changed. |

---

# 12. Event Metadata

| Attribute | Description |
|---|---|
| Producer | The component that published the event. |
| Correlation | The Correlation Identifier linking the event to the broader chain of activity it belongs to. |
| Causation | The Causation Identifier linking the event to the specific event that produced it, if any. |
| Version | The version of the event's canonical contract. |
| Schema Version | The version of the canonical model (Domain, Market, Analysis, Decision, or Explanation) the event's content conforms to. |
| Creation Time | The point in time the event itself was created, distinct from the Event Timestamp of the fact it describes. |
| Trace Identifier | An identifier supporting end-to-end tracing of the event's processing across components. |
| Source | The originating context (such as a specific engine or service instance) that produced the event. |

---

# 13. Event Lifecycle

| Stage | Description |
|---|---|
| Created | A component has produced an event describing a fact that has occurred. |
| Validated | The event has been confirmed to satisfy the Validation Rules defined in Section 16. |
| Published | The event has been submitted to the Event Bus and made available for delivery. |
| Consumed | A subscriber has received and processed the event. |
| Archived | The event is retained for historical or audit purposes after it is no longer actively needed by subscribers. |

---

# 14. Event Ordering

| Concept | Description |
|---|---|
| Chronological Ordering | Events are ordered according to the Event Timestamp of the fact they describe. |
| Aggregate Ordering | Events pertaining to the same Aggregate Identifier are delivered in the order they were produced for that aggregate. |
| Causation Ordering | An event is never delivered before the event that caused it, where a Causation Identifier is present. |
| Replay Ordering | Replaying a sequence of events preserves the same relative order as their original publication. |
| Duplicate Handling | A redelivered event is recognized by its Event Identifier and is not treated as a new, distinct fact. |

---

# 15. Event Versioning

| Concept | Description |
|---|---|
| Backward Compatibility | New versions of an event contract preserve the meaning of fields already relied upon by existing consumers wherever possible. |
| Schema Evolution | Event contracts may evolve over time to add new information without breaking existing consumers. |
| Deprecation | A version of an event contract that will be retired is clearly communicated before removal. |
| Migration | Consumers are given a defined path to adopt a new event contract version before an old version is retired. |
| Version Governance | Every change to an event contract's structure is tracked against the Version attribute defined in Section 5. |

---

# 16. Event Validation Rules

| Rule | Description |
|---|---|
| Unique Identity | Every event must carry a unique Event Identifier. |
| Timestamp Required | Every event must carry a valid Event Timestamp. |
| Aggregate Required | Every event must reference a valid Aggregate Type and Aggregate Identifier. |
| Producer Required | Every event must identify its Producer. |
| Version Required | Every event must carry a Version. |
| Immutable | An event's content does not change after it has been published. |
| Traceability Preserved | Every event must preserve its Correlation Identifier and, where applicable, its Causation Identifier. |

---

# 17. Event Relationships

| From | To | Relationship |
|---|---|---|
| Market | Market Events | A Market's lifecycle and state changes are recorded as Market Events. |
| Instrument | Tick Events | An Instrument's observed activity is recorded as Tick Observed events, among other Market Events. |
| Assessment | Analysis Events | Every published Liquidity, Options, Momentum, Context, or Contradiction Assessment is recorded as an Analysis Event. |
| Decision | Decision Events | Every published, superseded, or archived Decision is recorded as a Decision Event. |
| Explanation | Explanation Events | Every published, superseded, or archived Explanation is recorded as an Explanation Event. |
| Platform | Platform Events | Every User, Configuration, Alert, or Watchlist change is recorded as a Platform Event. |

---

# 18. Domain Constraints

- No mutable events. An event's content is fixed at the moment of publication.
- No commands. No event may instruct a component to perform an action.
- No requests. No event may ask another component to act on the publisher's behalf.
- No hidden state. Every event's meaning must be fully expressed within its own canonical structure.
- Immutable history. Published events are never altered or retracted; corrections are expressed as new events.
- Technology independent. This specification defines no transport, serialization, or messaging technology.

---

# 19. Governance

This Event Contracts Specification is owned by MIOS Architecture and serves as the single source of truth for the canonical shape of every event published and consumed within MIOS.

Any new Event Type must be added to the appropriate category in Sections 7 through 11 before it is used elsewhere.

Any change to the Canonical Event Object, Event Metadata, or Event Validation Rules requires an approved Architecture Decision Record (ADR).

Schema governance for individual event categories must preserve backward compatibility wherever possible, per the versioning principles in Section 15; where a conflict arises between an implementation and this document, this document takes precedence.

---

# 20. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Canonical
- [ ] Technology Independent
- [ ] Ready for Technical Design

---

# 21. ADR-001

**Decision:**
MIOS adopts canonical event contracts independent of transport technology.

**Reason:**
Defining event contracts at a canonical, technology-independent level ensures that every engine and service in MIOS agrees on the meaning and shape of events before any messaging technology is selected or implemented, consistent with the single source of truth and event-driven architecture principles defined in [02-architecture.md](02-architecture.md) and [06-event-bus.md](06-event-bus.md). This also ensures the platform's event model remains stable even if the underlying transport technology defined in [00-technology-stack.md](00-technology-stack.md) is ever revised.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Define event contracts directly in terms of a specific serialization format | Would couple the platform's canonical event meaning to a specific technology choice, making future transport changes disruptive to every engine. |
| Allow each engine to define its own event shape | Would risk inconsistent event structure across the platform, undermining the Contradiction Engine's and Decision Engine's ability to reliably consume upstream events. |
| Omit correlation and causation tracking from the canonical event model | Would undermine the traceability principle defined in [06-event-bus.md](06-event-bus.md) and make it difficult to reconstruct the chain of activity behind a given Decision or Explanation. |

**Consequences:**

- Every engine and service must produce and consume events conforming to the Canonical Event Object defined in Section 5.
- Any future messaging technology implementation must map cleanly onto the canonical event categories defined in Sections 7 through 11.
- New event types must be added to this specification before being introduced into the platform.

---

# 22. Dependencies

This Event Contracts Specification depends on:

- 17-domain-model.md
- 18-market-model.md
- 19-analysis-model.md
- 20-decision-model.md
- 21-explanation-model.md

This document is referenced by:

- Event Bus
- All Engines
- OpenAPI
- Database Design
- Frontend

---

# 23. Glossary

| Term | Meaning |
|------|---------|
| Event | An immutable canonical record that a fact has occurred within MIOS. |
| Event Type | The specific category of fact an event describes. |
| Aggregate Type | The domain aggregate an event pertains to, per [17-domain-model.md](17-domain-model.md). |
| Correlation Identifier | A shared reference linking an event to the broader chain of activity it belongs to. |
| Causation Identifier | A reference linking an event to the specific event that directly caused it. |
| Event Lifecycle | The sequence of stages an event passes through from creation to archival. |
| Event Ordering | The set of guarantees governing the sequence in which events are delivered and processed. |
| Event Versioning | The practice of evolving event contracts over time while preserving compatibility. |
| Idempotent | The property of an operation producing the same outcome even if repeated. |
| Replay | The act of reprocessing a previously published sequence of events. |

---

# 24. Event Contracts Freeze

This Event Contracts Specification becomes the authoritative canonical event model for MIOS after approval.

Every engine and service shall produce and consume events conforming to the Canonical Event Object, categories, metadata, and validation rules defined here.

Changes to this specification require an approved Architecture Decision Record (ADR).

---

# 25. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Event Contracts Specification for MIOS. |
