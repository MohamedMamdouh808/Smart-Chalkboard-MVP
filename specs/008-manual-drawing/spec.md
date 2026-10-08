# Feature Specification: Manual Drawing

**Feature Branch**: `008-manual-drawing`
**Created**: 2026-10-04
**Status**: Draft
**Input**: User description: "Add manual drawing so the teacher can write and draw freely on the same board voice commands edit... (unified pen/mouse/touch input, Pen/Select modes, 1.5 s stroke grouping, engine-committed drawings with unique IDs and undo, voice-drawings coexistence with proportional resize and translation, proximity selection with outline/handles, canvas clipping rules, offline and queued coexistence, palette color with thin/medium/thick widths, point-preserving save/reopen; out of scope: handwriting recognition, drawing-to-shape/text conversion, partial stroke erase, palm tuning, multi-pen, voice pen)"

## Clarifications

### Session 2026-10-04

- Q: Should Pen mode be the default at startup? → A: No — start in Select mode; Pen is entered deliberately.
- Q: Should "this" fall back to the most recent drawing with nothing selected? → A: No — always ask to select; the never-guess rule holds for drawings too.
- Q: How long should stroke grouping wait before closing a group? → A: 1.5 seconds (confirmed).
- Q: Should there be a stroke width control in the main bar? → A: No — width lives in settings (default medium); the main bar stays uncluttered.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Draw freely with pen or mouse (Priority: P1)

A teacher switches to Pen mode and draws freehand strokes with live
rendering, using a pen/stylus (with pressure when available), a mouse,
or touch. No specific pen hardware is required, and a missing pen never
blocks mouse drawing.

**Why this priority**: Freehand writing is the core of this feature;
without device-independent drawing there is no product.

**Independent Test**: Can be fully tested with the mouse alone (no pen
connected) by drawing strokes and verifying live rendering plus a
committed drawing element afterward.

**Acceptance Scenarios**:

1. **Given** Pen mode with no pen connected, **When** the teacher
   presses and drags with the mouse, **Then** the stroke renders live
   as it is drawn.
2. **Given** several strokes drawn within 1.5 seconds of each other
   with no selection or command between them, **When** the group
   finishes, **Then** one drawing element with a unique ID (such as
   `drawing_001`) appears in history, supports Undo/Redo, and triggers
   autosave.

---

### User Story 2 - Switch between Pen and Select (Priority: P1)

A visible Pen / Select toggle (keyboard shortcuts P and S) switches
modes. In Select mode, clicking an element selects it; clicking near a
drawing's strokes (within a small tolerance) selects the drawing and
shows its outline with handles over its bounding box.

**Why this priority**: Mode confusion destroys drawings (stray marks) or
blocks selection; explicit visible modes keep both safe.

**Independent Test**: Can be fully tested by toggling with button and
shortcuts, drawing in Pen mode, then selecting the drawing in Select
mode and verifying outline plus handles.

**Acceptance Scenarios**:

1. **Given** either mode, **When** the teacher uses the toggle button or
   presses P/S, **Then** the mode switches visibly and immediately.
2. **Given** Select mode and an existing drawing, **When** the teacher
   clicks near (within tolerance of) one of its strokes, **Then** that
   drawing selects with outline and handles over its bounding box.

---

### User Story 3 - Command drawings by voice (Priority: P1)

Drawings coexist with headings, text, equations, and shapes in one
board with one ordering. Voice commands act on drawings exactly as on
other elements — move, resize, recolor, and confirmed delete — by
selection or by ID. Resize scales all stroke points proportionally,
move shifts them, results stay inside the canvas, and new voice-created
elements never erase or alter existing strokes.

**Why this priority**: Drawings must be first-class board citizens, not
second-class ink.

**Independent Test**: Can be fully tested by selecting a drawing and
issuing move, resize, recolor, and confirmed-delete commands, then
undoing each and verifying stroke points match exactly.

**Acceptance Scenarios**:

1. **Given** a drawing is selected, **When** the teacher says "make
   this bigger", **Then** every stroke point scales proportionally and
   the result stays inside the canvas.
2. **Given** a drawing is selected, **When** the teacher says "delete
   this" and confirms, **Then** it deletes (undo restores identical
   points); without confirmation nothing changes.
3. **Given** existing strokes, **When** a voice command creates new
   content, **Then** all stroke points are byte-identical afterward.

---

### User Story 4 - Keep drawing through failures (Priority: P2)

Drawing works with no network, while a voice command processes (the
stroke commit queues behind it, never concurrently), and across window
resizes without losing in-progress strokes. Strokes starting outside
the board are ignored; outside points clip to the canvas edge.

**Why this priority**: Lessons survive outages and multitasking only if
the pen never depends on services or timing luck.

**Independent Test**: Can be fully tested offline, during a processing
command, and mid-stroke through a resize, verifying committed strokes
and unchanged behavior afterward.

**Acceptance Scenarios**:

1. **Given** no network, **When** the teacher draws, **Then** strokes
   commit, undo, and save normally.
2. **Given** a voice command processing, **When** the teacher finishes
   a stroke group, **Then** it commits after the command (queued, never
   concurrent) with correct coordinates.
