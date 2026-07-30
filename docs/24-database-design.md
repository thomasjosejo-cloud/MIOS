---
id: DATABASE-DESIGN-001
title: MIOS Database Design Specification
document: 24-database-design.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the canonical persistence architecture for MIOS. Persistence implements the canonical models already defined in [17-domain-model.md](17-domain-model.md) through [23-openapi-specification.md](23-openapi-specification.md) without redefining them; it is the architectural layer responsible for durably storing and retrieving canonical concepts, not for interpreting or altering their meaning.

This document remains technology independent. It becomes the single source of truth for database architecture across MIOS, and defines persistence architecture only — it does not define SQL, DDL, CREATE TABLE statements, indexes, ORM models, vendor-specific features, or migrations.

---

# 2. Scope

This document covers the canonical persistence architecture for:

- Market Persistence
- Analysis Persistence
- Decision Persistence
- Explanation Persistence
- Platform Persistence
- Audit Persistence
- Metadata Persistence

---

# 3. Database Design Principles

| Principle | Description |
|---|---|
| Canonical First | Persistence structures exist to store canonical concepts already defined in [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md); persistence never introduces new business meaning. |
| Consistency | Persisted data reflects a single, internally consistent representation of each canonical concept. |
| Immutability | Persisted historical concepts (Ticks, Candles, Order Book Snapshots, Assessments, Decisions, Explanations) are never modified once written. |
| Traceability | Every persisted record can be traced back to the canonical concept and evidence it represents. |
| Technology Independence | This architecture is defined independently of any specific database product or engine. |
| Separation of Concerns | Persistence is separated from business logic, analysis, and presentation, consistent with [02-architecture.md](02-architecture.md). |
| Integrity | Persisted data accurately reflects the canonical concept it represents, without corruption or drift. |
| Auditability | The history of persisted data can be reviewed and verified. |
| Version Awareness | Persisted data is associated with the version of the canonical model it conforms to. |
| Identity Preservation | A canonical concept's identity, once assigned, is preserved unchanged throughout its persisted lifecycle. |

---

# 4. Database Philosophy

- Database ≠ Domain Model. The database is not the definition of MIOS's business concepts; the Domain Model defined in [17-domain-model.md](17-domain-model.md) is.
- Database ≠ Business Logic. The database contains no analysis, synthesis, or decision-making logic.
- Database = Persistence of canonical concepts. The database exists solely to durably store and retrieve the canonical concepts already defined elsewhere in this documentation set.

Persistence never defines business meaning; it only preserves it.

---

# 5. Persistence Architecture

Persistence occupies the architectural role of durable storage beneath the Market Store and other stateful components defined in [02-architecture.md](02-architecture.md) and [05-market-store.md](05-market-store.md). It receives canonical concepts already validated and normalized upstream, and is responsible for storing them durably, retrieving them consistently, and preserving their historical integrity.

This document describes persistence at the architectural role level only. It does not describe physical database engines, storage products, or vendor-specific implementation details; those choices, informed by [00-technology-stack.md](00-technology-stack.md), belong to a future implementation-level document.

---

# 6. Canonical Persistence Objects

Persistence exists conceptually for each of the following canonical concepts, already defined in prior documents:

| Canonical Concept | Defined In |
|---|---|
| Market | [17-domain-model.md](17-domain-model.md), [18-market-model.md](18-market-model.md) |
| Instrument | [17-domain-model.md](17-domain-model.md), [18-market-model.md](18-market-model.md) |
| Tick | [17-domain-model.md](17-domain-model.md), [18-market-model.md](18-market-model.md) |
| Candle | [17-domain-model.md](17-domain-model.md), [18-market-model.md](18-market-model.md) |
| Order Book Snapshot | [17-domain-model.md](17-domain-model.md), [18-market-model.md](18-market-model.md) |
| Assessment | [17-domain-model.md](17-domain-model.md), [19-analysis-model.md](19-analysis-model.md) |
| Decision | [17-domain-model.md](17-domain-model.md), [20-decision-model.md](20-decision-model.md) |
| Explanation | [17-domain-model.md](17-domain-model.md), [21-explanation-model.md](21-explanation-model.md) |
| User | [17-domain-model.md](17-domain-model.md) |
| Alert | [17-domain-model.md](17-domain-model.md) |
| Watchlist | [17-domain-model.md](17-domain-model.md) |
| Configuration | [17-domain-model.md](17-domain-model.md) |
| Metadata | Supporting descriptive information attached to any of the above concepts. |

This document defines the persistence role of each concept only; it does not define their structural schema.

---

# 7. Storage Categories

