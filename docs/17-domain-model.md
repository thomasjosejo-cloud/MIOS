---
id: DOMAIN-001
title: MIOS Domain Model Specification
document: 17-domain-model.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document is the first Technical Design document in MIOS's Volume II. It defines the canonical business domain of MIOS: the aggregates, entities, value objects, relationships, and invariants that every engine, service, and interface in the platform must conform to.

The domain model translates the architectural roles defined in [02-architecture.md](02-architecture.md) and the responsibilities of each engine defined in [07-price-engine.md](07-price-engine.md) through [16-frontend.md](16-frontend.md) into a single, coherent set of business concepts. It is implementation-focused in the sense that it defines the concrete shape of the MIOS domain, but it remains technology-independent: it does not prescribe databases, APIs, events, or algorithms.

All subsequent Technical Design documents shall conform to this domain model.

---

# 2. Domain Modeling Principles

| Principle | Description |
|---|---|
| Single Domain Language | Every engine, service, and document must use the same names and meanings for domain concepts defined here. |
| Evidence-Backed Concepts | Domain concepts that represent intelligence must carry a reference to the evidence that supports them, consistent with [01-product.md](01-product.md). |
| Aggregate Consistency | Each aggregate defines its own internal consistency boundary; consistency across aggregates is achieved through the Event Bus, not shared mutable state. |
| Immutability of History | Domain concepts representing something that has already occurred are immutable once created. |
| Clear Ownership | Every domain concept has exactly one owning component responsible for creating and maintaining it. |
| No Hidden State | Domain concepts do not carry state or meaning that cannot be traced to an observable origin. |
| Separation of Fact and Interpretation | Domain concepts that represent raw market fact (such as a Candle or Tick) are modeled separately from domain concepts that represent interpretation (such as an Assessment). |

---

# 3. Core Domain Overview

The MIOS domain is organized around three broad domain groupings:

1. **Market Domain** — the raw, observable facts of the market: Market, Instrument, Candle, Tick, Order Book Snapshot.
2. **Intelligence Domain** — the evidence-backed interpretations produced by the engines defined in [02-architecture.md](02-architecture.md): Liquidity Assessment, Options Assessment, Momentum Assessment, Context Assessment, Contradiction Assessment, Decision Assessment, Explanation.
3. **Platform Domain** — the concepts that support trader use of the platform: Alert, Configuration, User, Watchlist, Session.

Every concept in the Intelligence Domain traces back to one or more concepts in the Market Domain. Every concept in the Platform Domain exists to help a trader access and configure their view of the Market and Intelligence Domains.

---

# 4. Domain Boundaries

| Domain Grouping | Boundary Description |
|---|---|
| Market Domain | Bounded by what has been observed in the market. Contains no interpretation, confidence, or synthesis. |
| Intelligence Domain | Bounded by the evidence-based observations and assessments produced by the Analysis, Contradiction, Decision, and AI Explanation Engines. Contains no raw market data ingestion logic. |
| Platform Domain | Bounded by concepts that exist to support trader interaction with MIOS. Contains no market analysis or intelligence generation. |

No concept may exist across more than one domain grouping. A concept requiring characteristics of two groupings must be modeled as related, distinct aggregates.

---

# 5. Aggregate Roots

Each aggregate below is described by its Purpose, Identity, Lifecycle, Ownership, and Invariants. Aggregates are the consistency boundary for the domain concepts they contain.

## 5.1 Market

| Attribute | Description |
|---|---|
| Purpose | Represents a distinct tradable market within MIOS (for example, the Nifty Options market). |
| Identity | A unique Market Identifier, stable for the lifetime of the market. |
| Lifecycle | Created when a market is onboarded into MIOS; remains active indefinitely once onboarded. |
| Ownership | Owned by the Data Layer and Market Store, defined in [04-data-layer.md](04-data-layer.md) and [05-market-store.md](05-market-store.md). |
| Invariants | A Market must have a unique identifier. A Market must contain at least one Instrument to be considered active. |

