---
id: DS-001
title: MIOS Design System
document: 03-design-system.md
version: 1.0.0
status: Approved
owner: MIOS Architecture
last_updated: 2026-07-29
---

# 1. Executive Summary

This document defines the complete visual and interaction language of MIOS. It establishes the principles, hierarchies, and constraints that govern how every screen, dashboard, component, and interaction in MIOS looks, behaves, and communicates.

Every interface in MIOS must follow this document. No screen, dashboard, or component may be designed or implemented in a way that contradicts the principles defined here.

The objective of this design system is to produce a professional, institutional-grade market intelligence platform — the visual equivalent of the evidence-based, non-promotional product philosophy defined in [01-product.md](01-product.md) — rather than a retail trading application built around excitement, urgency, or gamification.

Throughout this document, consistency, readability, and clarity take priority over decoration. A design choice that adds visual interest at the expense of clarity or consistency does not belong in MIOS.

---

# 2. Design Philosophy

| Principle | Explanation |
|---|---|
| Clarity over Complexity | Every screen must communicate its content in the simplest form possible. Complexity is only acceptable when it reduces the trader's overall effort to understand the market. |
| Evidence over Emotion | Visual design must support the evidence behind an insight, not create an emotional reaction to it. Nothing should be designed to provoke urgency, excitement, or fear. |
| Intelligence over Information | Presenting raw data is not sufficient. Every visual element should present data already structured into intelligence, consistent with the product mission in [01-product.md](01-product.md). |
| Calm over Urgency | The interface must feel steady and composed at all times, even during volatile market conditions. Nothing in the design should imply that the trader must act immediately. |
| Professional over Promotional | The design language avoids marketing-style visual techniques (banners, badges of excitement, promotional colour use) in favour of a restrained, professional tone. |
| Minimal but Information Rich | Screens should be visually uncluttered while still conveying the depth of intelligence the trader needs. Minimalism is achieved through hierarchy and structure, not by removing necessary information. |
| Consistency over Creativity | The same type of information must look and behave the same way everywhere it appears. Novel visual treatments are avoided in favour of a predictable, unified design language. |

---

# 3. User Experience Principles

| Principle | Explanation |
|---|---|
| Single Source of Truth | Every piece of information must have exactly one authoritative visual representation in the interface, so the trader never has to reconcile conflicting displays of the same data. |
| Progressive Disclosure | Interfaces should present the most important information first, with supporting detail and evidence available on demand rather than shown all at once. |
| Fast Scanning | Layouts must be structured so a trader can absorb the current market situation in a few seconds, without needing to read dense blocks of text. |
| Low Cognitive Load | The interface should minimize the mental effort required to interpret it, through consistent structure, clear hierarchy, and restrained visual density. |
| Immediate Recognition | Recurring elements (evidence, context, states) must be immediately recognizable by their consistent visual treatment, without the trader needing to re-learn what they mean. |
| Predictable Behaviour | Interactive elements must behave the same way every time they are used, across every screen in the product. |
| No Surprise Interactions | The interface must never respond in a way the trader would not expect from a similar element elsewhere in the product. |

---

# 4. Information Hierarchy

MIOS presents information in the following order of priority:

1. Critical Intelligence
2. Supporting Evidence
3. Market Context
4. Historical Context
5. Metadata
6. Secondary Information

| Level | Description |
|---|---|
| Critical Intelligence | The most important, evidence-backed observation about current market conditions. This is what the trader should see first. |
| Supporting Evidence | The specific observable facts that justify the critical intelligence, allowing the trader to verify the reasoning behind it. |
| Market Context | Broader current conditions (such as structural levels or positioning) that frame the critical intelligence without being the primary focus. |
| Historical Context | Relevant prior market behavior that helps the trader interpret the current situation, presented as secondary reference material. |
| Metadata | Details such as timestamps, data freshness, or source information that support trust and traceability without competing for primary attention. |
| Secondary Information | Any additional information that may be useful but is not required to understand the current market situation at a glance. |

This order exists because a trader under time pressure must be able to identify what matters most before anything else. Placing evidence and context ahead of metadata and secondary detail ensures the interface serves decision-making first and completeness second, consistent with the "Explain Everything" and "Evidence-Based Intelligence" principles in [01-product.md](01-product.md).

---

# 5. Dashboard Philosophy

Every dashboard in MIOS must be organized to answer the following questions, in this order:

1. What is happening?
2. Why is it happening?
3. What evidence supports it?
4. What changed?
5. What should I watch?

