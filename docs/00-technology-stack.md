---
id: TECH-STACK-001
title: MIOS Technology Stack Specification
document: 00-technology-stack.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the official implementation technologies for MIOS. It marks the transition from Architecture (Volume I) to Technical Design (Volume II): where the documents in [02-architecture.md](02-architecture.md) through [16-frontend.md](16-frontend.md) deliberately remained technology-neutral, this specification names the concrete technologies that implement those architectural roles.

Every engineering decision made after this document shall comply with the selected technology stack.

Changing technologies requires an approved Architecture Decision Record (ADR).

---

# 2. Technology Selection Principles

| Principle | Description |
|---|---|
| Production Ready | Selected technologies must be proven and stable enough for production use, not experimental. |
| Long Term Support | Selected technologies must have a maintained support lifecycle. |
| Strong Ecosystem | Selected technologies must have a mature surrounding ecosystem of tooling and libraries. |
| Scalability | Selected technologies must support the platform's growth in data volume and usage. |
| Observability | Selected technologies must support monitoring, logging, and tracing of system behaviour. |
| Maintainability | Selected technologies must be maintainable by the engineering team over the long term. |
| Performance | Selected technologies must meet the low-latency requirements defined throughout the architecture specifications. |
| Security | Selected technologies must support the security principles defined in [02-architecture.md](02-architecture.md) and [15-api-specification.md](15-api-specification.md). |
| Community Adoption | Selected technologies must have broad adoption and an active community. |
| Cloud Native | Selected technologies must be suited to containerized, cloud-based deployment. |

---

# 3. Official Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Backend Language | Python | 3.13 | Primary language for all backend services and engines. |
| Backend Framework | FastAPI | Latest stable | Framework implementing the MIOS API defined in [15-api-specification.md](15-api-specification.md). |
| API Standard | REST | — | Standard for the external API contract. |
| API Documentation | OpenAPI | 3.1 | Standard for describing the API's external contract. |
| Application Server | Uvicorn | Latest stable | ASGI server running the backend application. |
| ORM | SQLAlchemy | 2.x | Object-relational mapping for backend data access. |
| Validation | Pydantic | v2 | Data validation and normalization within backend services. |
| Primary Database | PostgreSQL | 17 | System of record for the Market Store and platform data. |
| Time Series Extension | TimescaleDB | Latest stable | Extension supporting historical market data storage in the Market Store. |
| Cache | Redis | Latest stable | Caching layer supporting low-latency reads. |
| Message Broker | NATS JetStream | Latest stable | Implementation of the Event Bus defined in [06-event-bus.md](06-event-bus.md). |
| Background Processing | Celery | Latest stable | Asynchronous and scheduled background task processing. |
| Task Queue Broker | Redis | Latest stable | Broker supporting background task processing. |
| Frontend Language | TypeScript | Latest stable | Primary language for the Frontend defined in [16-frontend.md](16-frontend.md). |
| Frontend Framework | React | Latest stable | Framework implementing the MIOS Frontend. |
| Build Tool | Vite | Latest stable | Frontend build and development tooling. |
| State Management | TanStack Query | Latest stable | Management of API-derived state within the Frontend. |
| Routing | React Router | Latest stable | Frontend navigation. |
| Charts | TradingView Lightweight Charts | Latest stable | Rendering of market data visualizations. |
| Styling | Tailwind CSS | Latest stable | Implementation of the visual design language defined in [03-design-system.md](03-design-system.md). |
| Component Library | shadcn/ui | Latest stable | Base component library for the Frontend. |
| Authentication | OAuth2 / OpenID Connect | — | Standard for identity verification, per [15-api-specification.md](15-api-specification.md). |
| Containerization | Docker | Latest stable | Packaging of all platform services. |
| Container Orchestration | Kubernetes | Latest stable | Orchestration of containerized services. |
| Reverse Proxy | NGINX | Latest stable | Routing and termination in front of platform services. |
| Object Storage | S3 Compatible Storage | — | Storage of unstructured or archival platform data. |
| Logging | Structured JSON Logs | — | Standard log format across all services. |
| Metrics | Prometheus | Latest stable | Collection of platform operational metrics. |
| Visualization | Grafana | Latest stable | Visualization of operational metrics and dashboards. |
| Distributed Tracing | OpenTelemetry | Latest stable | Tracing of requests and events across services. |
| CI/CD | GitHub Actions | — | Continuous integration and deployment pipeline. |
| Testing | pytest | Latest stable | Backend test framework. |
| Frontend Testing | Vitest | Latest stable | Frontend unit test framework. |
| End-to-End Testing | Playwright | Latest stable | End-to-end testing across the Frontend and API. |
| Package Management | uv (Python), npm | Latest stable | Dependency management for backend and frontend. |
| Secrets Management | Kubernetes Secrets | — | Storage and distribution of sensitive configuration values. |
| Version Control | Git | — | Source control for all MIOS code and documentation. |
| Repository Hosting | GitHub | — | Hosting of the MIOS source repository. |