## 5.2 Instrument

| Attribute | Description |
|---|---|
| Purpose | Represents a specific tradable contract or index within a Market (for example, a specific option strike and expiry, a future, or the underlying index). |
| Identity | A unique Instrument Identifier, scoped within its owning Market. |
| Lifecycle | Created when an instrument is listed; for derivative instruments, reaches end-of-life at expiry; for the underlying, persists indefinitely. |
| Ownership | Owned by the Data Layer and Market Store. |
| Invariants | An Instrument belongs to exactly one Market. An Instrument's identity does not change over its lifecycle. |

## 5.3 Candle

| Attribute | Description |
|---|---|
| Purpose | Represents the Open, High, Low, and Close of an Instrument over a defined time interval. |
| Identity | The combination of Instrument, interval duration, and interval start time. |
| Lifecycle | Created once the corresponding time interval has closed; immutable thereafter. |
| Ownership | Owned by the Data Layer and Market Store. |
| Invariants | A Candle's High is never less than its Open, Close, or Low. A Candle's Low is never greater than its Open, Close, or High. A Candle, once finalized, is never modified. |

## 5.4 Tick

| Attribute | Description |
|---|---|
| Purpose | Represents a single observed market update for an Instrument at a point in time. |
| Identity | The combination of Instrument, timestamp, and sequence within that timestamp. |
| Lifecycle | Created upon receipt and validation by the Data Layer; immutable thereafter. |
| Ownership | Owned by the Data Layer and Market Store. |
| Invariants | A Tick always carries a Timestamp. A Tick is never modified after creation. Ticks for an Instrument are ordered chronologically. |

## 5.5 Order Book Snapshot

| Attribute | Description |
|---|---|
| Purpose | Represents the observed state of bid and ask depth for an Instrument at a point in time. |
| Identity | The combination of Instrument and snapshot timestamp. |
| Lifecycle | Created at each snapshot interval; immutable thereafter. |
| Ownership | Owned by the Data Layer and Market Store. |
| Invariants | A Snapshot always carries a Timestamp. A Snapshot's recorded levels are internally consistent with one another at the moment of capture. |

## 5.6 Liquidity Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents a structured, evidence-backed observation about liquidity conditions, produced by the Liquidity Engine. |
| Identity | A unique Assessment Identifier, associated with an Instrument and a point or window in time. |
| Lifecycle | Created when the Liquidity Engine publishes intelligence, per [08-liquidity-engine.md](08-liquidity-engine.md); immutable thereafter. |
| Ownership | Owned exclusively by the Liquidity Engine. |
| Invariants | A Liquidity Assessment always references the evidence that supports it. A Liquidity Assessment never references intelligence produced by another engine. |

## 5.7 Options Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents a structured, evidence-backed observation about options positioning and activity, produced by the Options Engine. |
| Identity | A unique Assessment Identifier, associated with an Instrument and a point or window in time. |
| Lifecycle | Created when the Options Engine publishes intelligence, per [09-options-engine.md](09-options-engine.md); immutable thereafter. |
| Ownership | Owned exclusively by the Options Engine. |
| Invariants | An Options Assessment always references the evidence that supports it. An Options Assessment never references intelligence produced by another engine. |

## 5.8 Momentum Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents a structured, evidence-backed observation about market movement, produced by the Momentum Engine. |
| Identity | A unique Assessment Identifier, associated with an Instrument and a point or window in time. |
| Lifecycle | Created when the Momentum Engine publishes intelligence, per [10-momentum-engine.md](10-momentum-engine.md); immutable thereafter. |
| Ownership | Owned exclusively by the Momentum Engine. |
| Invariants | A Momentum Assessment always references the evidence that supports it. A Momentum Assessment never references intelligence produced by another engine. |

