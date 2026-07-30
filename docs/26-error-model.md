---
id: ERROR-MODEL-001
title: MIOS Error Model Specification
document: 26-error-model.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the canonical error architecture used throughout MIOS. It builds upon the aggregates and canonical models defined in [17-domain-model.md](17-domain-model.md) through [24-database-design.md](24-database-design.md), and the lifecycle architecture defined in [25-state-machine-specification.md](25-state-machine-specification.md).

Every component communicates failures through canonical error concepts rather than through implementation-specific mechanisms. This document remains technology independent and becomes the single source of truth for all errors generated, propagated, stored, and exposed within MIOS. It defines canonical error architecture only — it does not define HTTP status codes, exception classes, programming language exceptions, framework-specific error handling, logging implementation, or retry implementation.

---

# 2. Scope

This document covers the canonical architecture for:

- Validation errors
- Domain errors
- Infrastructure errors
- Integration errors
- Security errors
- Error lifecycle
- Error classification
- Error traceability

---

# 3. Error Design Principles

| Principle | Description |
|---|---|
| Canonical First | Every error conforms to the Canonical Error Object defined in Section 5, regardless of category. |
| Deterministic | The same underlying failure condition always produces an error with the same canonical classification. |
| Traceable | Every error carries information sufficient to trace it back to its origin and any error that caused it. |
| Immutable | An error's canonical record, once produced, is never altered. |
| Technology Independent | Error contracts are defined independently of any specific programming language, framework, or transport. |
| Consistent | Errors of the same category are classified and structured consistently across every component. |
| Version Aware | Every error is associated with a version, supporting safe evolution of the error taxonomy over time. |
| Auditable | The history of errors across the platform can be reviewed and verified. |
| Consumer Independent | An error's canonical shape does not depend on the identity of the component that ultimately handles it. |
| Single Source of Truth | This document is the sole authority for the categories and structure of errors across MIOS. |

---

# 4. Error Philosophy

- Error = Canonical description of failure. An error is a structured, traceable record that something did not proceed as expected.
- Error ≠ Exception. This model does not define a programming language exception type.
- Error ≠ HTTP status. This model does not define an HTTP status code or response convention.
- Error ≠ Log entry. This model does not define a logging format or implementation.
- Error ≠ Retry strategy. This model does not define how or whether a failed operation is retried.

---

# 5. Canonical Error Object

| Attribute | Description |
|---|---|
| Error Identifier | A unique identifier for the error instance. |
| Error Category | The canonical category the error belongs to, per Section 6. |
| Origin | The component or aggregate concept, per [17-domain-model.md](17-domain-model.md), where the error originated. |
| Timestamp | The point in time the error occurred. |
| Severity | The classified severity of the error, per Section 13. |
| Correlation Identifier | A shared reference linking the error to the broader chain of activity it belongs to, consistent with [22-event-contracts.md](22-event-contracts.md). |
| Causation Identifier | A reference to the specific error or event, if any, that directly caused this error. |
| Metadata | Supporting descriptive information relevant to interpreting the error. |
| Version | The version of the canonical error taxonomy the error conforms to. |
| Validation Rules | The error must satisfy the Validation Rules defined in Section 16 before being considered a valid canonical error record. |

---

# 6. Error Categories

| Category | Description |
|---|---|
| Validation | Errors arising when data or a request does not conform to a canonical model defined elsewhere in this documentation set. |
| Domain | Errors arising when an operation would violate a domain invariant or lifecycle rule. |
| Infrastructure | Errors arising from the failure of a persistence, messaging, storage, or compute dependency. |
| Integration | Errors arising from failures at a boundary with an external system or data provider. |
| Security | Errors arising from failures of authentication, authorization, integrity, or confidentiality. |

---

# 7. Validation Errors

Validation errors arise when data presented to a component does not conform to the canonical structure, attributes, or rules defined in [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md). This includes, conceptually:

- A request or record missing a required canonical attribute.
- A value that violates a canonical Validation Rule, such as those defined in [18-market-model.md](18-market-model.md) or [19-analysis-model.md](19-analysis-model.md).
- A reference to another canonical concept that does not resolve to an existing instance.

---

# 8. Domain Errors

