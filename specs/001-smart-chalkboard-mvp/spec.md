# Feature Specification: Smart Chalkboard MVP — Voice and Pen Classroom Board

**Feature Branch**: `001-smart-chalkboard-mvp`
**Created**: 2026-10-03
**Status**: Draft
**Input**: User description: "Build Smart Chalkboard, a desktop classroom app where a teacher creates and modifies structured board content using push-to-talk voice commands and manual Smart Pen drawing..."

## Clarifications

### Session 2026-10-03

- Q: How are equations created given there is no create_equation command? → A: Equations are equation-styled text elements created via the create_text path (no 13th command).
- Q: Which shape types must create_shape support in V1? → A: Exactly rectangle, circle, line, arrow, triangle; anything else is rejected.
- Q: What color model must change_color accept? → A: Named palette (8–10 colors) plus #RRGGBB hex; unknown values rejected.
- Q: How must destructive confirmations behave? → A: Modal dialog with large pen-usable Cancel/Confirm; 30-second timeout counts as cancel.
- Q: Must push-to-talk be press-and-hold or click-toggle? → A: Press-and-hold (release submits), 15-second cap; no toggle in V1.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create board content by voice (Priority: P1)

A teacher holds the microphone button, speaks a plain-English instruction,
releases the button, sees what was heard on screen, and watches the board
update after automatic validation. Example: "Create a heading called
Newton's Second Law."

**Why this priority**: This is the core value proposition — hands-free
structured content creation without menu navigation. Without it there is
no product.

**Independent Test**: Can be fully tested by speaking one creation
instruction and verifying a correctly placed heading or text element
appears with a visible highlight, plus a visible transcription of what
was heard.

**Acceptance Scenarios**:

1. **Given** an open lesson with an empty board, **When** the teacher
   holds the microphone button, says "Create a heading called Newton's
   Second Law" and releases, **Then** a heading element with that exact
   text appears on the board and the transcription is shown on screen.
2. **Given** a board with a heading, **When** the teacher says "Add the
   equation F = ma below it", **Then** an equation-styled text element
   with content "F = ma" appears below the heading.
3. **Given** the teacher is recording, **When** the status is observed,
   **Then** it progresses through Listening → Processing → Validating →
   Executing → Idle, and the transcription remains visible after
   recognition.

---

### User Story 2 - Adjust existing content by referring to "this" (Priority: P1)

