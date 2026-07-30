---
id: MARKET-MODEL-001
title: MIOS Market Model Specification
document: 18-market-model.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the canonical representation of market data used throughout MIOS. It builds upon the technology baseline defined in [00-technology-stack.md](00-technology-stack.md) and the Market Domain aggregates introduced in [17-domain-model.md](17-domain-model.md) — Market, Instrument, Candle, Tick, Order Book Snapshot, and Session — giving each of them a precise, canonical shape.

Every engine in MIOS — the Price Engine, Liquidity Engine, Options Engine, Momentum Engine, and Context Engine, as well as the Data Layer and Market Store — consumes market information exclusively in the form defined by this model.

This document is the single source of truth for all market-related data structures used by every engine. It does not define database schemas, REST APIs, event payloads, implementation classes, or algorithms; it defines the canonical model those future Technical Design documents must implement.

---

# 2. Scope

This document covers the canonical representation of:

- Markets
- Instruments
- Sessions
- Ticks
- Candles
- Order Book Snapshots
- Trading Calendars
- Time
- Market Metadata
- Market Status

---

# 3. Design Principles

| Principle | Description |
|---|---|
| Single Source of Truth | Every engine and service references the same canonical definitions of Market, Instrument, and related concepts defined here. |
| Immutable Historical Data | Once recorded, a Tick, Candle, or Order Book Snapshot is never altered. |
| Chronological Integrity | Market data is always ordered consistently with the sequence in which it actually occurred. |
| Timezone Consistency | Time is represented and interpreted consistently across every component that consumes it. |
| Precision Preservation | Price, quantity, and time values retain the precision required for accurate historical and live analysis. |
| Deterministic Identity | Every canonical concept has an identity that can be derived consistently and does not change over its lifetime. |
| No Derived Intelligence | This model represents observed market fact only; it never contains interpretation, confidence, or synthesis, consistent with the Market Domain boundary defined in [17-domain-model.md](17-domain-model.md). |
| Evidence First | Every downstream Assessment traces back to concepts defined in this model, consistent with [01-product.md](01-product.md). |
| Replay Safe | The model supports faithful replay of historical market data without ambiguity. |
| Vendor Independent | The model is independent of any specific external data provider, consistent with [04-data-layer.md](04-data-layer.md). |

---

# 4. Core Concepts

| Concept | Description |
|---|---|
| Market | A distinct tradable market within MIOS, such as the Nifty Options market. |
| Instrument | A specific tradable contract or index within a Market. |
| Underlying | The instrument from which a derivative instrument's value is derived, such as an index. |
| Derivative | An instrument whose value is derived from an Underlying, such as a future or option. |
| Index | A representative measure of a market or segment, often serving as an Underlying. |
| Future | A derivative instrument obligating a trade of the Underlying at a future date. |
| Option | A derivative instrument granting the right, but not the obligation, to transact the Underlying at a defined Strike before or at Expiry. |
| Expiry | The date on which a derivative instrument ceases to be valid. |
| Strike | The price level at which an Option can be exercised. |
| Option Type | The classification of an Option as a call or a put. |
| Trading Session | A defined period of market activity within a Trading Calendar. |
| Trading Calendar | The definition of trading days, holidays, and session boundaries for a Market. |
| Exchange | The venue on which a Market's instruments are traded. |
| Timezone | The time reference frame in which a Market's sessions are defined. |
| Market Status | The current operational state of a Market, such as open or closed. |
| Instrument Status | The current operational state of an Instrument, such as active or expired. |

---

# 5. Canonical Market Object

| Attribute | Description |
|---|---|
| Identity | A unique, stable Market Identifier. |
| Display Name | A human-readable name for the Market. |
| Exchange | The Exchange on which the Market operates. |
| Timezone | The Timezone in which the Market's sessions are defined. |
| Trading Calendar | The Trading Calendar governing the Market's trading days and sessions. |
| Market Type | The classification of the Market, such as spot, futures, or options. |
| Status | The current Market Status. |
| Metadata | Supporting descriptive information about the Market, as defined in Section 12. |
| Lifecycle | Created when a Market is onboarded into MIOS; remains active indefinitely once onboarded, consistent with [17-domain-model.md](17-domain-model.md). |
| Validation Rules | A Market must have a unique Identity, an assigned Exchange, and an assigned Timezone. |