---

# 4. Backend Architecture

- Python-first architecture across all backend services and engines.
- FastAPI services implementing the API layer defined in [15-api-specification.md](15-api-specification.md).
- Async-first design to support the low-latency requirements defined throughout the engine specifications.
- Dependency injection to keep components loosely coupled and testable.
- Layered architecture, mirroring the separation of Data Layer, Market Store, Event Bus, Analysis Engines, and orchestration engines defined in [02-architecture.md](02-architecture.md).
- Service isolation, so that each engine remains an independently deployable unit.
- Stateless services wherever possible, with authoritative state held in the Market Store.

---

# 5. Frontend Architecture

- Single Page Application, consistent with the Frontend's role as the presentation layer defined in [16-frontend.md](16-frontend.md).
- Component-based architecture, aligned with the component philosophy defined in [03-design-system.md](03-design-system.md).
- API-first communication, with all data obtained exclusively through the MIOS API.
- Server state management, keeping presentation state synchronized with API state.
- Responsive interface, adapting to the contexts in which MIOS is used.
- Accessibility, consistent with the accessibility principles defined in [03-design-system.md](03-design-system.md) and [16-frontend.md](16-frontend.md).

---

# 6. Data Architecture

- PostgreSQL as the system of record, implementing the authoritative role of the Market Store defined in [05-market-store.md](05-market-store.md).
- TimescaleDB for market history, supporting efficient storage and retrieval of time-series market data.
- Redis for caching, supporting low-latency reads without compromising the Market Store's authoritative role.
- Immutable historical records, consistent with the immutability principles defined in [05-market-store.md](05-market-store.md).
- Transactional consistency, ensuring the Market Store's state remains internally consistent.
- Backup strategy, ensuring recoverability of the authoritative market record.

---

# 7. Event Architecture

- NATS JetStream as the implementation of the Event Bus defined in [06-event-bus.md](06-event-bus.md).
- Publish/Subscribe as the fundamental communication pattern between components.
- Event persistence, supporting durability of published events.
- Reliable delivery, consistent with the delivery rules defined in [06-event-bus.md](06-event-bus.md).
- Replay capability, supporting the consistent replay principle defined in [06-event-bus.md](06-event-bus.md).
- Loose coupling, preserving the independence of publishers and subscribers.

---

# 8. Deployment Architecture

- Docker containers packaging every platform service.
- Kubernetes orchestrating containerized services across the platform.
- Horizontal scaling of services to accommodate platform growth.
- Rolling deployments, minimizing disruption during updates.
- Health checks, supporting the observability of each service's operational status.
- Service discovery, allowing services to locate one another within the orchestrated environment.
- Load balancing, distributing traffic across service instances.

---

# 9. Observability Stack

- Prometheus collecting operational metrics across platform services.
- Grafana visualizing operational metrics and dashboards.
- OpenTelemetry providing distributed tracing across services.
- Structured logging in a consistent JSON format across all services.
- Health endpoints exposing the operational status of each service.
- Metrics covering the performance and reliability requirements defined throughout the engine specifications.
- Tracing supporting end-to-end traceability of requests and events.
- Audit logs supporting the auditability principles defined in [05-market-store.md](05-market-store.md) and [15-api-specification.md](15-api-specification.md).

---

# 10. Security Stack

- OAuth2 as the standard for client authentication.
- OpenID Connect (OIDC) as the standard for identity verification.
- HTTPS everywhere across all external and internal communication.
- TLS securing data in transit.
- Secrets management via Kubernetes Secrets.
- Least privilege applied to every service and client.
- Encryption at rest for stored platform data.
- Encryption in transit for all communication between services and clients.

---

# 11. Development Standards

