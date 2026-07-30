---
id: STATE-MACHINE-001
title: MIOS State Machine Specification
document: 25-state-machine-specification.md
version: 1.0.0
status: Draft
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the canonical lifecycle and state transition architecture for every stateful concept in MIOS. It builds upon the aggregates defined in [17-domain-model.md](17-domain-model.md), the canonical Market, Analysis, Decision, and Explanation Models in [18-market-model.md](18-market-model.md) through [21-explanation-model.md](21-explanation-model.md), the Event Contracts in [22-event-contracts.md](22-event-contracts.md), the OpenAPI Specification in [23-openapi-specification.md](23-openapi-specification.md), and the Database Design in [24-database-design.md](24-database-design.md).

Lifecycle behavior is defined independently of implementation. This document remains technology independent and becomes the single source of truth for lifecycle behavior across MIOS. It defines canonical state machines only — it does not define implementation code, workflow engines, BPMN, UML diagrams, event handlers, or persistence implementation.

---

# 2. Scope

This document covers the canonical lifecycle of:

- Market lifecycle
- Analysis lifecycle
- Decision lifecycle
- Explanation lifecycle
- Platform lifecycle
- Transition rules
- Transition validation
- State versioning

---

# 3. State Machine Principles

| Principle | Description |
|---|---|
| Canonical First | Every lifecycle defined here governs a concept already established in [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md); no new concepts are introduced. |
| Deterministic | Given the same current state and the same triggering condition, the resulting transition is always the same. |
| Immutable History | A concept's history of past states is never rewritten once recorded. |
| Explicit Transitions | Every movement from one state to another is explicitly defined; no implicit or undocumented transitions are permitted. |
| Traceable | Every state transition can be traced back to the event or condition that caused it. |
| Consistent | The same category of concept transitions through its lifecycle the same way everywhere it occurs. |
| Technology Independent | Lifecycle behavior is defined independently of any specific workflow or state-management technology. |
| Replay Safe | Replaying the same sequence of transition-triggering events produces the same resulting state. |
| Version Aware | Lifecycle definitions are associated with a version, supporting safe evolution over time. |
| Single Source of Truth | This document is the sole authority for valid states and transitions across MIOS. |

---

# 4. State Philosophy

- State = Current lifecycle position. A state describes where a concept currently stands in its defined lifecycle.
- Transition = Valid movement. A transition is a defined, permitted movement from one state to another.
- State ≠ Event. A state is a condition; an event, per [22-event-contracts.md](22-event-contracts.md), is the immutable record of a fact that occurred, which may cause a transition.
- State ≠ Action. A state does not itself perform any operation; it is a descriptive position in a lifecycle.
- State ≠ Business Logic. A state machine defines valid lifecycle positions and movements only; it contains no analysis, synthesis, or decision-making logic.

---

# 5. Canonical State Machine Model

| Attribute | Description |
|---|---|
| State Identifier | A unique identifier for the state transition record. |
| Aggregate Identifier | A reference to the specific aggregate instance, per [17-domain-model.md](17-domain-model.md), whose lifecycle this transition describes. |
| Current State | The state the aggregate occupies following this transition. |
| Previous State | The state the aggregate occupied prior to this transition. |
| Transition Timestamp | The point in time the transition occurred. |
| Transition Reason | A reference to the event or condition that caused the transition. |
| Version | The version of the lifecycle definition this transition conforms to. |
| Metadata | Supporting descriptive information relevant to interpreting the transition. |
| Validation Rules | The transition must satisfy the Validation Rules defined in Section 16 before being considered valid. |

---

# 6. Aggregate Lifecycles

Every aggregate defined in [17-domain-model.md](17-domain-model.md) has exactly one canonical lifecycle, governed by this document. An aggregate's lifecycle is composed of a defined, ordered set of states and the permitted transitions between them. No aggregate may occupy a state, or undergo a transition, that is not explicitly defined for its lifecycle category in Sections 7 through 11.

---

# 7. Market Lifecycles

## 7.1 Market

| State | Description |
|---|---|
| Onboarded | The Market has been created and registered within MIOS. |
| Active | The Market is available for Instruments to be listed and traded, consistent with the Market lifecycle described in [17-domain-model.md](17-domain-model.md). |
| Deactivated | The Market is no longer accepting new activity, though its historical record is preserved. |

## 7.2 Instrument

| State | Description |
|---|---|
| Listed | The Instrument has been created and is available within its Market. |
| Active | The Instrument is currently tradable. |
| Expired | The Instrument's Expiry has passed, applicable to derivative Instruments. |
| Delisted | The Instrument has been removed from active trading without reaching a defined Expiry. |

## 7.3 Session

| State | Description |
|---|---|
| Scheduled | The Session's boundaries have been defined but trading has not yet begun. |
| Open | The Session is currently active, consistent with the Market Status model in [18-market-model.md](18-market-model.md). |
| Closed | The Session has ended and its boundaries are final. |

This lifecycle describes the existence of a Session record and is distinct from the operational Market Status values (Open, Closed, Auction, and so on) defined in [18-market-model.md](18-market-model.md), which describe trading activity within an Open Session.

