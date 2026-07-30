---
id: OPENAPI-SPEC-001
title: MIOS OpenAPI Specification
document: 23-openapi-specification.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the canonical REST API contract for MIOS, giving concrete architectural shape to the technology-neutral API boundary defined in [15-api-specification.md](15-api-specification.md). It builds upon the Domain Model in [17-domain-model.md](17-domain-model.md), the canonical Market, Analysis, Decision, and Explanation Models in [18-market-model.md](18-market-model.md) through [21-explanation-model.md](21-explanation-model.md), and the canonical Event Contracts in [22-event-contracts.md](22-event-contracts.md).

The REST API layer exposes canonical platform resources to external clients. It never contains business logic, and it is independent of any specific implementation framework named in [00-technology-stack.md](00-technology-stack.md).

This document becomes the single source of truth for every REST API exposed by MIOS. It defines API architecture and contracts only; it does not define OpenAPI YAML or JSON, request or response schemas, endpoint payloads, authentication implementation, controller code, or framework-specific details.

---

# 2. Scope

This document covers the canonical API architecture for:

- Market APIs
- Analysis APIs
- Decision APIs
- Explanation APIs
- Platform APIs
- Administration APIs
- Metadata APIs

---

# 3. API Design Principles

| Principle | Description |
|---|---|
| RESTful | The API is organized around resources, consistent with representational state transfer conventions. |
| Resource Oriented | Every capability of the API is expressed as an operation on a canonical resource, not as a remote procedure call. |
| Stateless | Each request is processed independently, without reliance on state retained from a previous request, consistent with [15-api-specification.md](15-api-specification.md). |
| Technology Independent | The API's canonical contract is defined independently of any specific implementation framework. |
| Consistent | Resources of the same kind behave consistently across the API. |
| Predictable | A client can reliably anticipate the general shape and behaviour of the API before making a request. |
| Versioned | The API's contract evolves through explicit, managed versions. |
| Idempotent | Where applicable, repeating the same request produces the same outcome without unintended side effects. |
| Traceable | Every request and response can be traced back to the canonical event and domain concepts it pertains to, per [22-event-contracts.md](22-event-contracts.md). |
| Canonical First | Every resource exposed by the API conforms to a canonical model already defined in [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md). |

---

# 4. API Philosophy

- API ≠ Business Logic. The API contains no analysis, synthesis, or decision-making logic of its own.
- API ≠ Database. The API does not expose or imply a specific storage structure.
- API = Contract. The API is the external, stable contract through which clients access MIOS's canonical resources.
- The API exposes canonical resources only; every resource it exposes maps directly to a concept already defined in the Domain, Market, Analysis, Decision, or Explanation Models.

---

# 5. API Categories

| Category | Description |
|---|---|
| Market | Exposes canonical Market Domain resources — Market, Instrument, Candle, Tick, Order Book Snapshot, and Session — defined in [18-market-model.md](18-market-model.md). |
| Analysis | Exposes canonical Analysis resources — Liquidity, Options, Momentum, Context, and Contradiction Assessments — defined in [19-analysis-model.md](19-analysis-model.md). |
| Decision | Exposes canonical Decision resources defined in [20-decision-model.md](20-decision-model.md). |
| Explanation | Exposes canonical Explanation resources defined in [21-explanation-model.md](21-explanation-model.md). |
| Platform | Exposes canonical Platform Domain resources — User, Watchlist, Configuration, Alert — defined in [17-domain-model.md](17-domain-model.md). |
| Administration | Exposes resources supporting platform administration, scoped to authorized administrative clients. |
| Metadata | Exposes resources describing the API itself, such as health and version information. |

---

# 6. Resource Model

Every resource exposed by the API corresponds directly to a canonical aggregate, entity, or value object already defined elsewhere in this documentation set. The API introduces no new conceptual structure; it exposes:

- Market Domain resources, as canonically defined in [18-market-model.md](18-market-model.md).
- Intelligence Domain resources (Assessments, Decisions, Explanations), as canonically defined in [19-analysis-model.md](19-analysis-model.md), [20-decision-model.md](20-decision-model.md), and [21-explanation-model.md](21-explanation-model.md).
- Platform Domain resources, as canonically defined in [17-domain-model.md](17-domain-model.md).