A dashboard that cannot answer these five questions clearly is not complete. A dashboard that answers a sixth, implicit question — "what trade should I take?" — has violated the product's core identity. The dashboard must never tell the trader what trade to take. It may surface intelligence, evidence, and context; the interpretation and the trading decision belong entirely to the trader, consistent with the "Trader Makes Every Decision" principle in [01-product.md](01-product.md).

---

# 6. Layout System

| Element | Intended Behaviour |
|---|---|
| Top Navigation | Provides global orientation and access to major sections of the product. Remains stable and consistent across all screens. |
| Sidebar | Provides secondary navigation or contextual controls relevant to the current workspace, without competing with the primary workspace for attention. |
| Workspace | The primary content area where critical intelligence and supporting evidence are presented. This is the visual focus of every screen. |
| Cards | Group related information into a single, self-contained visual unit, used to separate distinct pieces of intelligence or evidence. |
| Panels | Larger structural containers used to organize related cards, tables, or sections within the workspace. |
| Spacing | Used consistently to separate unrelated elements and group related elements, reinforcing hierarchy without relying on borders or colour. |
| Alignment | Elements align to a consistent structure so that related information lines up predictably across the interface. |
| Grid System | Provides the underlying structural consistency that ensures layouts remain orderly and predictable across different screens and content densities. |
| Whitespace | Used deliberately to reduce visual density and support fast scanning, rather than treated as wasted space to be filled. |

---

# 7. Typography System

| Level | Purpose |
|---|---|
| Display | Reserved for the single most prominent piece of information on a screen, used sparingly. |
| Heading 1 | Identifies the primary section or screen the trader is currently viewing. |
| Heading 2 | Identifies major subsections within a screen. |
| Heading 3 | Identifies smaller groupings of related content within a subsection. |
| Body | Used for standard explanatory text, evidence descriptions, and general reading content. |
| Secondary Text | Used for supporting detail that is related to, but less important than, adjacent body text. |
| Caption | Used for short, small annotations attached to a specific element, such as a note on a chart or table. |
| Labels | Used to identify the purpose of a field, column, or control, distinct from the content itself. |
| Numbers | Used for numeric market data, styled for precise alignment and fast comparison. |
| Monospace | Used where consistent character width improves readability of aligned figures, such as tabular numeric data. |

Specific typefaces are intentionally not defined in this document; this section governs the hierarchy of purpose, not typeface selection.

---

# Numeric Presentation Standards

Financial software depends heavily on numerical readability. Traders scan large volumes of numeric data under time pressure, and inconsistent numeric presentation directly increases the risk of misreading a value during a live session.

| Rule | Description |
|------|-------------|
| Right Alignment | Numeric values should be right aligned whenever comparison is important. |
| Consistent Decimal Precision | Similar values must use identical decimal formatting. |
| Monospaced Numeric Display | Numbers that change frequently should use monospaced presentation where appropriate. |
| Thousands Separation | Large numbers should always be grouped for readability. |
| Timestamp Consistency | Every timestamp must follow a single format throughout the application. |
| Missing Values | Missing values must be represented consistently and never as zero unless zero is the actual value. |

These standards improve rapid scanning and reduce interpretation errors during live trading.

---

# 8. Colour Philosophy

This document defines colour behaviour, not a specific palette. Exact colour values are out of scope for this specification.

| Category | Where It Should Be Used |
|---|---|
| Primary | Used to draw attention to the single most important interactive or informational element on a screen. Used sparingly. |
| Secondary | Used to support the primary colour for related but less dominant elements. |
| Neutral | Used for the majority of interface surfaces, text, and structural elements, forming the calm visual baseline of the product. |
| Success | Used to indicate a positive or favourable state of a condition being described, not a trading outcome. |
| Warning | Used to indicate a condition that requires attention or carries elevated uncertainty. |
| Error | Used to indicate a failure, invalid state, or a problem that must be addressed. |
| Information | Used to indicate neutral, explanatory context that is neither positive nor negative. |
| Muted | Used for de-emphasized content, such as secondary or historical information, to visually recede behind critical intelligence. |
| Background | Used as the base surface of the interface, providing a calm, low-contrast foundation for content. |
| Surface | Used for containers such as cards and panels that sit above the background, providing subtle separation of content groups. |
| Border | Used to define the edges of structural elements where separation is needed without relying on strong colour contrast. |

Colour must never be the only communication mechanism. Any meaning conveyed through colour must also be conveyed through text, iconography, or structure, so that the interface remains understandable independent of colour perception.