---

# 8. Analysis Lifecycles

Every Assessment type (Liquidity, Options, Momentum, Context, and Contradiction) follows the same canonical lifecycle, consistent with the Assessment Lifecycle and Assessment States defined in [19-analysis-model.md](19-analysis-model.md):

| State | Description |
|---|---|
| Draft | The Assessment has been created by its owning engine but not yet validated. |
| Valid | The Assessment has satisfied all Validation Rules defined in [19-analysis-model.md](19-analysis-model.md). |
| Invalid | The Assessment has failed validation and cannot be published. |
| Published | The Assessment has been made available to downstream consumers and is immutable. |
| Deprecated | The Assessment remains published but has been superseded by a newer Assessment for the same Instrument or Market. |
| Archived | The Assessment is retained for historical or audit purposes only. |

---

# 9. Decision Lifecycle

Consistent with the Decision Lifecycle and Decision States defined in [20-decision-model.md](20-decision-model.md):

| State | Description |
|---|---|
| Created | The Decision Engine has produced a Decision instance but has not yet confirmed it satisfies all Validation Rules. |
| Validated | The Decision has been confirmed to satisfy all Validation Rules defined in [20-decision-model.md](20-decision-model.md). |
| Published | The validated Decision has been made available to downstream consumers and is immutable. |
| Superseded | A newer Decision for the same Instrument or Market and a later Time Window has since been published. |
| Archived | The Decision is retained for historical reference but is no longer the subject of active downstream consumption. |

---

# 10. Explanation Lifecycle

Consistent with the Explanation Lifecycle and Explanation States defined in [21-explanation-model.md](21-explanation-model.md):

| State | Description |
|---|---|
| Created | The AI Explanation Engine has produced an Explanation instance but has not yet confirmed it satisfies all Validation Rules. |
| Validated | The Explanation has been confirmed to satisfy all Validation Rules defined in [21-explanation-model.md](21-explanation-model.md). |
| Published | The validated Explanation has been made available to downstream consumers and is immutable. |
| Superseded | A newer Explanation describing a subsequent Decision for the same Instrument or Market has since been published. |
| Archived | The Explanation is retained for historical reference but is no longer the subject of active downstream consumption. |

---

# 11. Platform Lifecycles

## 11.1 User

| State | Description |
|---|---|
| Created | A User account has been created. |
| Active | The User account is currently usable. |
| Deactivated | The User account is no longer usable, though its historical record is preserved. |

## 11.2 Watchlist

| State | Description |
|---|---|
| Created | The Watchlist has been defined by its owning User. |
| Active | The Watchlist is currently maintained and available for use. |
| Archived | The Watchlist is retained for historical reference but is no longer actively maintained. |

## 11.3 Configuration

| State | Description |
|---|---|
| Created | The Configuration has been defined for its owning User or the platform. |
| Active | The Configuration currently governs platform or User behaviour. |
| Superseded | The Configuration has been replaced by a newer Configuration for the same owner. |

## 11.4 Alert

| State | Description |
|---|---|
| Created | The Alert has been generated in response to its defining condition. |
| Acknowledged | The Alert has been viewed by its owning User. |
| Archived | The Alert is retained for historical reference only. |

---

# 12. State Transition Rules

| Concept | Description |
|---|---|
| Allowed Transitions | Only the transitions explicitly enumerated for a given lifecycle in Sections 7 through 11 may occur. |
| Forbidden Transitions | Any transition not explicitly enumerated for a given lifecycle is forbidden, including any transition out of a terminal state such as Archived. |
| Transition Invariants | A transition may only occur if the aggregate's Current State matches the defined origin state for that transition. |
| Transition Ordering | Transitions occur strictly in the order permitted by the lifecycle; a state may not be skipped unless the lifecycle explicitly allows it. |

---

# 13. Transition Validation

| Principle | Description |
|---|---|
| Identity Preservation | A transition never changes the identity of the aggregate it applies to. |
| Chronological Validation | A transition's Transition Timestamp must be later than that of the aggregate's previous transition. |
| Consistency Validation | A transition must be consistent with the aggregate's canonical model, per [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md). |
| Referential Validation | A transition's Transition Reason must reference an event or condition that actually exists, per [22-event-contracts.md](22-event-contracts.md). |

---

# 14. State Consistency

| Principle | Description |
|---|---|
| Lifecycle Consistency | An aggregate occupies exactly one state at any given point in time. |
| Aggregate Consistency | A transition is applied atomically with respect to the aggregate it affects. |
| Temporal Consistency | An aggregate's recorded state history remains consistent with the chronological order of its transitions. |
| Version Consistency | A transition is evaluated against the lifecycle definition version in effect at the time it occurs. |

---

# 15. State Versioning

| Concept | Description |
|---|---|
| Evolution | A lifecycle definition may evolve over time to add new states or transitions as the platform grows. |
| Compatibility | Existing aggregates continue to be interpretable under a newer lifecycle version wherever possible. |
| Deprecation | A state or transition scheduled for removal is clearly communicated before being retired. |
| Migration | Aggregates persisted under an older lifecycle version are given a defined path to align with a newer version. |

