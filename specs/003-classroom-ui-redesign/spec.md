# Feature Specification: Classroom UI Redesign

**Feature Branch**: `003-classroom-ui-redesign`
**Created**: 2026-10-03
**Status**: Draft
**Input**: User description: "Redesign the Smart Chalkboard UI for classroom readability and clear system status, without changing any board behavior, commands or data... (dark slate theme, distinct board surface, transcription strip with Heard label + result chip, circular mic with per-state appearance, icon secondary buttons, status pill, typography scale, WCAG AA contrast, selection with handles, button states, themed dialogs, 'Smart Chalkboard' title, central theme definition; out of scope: new features/commands, light theme, custom themes)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read the board from the back of the room (Priority: P1)

A teacher and students see board content on a dark slate surface that is
visibly distinct from the surrounding window. Headings and body text are
large, high-contrast, and never clipped.

**Why this priority**: Classroom readability is the purpose of the whole
redesign; if content isn't legible at distance, nothing else matters.

**Independent Test**: Can be fully tested by viewing a board with a
heading, body text, shape, and drawing at fullscreen and at 960×540 and
verifying every element is legible, undistorted, and visually inside a
distinct board surface.

**Acceptance Scenarios**:

1. **Given** a board with a heading and body text, **When** viewed
   fullscreen from a normal classroom distance, **Then** the heading
   (≥64px at full canvas scale) and body text (≥36px) are legible and
   fully inside their element bounds.
2. **Given** any window size, **When** the teacher looks at the canvas
   area, **Then** the board surface is visibly distinct from the darker
   surrounding margins (lighter fill, thin border, soft shadow).

---

### User Story 2 - Know what the system heard and what happened (Priority: P1)

A teacher glances at the top bar and sees a "Heard:" label with the latest
transcript in large text (or an inviting placeholder when empty) plus a
result chip on the right showing the outcome — Done, Needs confirmation,
Needs clarification, or Error — each with its own color, icon, AND text
label, never color alone.

**Why this priority**: Voice teaching fails silently without visible
confirmation of what was heard and what the system did about it.

**Independent Test**: Can be fully tested by issuing one command in each
outcome class and verifying the strip shows the transcript and the chip
shows the matching icon + text + color.

**Acceptance Scenarios**:

1. **Given** no command has been spoken yet, **When** the teacher looks at
   the top bar, **Then** it shows "Heard:" with the placeholder "Hold the
   mic and speak a command" in large readable text.
2. **Given** a voice command completes, **When** the teacher checks the
   top bar, **Then** the transcript is shown and the result chip reads
   Done (or Needs confirmation / Needs clarification / Error as
   appropriate), each distinguishable without relying on color.
3. **Given** transcript and status text anywhere in the top bar, **When**
   measured, **Then** the text is at least 20px and meets the contrast
   requirement.

---

### User Story 3 - Operate controls by sight and touch (Priority: P1)

A teacher finds a large circular microphone button as the primary control
that visibly reflects the system state (idle, listening with a pulsing
ring, processing, validating, executing), flanked by smaller secondary
Undo, Redo, and window-toggle buttons with consistent icons (no emoji),
plus a status pill naming the current state with its own color and icon.

**Why this priority**: Mid-lesson operation is glance-driven; the primary
action and the system state must be recognizable instantly.

**Independent Test**: Can be fully tested by stepping through all five
states and verifying the mic appearance, status pill text/color/icon, and
that every button shows distinct hover, pressed, focus, and (where
applicable) disabled treatments.

**Acceptance Scenarios**:

1. **Given** any system state, **When** the teacher looks at the control
   bar, **Then** the mic button (≥96px, circular) shows that state's
   appearance and the status pill names the state with matching color
   and icon.
2. **Given** nothing to undo or redo, **When** the teacher looks at Undo
   and Redo, **Then** both are visibly disabled; after an action, the
   corresponding button enables with a visible change.
3. **Given** keyboard navigation, **When** a button receives focus,
   **Then** a visible focus indicator appears, distinct from hover and
   pressed states.

---

### User Story 4 - Confirm and select with confidence (Priority: P2)

Confirmation and clarification dialogs share the same theme with large
(≥48px) Cancel/Confirm buttons, and the selected board element shows a
clear outline with corner handles. The window title reads exactly
"Smart Chalkboard".

**Why this priority**: Destructive decisions and selection targets must
be unmistakable; consistent theming keeps the classroom trust established
by the main surfaces.

**Independent Test**: Can be fully tested by opening each dialog,
checking theme consistency and button sizes, selecting an element and
verifying outline + handles, and reading the window title.

**Acceptance Scenarios**:

1. **Given** a delete confirmation is open, **When** inspected, **Then**
   it uses the same dark slate theme with Cancel/Confirm buttons at
   least 48px high.