---

# 9. Data Visualisation Principles

| Element | Appropriate Usage |
|---|---|
| Tables | Used to present structured, comparable data where precise values and alignment matter. |
| Charts | Used to reveal trends, relationships, or patterns in data that are difficult to perceive from raw numbers alone. |
| Badges | Used to attach a short, categorical label to an item, such as a status or classification. |
| Indicators | Used to represent the current state of a specific, well-defined condition at a glance. |
| Tags | Used to classify or group items by attribute, supporting filtering and scanning. |
| Highlights | Used sparingly to draw attention to a specific data point that is directly relevant to the critical intelligence being shown. |
| Trend Indicators | Used to show the direction of change of a value over time, in a way that is easy to scan quickly. |
| Confidence Indicators | Used to represent how strongly the available evidence supports a given observation, without implying certainty about future outcomes. |
| Evidence Indicators | Used to visually link a piece of intelligence to the specific evidence that supports it, reinforcing the "Explain Everything" principle in [01-product.md](01-product.md). |

Every visualisation must prioritize accurate, honest representation of the underlying data over visual appeal.

---

# Dashboard Composition Rules

Every dashboard should follow the same structural pattern.

Recommended order:

1. Market Story
2. Critical Intelligence
3. Supporting Evidence
4. Market Structure
5. Options Intelligence
6. Liquidity
7. Momentum
8. Context
9. Contradictions
10. Recent Changes
11. Metadata

This order minimizes cognitive load and allows traders to develop muscle memory when navigating MIOS.

Dashboards may omit sections when data is unavailable, but they must never rearrange the order.

---

# 10. Component Philosophy

| Component | Purpose |
|---|---|
| Cards | Present a single, self-contained unit of intelligence or evidence, grouped visually apart from unrelated content. |
| Tables | Present structured, multi-attribute data in a form that supports comparison and precise reading. |
| Accordions | Allow secondary or supporting detail to remain collapsed until the trader chooses to expand it, supporting progressive disclosure. |
| Tabs | Allow related but distinct groupings of content to share the same screen space without competing for attention simultaneously. |
| Lists | Present a sequence of related items in a simple, scannable form. |
| Filters | Allow the trader to narrow displayed information to what is currently relevant to them. |
| Search | Allow the trader to locate specific information directly, without browsing through unrelated content. |
| Modals | Present a focused task or piece of information that temporarily takes priority over the underlying screen. |
| Dialogs | Present a specific decision or confirmation the trader must respond to before continuing. |
| Drawers | Present supplementary content or controls alongside the current screen without fully replacing it. |
| Buttons | Represent a clear, singular action the trader can take. |
| Input Fields | Allow the trader to provide specific information or parameters to the system. |
| Dropdowns | Allow the trader to select one option from a constrained set of choices. |
| Tooltips | Provide brief, contextual clarification about an element without requiring navigation away from the current screen. |

Each component's purpose is defined here; visual treatment, structure, and implementation are addressed in future frontend documentation.

---

# 11. State Design

| State | Purpose |
|---|---|
| Loading | Communicates that requested information is being retrieved or processed and is not yet available. |
| Empty | Communicates that no data currently exists for a given view, distinct from a failure or loading condition. |
| Offline | Communicates that the system is currently disconnected from a required data source. |
| Updating | Communicates that displayed information is being refreshed with newer data. |
| Success | Communicates that an action or process has completed as expected. |
| Warning | Communicates that a condition requires the trader's attention without representing an outright failure. |
| Error | Communicates that an action or process has failed and requires acknowledgement or correction. |
| Disabled | Communicates that an element is currently unavailable for interaction. |
| Read Only | Communicates that displayed content cannot currently be modified. |

Every state must be visually distinct and consistently represented wherever it occurs, so the trader can recognize system status without ambiguity.

---

# 12. Accessibility Principles

| Principle | Requirement |
|---|---|
| Contrast | Text and meaningful visual elements must remain distinguishable against their background at all times. |
| Keyboard Navigation | Every interactive element must be operable without requiring a pointing device. |
| Screen Readers | Content and interactive elements must be structured so their meaning can be conveyed by assistive technology. |
| Focus States | The currently focused element must be clearly and consistently indicated. |
| Touch Targets | Interactive elements must be sized appropriately to be reliably operable. |
| Scalable Text | Text must remain legible when resized by the trader or their operating environment. |
| Motion Sensitivity | Motion must be reducible or disabled for traders sensitive to animated interfaces. |
| Colour Independence | No information may be conveyed by colour alone, consistent with Section 8. |
| Readable Tables | Tabular data must remain comprehensible and navigable regardless of assistive technology or display constraints. |

