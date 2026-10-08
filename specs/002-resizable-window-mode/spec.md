# Feature Specification: Resizable Window Mode

**Feature Branch**: `002-resizable-window-mode`
**Created**: 2026-10-03
**Status**: Draft
**Input**: User description: "Add a resizable window mode to Smart Chalkboard... (fullscreen/window toggle, persisted mode, aspect-preserving canvas scaling, coordinate mapping, readable controls, centered dialogs, resize safety, text-clipping and button-contrast fixes; out of scope: canvas-size changes, multi-monitor, multiple windows, zoom/pan)"

## Clarifications

### Session 2026-10-03

- Q: Should window mode use the same letterboxing for any aspect ratio? → A: Yes — always fit the whole canvas, preserve ratio, center, letterbox; no exceptions.
- Q: Should the last window size and position be remembered between sessions? → A: Yes — restore size, position, and mode (fresh install defaults to fullscreen).
- Q: Should text auto-grow its box or wrap when wider than the element? → A: Wrap inside the fixed box (size/coords never change); text that cannot fit the default box is rejected at creation with "Text is too long for this element. Resize it or shorten the text."; if a later resize makes the box too short, render clips at the box edge.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Switch between fullscreen and window (Priority: P1)

A teacher switches between a fullscreen board and a movable window at any
time using a visible toggle button or the F11 key. The app reopens in
whichever mode was active when it was last closed.

**Why this priority**: Teachers present fullscreen but prepare and
multitask in a window; without an always-available toggle the new mode is
unreachable mid-lesson.

**Independent Test**: Can be fully tested by pressing F11 and the toggle
button alternately (mode changes each time), closing and reopening the
app, and verifying the reopened mode matches the closing mode.

**Acceptance Scenarios**:

1. **Given** the app is fullscreen, **When** the teacher presses F11 or
   the toggle button, **Then** a normal window appears at a usable size
   with the same board content unchanged.
2. **Given** the app is windowed, **When** the teacher presses F11 or the
   toggle button, **Then** the board returns to fullscreen with identical
   content.
3. **Given** the teacher closes the app while windowed, **When** the app
   is reopened, **Then** it starts windowed; closing fullscreen reopens
   fullscreen.

---

### User Story 2 - Resize freely with a stable canvas (Priority: P1)

A teacher drags window borders to resize, moves, minimizes, and maximizes
the window. The board keeps its fixed logical size: content scales to fit,
preserves aspect ratio, stays centered with letterboxing, and nothing
about the lesson (coordinates, saves, exports) changes with window size.

**Why this priority**: This is the core promise of the feature — flexible
placement with zero effect on lesson data.

**Independent Test**: Can be fully tested by resizing through several
sizes (including the 960×540 minimum), saving, exporting, and verifying
byte-identical lesson data and exports across sizes.

**Acceptance Scenarios**:

1. **Given** a board with content, **When** the teacher drags the window
   from large to the 960×540 minimum and back, **Then** all content stays
   fully visible, undistorted, and centered, with empty margins
   letterboxed.
2. **Given** content created fullscreen, **When** the teacher saves and
   exports in a small window, **Then** the saved lesson and exported file
   are identical to ones produced fullscreen.
3. **Given** any supported window size, **When** the teacher taps an
   element with the pen, **Then** the intended element (and only it) is
   selected.

---

### User Story 3 - Readable controls at every size (Priority: P1)

The control bar (microphone, Undo, Redo, status) and transcription strip
stay fully visible, readable, and usable from the 960×540 minimum up to
fullscreen, never overlapping the board. Button text meets a readable
contrast against its background.

**Why this priority**: Small-window controls that are unreadable or
unreachable break voice and undo exactly when the teacher multitasks.

**Independent Test**: Can be fully tested at 960×540 by reading every
control label, activating each control by pen/mouse, and confirming no
control overlaps the board area.

**Acceptance Scenarios**:

1. **Given** the minimum 960×540 window, **When** the teacher looks at the
   control bar and transcription strip, **Then** every label is readable
   and every control responds with at least a 48px touch target.
2. **Given** any window size, **When** the board is inspected, **Then** no
   control or strip covers any board content.
3. **Given** a heading on the board, **When** viewed at any supported
   size, **Then** the full heading text is visible and never clipped by
   its element box.

---

### User Story 4 - Resize safely mid-activity (Priority: P2)

Resizing (or mode switching) while a voice command processes, a pen
stroke is in progress, or a dialog is open never loses input or corrupts
state; dialogs stay centered over the window.

**Why this priority**: Mid-lesson resizes coincide with teaching actions;
losing a stroke or a confirmation decision is a data-loss class failure.

**Independent Test**: Can be fully tested by resizing during a processing
command, mid-stroke, and with a confirmation dialog open, then verifying
the command result, the completed stroke, and the dialog decision all
land correctly.

**Acceptance Scenarios**:

1. **Given** a voice command is processing, **When** the teacher resizes
   the window, **Then** the command still completes with the correct
   board result.
2. **Given** a pen stroke is being drawn, **When** the window is resized
   mid-stroke, **Then** the finished stroke commits whole with correct
   coordinates.