## 5.9 Context Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents a structured, evidence-backed observation about the broader market environment, produced by the Context Engine. |
| Identity | A unique Assessment Identifier, associated with a Market or Instrument and a point or window in time. |
| Lifecycle | Created when the Context Engine publishes intelligence, per [11-context-engine.md](11-context-engine.md); immutable thereafter. |
| Ownership | Owned exclusively by the Context Engine. |
| Invariants | A Context Assessment always references the evidence that supports it. A Context Assessment never references intelligence produced by another engine. |

## 5.10 Contradiction Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents the evaluated relationship (agreement, contradiction, ambiguity, or evidence gap) between the outputs of two or more Analysis Engines, produced by the Contradiction Engine. |
| Identity | A unique Assessment Identifier, associated with the set of engine Assessments it evaluates. |
| Lifecycle | Created when the Contradiction Engine publishes intelligence, per [12-contradiction-engine.md](12-contradiction-engine.md); immutable thereafter. |
| Ownership | Owned exclusively by the Contradiction Engine. |
| Invariants | A Contradiction Assessment always references the specific Assessments it compares. A Contradiction Assessment never introduces new market observations. |

## 5.11 Decision Assessment

| Attribute | Description |
|---|---|
| Purpose | Represents the synthesized decision-support view combining engine Assessments and the Contradiction Assessment, produced by the Decision Engine. |
| Identity | A unique Assessment Identifier, associated with an Instrument or Market and a point in time. |
| Lifecycle | Created when the Decision Engine publishes intelligence, per [13-decision-engine.md](13-decision-engine.md); immutable thereafter. |
| Ownership | Owned exclusively by the Decision Engine. |
| Invariants | A Decision Assessment always references the upstream Assessments it synthesizes. A Decision Assessment never contains a buy, sell, or hold instruction. |

## 5.12 Explanation

| Attribute | Description |
|---|---|
| Purpose | Represents the human-readable narrative describing a Decision Assessment, produced by the AI Explanation Engine. |
| Identity | A unique Explanation Identifier, associated with exactly one Decision Assessment. |
| Lifecycle | Created when the AI Explanation Engine publishes an explanation, per [14-ai-explanation-engine.md](14-ai-explanation-engine.md); immutable thereafter. |
| Ownership | Owned exclusively by the AI Explanation Engine. |
| Invariants | An Explanation always references the Decision Assessment and evidence it describes. An Explanation never introduces meaning absent from the Decision Assessment it explains. |

## 5.13 Alert

| Attribute | Description |
|---|---|
| Purpose | Represents a notification that a specific, trader-defined or system-defined condition regarding published intelligence has occurred. An Alert is a pointer to intelligence that has already been produced; it is never itself a trading signal or recommendation. |
| Identity | A unique Alert Identifier, associated with a User and the intelligence that triggered it. |
| Lifecycle | Created when its defining condition is met; transitions to an acknowledged state once viewed by the User. |
| Ownership | Owned by the Platform Domain, on behalf of the User who configured or received it. |
| Invariants | An Alert always references the Assessment or Explanation that triggered it. An Alert never contains a buy, sell, or hold instruction. |

## 5.14 Configuration

| Attribute | Description |
|---|---|
| Purpose | Represents a set of preferences or settings governing how MIOS behaves for a User or for the platform as a whole. |
| Identity | A unique Configuration Identifier, scoped to either a User or the platform. |
| Lifecycle | Created when a User or administrator first sets a preference; updated as preferences change. |
| Ownership | Owned by the Platform Domain, on behalf of the User or platform administrator. |
| Invariants | A Configuration is always scoped to exactly one owner (a User or the platform). A Configuration never contains market intelligence. |

## 5.15 User

| Attribute | Description |
|---|---|
| Purpose | Represents a trader who uses MIOS, consistent with the target users defined in [01-product.md](01-product.md). |
| Identity | A unique User Identifier, stable for the lifetime of the account. |
| Lifecycle | Created upon account creation; may become inactive upon deactivation. |
| Ownership | Owned by the Platform Domain. |
| Invariants | A User has a unique identifier. A User owns their own Watchlists, Configurations, and Alerts. |