| Category | Description |
|---|---|
| Operational Data | Data actively used to support current platform operation, such as the latest Market and Instrument state. |
| Reference Data | Relatively stable data describing Instruments, Markets, and Trading Calendars. |
| Historical Data | Immutable time-series data, such as Ticks, Candles, Order Book Snapshots, and published Assessments, Decisions, and Explanations. |
| Audit Data | Data recording the history of changes and access relevant to compliance and traceability. |
| Configuration Data | Data describing User and platform Configuration. |
| Metadata | Supporting descriptive information relevant to interpreting other stored data. |

---

# 8. Data Relationships

| From | To | Relationship |
|---|---|---|
| Market | Instrument | A Market's persisted record is associated with one or more persisted Instrument records. |
| Instrument | Tick, Candle, Order Book Snapshot | An Instrument's persisted record is associated with a chronological history of persisted Tick, Candle, and Order Book Snapshot records. |
| Instrument or Market | Assessment | An Instrument or Market's persisted record is associated with zero or more persisted Assessment records. |
| Assessment | Decision | A Decision's persisted record references the persisted Assessment records it synthesizes. |
| Decision | Explanation | A Decision's persisted record is associated with exactly one persisted Explanation record. |
| User | Watchlist, Configuration, Alert | A User's persisted record is associated with the Watchlist, Configuration, and Alert records it owns. |

These relationships are described conceptually; no entity-relationship diagrams are included in this specification.

---

# 9. Identity Strategy

| Principle | Description |
|---|---|
| Canonical Identifiers | Persisted records use the same identity defined by the canonical Identity Strategy in [17-domain-model.md](17-domain-model.md). |
| Stable Identities | A canonical concept's persisted identity remains stable for the lifetime of the record. |
| Immutable Identifiers | A persisted record's identifier is never reassigned or reused. |
| Cross-reference Support | Persisted records support reliable cross-referencing between related canonical concepts, consistent with the relationships defined in Section 8. |

---

# 10. Data Lifecycle

| Stage | Description |
|---|---|
| Created | A canonical concept is persisted for the first time. |
| Updated | A mutable canonical concept (such as a Configuration or Watchlist) is persisted with revised content. |
| Published | An immutable canonical concept (such as an Assessment, Decision, or Explanation) is persisted in its final, unchanging form. |
| Archived | A persisted record is retained for historical or audit reference, no longer part of active operational data. |
| Retained | A persisted record continues to be preserved in accordance with the retention strategy defined in Section 13. |

---

# 11. Consistency Model

| Principle | Description |
|---|---|
| Canonical Consistency | Persisted data always reflects the structure and meaning defined by the corresponding canonical model. |
| Referential Consistency | Every persisted reference between concepts (Section 8) resolves to a record that actually exists. |
| Temporal Consistency | Persisted historical data preserves the chronological order in which it occurred. |
| Version Consistency | Persisted data is associated with the version of the canonical model it was written against, supporting safe evolution over time. |

---

# 12. Transaction Principles

Persistence operations that affect the internal consistency of a single canonical concept (for example, publishing a Decision along with its references to Supporting Assessments) are completed as a single, all-or-nothing unit of work. This ensures that no downstream reader ever observes a canonical concept in a partially persisted or internally inconsistent state. Specific transactional mechanisms are outside the scope of this specification.

---

# 13. Retention Strategy

| Category | Retention Approach |
|---|---|
| Operational Retention | Operational Data is retained for as long as it remains the current, authoritative state of a canonical concept. |
| Historical Retention | Historical Data is retained to preserve the platform's complete, immutable market and intelligence record. |
| Audit Retention | Audit Data is retained for the period required to support traceability and compliance review. |
| Archival | Data no longer required for active operation is moved to archival storage while remaining recoverable for historical reference. |

---

# 14. Auditability

| Principle | Description |
|---|---|
| Traceability | Every persisted record can be traced back to the canonical concept and evidence it represents. |
| Lineage | The origin of a persisted record, including the engine or process that produced it, can be established. |
| Change History | Changes to mutable canonical concepts (such as Configuration) preserve a history of prior states. |
| Identity Preservation | A record's identity remains consistent throughout its lineage, supporting reliable audit trails. |

---

# 15. Versioning

| Concept | Description |
|---|---|
| Schema Evolution | The persistence structure supporting a canonical concept may evolve as the corresponding canonical model evolves. |
| Data Evolution | Existing persisted data may be migrated to reflect an evolved canonical model, without altering its original meaning. |
| Migration Principles | Migrations preserve the identity, traceability, and immutability guarantees defined in this document. |
| Compatibility | Persistence changes are managed to minimize disruption to components that depend on previously persisted data. |

