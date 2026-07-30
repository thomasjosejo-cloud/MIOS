---

# MIOS Documentation Standard

## Purpose

This document defines the standard that every document in the `docs/` folder must follow.

The objective is to ensure every specification is written consistently and can serve as the single source of truth for the project.

---

# Document Header

Every document must begin with the following metadata.

```yaml
---
title:
document:
version:
status:
owner:
last_updated:
---
```

---

# Required Sections

Every specification must contain the following sections where applicable.

1. Purpose
2. Scope
3. Objectives
4. Functional Requirements
5. Non-Functional Requirements
6. Architecture Overview
7. Diagrams
8. Data Models
9. Inputs
10. Outputs
11. Processing Logic
12. Error Handling
13. Dependencies
14. Acceptance Criteria
15. Open Questions
16. Future Enhancements
17. Decision Record (ADR)
18. Revision History

---

# Formatting Rules

- Use Markdown only.
- Use clear headings.
- Use tables wherever they improve readability.
- Use fenced code blocks for examples.
- Use ASCII diagrams where appropriate.
- Do not mix implementation code with specifications unless explicitly requested.
- Every requirement should have a unique identifier when applicable.

---

# Acceptance Criteria

Every document must end with a checklist.

Example:

- [ ] Reviewed
- [ ] Approved
- [ ] Ready for Implementation

---

# Decision Records

Important architectural decisions must include:

- Decision
- Reason
- Alternatives Considered
- Consequences

---

# Goal

Every document should be understandable by a developer who has never worked on MIOS before.