---

# 16. Validation Rules

| Rule | Description |
|---|---|
| Valid Transition Required | Every transition must correspond to an explicitly defined transition in Sections 7 through 11. |
| Immutable History | A recorded state transition is never altered or removed once written. |
| Identity Preserved | A transition never alters the identity of the aggregate it applies to. |
| Chronological Ordering | Transitions for a given aggregate are always recorded in chronological order. |
| Traceability Maintained | Every transition preserves its reference to the triggering event or condition. |

---

# 17. Relationships

| From | To | Relationship |
|---|---|---|
| State Machines | Models | Every lifecycle defined here governs an aggregate already defined in [17-domain-model.md](17-domain-model.md) through [21-explanation-model.md](21-explanation-model.md). |
| State Machines | Events | Transitions are triggered by canonical events defined in [22-event-contracts.md](22-event-contracts.md). |
| State Machines | Database | Recorded state and transition history is persisted in accordance with [24-database-design.md](24-database-design.md). |
| State Machines | API | The current state of a resource, as exposed through the API defined in [23-openapi-specification.md](23-openapi-specification.md), reflects its canonical lifecycle position. |

---

# 18. Domain Constraints

- No business logic may reside within a state machine definition.
- No algorithms may be implemented within a state machine definition.
- No implementation technology is defined in this specification.
- This architecture remains technology independent.
- Only canonical lifecycles, already governing concepts defined elsewhere in this documentation set, are described here.

---

# 19. Governance

This State Machine Specification is owned by MIOS Architecture and serves as the single source of truth for lifecycle behavior across MIOS.

Any new state or transition must be added to the appropriate lifecycle in Sections 7 through 11 before it is used elsewhere.

Lifecycle governance requires that no aggregate be permitted to occupy an undefined state or undergo an unlisted transition.

Version governance follows the principles defined in Section 15; any change to an existing lifecycle's states or transitions requires an approved Architecture Decision Record (ADR).

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
MIOS adopts canonical lifecycle state machines independent of implementation technology.

**Reason:**
Defining every aggregate's lifecycle at a canonical, technology-independent level ensures that every engine, service, and interface in MIOS agrees on what states are valid and what transitions are permitted, consistent with the single source of truth and determinism principles defined in [02-architecture.md](02-architecture.md). This prevents any component from introducing an undocumented state or an implicit transition that could compromise the immutability, traceability, or explainability guarantees established throughout [17-domain-model.md](17-domain-model.md) through [24-database-design.md](24-database-design.md).

**Alternatives Considered:**

| Alternative | Reason Rejected |
|---|---|
| Allow each engine to define its own lifecycle for the Assessments or Decisions it produces | Would risk inconsistent lifecycle behavior across engines, undermining the shared Assessment and Decision Lifecycles already defined in [19-analysis-model.md](19-analysis-model.md) and [20-decision-model.md](20-decision-model.md). |
| Define lifecycle behavior only informally, within implementation code | Would leave no canonical, technology-independent reference for valid states and transitions, risking drift between components over time. |
| Permit implicit or undocumented state transitions for operational flexibility | Would violate the Explicit Transitions and Deterministic principles defined in Section 3, and undermine the platform's auditability requirements defined in [24-database-design.md](24-database-design.md). |

**Consequences:**

- Every aggregate's lifecycle must conform to the states and transitions explicitly defined in Sections 7 through 11.
- Any new lifecycle requirement must first be added to this specification before being implemented elsewhere.
- Engines, the Event Bus, persistence, and the API can all rely on a single, consistent definition of valid lifecycle behavior.

---

# 22. Dependencies

This State Machine Specification depends on:

- 17-domain-model.md
- 18-market-model.md
- 19-analysis-model.md
- 20-decision-model.md
- 21-explanation-model.md
- 22-event-contracts.md
- 23-openapi-specification.md
- 24-database-design.md

This document is referenced by:

- All Engines
- Event Bus
- Repositories
- Technical Design

---

# 23. Glossary

| Term | Meaning |
|------|---------|
| State | The current lifecycle position of an aggregate. |
| Transition | A defined, permitted movement from one state to another. |
| Lifecycle | The complete, ordered set of states and transitions governing an aggregate's existence. |
| Transition Reason | The event or condition that caused a state transition to occur. |
| Terminal State | A state from which no further transition is defined, such as Archived. |
| State Consistency | The property that an aggregate occupies exactly one state at any given point in time. |
| Deterministic Transition | A transition that always produces the same resulting state given the same current state and triggering condition. |
| Version Awareness | The property of a lifecycle definition being associated with a specific version, supporting safe evolution over time. |

---

# 24. State Machine Freeze

This State Machine Specification becomes the authoritative canonical lifecycle model for MIOS after approval.

Every engine, service, and interface shall conform to the states and transitions defined here for each aggregate lifecycle.

Changes to this specification require an approved Architecture Decision Record (ADR).

---

# 25. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial State Machine Specification for MIOS. |