3. **Given** a stroke in progress, **When** the window resizes, **Then**
   the stroke is not lost and commits whole.

---

### User Story 5 - Reopen lessons with drawings intact (Priority: P2)

Drawings save with the lesson including every point (position plus
pressure when captured) and restore exactly on reopen, using the
current palette color with thin/medium/thick widths (default medium).

**Why this priority**: Lesson continuity is the teacher's work product;
lossy strokes destroy trust.

**Independent Test**: Can be fully tested by drawing with varied widths
and colors, saving, reopening, and verifying point-for-point identity.

**Acceptance Scenarios**:

1. **Given** drawings with several colors and widths, **When** the
   lesson is saved and reopened, **Then** every point, color, and width
   matches exactly.

---

### Edge Cases

- What happens when a stroke starts outside the board? → Ignored
  entirely; no element, no history entry.
- What happens when points leave the canvas mid-stroke? → Clipped to
  the edge; the stroke continues and commits.
- What happens when a resize would push scaled strokes off-canvas? →
  Rejected like any other element move, with the drawing untouched.
- What happens when two drawings overlap? → Topmost ordering decides
  selection; proximity tolerance never selects through a closer stroke.
- What happens when the teacher draws during AI confirmation? → The
  stroke previews live and commits in queue order after the dialog
  resolves.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The board MUST accept pen/stylus (pressure when
  available), mouse, and touch through one unified input path with no
  dependence on a specific pen protocol; missing pen hardware MUST never
  block mouse drawing.
- **FR-002**: A visible Pen / Select toggle MUST switch modes, with
  keyboard shortcuts P (pen) and S (select); the app MUST start in
  Select mode (LOCKED 2026-10-04); Pen mode draws live on
  press-and-drag, Select mode selects on click.
- **FR-003**: Strokes within 1.5 seconds of each other (LOCKED
  2026-10-04) with no intervening selection or command MUST group into
  one drawing element.
- **FR-004**: Finished groups MUST commit through the same
  deterministic engine as voice commands as an internal
  drawing operation (never a voice-addressable command), receiving a
  unique never-reused ID, history entry, state update, and autosave.
- **FR-005**: All element kinds MUST share one board state and one
  ordering; voice-created content MUST never erase or alter strokes.
- **FR-006**: Move, resize, recolor, and confirmed delete MUST work on
  drawings by selection or ID; resize MUST scale stroke points
  proportionally, move MUST translate them, and results MUST stay
  inside the canvas. With no usable selection, the system MUST ask the
  teacher to select one and MUST NOT guess — including no recency
  fallback to the most recently drawn element (LOCKED 2026-10-04).
- **FR-007**: Clicking near a drawing's strokes (within tolerance) MUST
  select it and show the outline with handles over its bounding box.
- **FR-008**: Strokes starting outside the board MUST be ignored; points
  outside the canvas MUST clip to its edge.
- **FR-009**: Drawing MUST work offline, during voice processing
  (commits queued, never concurrent), and across resizes without stroke
  loss.
- **FR-010**: Drawings MUST use the current palette color with thin,
  medium, and thick widths (default medium); stroke width is fixed per
  drawing element and chosen in settings — there is deliberately no
  width control in the main bar (LOCKED 2026-10-04).
- **FR-011**: Drawings MUST save with the lesson including all points
  (position plus pressure when captured) and restore exactly on reopen.
- **FR-012**: Out of scope: handwriting recognition, conversion of
  drawings to shapes or text, partial erasing of strokes, palm
  rejection tuning, multi-pen or multi-user input, voice-enabled pen.

### Key Entities

- **Stroke**: One press-and-drag path: ordered points with positions
  plus pressure when captured; live-rendered while in progress.
- **Drawing element**: A committed stroke group with a unique ID,
  color, width, bounding box, and ordering rank; fully commandable.
- **Pen / Select mode**: Visible input mode (P/S shortcuts) deciding
  whether pointer contact draws or selects.
- **Stroke grouping**: The 1.5 s no-interruption rule turning strokes
  into one undoable element.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A teacher draws, groups, moves, resizes, recolors,
  deletes (confirmed), and undoes a drawing with mouse alone in under
  5 minutes without assistance.
- **SC-002**: 100 pen taps across pen/mouse inputs select the intended
  element every time, including near-stroke proximity picks.
- **SC-003**: Stroke points are byte-identical across voice edits,
  save/reopen round trips (50 trials), and offline sessions.
- **SC-004**: Zero lost strokes across 20 trials each of offline
  drawing, draw-during-processing, and resize-mid-stroke.
- **SC-005**: 9 out of 10 first-time teachers draw, select, and undo a
  drawing without guidance.

## Assumptions

- Proximity tolerance defaults to about 12 canvas units around a
  stroke; topmost ordering breaks ties.
- Widths default to thin 2, medium 4 (default), thick 8 canvas units;
  one width per drawing element, chosen before drawing.
- Pressure is recorded when the device reports it and ignored (not
  simulated) when absent.
- "Current color" means the active palette selection at stroke start;
  changing color later affects new strokes and explicit recolor
  commands only.
