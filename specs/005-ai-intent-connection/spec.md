# Feature Specification: AI Intent Connection

**Feature Branch**: `005-ai-intent-connection`
**Created**: 2026-10-04
**Status**: Draft
**Input**: User description: "Connect the Smart Chalkboard AI intent layer so that a text transcript becomes a validated board change, replacing all hardcoded demo content... (12-command vocabulary, clarification flow, untrusted-output handling, regeneration and failure behavior, contextual references, empty startup board, hidden developer text input; out of scope: microphone recording and speech-to-text, new commands, primary provider integration)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Turn a typed command phrase into a board change (Priority: P1)

A teacher provides a command phrase (currently typed into a hidden
developer testing control until speech capture arrives); the system sends
the phrase plus a board summary to the AI service, receives a strict
structured command, validates it through the existing deterministic
engine, updates the board, and shows the transcript and outcome.

**Why this priority**: This is the whole feature — real AI-driven board
changes with no hardcoded demo content.

**Independent Test**: Can be fully tested by typing "Create a heading
called Newton's Second Law" and verifying a heading appears with the
transcription shown and the result chip reading Done.

**Acceptance Scenarios**:

1. **Given** an empty board, **When** the tester types "Create a heading
   called Newton's Second Law", **Then** a heading with that exact text
   appears, the transcription is shown, and the outcome reads Done.
2. **Given** a board with a heading, **When** the tester types "Add the
   equation F = ma below it", **Then** an equation-styled text element
   with content "F = ma" appears below the heading.
3. **Given** any completed command, **When** the outcome is shown, **Then**
   the transcription strip shows what was sent and the result chip shows
   the matching outcome (Done, Needs confirmation, Needs clarification,
   or Error).

---

### User Story 2 - Refer to the selected element naturally (Priority: P1)

A teacher says "make this bigger" meaning the currently selected
element. With a selection the element changes; with no selection the
system asks the teacher to select one and changes nothing.

**Why this priority**: Contextual reference is the natural teaching
interaction; guessing wrong would break trust.

**Independent Test**: Can be fully tested by selecting the equation,
typing "Make the equation bigger" (only it grows), then clearing the
selection and repeating (clarification prompt, no change).

**Acceptance Scenarios**:

1. **Given** the equation "F = ma" is selected, **When** the tester types
   "Make the equation bigger", **Then** only the selected equation grows
   and stays inside the board.
2. **Given** no element is selected, **When** the tester types "Make this
   bigger", **Then** nothing changes and the system asks the teacher to
   select an object first.

---

### User Story 3 - Ask instead of guessing (Priority: P1)

When a request is ambiguous, the AI returns a clarification response
with a question; the app shows the question to the teacher and changes
nothing on the board.

**Why this priority**: Never-guess behavior is the safety contract that
makes AI control of a classroom board acceptable.

**Independent Test**: Can be fully tested by typing an ambiguous delete
("delete that" with no selection) and verifying a question appears with
zero board or history change.

**Acceptance Scenarios**:

1. **Given** no selection and several elements, **When** the tester types
   "Delete that", **Then** the system asks which object to delete and the
   board and history are unchanged.

---

### User Story 4 - Reject bad output and survive outages (Priority: P1)

Malformed or unsupported AI output is rejected with a clear message and
zero state change (one regeneration attempt first); network or provider
failure shows a clear error, keeps the board and pen working, and offers
retry.

**Why this priority**: AI output is untrusted and networks fail in
classrooms; both must degrade gracefully.

**Independent Test**: Can be fully tested by forcing malformed output,
an unsupported command, and a provider outage, verifying messages,
unchanged state, working pen, and successful retry.

**Acceptance Scenarios**:

1. **Given** the AI returns malformed data twice, **When** processing
   finishes, **Then** the teacher sees "Unable to understand the
   command. Please try again." with no board or history change.
2. **Given** the AI returns an unsupported 13th command, **When**
   validated, **Then** it is rejected with a plain-language reason and
   no state change.
3. **Given** the AI service is unreachable, **When** a command is sent,
   **Then** a clear error appears, the existing board is preserved, pen
   drawing still works, and retry is offered.

---

### User Story 5 - Start clean with no demo content (Priority: P1)

The app starts with an empty board; no static demo text, equations, or
shapes are baked in. All board content comes from validated commands or
pen drawing.

**Why this priority**: Hardcoded demo content would mask whether the
AI-to-board path genuinely works.

**Independent Test**: Can be fully tested by launching fresh and
verifying an empty board with working voice-path controls.

**Acceptance Scenarios**:

1. **Given** a fresh launch, **When** the board loads, **Then** it is
   empty with no demo headings, equations, or shapes.

---

### User Story 6 - Developer-only testing control stays hidden (Priority: P2)

