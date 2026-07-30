---
id: DATA-001
title: MIOS Data Layer Specification
document: 04-data-layer.md
version: 1.0.0
status: Approved
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

The Data Layer is the only component in MIOS permitted to communicate with external market data providers. No other component — no Analysis Engine, no Contradiction Engine, no Decision Engine, no AI Explanation Engine, and no Dashboard — is permitted to read from or connect to an external market data source directly.

Every other module in MIOS receives normalized data only. Raw provider formats never leave the Data Layer. This isolates the rest of the system from the variability, quirks, and inconsistencies of external data sources, and ensures that all downstream intelligence is built on a single, consistent representation of market data.

The Data Layer is responsible only for ingestion, validation, and normalization of market data. It performs no analysis. It does not interpret market conditions, does not derive intelligence, and does not generate any output beyond a clean, validated, normalized, timestamped stream of market data events. Analysis of any kind belongs exclusively to the Analysis Engines defined in [02-architecture.md](02-architecture.md).

---

# 2. Responsibilities

| Responsibility | Description |
|---|---|
| Receive Market Data | Accept incoming market data from external market data providers as the sole point of external ingestion for the system. |
| Validate Data | Check every incoming unit of data against the validation rules defined in Section 6 before it is accepted into the system. |
| Normalize Data | Convert validated data from its incoming provider-specific form into the single, common internal format used throughout MIOS. |
| Timestamp Data | Attach a timestamp to every unit of data, recording when it was received and processed by the Data Layer. |
| Publish Events | Publish normalized, validated, timestamped data as events for consumption by downstream components. |
| Handle Connection Status | Track and report the current state of connectivity to external market data providers. |
| Report Errors | Surface validation failures, connection issues, and other data-related problems transparently rather than silently discarding them. |

---

# 3. Non Responsibilities

| Non-Responsibility | Description |
|---|---|
| No Analysis | The Data Layer does not interpret, evaluate, or draw conclusions from market data. |
| No Predictions | The Data Layer does not forecast or estimate future market behavior. |
| No Intelligence | The Data Layer does not produce structured intelligence of any kind; it produces normalized data only. |
| No Dashboard Logic | The Data Layer has no awareness of, or responsibility for, how data is presented to the trader. |
| No AI | The Data Layer does not apply machine learning, statistical modeling, or explanatory logic to the data it handles. |
| No Trading Decisions | The Data Layer has no role in trade execution, order routing, or trading decisions of any kind. |
| No Storage Decisions | The Data Layer does not decide how or where data is persisted; that responsibility belongs to the Market Store defined in [02-architecture.md](02-architecture.md). |

---

# 4. Data Sources

The Data Layer supports the following categories of market data sources:

- Spot Market
- Futures
- Options
- Market Breadth
- Volatility Index

No specific broker, vendor, exchange feed, or data provider is named or assumed by this specification. Provider-specific integration details are outside the scope of this document and are addressed, where necessary, in dedicated engineering documentation.

---

# 5. Data Types

The Data Layer ingests and normalizes the following categories of data:

| Data Type | Description |
|---|---|
| Price Data | The traded price of an instrument at a given point in time. |
| OHLC | Open, High, Low, and Close values for a given instrument over a defined time interval. |
| Volume | The quantity of an instrument traded over a defined time interval. |
| Open Interest | The total number of outstanding derivative contracts for a given instrument. |
| Bid | The highest price a buyer is currently willing to pay for an instrument. |
| Ask | The lowest price a seller is currently willing to accept for an instrument. |
| Spread | The difference between the Bid and Ask prices for an instrument. |
| Timestamp | The point in time at which a given unit of data was recorded or received. |
| Instrument Metadata | Identifying and descriptive information about an instrument (such as instrument type and expiry, where applicable). |

---

# Internal Data Contract

Every piece of normalized market data inside MIOS must conform to a single internal contract before it is published. This section describes the conceptual structure of that contract only; it does not define implementation fields.