## 5.16 Watchlist

| Attribute | Description |
|---|---|
| Purpose | Represents a trader-curated collection of Instruments the trader wishes to monitor. |
| Identity | A unique Watchlist Identifier, scoped to its owning User. |
| Lifecycle | Created when a User first defines a watchlist; updated as Instruments are added or removed. |
| Ownership | Owned by exactly one User. |
| Invariants | A Watchlist belongs to exactly one User. A Watchlist references only valid, existing Instruments. |

## 5.17 Session

| Attribute | Description |
|---|---|
| Purpose | Represents a defined period of market activity (a trading session) against which market and intelligence data is organized, consistent with the session context described in [11-context-engine.md](11-context-engine.md). |
| Identity | A unique Session Identifier, scoped to a Market and a calendar date. |
| Lifecycle | Created at the start of a trading session; closed at the end of that session. |
| Ownership | Owned by the Data Layer and Market Store. |
| Invariants | A Session belongs to exactly one Market. A Session's boundaries do not change once the session has closed. |

---

# 6. Entities

The following entities exist within, and are owned by, the aggregates defined in Section 5. They have identity within their owning aggregate but are not independently addressable outside of it.

| Entity | Owning Aggregate | Description |
|---|---|---|
| Bid Level | Order Book Snapshot | A single observed price and quantity level on the bid side of the order book. |
| Ask Level | Order Book Snapshot | A single observed price and quantity level on the ask side of the order book. |
| Strike Observation | Options Assessment | A single observation of activity or positioning at a specific strike, referenced within an Options Assessment. |
| Watchlist Item | Watchlist | A single Instrument reference within a Watchlist, including the order or grouping the trader has assigned to it. |
| Configuration Setting | Configuration | A single named preference value within a Configuration. |

---

# 7. Value Objects

The following value objects are immutable, descriptive values used throughout the domain. They have no identity of their own and are defined entirely by their attributes.

| Value Object | Description |
|---|---|
| Price | A monetary value representing the traded or quoted level of an Instrument. |
| Quantity | A count representing volume, open interest, or order book depth. |
| Timestamp | A point in time associated with a domain concept, used to establish chronological order. |
| Time Window | A defined span of time bounded by a start and end Timestamp. |
| Confidence Level | A qualitative indication of how strongly evidence supports an Assessment. |
| Evidence Reference | A pointer from an Assessment or Explanation back to the specific market facts or upstream Assessments that support it. |
| Instrument Identifier | A stable value uniquely identifying an Instrument within its Market. |
| Market Identifier | A stable value uniquely identifying a Market. |
| Percentage | A proportional value used to describe relative change or composition. |

---

# 8. Domain Relationships

| From | To | Relationship |
|---|---|---|
| Market | Instrument | A Market contains one or more Instruments. |
| Market | Session | A Market has one or more Sessions over time. |
| Instrument | Candle | An Instrument has a history of Candles. |
| Instrument | Tick | An Instrument has a history of Ticks. |
| Instrument | Order Book Snapshot | An Instrument has a history of Order Book Snapshots. |
| Instrument | Liquidity Assessment | An Instrument is the subject of zero or more Liquidity Assessments over time. |
| Instrument | Options Assessment | An Instrument is the subject of zero or more Options Assessments over time. |
| Instrument | Momentum Assessment | An Instrument is the subject of zero or more Momentum Assessments over time. |
| Instrument or Market | Context Assessment | An Instrument or Market is the subject of zero or more Context Assessments over time. |
| Liquidity Assessment, Options Assessment, Momentum Assessment, Context Assessment | Contradiction Assessment | A Contradiction Assessment references two or more Assessments it evaluates. |
| Liquidity Assessment, Options Assessment, Momentum Assessment, Context Assessment, Contradiction Assessment | Decision Assessment | A Decision Assessment references the upstream Assessments it synthesizes. |
| Decision Assessment | Explanation | An Explanation references exactly one Decision Assessment. |
| Decision Assessment or Explanation | Alert | An Alert references the Assessment or Explanation that triggered it. |
| User | Watchlist | A User owns zero or more Watchlists. |
| User | Configuration | A User owns zero or more Configurations. |
| User | Alert | A User receives zero or more Alerts. |
| Watchlist | Instrument | A Watchlist references zero or more Instruments. |

