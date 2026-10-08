# Feature Specification: Dev Input Bottom Bar

**Feature Branch**: `006-dev-input-bottom-bar`
**Created**: 2026-10-04
**Status**: Draft
**Input**: User description: "Move the developer transcript input box from the top bar to the bottom bar... (dev-only flag gating unchanged, same submit-and-clear behavior, stretch-with-700px-max centered layout, 44px height, placeholder, focus outline, 18px theme text, top bar left with Heard/transcript/chip/Window, disabled-while-processing state, pixel-identical bar when flag off, no overlap down to 960x540, canvas unchanged; out of scope: new features, AI flow changes, mic button changes)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Type test commands from the bottom bar (Priority: P1)

A developer enables the existing developer setting and finds the
transcript input in the empty middle of the bottom bar, between the
Redo button and the status pill. Typing a command and pressing Enter
submits it through the unchanged AI-to-validation path and clears the
box, exactly as before.

**Why this priority**: This is the whole feature — same behavior, better
placed, freeing the top bar for transcript reading.

**Independent Test**: Can be fully tested with the developer setting on
by typing a heading command, verifying the board change plus box
clearing, and confirming the top bar no longer contains the input.

**Acceptance Scenarios**:

1. **Given** the developer setting enabled, **When** the developer types
   "Create a heading called Test" and presses Enter, **Then** the
   heading appears via the unchanged path and the box clears.
2. **Given** the developer setting enabled, **When** the bottom bar is
   inspected, **Then** the input sits between Redo and the status pill
   (not in the top bar).
3. **Given** a command is processing, **When** the input is viewed,
   **Then** it shows a subtle disabled state until the result lands.

---

### User Story 2 - Keep the teacher experience untouched (Priority: P1)

With the developer setting off, nothing appears in the middle of the
bottom bar: teachers see exactly the current layout, and the top bar
holds only the "Heard:" transcript, the result chip, and the Window
button with more room for transcript text.

**Why this priority**: The input is scaffolding, not product; teachers
must never notice it.

**Independent Test**: Can be fully tested with the setting off by
comparing the bottom bar against the current layout pixel-for-pixel in
spirit (same controls, same order, same empty middle).

**Acceptance Scenarios**:

1. **Given** the developer setting off, **When** the bottom bar is
   viewed, **Then** it shows mic, Undo, Redo, empty middle, and status
   pill exactly as now.
2. **Given** the top bar, **When** inspected, **Then** it contains only
   the "Heard:" label, transcript text, result chip, and Window button.

---

### User Story 3 - Fit at every window size (Priority: P2)

From 960×540 to fullscreen, the input stretches to fill its space (up
to 700px wide, centered), never overlaps any control, and the board
canvas layout and scaling are unchanged.

**Why this priority**: A dev tool that breaks the teaching layout at
small sizes defeats its own purpose.

**Independent Test**: Can be fully tested at 960×540 with the setting
on by verifying pairwise widget disjointness and unchanged board
geometry versus flag off.

**Acceptance Scenarios**:

1. **Given** the developer setting on at 960×540, **When** the bars are
   inspected, **Then** no widget overlaps another and the input is fully
   visible.
2. **Given** the input visible, **When** the board area is measured,
   **Then** canvas size, aspect ratio, and letterboxing match the
   flag-off layout pixel-identically in effect.

---

### Edge Cases

- What happens when the developer setting toggles mid-session? →
  Documented as launch-time behavior; no requirement to hot-swap (a
  restart applies it).
- What happens when Enter is pressed on an empty box? → Nothing is
  submitted (existing behavior preserved).
- What happens at exactly 960×540 with a long transcript showing? →
  Input, chip, and Window button all remain fully visible; transcript
  elision behaves as before.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The developer input MUST move from the top strip to the
  bottom bar, between the Redo button and the status pill; the top bar
  MUST then contain only the "Heard:" label, transcript, result chip,
  and Window button.
- **FR-002**: The input MUST stay developer-only: hidden unless the
  existing setting is enabled, with identical gating semantics as now.
- **FR-003**: Submit behavior MUST be unchanged: Enter submits the
  typed text as a transcript through the same AI-to-validation path,
  then clears the box.
- **FR-004**: The input MUST stretch to fill the space between the left
  group and the pill, capped at 700px wide and centered in that space,
  at about 44px high with placeholder "Dev transcript — type a command
  and press Enter", a visible focus outline, and text at least 18px from
  the central theme.
- **FR-005**: The input MUST show a subtle disabled state while a
  command is processing.
- **FR-006**: With the setting off, the bottom bar MUST look exactly as
  now (no gap, placeholder, or layout shift from the absent input).
- **FR-007**: The input MUST NOT overlap any control at any size down
  to 960×540; board canvas layout and scaling MUST be unchanged.
- **FR-008**: Out of scope: new features, AI flow changes, microphone
  button changes.

### Key Entities

- **Developer input**: Flag-gated transcript box; same submit/clear
  contract, new bottom-bar home.
- **Bottom-bar middle space**: Previously empty stretch; now hosts the
  input (when enabled) up to 700px centered, empty otherwise.
- **Top bar**: Heard label, transcript, chip, Window button — transcript
  gains the freed room.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 10 out of 10 typed submissions with the setting on produce
  the same board results as before the move, and the box clears each
  time.
- **SC-002**: With the setting off, bottom-bar control order, sizes,
  and positions match the current layout in 10 out of 10 inspections.
- **SC-003**: At 960×540, 1366×768, and 1920×1080 with the setting on,
  all bar widgets are pairwise disjoint and the input is fully visible.
- **SC-004**: Board-view geometry is identical with the setting on and
  off at the same window size (the 44px input fits inside the existing
  bar height set by the microphone control).
- **SC-005**: Zero behavior regressions: the full pre-change suite
  passes with only layout-assertion updates where the move requires
  them.

## Assumptions

- "Maximum 700px centered" means the input grows with the middle space
  to 700px, then stays centered while extra room stays empty.
- The existing setting name and semantics are reused unchanged; only
  the widget's parent layout changes.
- Disabled-while-processing reuses the existing button-disabled visual
  language (subtle, theme-consistent).