| Contract Element | Description |
|------------------|-------------|
| Instrument Identity | Uniquely identifies the market instrument. |
| Event Type | Describes what type of market event this represents. |
| Timestamp | The authoritative event timestamp. |
| Market Values | Price, volume, open interest and other normalized values. |
| Metadata | Supporting information required by downstream modules. |
| Validation Status | Indicates whether validation completed successfully. |

Downstream modules must never receive provider-specific payloads.

---

# 6. Data Validation Rules

| Rule ID | Validation Rule | Handling |
|---|---|---|
| VAL-001 | Missing Timestamp | Rejected. Data without a timestamp cannot be ordered or trusted, and is discarded with an error report. |
| VAL-002 | Invalid Price | Rejected. A price value that is non-numeric, zero where not permitted, or outside a sane bound is discarded with an error report. |
| VAL-003 | Negative Volume | Rejected. Volume must be zero or positive; negative volume indicates a corrupted or malformed record and is discarded with an error report. |
| VAL-004 | Duplicate Tick | Detected and discarded. A tick already received and processed is not reprocessed or re-published as a new event. |
| VAL-005 | Corrupted Payload | Rejected. A payload that cannot be parsed into the expected structure is discarded with an error report and does not enter the Market Store. |
| VAL-006 | Unknown Instrument | Rejected. Data referencing an instrument not recognized by the system is discarded with an error report. |

Every validation failure is reported in accordance with the error handling philosophy defined in [02-architecture.md](02-architecture.md); data that fails validation is never silently dropped without a corresponding, transparent error report.

---

# 7. Normalization

All incoming data, regardless of its originating format, must be converted into a single, common internal format before it is accepted by the Data Layer. This normalization step exists because MIOS's downstream components — the Market Store, Event Bus, Analysis Engines, Decision Layer, and Presentation Layer — must be able to rely on one consistent structure for all market data, regardless of which external source produced it.

Downstream modules never consume raw provider formats. This guarantees that Analysis Engines and every other downstream component can be built, reasoned about, and validated against a single data contract, independent of how many external data sources the Data Layer may ingest from over time.

---

# 8. Event Publishing

Once data has been validated, normalized, and timestamped, the Data Layer publishes it as an event on the Event Bus, in accordance with the event-driven architecture defined in [02-architecture.md](02-architecture.md).

The Data Layer publishes events only. It never calls the Market Store, any Analysis Engine, the Contradiction Engine, the Decision Engine, the AI Explanation Engine, or the Dashboard directly. This preserves the low coupling required by the architecture: the Data Layer has no knowledge of which components, if any, consume the events it publishes.

---

# Event Publishing Rules

| Rule | Description |
|------|-------------|
| Publish Only Valid Data | Invalid data must never be published. |
| Immutable Events | Published events must never be modified after publication. |
| Ordered Events | Events must preserve market sequence. |
| Timestamp Preservation | Original timestamps must remain intact. |
| Provider Independence | Events must not expose provider-specific formats. |
| Event Traceability | Every event must be traceable back to its originating data source. |

These rules guarantee deterministic downstream processing.

---

# 9. Error Handling

| Concern | Description |
|---|---|
| Reconnect Strategy | Upon loss of connectivity to an external market data provider, the Data Layer attempts to reestablish the connection and resumes ingestion once connectivity is restored. |
| Validation Failure | Data that fails validation (Section 6) is discarded and reported as an error; it is never passed downstream in an invalid or assumed form. |
| Discard Policy | Data that is discarded is never fabricated, substituted, or estimated. Absence of valid data is represented as absence. |
| Logging | Every error, validation failure, and connection status change is logged with a timestamp to support traceability and auditing. |
| Monitoring | The connection and validation state of the Data Layer must be observable, so that data gaps or failures can be identified as they occur. |
| Recovery | Following a disruption, the Data Layer resumes normal ingestion, validation, and publishing without requiring manual reconstruction of missed data. |

---

# 10. Performance Requirements