---

# 13. Motion Philosophy

| Principle | Explanation |
|---|---|
| Purposeful Motion | Motion is used only to communicate a meaningful change of state, never for visual embellishment. |
| No Decorative Motion | Animation that exists purely for aesthetic effect, without communicating information, is not permitted. |
| Fast Feedback | Motion used to acknowledge an interaction must occur quickly, so it supports rather than delays the trader's workflow. |
| Minimal Animation | Animation is used sparingly and only where it clarifies a transition or change that would otherwise be difficult to notice. |
| Reduced Motion Support | All motion must be capable of being reduced or disabled to accommodate trader preference or sensitivity. |

---

# 14. Design Constraints

| Constraint | Description |
|---|---|
| No Gamification | The interface must not use game-like mechanics (points, streaks, rewards) to encourage engagement. |
| No Flashing Indicators | Elements must not flash or strobe to draw attention. |
| No Buy/Sell Colours | Colour must never be used to imply a buy or sell action, consistent with the product's non-signal identity in [01-product.md](01-product.md). |
| No Fear-Based Design | The interface must not use visual techniques designed to provoke fear or anxiety about missing an opportunity. |
| No Artificial Scarcity | The interface must not imply limited availability or urgency where none genuinely exists. |
| No Promotional Language | Visual and textual treatment must avoid marketing-style promotional phrasing. |
| No Confetti | The interface must not use celebratory visual effects. |
| No Social Media Styling | The interface must avoid visual patterns associated with social media engagement mechanics (likes, feeds, streaks). |
| No Prediction Styling | The interface must not visually imply that any element is a forecast or prediction of future price movement. |
| No Signal Styling | The interface must not visually imply a buy/sell/hold signal or recommendation of any kind. |

---

# 15. Design Tokens

This section describes conceptual categories of design tokens used to maintain consistency across MIOS. Specific values are intentionally not defined in this document.

- Spacing
- Radius
- Elevation
- Border
- Shadow
- Typography
- Colours
- Opacity
- Transitions
- Icons

Each category represents a conceptual dimension of visual consistency that must be defined once and reused everywhere, rather than redefined independently within individual screens or components.

---

# 16. Document Dependencies

This Design System Specification depends on:

- 01-product.md
- 02-architecture.md

This document is referenced by:

- All frontend specifications
- Dashboard specification
- Component specification
- Frontend implementation
- Design QA
- UX testing

---

# 17. Glossary

| Term | Meaning |
|------|---------|
| Design System | The complete set of principles, hierarchies, and constraints governing visual and interaction design across MIOS. |
| Progressive Disclosure | Presenting essential information first while making supporting detail available on demand. |
| Information Hierarchy | The defined order of priority in which information is presented to the trader. |
| Design Token | A conceptual, reusable unit of design decision (such as spacing or colour behaviour) applied consistently across the product. |
| State | A defined condition of an interface element (such as Loading, Error, or Disabled) that must be visually distinguishable. |
| Evidence Indicator | A visual element that links a piece of intelligence to its supporting evidence. |
| Confidence Indicator | A visual element representing the strength of evidence behind an observation. |
| Design Decision Record (DDR) | A formal record of an approved deviation from, or addition to, this Design System. |

---

# Design Governance

The Design System is governed through Design Decision Records (DDR).

Every new component must comply with this document.

Every modification must preserve consistency with existing components.

Any exception requires an approved DDR.

Visual experimentation is not permitted inside production without formal review.

---

# 18. Design Freeze

This Design System is considered the authoritative visual language for MIOS.

No new component, screen, interaction, or visual pattern may be introduced without conforming to this document or without an approved Design Decision Record (DDR).

Consistency across the product is mandatory.

---

# Design Checklist

- [ ] Consistent hierarchy
- [ ] Uses approved components
- [ ] Accessibility compliant
- [ ] Supports keyboard navigation
- [ ] Supports colour independence
- [ ] No promotional styling
- [ ] No signal styling
- [ ] No prediction styling
- [ ] Matches dashboard composition rules
- [ ] Matches typography hierarchy
- [ ] Matches spacing rules
- [ ] Reviewed

---

# 19. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-07-29 | MIOS Architecture | Initial Design System Specification for MIOS. |