Domain errors arise when an operation would violate a business rule, invariant, or lifecycle constraint already established elsewhere in this documentation set. This includes, conceptually:

- An attempted state transition not permitted by the lifecycle defined in [25-state-machine-specification.md](25-state-machine-specification.md).
- An attempted modification of an immutable concept, such as a Published Assessment, Decision, or Explanation.
- A violation of a Domain Invariant defined in [17-domain-model.md](17-domain-model.md).

---

# 9. Infrastructure Errors

Infrastructure errors arise when a persistence, messaging, storage, or compute dependency fails to complete an operation as expected. This includes, conceptually:

- A failure to persist or retrieve a canonical concept, per [24-database-design.md](24-database-design.md).
- A failure to publish or deliver an event, per [22-event-contracts.md](22-event-contracts.md).
- Unavailability of a required compute resource.

No specific vendor or product is referenced in this description.

---

# 10. Integration Errors

Integration errors arise from failures at a boundary with an external system or data provider. This includes, conceptually:

- A failure to receive expected market data through the Data Layer, per [04-data-layer.md](04-data-layer.md).
- A failure in communication with an external system consuming the API defined in [23-openapi-specification.md](23-openapi-specification.md).
- An inconsistency between an external system's expectations and MIOS's canonical contract.

---

# 11. Security Errors

Security errors arise from failures related to authentication, authorization, integrity, or confidentiality. This includes, conceptually:

- A failure to verify the identity of a client, per the Authentication Principles in [15-api-specification.md](15-api-specification.md).
- A failure to confirm that a client is authorized to access a requested resource.
- A detected violation of data integrity or confidentiality.

---

# 12. Error Lifecycle

| Stage | Description |
|---|---|
| Detected | A component has identified that an operation has not proceeded as expected. |
| Classified | The detected failure has been assigned a canonical Error Category and Severity. |
| Reported | The classified error has been made available to relevant consumers, such as monitoring or the originating client. |
| Resolved | The condition underlying the error has been addressed, and the associated operation may proceed or has been abandoned deliberately. |
| Archived | The error record is retained for historical or audit purposes after it is no longer actively relevant. |

---

# 13. Error Classification

| Dimension | Description |
|---|---|
| Severity | The relative seriousness of the error, ranging from informational to critical. |
| Recoverability | Whether the error condition can be resolved automatically, requires a retry, or requires manual intervention. |
| Scope | Whether the error affects a single operation, a single component, or the platform broadly. |
| Impact | The effect of the error on the trader's ability to use MIOS, consistent with the transparent failure principle in [02-architecture.md](02-architecture.md). |
| Origin | The category of component (Analysis Engine, Orchestration Engine, Data Layer, API, Frontend, and so on) where the error originated. |

---

# 14. Error Traceability

| Concept | Description |
|---|---|
| Correlation | Every error carries a Correlation Identifier linking it to the broader chain of activity it belongs to. |
| Causation | Every error, where applicable, carries a Causation Identifier linking it to the specific error or event that produced it. |
| Lineage | The origin and propagation path of an error can be reconstructed from its Correlation and Causation Identifiers. |
| Auditability | The complete history of errors across the platform can be reviewed, consistent with the auditability principles defined in [24-database-design.md](24-database-design.md). |

---

# 15. Error Versioning

| Concept | Description |
|---|---|
| Evolution | The canonical error taxonomy may evolve over time to add new categories or classifications as the platform grows. |
| Compatibility | Existing error consumers remain able to interpret errors produced under a newer taxonomy version wherever possible. |
| Migration | Consumers are given a defined path to adopt a new error taxonomy version before an old version is retired. |
| Deprecation | A category or classification scheduled for removal is clearly communicated before being retired. |

---

# 16. Validation Rules

| Rule | Description |
|---|---|
| Category Required | Every error must be assigned exactly one canonical Error Category, per Section 6. |
| Identifier Required | Every error must carry a unique Error Identifier. |
| Timestamp Required | Every error must carry a valid Timestamp. |
| Traceability Preserved | Every error must preserve its Correlation Identifier and, where applicable, its Causation Identifier. |
| Immutable Identity | An error's Error Identifier and Category never change once assigned. |