This section does not define resource payloads or schemas; those belong to a future implementation-level API contract document.

---

# 7. Endpoint Taxonomy

Endpoints are conceptually grouped by the resource category they expose:

- Endpoints addressing a single resource instance.
- Endpoints addressing a collection of resource instances.
- Endpoints addressing a resource's relationship to another resource, as defined in the relevant canonical model's Relationships section.
- Endpoints addressing platform metadata, such as health and version.

This section does not define specific URLs or HTTP methods; those belong to a future implementation-level API contract document.

---

# 8. Request Principles

| Principle | Description |
|---|---|
| Validation | Every request is validated against the canonical resource model it targets before being processed. |
| Consistency | Requests addressing the same resource category behave consistently. |
| Idempotency | Where applicable, a repeated request produces the same outcome as its first submission. |
| Correlation | Every request carries or generates a Correlation Identifier, consistent with the Event Metadata defined in [22-event-contracts.md](22-event-contracts.md). |
| Traceability | Every request can be traced to the canonical resources and, where relevant, the events it interacts with. |

---

# 9. Response Principles

| Principle | Description |
|---|---|
| Canonical Responses | Every response represents a canonical resource or collection of canonical resources. |
| Consistency | Responses of the same resource category are structured consistently. |
| Metadata | Responses may include metadata relevant to interpreting the resource, consistent with [15-api-specification.md](15-api-specification.md). |
| Version | Responses reflect the API version under which the request was processed. |
| Traceability | Responses preserve traceability back to the canonical Assessments, Decisions, or Explanations they represent. |

---

# 10. Error Handling

| Error Category | Description |
|---|---|
| Validation Errors | Returned when a request does not conform to the canonical resource model it targets. |
| Authorization Errors | Returned when an authenticated client lacks permission to access the requested resource. |
| Authentication Errors | Returned when a client's identity cannot be verified. |
| Conflict Errors | Returned when a request conflicts with the current state of a canonical resource. |
| Not Found | Returned when a requested resource does not exist. |
| Rate Limiting | Returned when a client has exceeded the permitted request volume. |
| Internal Errors | Returned when the API is unable to fulfill a valid request due to an internal failure. |

This section does not define error payloads; those belong to a future implementation-level API contract document.

---

# 11. Pagination

Collections of canonical resources are accessed through a pagination mechanism that allows clients to retrieve results incrementally rather than all at once, preserving consistent ordering across pages. Specific pagination mechanics are outside the scope of this specification.

---

# 12. Filtering

Collections of canonical resources may be narrowed according to attributes of the underlying canonical model, allowing clients to retrieve only the resources relevant to their needs. Specific filtering mechanics are outside the scope of this specification.

---

# 13. Sorting

Collections of canonical resources may be ordered according to attributes of the underlying canonical model, such as Timestamp or Identifier. Specific sorting mechanics are outside the scope of this specification.

---

# 14. Versioning

| Concept | Description |
|---|---|
| Strategy | The API evolves through explicit, numbered versions rather than silent, breaking changes. |
| Compatibility | A given API version's behaviour remains stable for the duration of its supported lifecycle. |
| Deprecation | A version scheduled for retirement is clearly communicated to clients in advance. |
| Migration | Clients are given a defined path to move from a deprecated version to its replacement. |

---

# 15. Idempotency

Where an operation is intended to be safely repeatable, the API guarantees that repeating the same request under the same conditions produces the same outcome, without unintended duplicate effects. This applies in particular to operations that create or modify Platform Domain resources such as Configuration or Watchlist entries.

---

# 16. Validation Rules

| Rule | Description |
|---|---|
| Version Required | Every request must be processed under an identifiable API version. |
| Canonical Resources Only | Every resource exposed by the API must correspond to a concept already defined in the Domain, Market, Analysis, Decision, or Explanation Models. |
| Technology Independent | The API's canonical contract must not depend on any specific implementation framework. |
| Consistent Naming | Resources and their relationships are named consistently with the canonical models they represent. |
| Immutable Identifiers | A resource's identifier, once assigned, does not change over its lifecycle, consistent with the Identity Strategy defined in [17-domain-model.md](17-domain-model.md). |