---

# 6. Canonical Instrument Object

| Attribute | Description |
|---|---|
| Instrument Identifier | A unique Identifier scoped within the owning Market. |
| Market | The Market to which the Instrument belongs. |
| Trading Symbol | The symbol by which the Instrument is traded. |
| Display Name | A human-readable name for the Instrument. |
| Asset Class | The classification of the Instrument, such as index, future, or option. |
| Underlying | The Underlying instrument, where applicable. |
| Expiry | The Expiry date, where applicable. |
| Strike | The Strike price, where applicable. |
| Option Type | The Option Type, where applicable. |
| Lot Size | The standard trading quantity unit for the Instrument. |
| Tick Size | The minimum price increment for the Instrument. |
| Currency | The currency in which the Instrument is denominated. |
| Status | The current Instrument Status. |
| Metadata | Supporting descriptive information specific to the Instrument. |
| Lifecycle | Created when an Instrument is listed; reaches end-of-life at Expiry for derivative instruments, or persists indefinitely for the Underlying, consistent with [17-domain-model.md](17-domain-model.md). |
| Validation Rules | An Instrument must reference exactly one Market. Lot Size and Tick Size must be positive. Expiry, Strike, and Option Type must be present for derivative instruments and absent otherwise. |

---

# 7. Canonical Tick Model

| Attribute | Description |
|---|---|
| Identity | The combination of Instrument, Timestamp, and Sequence. |
| Timestamp | The point in time the Tick was observed. |
| Instrument | The Instrument the Tick describes. |
| Price | The observed traded or quoted Price. |
| Volume | The observed traded Quantity, where applicable. |
| Sequence | A value distinguishing multiple Ticks sharing the same Timestamp, preserving order. |
| Source | A reference indicating the data flow that produced the Tick, independent of any specific external provider. |
| Validation | A Tick must carry a valid Timestamp, a valid Instrument reference, and a valid Price. |
| Ordering | Ticks for a given Instrument are always ordered chronologically by Timestamp and Sequence. |
| Immutability | A Tick is never modified once created, consistent with [17-domain-model.md](17-domain-model.md). |

---

# 8. Canonical Candle Model

| Attribute | Description |
|---|---|
| OHLC | The Open, High, Low, and Close Price observed over the Candle's interval. |
| Volume | The total traded Quantity observed over the Candle's interval. |
| Open Interest | The observed Open Interest at the close of the Candle's interval, where applicable. |
| VWAP | The volume-weighted average Price observed over the Candle's interval, where applicable. |
| Interval | The duration the Candle represents. |
| Start Time | The Timestamp at which the Candle's interval begins. |
| End Time | The Timestamp at which the Candle's interval ends. |
| Instrument | The Instrument the Candle describes. |
| Status | Indicates whether the Candle is still forming or has been finalized. |
| Identity | The combination of Instrument, Interval, and Start Time. |
| Validation | High is never less than Open, Close, or Low. Low is never greater than Open, Close, or High. |
| Lifecycle | Created once its interval closes; immutable once finalized, consistent with [17-domain-model.md](17-domain-model.md). |

---

# 9. Canonical Order Book Snapshot

| Attribute | Description |
|---|---|
| Snapshot Time | The Timestamp at which the Snapshot was captured. |
| Instrument | The Instrument the Snapshot describes. |
| Bid Levels | The observed bid-side price and quantity levels at the Snapshot Time. |
| Ask Levels | The observed ask-side price and quantity levels at the Snapshot Time. |
| Depth | The number of levels captured on each side of the Snapshot. |
| Sequence | A value distinguishing multiple Snapshots sharing the same Snapshot Time, preserving order. |
| Integrity Rules | Bid Levels and Ask Levels captured within a Snapshot are internally consistent with one another at the moment of capture. |
| Lifecycle | Created at each snapshot interval; immutable thereafter, consistent with [17-domain-model.md](17-domain-model.md). |

---

# 10. Trading Session Model