A teacher refers to the currently selected element naturally ("make this
bigger", "move this down") instead of naming IDs. If nothing is selected
or the request is ambiguous, the system asks for clarification and never
guesses.

**Why this priority**: Natural reference is what makes voice usable while
teaching; guessing wrong would break trust and lesson flow.

**Independent Test**: Can be fully tested by selecting an element, saying
"make this bigger", and verifying only the selected element grows; then
repeating with no selection and verifying a clarification prompt appears
with no board change.

**Acceptance Scenarios**:

1. **Given** the equation "F = ma" is selected, **When** the teacher says
   "Make the equation bigger", **Then** only the selected equation
   increases in size and stays fully inside the board.
2. **Given** no element is selected, **When** the teacher says "Make this
   bigger", **Then** no board change occurs and the system asks the
   teacher to select an object first.
3. **Given** multiple candidate elements and an ambiguous instruction such
   as "delete that", **When** the command is issued, **Then** the system
   asks "Which object would you like me to delete?" and waits for a
   selection instead of acting.

---

### User Story 3 - Draw with the pen alongside voice (Priority: P1)

A teacher draws freehand with the pen at any time. Each finished drawing
becomes a first-class board element with its own unique ID that can later
be selected, moved, resized, recolored, or deleted by voice or pen.

**Why this priority**: Teaching requires sketching; drawings must coexist
with voice-created content in the same board, history, and saved lesson.

**Independent Test**: Can be fully tested by drawing one stroke group with
the pen while offline from voice services and verifying a new uniquely
identified drawing appears, is selectable, and survives save/reopen.

**Acceptance Scenarios**:

1. **Given** an open lesson, **When** the teacher draws with the pen and
   lifts the pen, **Then** a new drawing element with a unique ID appears
   on the board.
2. **Given** a pen drawing exists, **When** the teacher selects it and
   says "move this down" or "delete this" (with confirmation), **Then**
   the drawing moves or is deleted exactly like any other element.

---

### User Story 4 - Confirm destructive actions and undo mistakes (Priority: P1)

Destructive actions always ask for explicit confirmation before applying,
and any applied change can be undone and redone. Cancelling leaves the
board and history untouched.

**Why this priority**: Accidental loss of board content mid-lesson is the
highest-impact failure; confirmation plus undo keeps the teacher in
control.

**Independent Test**: Can be fully tested by issuing a delete, cancelling
it (no change), re-issuing it, confirming it (element removed), pressing
Undo (element restored with its original identity), and pressing Redo
(element removed again).

**Acceptance Scenarios**:

1. **Given** the equation "F = ma" exists, **When** the teacher says
   "Delete the equation" and confirms, **Then** the equation is removed
   and the removal is recorded in history.
2. **Given** a delete confirmation is showing, **When** the teacher
   cancels, **Then** the board and history are unchanged.
3. **Given** the equation was just deleted via confirmation, **When** the
   teacher presses Undo, **Then** the equation returns with its original
   identity and position.

---

### User Story 5 - Keep lessons across sessions (Priority: P1)

A teacher starts new lessons, opens past lessons, renames and deletes
them, saves manually, relies on automatic saving, and exports a lesson
for sharing.

**Why this priority**: Lessons are the teacher's work product; loss
between sessions destroys trust even if the live board works.

**Independent Test**: Can be fully tested by creating a board, saving,
closing, reopening, and verifying identical content; plus rename, delete
(with confirmation), and export producing a shareable file.

**Acceptance Scenarios**:

1. **Given** unsaved changes exist, **When** the teacher starts a new
   lesson, **Then** the system asks for confirmation offering to save
   first.
2. **Given** a saved lesson, **When** the teacher reopens it later,
   **Then** all elements, positions, and identities are restored exactly.
3. **Given** a lesson is open, **When** the teacher exports it, **Then**
   a portable shareable file of the board is produced.

---

### User Story 6 - Keep teaching when voice services fail (Priority: P2)

When speech understanding or connectivity fails, the teacher sees a clear
plain-language error while the board and pen keep working, with a way to
retry the voice command later.

**Why this priority**: Classrooms have unreliable networks; the lesson
must survive service outages even though voice is the headline feature.

**Independent Test**: Can be fully tested by disabling voice services,
verifying a clear error message, drawing and navigating the board with
the pen, then re-enabling and retrying the voice command successfully.

**Acceptance Scenarios**:

1. **Given** voice services are unavailable, **When** the teacher issues a
   voice command, **Then** a message such as "Voice commands are
   unavailable; drawing still works" appears and the existing board
   content is preserved.
2. **Given** an unheard or empty recording, **When** processing finishes,
   **Then** the teacher sees "I couldn't understand the audio. Please try
   again." with no board change.

---

### Edge Cases

- What happens when speech is silent, empty, or unintelligible? → Friendly
  retry message; no command generated; no state or history change.
- What happens when the instruction matches none of the 12 supported
  actions? → Rejected with a plain-language reason; no state change.
- What happens when a move or resize would push an element off the board?
  → Rejected with explanation; element stays where it was (no clamping
  by guessing).
- What happens when the board is already empty and "clear the board" is
  requested? → Inform "The board is already empty"; no history entry.
- What happens when Undo is pressed with nothing to undo (or Redo with
  nothing to redo)? → Inform "Nothing to undo / redo"; no state change.
- What happens when a second command arrives while one is being
  validated/executed? → It waits in order; only one runs at a time; the
  teacher is shown queue depth when more than one is waiting.
- What happens when a confirmation dialog times out or is dismissed? →
  Treated as cancel; no state or history change.
- What happens when saving fails? → Teacher sees "Couldn't save your
  lesson. Your board is still open."; in-memory board preserved; retry
  and export fallback offered.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide push-to-talk voice input (press-and-hold
  microphone control, always visible) and MUST NOT listen continuously;
  there is no wake word.
- **FR-002**: System MUST accept English speech and MUST display the
  recognized transcription on screen after every recording.
- **FR-003**: System MUST show voice status progressing through Listening,
  Processing, Validating, Executing, and Idle states.
- **FR-004**: System MUST support exactly these 12 voice-addressable
  actions and MUST reject anything else with a plain-language reason:
  create_heading, create_text, move_item, resize_item, delete_item,
  clear_board, create_shape, change_color, undo, redo, save_lesson,
  new_lesson.
- **FR-005**: Every command MUST conform to the schema fields `command`,
  `target_id`, `parameters`, `timestamp`; malformed or extra-field
  commands MUST be rejected with no state or history change.
- **FR-006**: Every board element, including each pen drawing, MUST carry
  a unique ID that is never reused after deletion within the lesson.
- **FR-007**: The phrase "this/that" MUST resolve only to the currently
  selected element; if nothing is selected or resolution is ambiguous,
  the system MUST ask for clarification and MUST NOT guess or act.
- **FR-008**: Destructive actions MUST require explicit confirmation
  before executing: delete_item always, clear_board always, and new_lesson
  when unsaved changes exist; cancel/timeout MUST leave state and history
  unchanged.
- **FR-009**: Commands MUST be validated before execution and executed one
  at a time in arrival order; rejected commands MUST leave board state
  and history unchanged.
- **FR-010**: System MUST provide Undo and Redo over recorded history;
  invalid commands are never recorded; undo/redo themselves are not
  recorded as new entries; a new command after undo clears the redo stack.
- **FR-011**: Board MUST be a fixed-size single page; every element's
  bounding box MUST lie wholly inside it; new headings/text default below
  existing content or to the top margin when empty.
- **FR-012**: Pen drawings MUST enter the same board state, history, and
  saved lesson as voice-created elements and MUST support select, move,
  resize, recolor, delete, and undo.
- **FR-013**: Lessons MUST support new, open, rename, delete (with
  confirmation), manual save, automatic periodic save, and export to a
  portable shareable file.
- **FR-014**: On speech-understanding, connectivity, or save failure, the
  system MUST show a clear plain-language error, MUST preserve the open
  board, and MUST keep pen drawing and board navigation working with a
  retry path for the failed action.
- **FR-015**: Raw voice audio MUST be discarded immediately after
  transcription, including on failure.
- **FR-016**: End-to-end voice latency from end of speech to visible board
  update MUST be under 3 seconds under normal conditions.

### Key Entities

- **Board**: Fixed-size single-page canvas holding all elements,
  the current selection, and a version; the authoritative lesson view.
- **Element**: Heading, text (including equation-styled text created via
  create_text — the locked path for equations such as "F = ma", no separate
  command), shape, or pen drawing; has unique ID, type, position, size,
  color, and ordering.
- **Command**: Structured instruction with `command`, `target_id`,
  `parameters`, `timestamp`; the only means of changing the board.
- **Command history**: Ordered log of applied state-changing commands with
  inverses enabling undo/redo; invalid or cancelled commands never appear.
- **Lesson**: Named container of a board plus its history and save
  metadata; supports new/open/rename/delete/save/autosave/export.
- **Transcription**: Visible text of what was heard for one utterance;
  shown for verification, never stored as audio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A teacher completes the acceptance scenario (heading
  "Newton's Second Law" → equation "F = ma" below it → enlarge equation
  → pen drawing → confirmed delete → Undo restores equation) without
  assistance in under 5 minutes.
- **SC-002**: At least 90% of clearly spoken voice attempts result in the
  intended board change without retry.
- **SC-003**: 100% of rejected, cancelled, or ambiguous commands leave
  the board and history exactly unchanged (verified by state comparison).
- **SC-004**: At least 95% of correctly understood instructions pass
  validation on first attempt; fewer than 10% require clarification.
- **SC-005**: Median voice latency from end of speech to visible board
  update is under 3 seconds; 95th percentile under 5 seconds over 100
  measured commands.
- **SC-006**: Zero board-content losses across save/reopen round trips in
  50 consecutive trials and across simulated service outages (board and
  pen remain usable, content preserved).
- **SC-007**: 9 out of 10 first-time teachers can create a heading, draw,
  delete with confirmation, and undo without training or help.

## Assumptions

- Equation content ("F = ma") is represented as an equation-styled text
  element created through the create_text path (LOCKED 2026-10-03); no
  separate 13th command is introduced (keeps the 12-command lock).
- Push-to-talk is press-and-hold with release to submit (LOCKED 2026-10-03,
  no click-toggle in V1); a 15-second per-utterance limit applies; empty/silent captures show a retry prompt.
- "Bigger/smaller" map to fixed size steps (e.g., ×1.25 / ×0.8) bounded
  by minimum size and canvas edges; off-canvas results are rejected, not
  clamped.
- New content defaults to the next free slot below existing content, else
  the top margin; create_shape supports exactly rectangle, circle, line,
  arrow, triangle (LOCKED 2026-10-03, unsupported types rejected with the
  supported list) and a named palette of 8–10 colors plus #RRGGBB hex
  (LOCKED 2026-10-03, unknown values rejected).
- Confirmation is a modal dialog with large pen-usable Cancel/Confirm
  targets (LOCKED 2026-10-03), with a 30-second timeout treated as cancel;
  while awaiting confirmation the command queue blocks.
- Command queue holds at most 5 waiting commands; further input shows
  "Please wait"; a command awaiting confirmation blocks later commands.
- Undo depth is 100 steps; save/confirmation-only actions themselves are
  not undoable state changes; autosave runs every ~30 seconds when dirty
  and after destructive commands without blocking the interface.
- Export produces at minimum a portable board image (PDF as follow-up);
  lesson delete uses the same explicit-confirmation pattern as board
  destructive actions.