---

# 17. Relationships

| From | To | Relationship |
|---|---|---|
| Errors | Events | An error may be represented as a canonical event, per [22-event-contracts.md](22-event-contracts.md), when it must be communicated asynchronously. |
| Errors | State Machines | A Domain error, per Section 8, may arise from an attempted violation of a lifecycle rule defined in [25-state-machine-specification.md](25-state-machine-specification.md). |
| Errors | Database | Error records may be persisted for audit and traceability purposes, consistent with [24-database-design.md](24-database-design.md). |
| Errors | API | Errors surfaced to external clients through the API, per [23-openapi-specification.md](23-openapi-specification.md), conform to the canonical Error Categories defined in Section 6. |
| Errors | Models | Validation errors, per Section 7, arise from violations of the canonical models defined in [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md). |

---

# 18. Domain Constraints

- No implementation detail may be defined within this canonical error architecture.
- No exception types are defined in this specification.
- No HTTP status codes are defined in this specification.
- This architecture remains technology independent.
- Only canonical errors, categorized per Section 6, are described here.

---

# 19. Governance

This Error Model Specification is owned by MIOS Architecture and serves as the single source of truth for the canonical error architecture of MIOS.

Any new error category or classification dimension must be added to this specification before being used elsewhere.

Taxonomy governance requires that every error produced by any component map to exactly one of the categories defined in Section 6.

Version governance follows the principles defined in Section 15; any change to the Canonical Error Object or Error Categories requires an approved Architecture Decision Record (ADR).

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
MIOS adopts a canonical error architecture independent of implementation technology.

**Reason:**
Defining errors at a canonical, technology-independent level ensures that every engine, service, and interface in MIOS classifies and communicates failure consistently, regardless of the programming language, framework, or transport involved, as selected in [00-technology-stack.md](00-technology-stack.md). This preserves the transparent failure principle defined in [02-architecture.md](02-architecture.md) and ensures that error traceability remains intact across the entire platform.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Allow each component to define its own error representation | Would risk inconsistent error classification and traceability across the platform, undermining the ability to reliably audit or correlate failures. |
| Define errors directly in terms of HTTP status codes | Would couple the canonical error model to a specific transport, and would not adequately represent errors originating outside the API layer, such as within an Analysis Engine. |
| Define errors directly in terms of a specific programming language's exception hierarchy | Would couple the canonical error model to a specific implementation technology, making a future technology change disruptive to error handling across the platform. |

**Consequences:**

- Every component must classify errors it produces using the canonical Error Categories defined in Section 6.
- Any future implementation-level error handling design must map cleanly onto the Canonical Error Object defined in Section 5.
- Error traceability, per Section 14, must be preserved across every layer of the platform, from the Analysis Engines through the API and Frontend.

---

# 22. Dependencies

This Error Model Specification depends on:

- 17-domain-model.md
- 18-market-model.md
- 19-analysis-model.md
- 20-decision-model.md
- 21-explanation-model.md
- 22-event-contracts.md
- 23-openapi-specification.md
- 24-database-design.md
- 25-state-machine-specification.md

This document is referenced by:

- All Engines
- API
- Repositories
- Frontend
- Technical Design

---

# 23. Glossary

| Term | Meaning |
|------|---------|
| Error | A canonical, traceable record that an operation did not proceed as expected. |
| Error Category | The canonical classification (Validation, Domain, Infrastructure, Integration, or Security) an error belongs to. |
| Severity | The relative seriousness of an error. |
| Recoverability | Whether an error condition can be resolved automatically, requires a retry, or requires manual intervention. |
| Correlation Identifier | A shared reference linking an error to the broader chain of activity it belongs to. |
| Causation Identifier | A reference linking an error to the specific error or event that directly caused it. |
| Lineage | The traceable origin and propagation path of an error. |
| Origin | The category of component where an error originated. |

---

# 24. Error Model Freeze

This Error Model Specification becomes the authoritative canonical error architecture for MIOS after approval.

Every component shall classify and structure errors it produces in conformance with the Canonical Error Object and Error Categories defined here.

Changes to this specification require an approved Architecture Decision Record (ADR).

---

# 25. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Error Model Specification for MIOS. |