---

# 17. Relationships

| From | To | Relationship |
|---|---|---|
| API | Resources | The API exposes canonical resources drawn from the Domain, Market, Analysis, Decision, and Explanation Models. |
| Resources | Models | Every exposed resource maps directly to a canonical model concept defined elsewhere in this documentation set. |
| Resources | Events | Changes to exposed resources correspond to canonical events defined in [22-event-contracts.md](22-event-contracts.md). |
| Resources | Database | Exposed resources are ultimately backed by persisted data, the structure of which is defined in a future Database Design document. |

---

# 18. Domain Constraints

- No business logic may reside in the API layer.
- No algorithms may be implemented within the API layer.
- No persistence logic may reside in the API layer.
- No transport implementation details are defined in this specification.
- Only canonical contracts, already defined elsewhere in this documentation set, may be exposed through the API.

---

# 19. Governance

This OpenAPI Specification is owned by MIOS Architecture and serves as the single source of truth for the canonical REST API architecture of MIOS.

Any new resource category exposed through the API must first be defined in the appropriate canonical model document before being added to this specification.

Any change to the API Categories, Resource Model, or Versioning strategy requires an approved Architecture Decision Record (ADR).

Version governance follows the principles defined in Section 14; where a conflict arises between an implementation and this document, this document takes precedence.

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
MIOS adopts a canonical REST API architecture independent of implementation framework.

**Reason:**
Defining the REST API's architecture at a canonical level, independent of any specific framework, ensures that the API's resource model remains stable and consistent regardless of which backend framework defined in [00-technology-stack.md](00-technology-stack.md) implements it. It also guarantees that the API exposes only concepts already defined in the canonical Domain, Market, Analysis, Decision, and Explanation Models, preserving the "API = Contract" principle defined in Section 4 and the thin-interface governance defined in [15-api-specification.md](15-api-specification.md).

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Define the API directly as an OpenAPI YAML document with framework-specific bindings | Would couple the canonical resource contract to a specific implementation framework prematurely, before that framework's suitability has been separately validated. |
| Allow API resource shapes to diverge from the canonical models | Would risk the API exposing inconsistent or duplicated concepts relative to [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md), undermining the single source of truth principle. |
| Design the API around business operations rather than resources | Would blur the separation between the API's contract role and the business logic that belongs exclusively to the internal engines, violating [15-api-specification.md](15-api-specification.md). |

**Consequences:**

- Every resource exposed by the REST API must trace back to a canonical model concept already defined in this documentation set.
- A future, implementation-level OpenAPI contract document may define concrete schemas and endpoints, but must conform to the architecture defined here.
- Any new API capability must first be reflected in the appropriate canonical model before being exposed.

---

# 22. Dependencies

This OpenAPI Specification depends on:

- 17-domain-model.md
- 18-market-model.md
- 19-analysis-model.md
- 20-decision-model.md
- 21-explanation-model.md
- 22-event-contracts.md

This document is referenced by:

- Frontend
- SDKs
- Mobile
- Integrations
- Technical Design

---

# 23. Glossary

| Term | Meaning |
|------|---------|
| Resource | A canonical concept exposed through the REST API, corresponding to a Domain, Market, Analysis, Decision, or Explanation Model concept. |
| Endpoint | A conceptual point of access to a resource or resource collection. |
| Idempotency | The property of an operation producing the same outcome when repeated. |
| Pagination | The mechanism by which large collections of resources are retrieved incrementally. |
| Filtering | The mechanism by which a collection of resources is narrowed according to specific attributes. |
| Sorting | The mechanism by which a collection of resources is ordered according to specific attributes. |
| Version | A defined, stable iteration of the API's canonical contract. |
| Correlation Identifier | A shared reference linking a request and response to the broader chain of activity it belongs to. |

---

# 24. API Freeze

This OpenAPI Specification becomes the authoritative canonical REST API architecture for MIOS after approval.

Every REST API implementation shall expose only resources conforming to the canonical models defined in [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md).

Changes to this specification require an approved Architecture Decision Record (ADR).

---

# 25. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial OpenAPI Specification for MIOS. |