A text input for exercising the AI-to-board path exists but is hidden
by default and enabled only through a restricted developer setting, so
teachers never see it.

**Why this priority**: Typing is the bridge until speech capture lands;
it must not leak into the teaching experience.

**Independent Test**: Can be fully tested by launching normally (no box
visible) and with the developer setting on (box visible and functional).

**Acceptance Scenarios**:

1. **Given** a normal launch, **When** the teacher looks at the UI,
   **Then** no developer text input is visible.
2. **Given** the developer setting enabled, **When** text is typed,
   **Then** it flows through the same AI → validation → board path as
   any transcript.

---

### Edge Cases

- What happens when the AI wraps a valid command in extra chatter? →
  Treated as malformed; one regeneration, then the clear error message.
- What happens when the AI invents a 13th command? → Rejected as
  unsupported with the supported list; no state change.
- What happens when context references a deleted element? → Target
  reported missing; teacher asked to select again; no guessing.
- What happens when the teacher cancels a delete confirmation? → No
  state or history change (existing confirmation behavior).
- What happens when the input box is enabled in a classroom? → It is a
  developer setting, off by default; teachers never see it in normal use.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST send transcript text plus a board context
  summary (element IDs, types, short labels, positions, and the selected
  element) and the list of supported commands to the AI service.
- **FR-002**: The AI MUST return either a strict structured command with
  exactly the fields `command`, `target_id`, `parameters`, `timestamp`,
  or a clarification response with a question — nothing else is accepted.
- **FR-003**: The system MUST accept only these 12 commands and reject
  anything else with a plain-language reason: create_heading,
  create_text, move_item, resize_item, delete_item, clear_board,
  create_shape, change_color, undo, redo, save_lesson, new_lesson.
- **FR-004**: Every AI response MUST pass through the existing
  deterministic validation engine before any board change; the AI MUST
  never modify board state, stored data, or interface controls directly,
  and its output MUST be treated as untrusted input.
- **FR-005**: A clarification response MUST be shown to the teacher as a
  question with zero board or history change.
- **FR-006**: Malformed responses MUST get exactly one regeneration
  attempt; still-unusable output MUST show "Unable to understand the
  command. Please try again." with no state change.
- **FR-007**: Network or provider failure MUST show a clear error, MUST
  preserve the open board and working pen input, and MUST offer retry.
- **FR-008**: Contextual references ("this", "that", "the equation")
  MUST resolve only to the selected element; with no usable selection
  the system MUST ask the teacher to select one and MUST NOT guess.
- **FR-009**: The startup board MUST be empty; all static demo text,
  equations, and shapes MUST be removed.
- **FR-010**: A developer-only text input for the transcript path MUST
  be hidden by default and enabled only through a restricted developer
  setting invisible to teachers.
- **FR-011**: The transcription strip MUST show the sent transcript and
  the result chip MUST show the outcome (Done, Needs confirmation,
  Needs clarification, or Error) for every AI-path attempt.
- **FR-012**: Out of scope: microphone recording and speech-to-text
  capture, new commands, and the designated primary provider
  integration.

### Key Entities

- **Transcript**: The teacher's command phrase as text; the single input
  to the intent layer (typed via the developer control until speech
  capture arrives).
- **Board context summary**: Element IDs, types, short labels, positions,
  and the selected element — the only board information sent with a
  transcript.
- **Structured command**: `command`, `target_id`, `parameters`,
  `timestamp` — the only AI output that can change the board, and only
  via validation.
- **Clarification response**: A question returned for ambiguous requests;
  display-only, never mutating.
- **Outcome display**: Transcript plus result chip shown for every
  attempt, including failures and retries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 10 out of 10 typed command phrases produce the intended
  validated board change with matching transcript and outcome display.
- **SC-002**: 100% of malformed, unsupported, or ambiguous AI responses
  leave the board and history exactly unchanged (verified by state
  comparison).
- **SC-003**: 10 out of 10 provider-outage trials preserve the open
  board, keep pen input working, show a clear error, and succeed on
  retry.
- **SC-004**: Fresh launch shows an empty board with no demo content in
  10 out of 10 trials, and the developer input is invisible in normal
  launches.
- **SC-005**: 9 out of 10 first-time teachers complete type → confirm →
  undo using the connected path without guidance.

## Assumptions

- The developer text control is temporary scaffolding until microphone
  recording and speech-to-text arrive as the next feature; it exercises
  the identical AI → validation → board path.
- The hidden control is governed by a restricted developer setting (not
  a teacher-facing option); normal launches never show it.
- The "already-available AI service" means the currently working
  provider path; the designated primary provider integration is
  explicitly out of scope for this feature.
- Retry re-sends the same transcript through the same path; no duplicate
  board change occurs from a single confirmed command.
