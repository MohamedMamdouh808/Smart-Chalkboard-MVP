# Feature Specification: Compact Control Layout

**Feature Branch**: `004-compact-control-layout`
**Created**: 2026-10-04
**Status**: Draft
**Input**: User description: "Adjust the Smart Chalkboard control layout without changing behavior, commands or data... (compact bottom-left mic/Undo/Redo, top-right Window toggle beside result chip, compact status pill, no stretched controls, larger board area, readable long transcripts, central theme sizing; out of scope: new features, new colors, board rendering changes)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compact bottom-left voice and history controls (Priority: P1)

A teacher finds the microphone, Undo, and Redo grouped compactly at the
bottom left, in that order. The microphone is a smaller circular control
(about 64px); Undo and Redo are compact (about 44px high). Every control
keeps at least a 44px touch/pen target with the existing icons and
hover, pressed, disabled, and focus treatments.

**Why this priority**: This is the requested layout change; compact
controls return vertical room to the board without weakening operability.

**Independent Test**: Can be fully tested by measuring control order,
sizes, targets, and states, and by operating each control with pen/mouse
and keyboard focus.

**Acceptance Scenarios**:

1. **Given** the bottom bar, **When** read left to right, **Then** the
   order is microphone, Undo, Redo, with no other primary controls in
   that group.
2. **Given** any supported window size, **When** each control is
   measured, **Then** the mic is about 64px circular, Undo/Redo are
   about 44px high, and every target is at least 44px.
3. **Given** empty versus non-empty history, **When** Undo/Redo are
   inspected, **Then** disabled and enabled treatments remain visibly
   distinct with existing icons and interaction states preserved.

---

### User Story 2 - Window toggle beside the result chip (Priority: P1)

A teacher finds a compact Window icon control at the top right,
immediately beside the result chip. It carries the accessible name
"Window", shows "Window" as a tooltip, and still toggles fullscreen with
F11.

**Why this priority**: Moving window switching out of the bottom bar is
required to shorten the bar and enlarge the board.

**Independent Test**: Can be fully tested by locating the control beside
the result chip, reading its tooltip/accessible name, and toggling with
both the control and F11.

**Acceptance Scenarios**:

1. **Given** the top bar, **When** inspected, **Then** the Window control
   sits immediately beside the result chip and is about 44px with at
   least a 44px target.
2. **Given** the Window control, **When** its tooltip and accessible
   name are read, **Then** both say "Window".
3. **Given** either window mode, **When** the teacher uses the control or
   presses F11, **Then** the mode toggles with board content unchanged.

---

### User Story 3 - Compact status with a larger board (Priority: P1)

A compact status pill (about 36px high, width fitting its text) sits at
the bottom right, still showing the colored dot, icon, and text for
Idle / Listening / Processing / Validating / Executing. Controls no
longer stretch to equal widths: the middle stays empty and the board
area grows taller.

**Why this priority**: A smaller bar directly increases visible board
room while preserving glanceable status.

**Independent Test**: Can be fully tested by measuring the pill, checking
all five states, verifying empty middle space, and comparing board-view
height before and after.

**Acceptance Scenarios**:

1. **Given** the bottom bar, **When** measured, **Then** the status pill
   is about 36px high with width fitting its text at the bottom right.
2. **Given** each pipeline state, **When** the pill is viewed, **Then**
   it shows the matching colored dot, icon, and text label.
3. **Given** the bottom bar, **When** inspected, **Then** controls are
   left- and right-anchored with empty space between them, and the board
   view is taller than before with identical canvas size, aspect ratio,
   and letterboxing.

---

### User Story 4 - Long transcripts stay readable (Priority: P2)

Long transcripts never break mid-word: the strip shortens text at a word
boundary with "..." and exposes the full transcript in a tooltip, while
the result chip and Window control stay fully visible down to 960×540.

**Why this priority**: The current strip can cut transcripts mid-word;
classroom voice feedback must remain complete and readable.

**Independent Test**: Can be fully tested with an overlong transcript at
960×540 by checking word-boundary shortening, tooltip completeness, and
chip/Window visibility.

**Acceptance Scenarios**:

1. **Given** an overlong transcript, **When** viewed, **Then** the
   visible text ends at a word boundary with "...", never mid-word.
2. **Given** a shortened transcript, **When** hovered, **Then** the full
   transcript appears in a tooltip.
3. **Given** 960×540 through fullscreen, **When** the top bar is
   inspected, **Then** the result chip and Window control remain fully
   visible and operable.

---

### Edge Cases

- What happens at exactly 960×540? → Left group, pill, Heard label,
  shortened transcript, chip, and Window control all fit without overlap.
- What happens with an extremely long single word? → It may break only
  because no word boundary exists; the full text remains in the tooltip.
- What happens when history is empty? → Compact Undo/Redo show disabled
  treatments from startup.
- What happens during state changes? → The compact pill updates
  text/icon/color together; no behavior or timing changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The bottom bar MUST anchor microphone, Undo, and Redo at
  the bottom left in that order, with empty space between that group and
  the bottom-right status pill and no equal-width stretching.
- **FR-002**: The microphone MUST be a circular control about 64px with
  at least a 44px target, keeping its existing icon and state
  appearances.
- **FR-003**: Undo and Redo MUST be compact controls about 44px high
  with at least 44px targets, keeping existing icons and hover,
  pressed, disabled, and focus states.
- **FR-004**: The Window toggle MUST move to the top right immediately
  beside the result chip as a compact icon control about 44px with at
  least a 44px target.
- **FR-005**: The Window control MUST expose accessible name "Window",
  tooltip "Window", and MUST remain bound to F11 with unchanged toggle
  behavior.
- **FR-006**: The status pill MUST be about 36px high, width fitting its
  text, anchored bottom right, preserving dot, icon, and text for all
  five states.
- **FR-007**: The board canvas MUST keep its fixed logical size, aspect
  ratio, and letterboxing; it MUST scale larger only because chrome uses
  less vertical room.
- **FR-008**: Long transcripts MUST NOT truncate mid-word; visible text
  MUST end at a word boundary with "..." and the full transcript MUST be
  available in a tooltip.
- **FR-009**: The result chip and Window control MUST remain fully
  visible and operable from 960×540 through fullscreen.
- **FR-010**: All sizes and spacing MUST come from the central theme
  definition; no behavior, commands, data, coordinates, colors, or board
  rendering may change.
- **FR-011**: Out of scope: new features, new colors, and board-rendering
  changes.

### Key Entities

- **Left control group**: Microphone, Undo, Redo in fixed order with
  compact sizes and preserved states.
- **Top-right window control**: Compact icon control beside the result
  chip with tooltip/accessible name "Window" and F11 behavior.
- **Compact status pill**: Bottom-right state indicator with dot, icon,
  and fitting text width.
- **Transcript presentation**: Word-boundary shortening with "..." plus
  full-text tooltip; chip and Window control always visible.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Control order, sizes, and targets verify in 10 out of 10
  inspections: mic/Undo/Redo bottom left; mic about 64px; Undo/Redo
  about 44px high; all targets at least 44px.
- **SC-002**: Window control found beside the result chip in 10 out of
  10 trials; tooltip and accessible name read "Window"; F11 and control
  both toggle modes with unchanged content.
- **SC-003**: Status pill measures about 36px high with fitting width in
  all five states, each showing dot, icon, and text.
- **SC-004**: Board-view height increases versus the prior layout while
  canvas size, aspect ratio, and letterboxing stay identical.
- **SC-005**: At 960×540, 20 out of 20 long-transcript trials show
  word-boundary "..." shortening, complete tooltips, and fully visible
  chip plus Window control.
- **SC-006**: Zero behavior regressions: the full pre-change test suite
  passes unchanged.
- **SC-007**: 9 out of 10 first-time teachers operate mic, Undo, Redo,
  Window, and status without guidance.

## Assumptions

- "About" sizes mean theme tokens may round to whole pixels without
  changing the specified targets or minima.
- Single-line word-boundary ellipsis plus tooltip is the default
  transcript treatment; a maximum two-line wrap is acceptable only if
  the theme reserves strip height and chip/Window visibility still holds.
- Existing icons, palettes, state appearances, and button-state styling
  are reused unchanged.