- Black for consistent Python code formatting.
- Ruff for Python linting.
- mypy for static type checking of Python code.
- Pre-commit hooks enforcing formatting and linting before commits.
- Conventional Commits for commit message consistency.
- GitFlow as the branching strategy.
- Semantic Versioning for releases of platform components.

---

# 12. Testing Stack

- pytest as the backend testing framework.
- Vitest as the frontend unit testing framework.
- Playwright for end-to-end testing across the Frontend and API.
- Unit testing covering individual components in isolation.
- Integration testing covering interactions between components.
- Contract testing covering the API's external contract.
- Performance testing covering the latency and reliability requirements defined throughout the engine specifications.

---

# 13. Version Matrix

| Technology | Approved Version |
|---|---|
| Python | 3.13 |
| FastAPI | Latest stable |
| Uvicorn | Latest stable |
| SQLAlchemy | 2.x |
| Pydantic | v2 |
| PostgreSQL | 17 |
| TimescaleDB | Latest stable |
| Redis | Latest stable |
| NATS JetStream | Latest stable |
| Celery | Latest stable |
| TypeScript | Latest stable |
| React | Latest stable |
| Vite | Latest stable |
| TanStack Query | Latest stable |
| React Router | Latest stable |
| TradingView Lightweight Charts | Latest stable |
| Tailwind CSS | Latest stable |
| shadcn/ui | Latest stable |
| Docker | Latest stable |
| Kubernetes | Latest stable |
| NGINX | Latest stable |
| Prometheus | Latest stable |
| Grafana | Latest stable |
| OpenTelemetry | Latest stable |
| pytest | Latest stable |
| Vitest | Latest stable |
| Playwright | Latest stable |
| uv | Latest stable |
| npm | Latest stable |
| Git | Latest stable |

---

# 14. Technology Governance

Only approved technologies may be used.

Introducing a new technology requires an ADR.

Replacing an approved technology requires an ADR.

Experimental technologies are prohibited in production.

---

# 15. Acceptance Criteria

- [ ] Reviewed
- [ ] Approved
- [ ] Production Ready
- [ ] Architecture Compliant
- [ ] Technology Locked

---

# 16. ADR-001

**Decision:**
MIOS shall standardize on a single production technology stack.

**Reason:**
A single, standardized technology stack ensures that every engineering team working on MIOS shares the same tooling, deployment model, and operational practices. This preserves the maintainability, observability, and consistency required by the architecture defined in [02-architecture.md](02-architecture.md), and avoids the overhead of supporting multiple, divergent implementations of the same architectural roles.

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Polyglot backend | Would fragment tooling, testing, and operational practices across multiple languages, increasing maintenance burden without a corresponding architectural benefit. |
| Multiple databases | Would complicate the Market Store's role as a single authoritative repository, defined in [05-market-store.md](05-market-store.md), and increase operational complexity without clear benefit. |
| Multiple frontend frameworks | Would fragment the presentation layer's consistency, violating the presentation consistency principles defined in [03-design-system.md](03-design-system.md) and [16-frontend.md](16-frontend.md). |

**Consequences:**

- All Technical Design and Engineering Handbook documents must conform to the technology stack defined in this specification.
- Any proposal to introduce or replace a technology must be submitted as a new, approved ADR.
- Engineering onboarding and tooling can be standardized around a single, well-defined stack.

---

# 17. Document Dependencies

This Technology Stack Specification is referenced by:

- Every Volume II Technical Design document.
- Every Engineering Handbook document.
- Every Deployment document.

---

# 18. Glossary

| Term | Meaning |
|------|---------|
| FastAPI | The Python web framework used to implement the MIOS API. |
| TimescaleDB | A time-series extension to PostgreSQL used for storing market history. |
| Redis | An in-memory data store used for caching and task queue brokering. |
| NATS | A messaging system used to implement the MIOS Event Bus. |
| Docker | A containerization technology used to package platform services. |
| Kubernetes | A container orchestration platform used to deploy and manage platform services. |
| OpenTelemetry | A standard for collecting distributed traces across services. |
| Prometheus | A metrics collection system used for platform observability. |
| Grafana | A visualization tool used to present operational metrics and dashboards. |
| SPA | Single Page Application — an application architecture in which the Frontend is delivered as a single, dynamically updated page. |

---

# 19. Technology Freeze

This technology stack becomes mandatory after approval.

Technology substitutions require an approved ADR.

Every implementation document shall conform to this specification.

---

# 20. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Technology Stack Specification for MIOS. |