| Attribute | Description |
|---|---|
| Session Identifier | A unique Identifier scoped to a Market and calendar date. |
| Market | The Market to which the Session belongs. |
| Open Time | The Timestamp at which regular trading begins. |
| Close Time | The Timestamp at which regular trading ends. |
| Auction | Indicates whether the Session includes a pre-open or post-close auction period. |
| Breaks | Any defined intraday trading breaks within the Session. |
| Holiday | Indicates whether the Session's calendar date is a non-trading holiday. |
| Early Close | Indicates whether the Session closes earlier than its standard Close Time. |
| Status | The current operational state of the Session, aligned with the Market Status model in Section 13. |
| Lifecycle | Created at the start of a trading session; closed at the end of that session, consistent with [17-domain-model.md](17-domain-model.md). |

---

# 11. Trading Calendar

| Attribute | Description |
|---|---|
| Trading Days | The set of calendar dates on which a Market conducts regular trading. |
| Weekends | Calendar days excluded from trading by default, per the Market's Exchange convention. |
| Holidays | Specific calendar dates on which trading does not occur. |
| Exceptional Closures | Unscheduled or one-off dates on which trading is closed outside the standard Holidays list. |
| Special Sessions | Sessions with non-standard timing, such as a shortened or extended trading day. |
| Calendar Version | An identifier tracking revisions to a Market's Trading Calendar over time. |

---

# 12. Market Metadata

| Attribute | Description |
|---|---|
| Exchange | The Exchange associated with the Market. |
| Segment | The trading segment the Market belongs to within its Exchange. |
| Country | The country associated with the Market's Exchange. |
| Currency | The primary currency associated with the Market. |
| Timezone | The Timezone associated with the Market. |
| Market Type | The classification of the Market, as defined in Section 5. |
| Instrument Count | The number of Instruments currently active within the Market. |
| Supported Asset Classes | The set of Asset Classes tradable within the Market. |

---

# 13. Market Status Model

| Status | Description |
|---|---|
| Open | Regular trading is currently active. |
| Closed | The Market is not currently conducting trading. |
| Auction | The Market is currently in a price-discovery auction period. |
| Pre-open | The Market is in a preparatory period before regular trading begins. |
| Post-close | The Market is in a preparatory or settlement period after regular trading ends. |
| Halted | Trading has been temporarily stopped due to a defined condition, with an expectation of resuming. |
| Suspended | Trading has been stopped for an Instrument or Market pending further action. |
| Maintenance | The Market is unavailable due to scheduled operational maintenance. |

---

# 14. Time Model

| Principle | Description |
|---|---|
| UTC Storage | All Timestamps are stored in Coordinated Universal Time (UTC) to preserve a single, unambiguous chronological reference. |
| Exchange Local Time | Timestamps may be presented in a Market's local Exchange time for readability, derived from the stored UTC value. |
| Timezone Conversion | Conversion between UTC and Exchange Local Time is performed consistently using the Market's assigned Timezone. |
| Timestamp Precision | Timestamps retain sufficient precision to preserve the true ordering of market events. |
| Clock Synchronization | Timestamps reflect a consistently synchronized time source across the platform. |
| Chronological Ordering | All time-series concepts (Tick, Candle, Order Book Snapshot) are ordered strictly by their UTC Timestamp. |

---

# 15. Validation Rules

| Rule | Description |
|---|---|
| Tick Timestamp Required | Every Tick must carry a valid Timestamp. |
| OHLC Validity | Every Candle's Open, High, Low, and Close values must be internally consistent. |
| High >= Open, Close, Low | A Candle's High is never less than its Open, Close, or Low. |
| Low <= Open, Close, High | A Candle's Low is never greater than its Open, Close, or High. |
| Expiry Validity | An Instrument classified as a derivative with an Expiry must carry a valid, future-dated Expiry at the time of listing. |
| Strike Validity | An Option Instrument must carry a valid, positive Strike. |
| Lot Size Positive | Every Instrument's Lot Size must be a positive value. |
| Tick Size Positive | Every Instrument's Tick Size must be a positive value. |
| Unique Identity | Every Market, Instrument, Session, Tick, Candle, and Order Book Snapshot must have a unique Identity within its defined scope. |
| Immutable History | No Tick, Candle, or Order Book Snapshot may be modified once created. |

---

# 16. Market Relationships