| ID | Requirement |
|---|---|
| PERF-001 | The Data Layer must process and publish incoming market data with low latency, suitable for use during live, time-sensitive trading sessions. |
| PERF-002 | Given identical input data, the Data Layer must produce identical normalized output, in accordance with the deterministic principle defined in [02-architecture.md](02-architecture.md). |
| PERF-003 | The Data Layer must perform no blocking operations that would delay the ingestion or publishing of subsequent market data. |
| PERF-004 | The Data Layer must preserve consistent ordering of market data events relative to the order in which the underlying data occurred. |

---

# 11. Constraints

| Constraint | Description |
|---|---|
| Only External Communication Layer | The Data Layer is the only component permitted to communicate with external market data providers. |
| No Business Logic | The Data Layer applies no business or trading logic to the data it processes. |
| No Intelligence Generation | The Data Layer does not generate market intelligence of any kind. |
| No Persistence Decisions | The Data Layer does not determine how or where data is stored; this is the responsibility of the Market Store. |
| No Engine Dependencies | The Data Layer does not depend on, call, or have knowledge of any Analysis Engine, the Contradiction Engine, the Decision Engine, the AI Explanation Engine, or the Dashboard. |

---

# Data Layer Governance

The Data Layer is governed by the following principles.

Every external integration must terminate inside the Data Layer.

No downstream component may bypass the Data Layer.

No provider-specific logic may exist outside the Data Layer.

Normalization rules must remain consistent for every provider.

Every change affecting normalization requires architectural review.

---

# 12. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Ready for Implementation

---

# 13. ADR-001

**Decision:**
The Data Layer is the single gateway for all external market data entering MIOS.

**Reason:**
Restricting external communication to a single component ensures that data validation and normalization occur in exactly one place, guaranteeing that every downstream component operates on the same consistent, trustworthy representation of market data. This directly supports the architecture principles of low coupling and explainability defined in [02-architecture.md](02-architecture.md), and prevents inconsistent or unvalidated data from entering the system through multiple uncoordinated paths.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Allow individual Analysis Engines to connect directly to external data sources | Would duplicate validation and normalization logic across engines, introduce inconsistency between engines, and violate the single-responsibility and low-coupling principles of the architecture. |
| Allow the Market Store to ingest directly from external sources | Would conflate the responsibility of maintaining authoritative market state with the responsibility of validating and normalizing external input, violating single responsibility. |
| Permit multiple, independently configured ingestion points across the system | Would make it difficult to guarantee consistent validation rules and normalized formats, undermining trust in the data used by every downstream component. |

**Consequences:**

- Every new external market data source must be integrated through the Data Layer, not through any other component.
- Any future requirement for a new category of market data must first be reflected in this specification's Data Sources (Section 4) and Data Types (Section 5).
- Downstream components can be developed and reasoned about without needing to account for provider-specific data formats.

---

# 14. Document Dependencies

This Data Layer Specification depends on:

- 01-product.md
- 02-architecture.md

This document is referenced by:

- 05-market-store.md
- 06-event-bus.md
- 07-price-engine.md
- 08-liquidity-engine.md
- 09-options-engine.md
- 10-momentum-engine.md
- 11-context-engine.md
- 12-contradiction-engine.md
- 13-decision-engine.md

---

# 15. Glossary

| Term | Meaning |
|------|---------|
| Data Layer | The only component permitted to communicate with external market data providers. |
| Ingestion | The process of receiving raw market data from an external source. |
| Validation | The process of checking incoming data against defined rules before it is accepted. |
| Normalization | The process of converting validated data into MIOS's common internal format. |
| Tick | A single unit of market data representing an update at a point in time. |
| OHLC | Open, High, Low, Close — the four price points describing an instrument over an interval. |
| Open Interest | The total number of outstanding derivative contracts for an instrument. |
| Spread | The difference between the Bid and Ask price of an instrument. |
| Event | A published notification carrying normalized market data or intelligence to downstream components. |

---

# Data Layer Freeze

This specification is considered locked after approval.

Future market data providers may be added.

Existing responsibilities may not be modified.

The Data Layer must remain the exclusive gateway for external market data.

Any deviation requires an approved Architecture Decision Record (ADR).

---

# 16. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Data Layer Specification for MIOS. |