3. **Given** a confirmation or clarification dialog is open, **When** the
   window is resized or the mode toggles, **Then** the dialog stays
   centered and its confirm/cancel outcome is honored exactly once.

---

### Edge Cases

- What happens at exactly 960×540? → Smallest supported layout: all
  controls visible, board letterboxed, nothing scrollable or cut off.
- What happens when the window is maximized/restored repeatedly? → Mode
  and content stable; last mode persisted only at close, not per toggle.
- What happens when a resize lands mid-confirmation-timeout? → Timeout
  still counts as cancel exactly once; no double execution.
- What happens to in-flight pen coordinates when the scale changes
  mid-stroke? → Points map through the scale active at each sample or the
  stroke re-maps consistently; the committed element matches what the
  teacher drew.
- What happens when the display is smaller than 960×540? → Window keeps
  its minimum size and the OS window controls remain reachable; content
  never scales below the minimum-size layout.
- What happens when entered text cannot fit its element box? → Rejected
  at creation with "Text is too long for this element. Resize it or
  shorten the text."; never silently truncated at creation time.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST offer both fullscreen and normal-window modes
  with a visible toggle button and the F11 key working at any time,
  including mid-lesson.
- **FR-002**: System MUST start in the window mode active at last close
  (persisted locally across restarts), restoring the last window size
  and position when reopening windowed (LOCKED 2026-10-03).
- **FR-003**: Window mode MUST support free drag-resize, move, minimize,
  and maximize, with a minimum window size of 960×540.
- **FR-004**: The board MUST keep its fixed logical size and coordinate
  system; the view MUST scale content to fit while preserving aspect
  ratio, centered, with letterbox margins for every aspect ratio without
  exception (LOCKED 2026-10-03); canvas size itself MUST NOT change.
- **FR-005**: Board state, element coordinates, saved lessons, and
  exported output MUST be identical regardless of window size or mode.
- **FR-006**: Pen input and element selection MUST map from screen to
  canvas coordinates correctly at every size and scale (tapping an
  element selects exactly it).
- **FR-007**: The control bar and transcription strip MUST remain fully
  visible and readable at every supported size with minimum 48px targets
  and MUST never overlap board content.
- **FR-008**: Board text (including headings) MUST wrap inside its fixed
  element box — box size and coordinates MUST never change to fit text
  (LOCKED 2026-10-03). Text that cannot fit the default box MUST be
  rejected at creation with "Text is too long for this element. Resize
  it or shorten the text." If a later resize makes the box too short,
  rendering clips at the box edge without altering layout.
- **FR-009**: Control-bar button text MUST meet a contrast ratio of at
  least 4.5:1 against its background.
- **FR-010**: Confirmation and clarification dialogs MUST be centered
  over the window and stay centered across resizes and mode switches.
- **FR-011**: Resize or mode switch during command processing, active
  drawing, or an open dialog MUST NOT lose input or corrupt state; dialog
  outcomes apply exactly once.
- **FR-012**: Out of scope: changing the canvas size, multi-monitor
  layouts, multiple windows, and zoom/pan gestures.

### Key Entities

- **Window mode**: Fullscreen or normal window; persisted preference
  restored at startup; toggled via button or F11.
- **Viewport mapping**: Reversible scale + centering offset between fixed
  canvas coordinates and current screen pixels; recomputed on every
  resize; the single source for rendering, pen, and selection hit-testing.
- **Control bar / transcription strip**: Fixed chrome outside the board
  area; layout guarantees visibility and minimum target sizes at 960×540
  and above.
- **Dialog anchor**: Center-of-window positioning rule for confirmation
  and clarification dialogs, re-evaluated on resize and mode change.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A teacher toggles fullscreen ↔ window via button and F11
  (4 switches) with zero content or selection changes, verified by state
  comparison.
- **SC-002**: Saved-lesson files and exports produced at 960×540,
  1280×720, and fullscreen are byte-identical for the same board.
- **SC-003**: 100 pen taps across three window sizes select the intended
  element every time (100% hit accuracy).
- **SC-004**: At 960×540, all control labels are readable and activatable
  (9 out of 10 first-time checks pass without assistance), no control
  overlaps the board, and the full heading text is visible without
  clipping.
- **SC-005**: Button-text contrast ratio measures at least 4.5:1 in both
  modes.
- **SC-006**: Zero lost inputs or state corruptions across 20
  resize-during-activity trials (processing command, mid-stroke, open
  dialog).
- **SC-007**: The app reopens in its closing mode in 10 out of 10 trials
  alternating fullscreen and windowed closes.

## Assumptions

- The persisted mode preference is lightweight local state (restored
  before first paint; a fresh install defaults to fullscreen); the last
  window size and position are restored with it (LOCKED 2026-10-03).
- The 960×540 minimum applies to the whole window including chrome; the
  board area is whatever remains after the always-visible control bar and
  transcription strip.
- Letterbox margins share the board background tone; no scrolling is
  introduced at any supported size.
- F11 is reserved for the mode toggle while teaching; Esc keeps its
  existing behavior.
- Text-fit fix keeps current element sizes and positions (LOCKED
  2026-10-03: text wraps inside the fixed box; over-long text rejected at
  creation; post-resize overflow clips at the edge; no layout or
  coordinate changes).