---

# 16. Validation Rules

| Rule | Description |
|---|---|
| Canonical Identity Required | Every persisted record must carry the canonical identity defined by its corresponding model. |
| Immutable Identifiers | A persisted record's identifier must never change once assigned. |
| Traceability Preserved | Every persisted record must preserve its traceable link to the canonical concept and evidence it represents. |
| Referential Integrity | Every persisted reference between canonical concepts must resolve to an existing record. |
| Version Awareness | Every persisted record must be associated with the version of the canonical model it conforms to. |

---

# 17. Relationships

| From | To | Relationship |
|---|---|---|
| Database | Models | Persistence structures implement the canonical concepts defined in [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md). |
| Database | Events | Persisted state changes correspond to canonical events defined in [22-event-contracts.md](22-event-contracts.md). |
| Database | API | Resources exposed by the API, defined in [23-openapi-specification.md](23-openapi-specification.md), are ultimately backed by persisted data. |
| Database | Engines | Engines read and write canonical concepts through the Market Store, which is itself backed by this persistence architecture. |

---

# 18. Domain Constraints

- No business logic may reside in the persistence layer.
- No algorithms may be implemented within the persistence layer.
- No transport implementation details are defined in this specification.
- The persistence architecture remains technology independent.
- Only canonical persistence, already defined by the models referenced in this document, is described here.

---

# 19. Governance

This Database Design Specification is owned by MIOS Architecture and serves as the single source of truth for the canonical persistence architecture of MIOS.

Any new persisted concept must first be defined in the appropriate canonical model document before being added to this specification.

Schema governance for any future implementation-level database design must remain compatible with the canonical persistence objects, identity strategy, and consistency model defined here.

Any change to the Persistence Architecture, Storage Categories, or Consistency Model requires an approved Architecture Decision Record (ADR).

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
MIOS adopts a canonical persistence architecture independent of database technology.

**Reason:**
Defining persistence architecture at a canonical level, independent of any specific database engine, ensures that the meaning and structure of stored data remain governed by the Domain, Market, Analysis, Decision, and Explanation Models, rather than by the constraints of a particular database product. This preserves the single source of truth principle defined in [02-architecture.md](02-architecture.md) and ensures that a future change in database technology, per [00-technology-stack.md](00-technology-stack.md), does not require redefining what MIOS's data actually means.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Define persistence directly through vendor-specific schema and DDL | Would couple the platform's canonical concepts to a specific database product prematurely, and would blur the distinction between canonical meaning and physical storage. |
| Allow each engine to persist its own data independently | Would fragment the authoritative record of market and intelligence data across multiple, potentially inconsistent stores, violating the single source of truth principle defined in [05-market-store.md](05-market-store.md). |
| Omit an explicit consistency and identity strategy from the persistence architecture | Would risk referential and temporal inconsistency across persisted canonical concepts, undermining traceability and auditability. |

**Consequences:**

- Any future implementation-level database design must conform to the canonical persistence objects, identity strategy, and consistency model defined here.
- Database technology, as selected in [00-technology-stack.md](00-technology-stack.md), may evolve without requiring a redefinition of what MIOS's persisted data represents.
- Every persisted canonical concept must remain traceable, immutable where historical, and consistent with its corresponding canonical model.

---

# 22. Dependencies

This Database Design Specification depends on:

- 17-domain-model.md
- 18-market-model.md
- 19-analysis-model.md
- 20-decision-model.md
- 21-explanation-model.md
- 22-event-contracts.md
- 23-openapi-specification.md

This document is referenced by:

- Repositories
- ORM
- Database Migrations
- Technical Design

---

# 23. Glossary

| Term | Meaning |
|------|---------|
| Persistence | The architectural responsibility of durably storing and retrieving canonical concepts. |
| Operational Data | Data actively used to support current platform operation. |
| Reference Data | Relatively stable descriptive data, such as Instrument and Market definitions. |
| Historical Data | Immutable time-series and intelligence data retained for the platform's permanent record. |
| Audit Data | Data recording the history of changes and access for compliance and traceability. |
| Referential Integrity | The property that every reference between persisted records resolves to a record that exists. |
| Lineage | The traceable origin and history of a persisted record. |
| Schema Evolution | The process by which persistence structures change over time to reflect an evolved canonical model. |

---

# 24. Database Freeze

This Database Design Specification becomes the authoritative canonical persistence architecture for MIOS after approval.

Every future implementation-level database design shall conform to the canonical persistence objects, identity strategy, and consistency model defined here.

Changes to this specification require an approved Architecture Decision Record (ADR).

---

# 25. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Database Design Specification for MIOS. |