---

# 9. Domain Invariants

| ID | Invariant |
|---|---|
| INV-001 | Every Assessment must reference the evidence that supports it. |
| INV-002 | No Assessment produced by one engine may reference the internal reasoning of another engine, only its published output. |
| INV-003 | Historical Market Domain concepts (Candle, Tick, Order Book Snapshot) are immutable once created. |
| INV-004 | Historical Intelligence Domain concepts (all Assessments, Explanation) are immutable once created. |
| INV-005 | No domain concept may represent a buy, sell, or hold instruction. |
| INV-006 | Every Instrument belongs to exactly one Market. |
| INV-007 | Every Watchlist, Configuration, and Alert belongs to exactly one User. |
| INV-008 | A Contradiction Assessment must reference at least two upstream Assessments. |
| INV-009 | A Decision Assessment must reference at least one upstream Assessment and the corresponding Contradiction Assessment, where one exists. |

---

# 10. Identity Strategy

| Concept Category | Identity Approach |
|---|---|
| Market Domain aggregates (Market, Instrument) | Identified by a stable, natural identifier assigned at creation, unique within its scope. |
| Time-series Market Domain aggregates (Candle, Tick, Order Book Snapshot, Session) | Identified by the combination of their owning Instrument or Market and their time boundary, reflecting their nature as observations at a point or interval in time. |
| Intelligence Domain aggregates (all Assessments, Explanation) | Identified by a unique Assessment or Explanation Identifier, generated at the time of publication, and always associated with the Instrument, Market, or upstream Assessments they describe. |
| Platform Domain aggregates (User, Watchlist, Configuration, Alert) | Identified by a unique identifier scoped to the owning User, where applicable. |

Identity, once assigned, never changes for the lifetime of a domain concept.

---

# 11. Lifecycle Rules

- Market Domain concepts are created upon observation and never modified afterward; they may only be superseded by newer observations.
- Intelligence Domain concepts are created upon publication by their owning engine and never modified afterward; a change in market conditions results in a new Assessment, not a modification of an existing one.
- Platform Domain concepts (User, Watchlist, Configuration) may be updated over time to reflect trader preference, but each update is a deliberate, trader-initiated action.
- Alerts transition from a created state to an acknowledged state, but the condition and triggering reference that created the Alert are never altered.
- No domain concept is ever deleted in a way that destroys traceability; retirement or archival preserves the historical record.

---

# 12. Consistency Rules

- Each aggregate is internally consistent at all times; its invariants (Section 9) must hold before any change is considered complete.
- Consistency between aggregates (for example, between an Instrument and its Assessments) is achieved through the Event Bus, per [06-event-bus.md](06-event-bus.md), not through shared mutable state.
- An Assessment is not considered valid until every aggregate it references (its Instrument, Market, or upstream Assessments) already exists.
- A Decision Assessment is not considered valid until all Assessments it synthesizes, and any relevant Contradiction Assessment, already exist.

---

# 13. Validation Rules

| Rule | Description |
|---|---|
| Identity Required | Every aggregate instance must have a valid, unique identity before it is considered part of the domain. |
| Evidence Required | Every Assessment and Explanation must carry at least one Evidence Reference. |
| Referential Validity | Every reference from one aggregate to another must resolve to an aggregate that actually exists. |
| Chronological Validity | Every Timestamp associated with a domain concept must be consistent with the chronological ordering of the aggregate's history. |
| Ownership Validity | Every Platform Domain aggregate must resolve to exactly one owning User or to the platform itself. |
| No Instruction Content | No aggregate may contain content representing a buy, sell, or hold instruction, consistent with [01-product.md](01-product.md). |