| From | To | Relationship |
|---|---|---|
| Market | Instruments | A Market contains one or more Instruments. |
| Instrument | Ticks | An Instrument has a chronological history of Ticks. |
| Instrument | Candles | An Instrument has a chronological history of Candles across one or more Intervals. |
| Instrument | Order Book | An Instrument has a chronological history of Order Book Snapshots. |
| Market | Sessions | A Market has one Session per Trading Day. |
| Market | Calendar | A Market is governed by exactly one Trading Calendar. |
| Underlying | Derivatives | An Underlying Instrument may be referenced by one or more Derivative Instruments. |

---

# 17. Domain Constraints

- Historical data (Ticks, Candles, Order Book Snapshots) is immutable once recorded.
- No duplicate Ticks may exist for the same Instrument, Timestamp, and Sequence.
- No overlapping Candle intervals may exist for the same Instrument and Interval.
- Every Instrument has a single owning Market.
- Every Market is governed by exactly one Trading Calendar.
- Every Exchange is associated with exactly one Timezone.

---

# 18. Governance

This Market Model is owned by MIOS Architecture and serves as the single source of truth for canonical market data structures across the platform.

Any engine, service, or Technical Design document requiring a new market-related concept must propose it as an addition to this specification before it is used elsewhere.

Changes to an existing canonical object's attributes, identity, or validation rules require an approved Architecture Decision Record (ADR).

Any future database design, API contract, or event contract derived from this model must remain compatible with the canonical definitions in this document; where a conflict arises, this document takes precedence.

---

# 19. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Canonical
- [ ] Technology Independent
- [ ] Ready for Technical Design

---

# 20. ADR-001

**Decision:**
MIOS adopts a single canonical market model as the definitive representation of all market data used across the platform.

**Reason:**
A single canonical model ensures that every engine — Price, Liquidity, Options, Momentum, and Context — interprets Market, Instrument, Tick, Candle, and Order Book data identically, consistent with the single source of truth principle defined in [02-architecture.md](02-architecture.md) and the Market Domain boundary defined in [17-domain-model.md](17-domain-model.md). Without a canonical model, individual engines or services could adopt subtly different interpretations of the same market concepts, undermining explainability and cross-engine consistency.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Allow each engine to define its own market data representation | Would risk inconsistent interpretation of the same underlying market facts across engines, undermining the Contradiction Engine's ability to meaningfully compare their outputs. |
| Derive the market model directly from a specific vendor's data format | Would violate the vendor independence principle defined in [04-data-layer.md](04-data-layer.md) and couple the platform's core data representation to a single external provider. |
| Define market data structures only at the database or API layer | Would leave no canonical, technology-independent reference for engines and services to align on, risking drift between layers over time. |

**Consequences:**

- Every future database design, API contract, and event contract must conform to the canonical objects defined in this document.
- Any new market data concept must be added to this specification before implementation.
- Engines can rely on a consistent, well-defined representation of market data regardless of which external provider originally supplied it.

---

# 21. Dependencies

This Market Model Specification depends on:

- 00-technology-stack.md
- 17-domain-model.md

This document is referenced by:

- Every engine specification
- Database Design
- OpenAPI
- Event Contracts
- Algorithms

---

# 22. Glossary

| Term | Meaning |
|------|---------|
| Market | A distinct tradable market within MIOS. |
| Instrument | A specific tradable contract or index within a Market. |
| Underlying | The instrument from which a derivative instrument's value is derived. |
| Expiry | The date on which a derivative instrument ceases to be valid. |
| Strike | The price level at which an Option can be exercised. |
| Tick | A single observed market update for an Instrument at a point in time. |
| Candle | The Open, High, Low, and Close of an Instrument over a defined interval. |
| Order Book Snapshot | The observed state of bid and ask depth for an Instrument at a point in time. |
| Trading Session | A defined period of market activity within a Trading Calendar. |
| Trading Calendar | The definition of trading days, holidays, and session boundaries for a Market. |
| VWAP | Volume-weighted average price observed over a given interval. |
| Open Interest | The total number of outstanding derivative contracts for an Instrument. |
| Timezone | The time reference frame in which a Market's sessions are defined. |
| Market Status | The current operational state of a Market. |

---

# 23. Market Model Freeze

This Market Model becomes the authoritative canonical market model for MIOS after approval.

All engines, services, and Technical Design documents shall conform to the canonical objects, relationships, and validation rules defined here.

Changes to this model require an approved Architecture Decision Record (ADR).

---

# 24. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Market Model Specification for MIOS. |