2. **Given** an element is selected, **When** viewed, **Then** a clear
   outline with corner handles marks exactly that element.
3. **Given** the app window, **When** the title is read, **Then** it is
   exactly "Smart Chalkboard".

---

### Edge Cases

- What happens for color-blind teachers? → No meaning is carried by
  color alone: every state and outcome pairs color with an icon and text.
- What happens at the 960×540 minimum? → All bars, chips, pills, and
  dialogs remain fully visible and readable; nothing overlaps the board.
- What happens when a transcript is very long? → The strip shows the
  latest transcript readably (truncation, if any, never hides the result
  chip).
- What happens when the system has no command history? → Undo/Redo show
  their disabled treatment from startup until actions occur.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The app MUST use a dark slate theme with the board canvas
  drawn as a slightly lighter rounded rectangle (thin border, soft
  shadow) inside a darker window background, so board and margins are
  visibly distinct.
- **FR-002**: The top bar MUST show a small "Heard:" label, the latest
  transcript in large readable text, the placeholder "Hold the mic and
  speak a command" when empty, and a result chip (Done / Needs
  confirmation / Needs clarification / Error) using color plus icon plus
  text — never color alone.
- **FR-003**: The bottom bar MUST feature a large circular microphone
  button (≥96px) as the primary control with a distinct appearance per
  state (idle, listening with pulsing ring, processing, validating,
  executing).
- **FR-004**: Undo, Redo, and window-toggle MUST be smaller secondary
  buttons with consistent vector icons (no emoji), plus a status pill for
  Idle / Listening / Processing / Validating / Executing with a distinct
  color and icon per state.
- **FR-005**: Typography MUST use one sans-serif family with transcript
  and status text ≥20px, button labels ≥18px, board heading ≥64px and
  body text ≥36px at full canvas scale.
- **FR-006**: ALL text and controls MUST meet WCAG AA contrast against
  their backgrounds (≥4.5:1 normal text, ≥3:1 large text and controls).
- **FR-007**: The selected element MUST show a clear outline with corner
  handles marking exactly that element.
- **FR-008**: Buttons MUST show visible hover, pressed, disabled, and
  keyboard-focus states; Undo and Redo MUST appear disabled when
  unavailable and enable visibly when available.
- **FR-009**: Confirmation and clarification dialogs MUST share the theme
  with Cancel/Confirm buttons ≥48px high and stay centered over the
  window.
- **FR-010**: The window title MUST read exactly "Smart Chalkboard".
- **FR-011**: ALL colors, sizes, and fonts MUST come from one central
  theme definition; no hard-coded visual values elsewhere.
- **FR-012**: No board behavior, commands, data, or coordinates may
  change; out of scope: new features, new commands, light theme,
  user-customizable themes.

### Key Entities

- **Theme definition**: The single source for every color, size, and font
  (palette, typography scale, target sizes, state appearances); the only
  file visual values may originate from.
- **Result chip**: Transcript-outcome indicator (Done / Needs
  confirmation / Needs clarification / Error) combining color, icon, and
  text; never color alone.
- **Status pill**: Current-state indicator (Idle / Listening / Processing
  / Validating / Executing) combining color, icon, and text.
- **Selection adornment**: Outline plus corner handles drawn around
  exactly the selected element.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 10 out of 10 viewers correctly name the system state and
  the last outcome from across a room using the pill and chip alone
  (icons + text, color ignored in the test).
- **SC-002**: Measured contrast meets WCAG AA everywhere (≥4.5:1 normal
  text, ≥3:1 large text/controls) in both fullscreen and 960×540 window.
- **SC-003**: All five mic appearances and all five status-pill states
  are pairwise visually distinguishable in a side-by-side review.
- **SC-004**: Undo/Redo disabled-vs-enabled states are correctly
  identified in 20 out of 20 trials alternating empty and non-empty
  history.
- **SC-005**: Board heading (≥64px) and body (≥36px) at full canvas
  scale verified by measurement; full heading visible without clipping.
- **SC-006**: Zero board-behavior regressions: the full pre-redesign
  test suite passes unchanged (same commands, same coordinates, same
  saved data).
- **SC-007**: 9 out of 10 first-time teachers complete speak → confirm →
  undo using only the redesigned controls without guidance.

## Assumptions

- "One sans-serif family" defaults to the platform's standard UI
  sans-serif stack; headings may use a heavier weight of the same family.
- The pulsing listening ring animates at ~1 Hz with a reduced-motion
  fallback of a static ring (standard accessibility practice).
- Icon set uses simple geometric/vector glyphs drawn in the theme's
  text color; exact glyph shapes are a plan-level detail.
- The outdated "press Esc to exit" title suffix is removed; Esc keeps
  its existing behavior.
- "Heard:" label is small relative to the transcript text but itself
  meets the contrast requirement.
