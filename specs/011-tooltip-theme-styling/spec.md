# Feature Specification: Tooltip Theme Styling

**Feature Branch**: `011-tooltip-theme-styling`  
**Created**: 2026-10-06  
**Status**: Draft  
**Input**: User description: "Style all tooltips to match the dark Smart Chalkboard theme: dark surface background, light text of at least 16px, a thin border from the theme tokens, rounded corners, and 6px by 10px padding, with a 500ms show delay. Tooltips must be readable (WCAG AA contrast), never white, and must not cover the control they describe more than necessary. Keep all existing tooltip texts, including the transcript tooltip with the full text. All values come from the central theme module. Out of scope: new tooltips, new features."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read every tooltip comfortably (Priority: P1)

A teacher hovers over controls and reads each tooltip against the dark classroom theme. Every tooltip uses a dark surface, sufficiently large light text, a thin theme border, rounded corners, and comfortable padding. No tooltip appears white or unreadable.

**Why this priority**: Tooltips explain classroom controls, and unreadable help directly harms usability during lessons.

**Independent Test**: Can be fully tested by displaying every existing tooltip and checking background, text size and contrast, border, corner shape, padding, and text preservation, without changing application behavior.

**Acceptance Scenarios**:

1. **Given** any existing tooltip, **When** it appears, **Then** it uses a dark surface background and light text of at least 16 pixels.
2. **Given** any existing tooltip, **When** it appears, **Then** it has a thin theme-derived border, rounded corners, and 6-pixel vertical by 10-pixel horizontal padding.
3. **Given** any existing tooltip text, **When** styling is applied, **Then** the complete original text remains unchanged.

---

### User Story 2 - Avoid disruptive tooltip timing and placement (Priority: P1)

A teacher receives help only after a brief intentional hover, and tooltips do not unnecessarily cover the control being described. The full transcript tooltip continues to provide the complete heard text.

**Why this priority**: Well-timed and minimally obstructive help preserves lesson flow, while the full transcript remains necessary when visible text is shortened.

**Independent Test**: Can be fully tested by hovering, waiting, moving away, and checking tooltip timing, placement, dismissal, and transcript completeness.

**Acceptance Scenarios**:

1. **Given** a brief or accidental hover, **When** less than 500 milliseconds elapses, **Then** no tooltip appears.
2. **Given** a sustained hover, **When** 500 milliseconds elapses, **Then** the corresponding tooltip appears.
3. **Given** the shortened visible transcript, **When** its tooltip appears, **Then** it contains the complete transcript text.
4. **Given** any tooltip, **When** it appears, **Then** it covers the described control only as much as necessary to remain readable.

---

### User Story 3 - Keep one consistent tooltip theme (Priority: P2)

A teacher encounters the same tooltip appearance everywhere in the application. All visual tooltip values come from the central theme, preventing mismatched styles.

**Why this priority**: Consistency reduces visual distraction and makes future theme maintenance safer.

**Independent Test**: Can be fully tested by comparing all tooltips against the central theme values and confirming that no tooltip uses separate styling values.

**Acceptance Scenarios**:

1. **Given** tooltips across the application, **When** they appear, **Then** they share the same background, text, border, corner, padding, and delay behavior.
2. **Given** the central theme, **When** tooltip values are inspected, **Then** every tooltip appearance value originates there rather than from separate widget-level values.

---

### Edge Cases

- What happens with very long tooltip text? The complete text remains available and readable without changing the requested padding, border, or delay behavior.
- What happens when the pointer moves quickly across controls? Tooltips do not appear or persist in a way that obscures lesson content unnecessarily.
- What happens when a tooltip appears near a window edge? It remains readable while covering as little of its control and surrounding content as possible.
- What happens to existing accessibility contrast? Every tooltip combination continues to meet WCAG AA contrast and never uses a white background.
- What happens to controls without tooltips? No new tooltips are added.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All tooltips MUST use a dark surface background and MUST never use a white background.
- **FR-002**: All tooltip text MUST be light, MUST be at least 16 pixels in size, and MUST meet WCAG AA contrast against its background.
- **FR-003**: All tooltips MUST use a thin border derived from theme tokens.
- **FR-004**: All tooltips MUST use rounded corners.
- **FR-005**: All tooltips MUST use 6 pixels of vertical padding and 10 pixels of horizontal padding.
- **FR-006**: Tooltips MUST appear after a 500-millisecond hover delay.
- **FR-007**: Tooltips MUST cover the control they describe only as much as necessary for readability.
- **FR-008**: All existing tooltip texts MUST remain unchanged, including the transcript tooltip containing the complete transcript.
- **FR-009**: Every tooltip appearance value MUST come from the central theme module.
- **FR-010**: Out of scope: adding new tooltips and adding new application features.

### Key Entities *(include if feature involves data)*

- **Tooltip appearance**: The shared background, text, border, corner, padding, and timing presentation applied to every tooltip.
- **Tooltip delay**: The 500-millisecond hover interval before help appears.
- **Tooltip text preservation**: The unchanged existing text for every tooltip, including the complete transcript.
- **Central theme source**: The single authoritative source for all tooltip appearance values.
- **Tooltip placement**: The on-screen position that preserves readability while minimizing coverage of the described control.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every existing tooltip passes dark-background, light-text, minimum-size, border, corner, and padding checks in every tooltip inspection.
- **SC-002**: Every tooltip-text comparison shows byte-identical text before and after styling, including the complete transcript tooltip.
- **SC-003**: Tooltips appear in at least 95 of 100 sustained-hover trials after the required delay and in zero of 100 brief-hover trials before it.
- **SC-004**: Every tooltip foreground/background combination meets WCAG AA contrast, with no white tooltip background observed.
- **SC-005**: At least 9 out of 10 teachers rate tooltips as readable, consistent, and non-obstructive without guidance.
- **SC-006**: No new tooltip or unrelated application behavior is introduced in tooltip-styling verification.

## Assumptions

- The existing set of tooltips is complete and no inventory change is required.
- A 500-millisecond delay distinguishes intentional hovers from incidental pointer movement.
- “Thin border” means the theme’s established lightweight border treatment rather than a heavy visual frame.
- “Rounded corners” means the theme’s established corner treatment rather than square tooltip edges.
- “As necessary” means tooltips may overlap nearby content when required for readability, but do not cover their control more than needed.
- All measurements use the application’s existing pixel and timing conventions.