---

# 14. Domain Governance

This domain model is the single source of truth for MIOS business concepts.

No Technical Design document may introduce a domain concept that contradicts this model.

Any new aggregate, entity, or value object must be added to this specification before it is used elsewhere.

Any change to an existing aggregate's identity, lifecycle, ownership, or invariants requires an approved Architecture Decision Record (ADR).

Engines and services may extend this model with additional detail, but may not redefine concepts already established here.

---

# 15. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Architecture Compliant
- [ ] Technology Independent
- [ ] Consistent with Engine Specifications
- [ ] Ready for Technical Design

---

# 16. ADR-001

**Decision:**
MIOS shall adopt a single, explicit domain model organized around aggregates, entities, and value objects, separating raw Market Domain facts from Intelligence Domain assessments.

**Reason:**
An explicit, shared domain model ensures that every engine, service, and interface in MIOS uses the same concepts with the same meaning, consistent with the single source of truth and explainability principles defined in [02-architecture.md](02-architecture.md) and [01-product.md](01-product.md). Separating raw market fact from interpretation preserves the evidence-based nature of MIOS's intelligence: an Assessment can always be traced back to the Market Domain facts that produced it.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Anemic, implicit data model defined independently by each engine | Would allow each engine to define its own concepts and terminology, risking inconsistency and undermining the single source of truth required across the platform. |
| Single flat schema combining market facts and intelligence in one concept | Would blur the distinction between observed fact and interpretation, making it harder to guarantee that every Assessment is genuinely evidence-based. |
| Engine-specific private models with no shared domain layer | Would duplicate concepts such as Instrument and Timestamp across engines, and would make cross-engine relationships (such as those required by the Contradiction Engine) difficult to reason about consistently. |

**Consequences:**

- All Technical Design documents that follow must reference and conform to the aggregates, entities, and value objects defined here.
- Any engine or service requiring a new domain concept must propose it as an addition to this specification.
- The separation between Market Domain and Intelligence Domain must be preserved as the platform grows.

---

# 17. Document Dependencies

This Domain Model Specification depends on:

- 01-product.md
- 02-architecture.md
- 00-technology-stack.md
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

This document is referenced by every subsequent Technical Design document.

---

# 18. Glossary

| Term | Meaning |
|------|---------|
| Aggregate Root | A domain concept that defines its own consistency boundary and is the entry point for interacting with the concepts it owns. |
| Entity | A domain concept with identity scoped within its owning aggregate. |
| Value Object | An immutable domain concept defined entirely by its attributes, with no identity of its own. |
| Domain Invariant | A rule that must always hold true for a domain concept to be considered valid. |
| Identity | The stable, unique reference by which a domain concept is recognized over its lifetime. |
| Lifecycle | The sequence of states a domain concept passes through from creation onward. |
| Assessment | A structured, evidence-backed observation produced by an Analysis, Contradiction, or Decision Engine. |
| Evidence Reference | A pointer from an Assessment or Explanation to the specific facts or upstream Assessments that support it. |
| Market Domain | The grouping of domain concepts representing raw, observable market fact. |
| Intelligence Domain | The grouping of domain concepts representing evidence-backed interpretation of the Market Domain. |
| Platform Domain | The grouping of domain concepts supporting trader use of MIOS. |

---

# 19. Domain Freeze

This domain model becomes authoritative after approval.

All subsequent Technical Design documents shall conform to the aggregates, entities, value objects, and invariants defined here.

New domain concepts may be added as the platform grows.

Existing aggregates, their identity, lifecycle, ownership, and invariants may not be changed without an approved Architecture Decision Record (ADR).

---

# 20. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Domain Model Specification for MIOS. |
