# Smart Chalkboard — Product Requirements Document

| Field | Value |
|---|---|
| Project Name | Smart Chalkboard |
| Project ID | PRD-001 |
| Version | v1.0 |
| Status | Draft |
| Priority | High |
| Created Date | 2026-10-03 |
| Last Updated | 2026-10-03 |
| Owner | Mohamed |
| Team Members | Frontend Dev / Backend Dev / Designer / QA |
| Tech Stack | Python, PyQt6, local Whisper, Gemini (primary), Groq (fallback), SQLite, GitHub |
| Repository | [TBD] |
| Git Branch Prefix | NNN-feature-name |
| PRD File Path | docs/PRD.md |

**Priority legend:** **P0 — Must Have** · **P1 — Should Have** · **P2 — Could Have** · **P3 — Out of Scope**

**Requirement labels used throughout:** `[LOCKED]` = defined in the agreed scope; `[OPEN QUESTION]`; `[TECH DECISION REQUIRED]`; `[RECOMMENDED DEFAULT]`.

---

## 1. Executive Summary

Smart Chalkboard is a desktop classroom application that lets a teacher create and modify structured board content using natural-language voice commands and manual Smart Pen drawing. The defining architectural rule is that **AI never controls the board**. AI only converts a transcribed request into a strict structured command. A deterministic validation and execution engine is the sole component permitted to change board state.

Pipeline `[LOCKED]`:

Teacher Speech → Local Whisper STT → AI Intent Understanding → Strict Structured Command → Deterministic Validation Engine → Command Execution → Board State Update → Board Renderer

The MVP is complete when a teacher can run the full success scenario (Section 8) reliably in a realistic classroom demonstration, with voice-command latency under 3 seconds under normal conditions.

## 2. Product Vision

A teacher speaks naturally while teaching and the board responds predictably, without menu navigation or tool switching. Reliability is valued above feature breadth: every board change is validated, reversible where possible, and never the result of unchecked AI output.

## 3. Problem Statement

Teachers lose teaching time on digital boards because they switch between tools, manually build structured content, navigate menus, redraw or modify elements by hand, and interrupt their explanation to operate the interface. Unrestricted AI control would add unpredictability. Smart Chalkboard combines voice interaction, pen interaction, AI intent understanding, deterministic validation and structured board state so interaction feels natural while execution stays controlled.

**Business value:** saves teacher time during lessons, simplifies board interaction, and reduces AI-caused errors through a deterministic validation layer.

## 4. Target Users

| Type | Description |
|---|---|
| Primary | Classroom teachers: K-12 teachers, university instructors, technical instructors who regularly use a physical or digital board |
| Secondary | Students viewing the board (passive viewers only; no student devices in V1) |

**Pain points:** switching between board tools; manually creating structured content; redrawing content; difficulty manipulating existing elements; unpredictable AI behavior; lack of reliable natural-language interaction.

## 5. User Personas

**Persona 1 — Lina Hassan (Primary)**
- Role: High school physics teacher.
- Goal: Build structured board content while explaining, without stopping to operate menus.
- Pain point: Redrawing and reformatting content breaks lesson flow; AI tools she tried behaved unpredictably.
- Tech level: Medium.
- Frequency: Daily, 4–6 lessons.
- Success definition: Completes a lesson board using voice and pen with fewer than 1 correction per 10 commands.

**Persona 2 — Dr. Karim Adel (Primary)**
- Role: University computer science instructor.
- Goal: Place headings, text, equations and diagrams quickly during lectures.
- Pain point: Switching between slide software, drawing tools and a whiteboard.
- Tech level: High.
- Frequency: 3–4 lectures weekly.
- Success definition: Saves and reopens a lecture board with no data loss.

**Persona 3 — Nadia (Secondary, viewer)**
- Role: Student.
- Goal: Read clearly rendered board content.
- Pain point: Small or cluttered text.
- Tech level: Low to Medium.
- Frequency: Daily.
- Success definition: Reads all board content from the back of the room.

## 6. Jobs To Be Done

1. When I am explaining a concept, I want to add structured content by speaking, so that I do not interrupt my teaching.
2. When I need to adjust something on the board, I want to refer to it naturally ("make this bigger"), so that I avoid hunting through menus.
3. When I make a mistake or the system misunderstands, I want to undo instantly, so that I stay in control.
4. When I draw by hand, I want the drawing to be a first-class board object, so that I can later move, resize or delete it.
5. When class ends, I want my lesson saved and reopenable, so that I can continue next time.

## 7. User Stories

| ID | Priority | Story |
|---|---|---|
| US-01 | P0 | As Lina, I want to hold a microphone button and speak a command so that the board is updated without touching menus. |
| US-02 | P0 | As Lina, I want to see my transcription on screen so that I can verify what the system heard. |
| US-03 | P0 | As Lina, I want to create headings and text by voice so that I can structure content quickly. |
| US-04 | P0 | As Lina, I want to say "make this bigger" and have the selected element resized so that I do not need to name it. |
| US-05 | P0 | As Karim, I want to draw with the Smart Pen so that I can sketch diagrams. |
| US-06 | P0 | As Lina, I want destructive commands to ask for confirmation so that I never lose content accidentally. |
| US-07 | P0 | As Lina, I want Undo and Redo so that I can recover from mistakes. |
| US-08 | P0 | As Lina, I want the system to ask for clarification when my command is ambiguous so that it never guesses wrongly. |
| US-09 | P0 | As Karim, I want lessons saved automatically and manually so that I do not lose work. |
| US-10 | P0 | As Karim, I want the board to keep working with the pen when the internet fails. |
| US-11 | P1 | As Karim, I want to export a lesson so that I can share it. |
| US-12 | P1 | As Lina, I want to rename and delete lessons so that I can manage my library. |

## 8. MVP Goal

> Prove that a teacher can reliably create and modify structured board content using natural voice commands and manual pen interaction, while every AI-generated board change passes through deterministic validation and execution.

**Primary acceptance scenario `[LOCKED]`:**

1. Teacher says "Create a heading called Newton's Second Law." → heading created.
2. Teacher says "Add the equation F = ma below it." → equation created below the heading.
3. Teacher says "Make the equation bigger." → the currently selected equation is resized.
4. Teacher draws an object with the Smart Pen → drawing becomes a board element with a unique ID.
5. Teacher says "Delete the equation." → deleted after validation and required confirmation.
6. Teacher presses Undo → equation restored.

> Note: Step 2 introduces an `equation` element. The locked command list has no `create_equation` command. See Open Question OQ-11.

## 9. Scope

### In Scope (V1)

| Feature | Priority |
|---|---|
| Push-to-talk voice input, local Whisper transcription (English) | P0 |
| AI intent interpretation (Gemini) producing strict JSON | P0 |
| Groq fallback provider | P0 |
| Deterministic validation and execution engine | P0 |
| 12 board commands (Section 17) | P0 |
| Contextual reference to selected element | P0 |
| Clarification and confirmation flows | P0 |
| Manual Smart Pen drawing as board elements | P0 |
| Fixed-size, single-page canvas | P0 |
| Sequential command queue | P0 |
| Undo/Redo via command history | P0 |
| SQLite persistence, autosave, manual save | P0 |
| New, Open lesson | P0 |
| Rename, Delete lesson | P1 |
| Export lesson | P1 (format `[TECH DECISION REQUIRED]`) |
| Metrics instrumentation (local) | P1 |
| Voice status indicator and transcription display | P0 |

### Out of Scope (P3)

Custom hardware, touchscreen hardware, multi-page/slides, infinite canvas, Arabic, continuous listening, wake word, voice-enabled pen, handwriting-to-structure conversion, multi-teacher collaboration, student devices, LMS integrations, AI-generated lessons, offline AI intent understanding, complex educational content generation.

## 10. Non-Goals

- Making the AI an autonomous agent or allowing it to execute code.
- Adding commands beyond the 12 locked commands.
- Replacing presentation software.
- Supporting classroom networks with restricted internet for AI features (AI requires connectivity).

## 11. Hardware Environment

| Item | Detail |
|---|---|
| Computer | HP EliteBook: runs the app, local Whisper, board logic, validation, AI API calls, local lesson data |
| Display | Dell standard monitor, **not touchscreen** `[LOCKED]` |
| Input | Smart Pen (USB or Bluetooth). Protocol is an implementation decision. Preferred: standard HID/stylus/mouse-like input `[RECOMMENDED DEFAULT]` |
| Microphone | Laptop or external microphone `[TECH DECISION REQUIRED]` |
| Network | Internet connection for Gemini/Groq |

Because the display is not touch-capable, all on-screen interaction (selection, buttons, confirmation dialogs) must be operable with the pen acting as a pointer, plus mouse/keyboard.

## 12. Technology Stack

| Layer | Choice | Responsibility |
|---|---|---|
| Application | Python | Logic, board state, commands, validation, integrations |
| UI | PyQt6 | Fullscreen UI, renderer, controls, voice status, transcription, drawing interface |
| STT | Whisper (local) | Offline transcription; model per hardware `[OPEN QUESTION]` |
| AI primary | Gemini | Intent understanding, parameter extraction, structured commands |
| AI fallback | Groq | Used when Gemini fails or is unavailable |
| Database | SQLite | Lessons, board state (JSON), command history, metadata |
| VCS | GitHub | Version control, branching, issues, code review |

**Architecture decision AD-01:** Core business logic (board model, commands, validation, history, persistence) is independent of PyQt6. The engine must not import or reference UI widgets.

## 13. System Architecture

```text
PyQt6 UI (Board / Controls / Status)
        │
Application Layer (Session / Input / Queue)
   │                         │
Voice Layer (Whisper)    Pen Input Device
   │                         │
AI Intent Layer (Gemini / Groq)       │
   │                         │
Deterministic Command Validation & Execution
        │
Board State + Command History
   │                         │
Board Renderer          SQLite Persistence
```

| Layer | Responsibilities | Boundaries |
|---|---|---|
| UI (PyQt6) | Display board, controls, status, transcription, confirmation/clarification dialogs | Emits user intents; never mutates board state directly |
| Application | Session lifecycle, input routing, command queue, orchestration | Calls layers in order; owns no business rules |
| Voice | Record push-to-talk audio, run Whisper, delete audio | Outputs text only |
| Pen Input | Capture stylus events, produce stroke data | Submits drawing as an internal command, same validation path |
| AI Intent | Convert text + context to a structured command via provider abstraction | Returns data only; no side effects |
| Validation & Execution | Schema, parameter, target, state, safety checks; execute; record history | **Only** component allowed to mutate board state |
| Board State + History | In-memory authoritative model and command log | Mutated only via the engine |
| Renderer | Draw state to canvas | Read-only consumer of board state |
| Persistence | SQLite read/write, autosave | Invoked by engine/application, never by AI |

**Pen drawing path:** Pen strokes are not AI-generated. They are converted by the application layer into an internal `add_drawing` operation that passes through the same deterministic engine and history so drawings are undoable and have unique IDs. This internal operation is not an AI-addressable command. `[TECH DECISION REQUIRED]` confirm that an internal-only operation is acceptable given "no additional command types."

## 14. User Flows

**Flow A — Voice command (primary)**
1. Teacher opens a lesson; board loads; microphone control is idle.
2. Teacher presses and holds the microphone button; status shows *Listening*.
3. Teacher speaks; teacher releases.
4. Status shows *Processing*; Whisper transcribes locally; transcription appears on screen; audio file is deleted.
5. Transcription and board context are sent to the AI provider; a structured command is returned.
6. Status shows *Validating*; engine validates schema, command, parameters, target, state.
7. If clarification or confirmation is needed, a prompt is shown and the command waits.
8. Status shows *Executing*; engine mutates state and records history; renderer updates.
9. Status returns to idle; the new element is visibly highlighted.

**Flow B — Manual drawing**
1. Teacher selects the pen tool (or pen is active by default).
2. Teacher draws; live stroke preview is rendered.
3. On pen-up, the stroke group is committed through the engine as a `drawing` element with a unique ID.
4. The drawing becomes selectable and can be referenced by later voice commands.

**Flow C — Destructive command**
1. Teacher says "Clear the board."
2. Engine validates and flags confirmation required.
3. Dialog: "Clear the entire board? [Cancel] [Confirm]".
4. Confirm → executed and recorded; Cancel → no state change, no history entry.

**Flow D — Ambiguity**
1. Teacher says "Delete that" with no selection and multiple candidates.
2. System shows: "Which object would you like me to delete?" and enables pen/mouse selection.
3. Once an element is selected, the teacher re-issues or confirms the command.

**Flow E — AI unavailable**
1. AI call fails on both providers.
2. Error shown; board and pen continue to work; Retry button available.

## 15. Voice Interaction

| ID | Requirement | Priority |
|---|---|---|
| VOI-01 | Push-to-talk only; a prominent microphone control the teacher presses to record `[LOCKED]` | P0 |
| VOI-02 | No continuous listening; no wake word `[LOCKED]` | P3 |
| VOI-03 | English only `[LOCKED]` | P0 |
| VOI-04 | Whisper runs locally; no audio uploaded for transcription `[LOCKED]` | P0 |
| VOI-05 | Raw audio deleted immediately after transcription, including on failure `[LOCKED]` | P0 |
| VOI-06 | Transcription displayed on screen after recognition | P0 |
| VOI-07 | Status sequence displayed: Listening → Processing → Validating → Executing | P0 |
| VOI-08 | Recording time limit of 15 seconds per utterance `[RECOMMENDED DEFAULT]` | P1 |
| VOI-09 | Empty or silent recording shows "I couldn't understand the audio. Please try again." | P0 |
| VOI-10 | Whisper model choice must meet latency budget on the HP EliteBook `[OPEN QUESTION]` | P0 |

**Push-to-talk mechanics:** "press and hold, release to stop" is the assumed interaction; toggle mode (click to start, click to stop) is `[OPEN QUESTION]` since the pen acts as a pointer and holding is harder than clicking.

## 16. Pen Interaction

| ID | Requirement | Priority |
|---|---|---|
| PEN-01 | Teacher can draw freehand on the board with the Smart Pen | P0 |
| PEN-02 | Each completed drawing is a board element with a unique ID (e.g., `drawing_001`) `[LOCKED]` | P0 |
| PEN-03 | Drawings share the same board state, history and persistence as voice-created elements | P0 |
| PEN-04 | Drawings are selectable, movable, resizable, deletable, recolorable via the same commands | P0 |
| PEN-05 | Stroke data stored as point sequences with pressure when available | P1 |
| PEN-06 | Pen device detection and a clear "pen not detected" message | P1 |
| PEN-07 | Drawing works with no network | P0 |
| PEN-08 | Pen protocol (HID/stylus vs vendor SDK) | `[OPEN QUESTION]` OQ-01 |

**Stroke grouping rule `[RECOMMENDED DEFAULT]`:** strokes made within 1.5 seconds of one another, with no intervening selection or command, are grouped into a single drawing element. `[TECH DECISION REQUIRED]`

## 17. Board Command Language

The following 12 commands are locked. No additional AI-addressable commands are permitted in V1.

`create_heading`, `create_text`, `move_item`, `resize_item`, `delete_item`, `clear_board`, `create_shape`, `change_color`, `undo`, `redo`, `save_lesson`, `new_lesson`

### Command Specifications

| Command | Purpose | Required params | Optional params | Target | Confirm | Undoable |
|---|---|---|---|---|---|---|
| `create_heading` | Create heading element | `text` (1–200 chars) | `position` | null | No | Yes |
| `create_text` | Create text element | `text` (1–2000 chars) | `position`, `size` | null | No | Yes |
| `move_item` | Move element | `position` (x,y) or `relative` (direction + distance) | none | existing id or selected | No | Yes |
| `resize_item` | Change element size | `scale_factor` (0.25–4.0) or `size` (w,h) | none | existing id or selected | No | Yes |
| `delete_item` | Delete element | none | none | existing id or selected | **Yes** | Yes |
| `clear_board` | Remove all elements | none | none | null | **Yes** | Yes |
| `create_shape` | Create basic shape | `shape_type` (enum) | `position`, `size`, `color` | null | No | Yes |
| `change_color` | Change element color | `color` | none | existing id or selected | No | Yes |
| `undo` | Revert previous valid command | none | none | null | No | Not recorded in history stack; moves pointer |
| `redo` | Reapply an undone command | none | none | null | No | Not recorded in history stack; moves pointer |
| `save_lesson` | Persist current lesson | none | none | null | No | No (persistence action) |
| `new_lesson` | Start a new lesson | none | `title` | null | **Yes if unsaved changes exist** `[RECOMMENDED DEFAULT]` | No (current lesson saved first) |

### Per-command details

**create_heading**
- Validation: `text` non-empty string, trimmed, ≤ 200 chars; resulting element must fit within canvas bounds; placement defaults to the next free slot under the lowest existing element, else top margin `[RECOMMENDED DEFAULT]`.
- Example: `{"command":"create_heading","target_id":null,"parameters":{"text":"Newton's Second Law"},"timestamp":"2026-10-03T18:15:00Z"}`
- Failure cases: empty text; text too long; no room on canvas → rejected with message "There is no room on the board for this heading."

**create_text**
- Validation: as above; text ≤ 2000 chars; overflow handled by auto-fitting within a bounded box or rejecting `[TECH DECISION REQUIRED]`.
- Example parameters: `{"text":"Force equals mass times acceleration"}`
- Failure cases: empty text; canvas full.

**move_item**
- Validation: target exists (explicit or resolved from `selected_element_id`); new bounding box fully inside the canvas; relative moves use a defined direction enum (`up`,`down`,`left`,`right`) and a distance in canvas units or a named step (`small`,`medium`,`large`) `[RECOMMENDED DEFAULT]`.
- Example: `{"command":"move_item","target_id":"equation_001","parameters":{"relative":{"direction":"down","distance":"medium"}}}`
- Failure cases: no target; target missing; move would leave canvas (rejected, not clamped, unless clamping is chosen `[TECH DECISION REQUIRED]`).

**resize_item**
- Validation: target exists; `scale_factor` between 0.25 and 4.0; result within min size (24×24 units) and canvas bounds. "Bigger" and "smaller" map to a fixed factor (1.25 and 0.8) `[RECOMMENDED DEFAULT]`.
- Example: `{"command":"resize_item","target_id":null,"parameters":{"scale_factor":1.25}}` with `selected_element_id = equation_001`.
- Failure cases: no selection and no target; result off-canvas.

**delete_item**
- Validation: target exists; confirmation required before execution.
- Example: `{"command":"delete_item","target_id":"equation_001","parameters":{}}`
- Failure cases: missing target; teacher cancels.

**clear_board**
- Validation: board has at least one element (otherwise "The board is already empty." with no history entry); confirmation required.

**create_shape**
- Validation: `shape_type` must be in the supported enum. Recommended: `rectangle`, `circle`, `line`, `arrow`, `triangle`. `[OPEN QUESTION]` OQ-06.
- Failure cases: unsupported shape → rejected with a list of supported shapes.

**change_color**
- Validation: `color` must be in the supported palette (named colors) or valid hex. `[OPEN QUESTION]` OQ-07. Recommended: named palette of 8–10 colors plus hex.
- Failure cases: unknown color; target missing.

**undo / redo**
- Validation: undo requires at least one undoable entry; redo requires a non-empty redo stack. Otherwise "Nothing to undo." / "Nothing to redo."

**save_lesson**
- Validation: active lesson exists; success or failure reported to the teacher.

**new_lesson**
- Validation: if unsaved changes exist, require confirmation offering save first. `[OPEN QUESTION]` exact UX (OQ-08).

## 18. Command Schema

```json
{
  "command": "command_name",
  "target_id": "element_id_or_null",
  "parameters": {},
  "timestamp": "ISO-8601 timestamp"
}
```

| Field | Rules |
|---|---|
| `command` | Must exactly match one of the 12 supported commands (case-sensitive) |
| `target_id` | String referencing an existing element when the command requires a target; `null` when it does not. If a command needs a target and `target_id` is null, the engine resolves it from `selected_element_id` only if the AI marked the reference as contextual (e.g., via a `use_selection: true` flag) `[TECH DECISION REQUIRED]`, otherwise requests clarification |
| `parameters` | Object containing only parameters allowed for that command; unknown keys cause rejection |
| `timestamp` | UTC ISO-8601 with `Z` suffix (e.g., `2026-10-03T18:15:00Z`) |

**Schema validation rules:** all four fields required; no extra top-level fields; JSON must parse; types strictly checked; the engine uses its own clock for the authoritative timestamp in history and treats the AI-supplied timestamp as informational `[RECOMMENDED DEFAULT]`.

**Clarification signal:** the AI may return a non-command response of the form `{"clarification_needed": true, "question": "..."}`. `[TECH DECISION REQUIRED]` This is a response envelope, not a board command, and never mutates state.

## 19. Board State Model

```json
{
  "lesson_id": "lesson_001",
  "canvas": { "width": 1920, "height": 1080, "unit": "px" },
  "elements": [
    { "id": "heading_001", "type": "heading", "text": "Newton's Second Law",
      "x": 160, "y": 80, "width": 800, "height": 96, "color": "#FFFFFF", "z": 1 },
    { "id": "equation_001", "type": "equation", "content": "F = ma",
      "x": 160, "y": 200, "width": 320, "height": 80, "color": "#FFFFFF", "z": 2 },
    { "id": "drawing_001", "type": "drawing", "strokes": [], "color": "#FFFFFF", "z": 3 }
  ],
  "selected_element_id": "equation_001",
  "version": 1
}
```

| Rule | Detail |
|---|---|
| Element IDs | `<type>_<NNN>`, unique per lesson, never reused after deletion `[RECOMMENDED DEFAULT]` |
| Element types | `heading`, `text`, `equation`, `shape`, `drawing` |
| Coordinate system | Fixed canvas, origin top-left, units in canvas units; default 1920×1080 `[OPEN QUESTION]` OQ-05 |
| Bounds | Every element's bounding box must lie wholly within the canvas |
| Selection | `selected_element_id` is null or references an existing element; deleting the selected element clears selection |
| Z-order | Integer `z`; new elements go on top |
| Determinism | Same valid command on same state produces identical state, including identical new element IDs and positions |

Exact schema is refined during technical design `[TECH DECISION REQUIRED]`.

## 20. Deterministic Validation Engine

**Pipeline (all steps mandatory, in order):**
1. Receive structured command.
2. Validate JSON/schema.
3. Verify command is supported.
4. Validate parameters (types, ranges, enums).
5. Validate `target_id` (exists, or resolvable from selection).
6. Validate board state (capacity, bounds, history preconditions).
7. Validate allowed operations.
8. Check for destructive operation → require confirmation.
9. Resolve execution rules (default positions, size mappings).
10. Reject invalid commands with a typed error.
11. Execute valid commands.
12. Update board state.
13. Record command history.
14. Trigger render update.

| ID | Requirement | Priority |
|---|---|---|
| VAL-01 | The engine is the only code path allowed to mutate board state | P0 |
| VAL-02 | A rejected command leaves board state and history unchanged | P0 |
| VAL-03 | Execution is atomic: a command fully applies or does not apply | P0 |
| VAL-04 | Engine contains no randomness, no wall-clock dependency, no network access in state transitions | P0 |
| VAL-05 | Every rejection returns a typed error code and teacher-friendly message | P0 |
| VAL-06 | Engine verified by unit tests with ≥ 95% line coverage `[RECOMMENDED DEFAULT]` | P0 |

**Error codes `[RECOMMENDED DEFAULT]`:** `E_SCHEMA`, `E_UNSUPPORTED_COMMAND`, `E_PARAM_INVALID`, `E_TARGET_MISSING`, `E_TARGET_NOT_FOUND`, `E_OUT_OF_BOUNDS`, `E_NOTHING_TO_UNDO`, `E_NOTHING_TO_REDO`, `E_CONFIRMATION_REQUIRED`, `E_AMBIGUOUS`.

**Confirmation UX `[OPEN QUESTION]` OQ-08; recommended default:** modal dialog with large [Cancel] and [Confirm] buttons, usable by pen pointer, with a 30-second timeout that cancels. Voice confirmation ("confirm"/"cancel") is a P2 extension and would pass through the same pipeline.

## 21. AI Responsibility Boundary

| AI may | AI may NOT |
|---|---|
| Interpret natural language | Directly modify the board |
| Identify the intended command | Modify SQLite |
| Extract parameters | Call PyQt UI methods |
| Resolve contextual references when possible | Execute Python code |
| Identify the target element | Create arbitrary commands |
| Produce structured JSON | Bypass validation |
| Flag ambiguity | Decide an invalid command is acceptable |
| | Perform destructive actions directly |

**Context sent to AI `[RECOMMENDED DEFAULT]`:** the transcription, the list of element IDs with type, short label and position summary, `selected_element_id`, and the list of supported commands with schemas. No raw audio, no API credentials, and no lesson content beyond the board summary.

**Prompt-injection stance:** content on the board (e.g., text a teacher wrote) is data, not instructions. Even if the AI is manipulated, it can only emit one of 12 validated commands.

## 22. AI Provider Architecture

```text
AIProvider (interface)
 ├── GeminiProvider   (primary)
 └── GroqProvider     (fallback)
```

| ID | Requirement | Priority |
|---|---|---|
| AI-01 | `AIProvider` interface exposes `interpret(transcript, context) -> RawResponse` | P0 |
| AI-02 | Providers are swappable by configuration without changes to the engine | P0 |
| AI-03 | Fallback to Groq on timeout (> 4 s `[RECOMMENDED DEFAULT]`), network error, HTTP 5xx, rate-limit | P0 |
| AI-04 | Malformed JSON: up to 1 regeneration on the same provider, then fallback provider, then show error | P0 |
| AI-05 | Regeneration never bypasses validation | P0 |
| AI-06 | Use provider structured-output/JSON mode where available | P1 |
| AI-07 | Provider failures are logged with provider name and error type, never with credentials | P0 |

**Latency budget implication:** a 4-second timeout alone would exceed the 3-second target, so fallback path latency is expected to exceed target; the 3-second target applies to the normal primary-provider path. Recommended AI call timeout is 2.0 seconds for the first attempt `[TECH DECISION REQUIRED]`.

Exact Gemini/Groq models and API configuration: `[OPEN QUESTION]` OQ-09.

## 23. Board Renderer

| ID | Requirement | Priority |
|---|---|---|
| REN-01 | Renders all element types: heading, text, equation, shape, drawing | P0 |
| REN-02 | Read-only consumer of board state; re-renders on state-change events | P0 |
| REN-03 | Fullscreen, scales fixed canvas to display preserving aspect ratio | P0 |
| REN-04 | Selected element shows a visible selection outline and handles | P0 |
| REN-05 | Render update within 100 ms of a state change `[RECOMMENDED DEFAULT]` | P0 |
| REN-06 | Live pen-stroke rendering with latency under 50 ms | P1 |
| REN-07 | Renderer failure must not corrupt board state; fall back to last good state and show recovery message | P0 |
| REN-08 | Equation rendering method (plain text vs LaTeX-style) | `[TECH DECISION REQUIRED]` |

## 24. Lesson Management

| Capability | Priority | Notes |
|---|---|---|
| New Lesson | P0 | Via UI and `new_lesson` command; confirmation if unsaved changes |
| Open Lesson | P0 | Lesson list from SQLite; loads latest saved board state |
| Save Lesson (manual) | P0 | UI button and `save_lesson` command |
| Auto-save | P0 | Every 30 seconds when state changed, and after each destructive command `[RECOMMENDED DEFAULT]` |
| Rename Lesson | P1 | UI only |
| Delete Lesson | P1 | UI only; confirmation required |
| Export Lesson | P1 | Format `[TECH DECISION REQUIRED]` |

**Export recommendation:** PNG image of the board as the minimal MVP format, with PDF as the recommended second format. Not finalized. See OQ-03.

## 25. Database Model

Proposed schema `[OPEN QUESTION]` OQ-04, subject to technical design.

```sql
CREATE TABLE schema_migrations (
  version     INTEGER PRIMARY KEY,
  applied_at  TEXT NOT NULL
);

CREATE TABLE lessons (
  id          TEXT PRIMARY KEY,
  title       TEXT NOT NULL,
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL,
  last_saved_at TEXT,
  deleted_at  TEXT
);

CREATE TABLE board_states (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  lesson_id   TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  state_json  TEXT NOT NULL,
  save_type   TEXT NOT NULL CHECK (save_type IN ('auto','manual')),
  saved_at    TEXT NOT NULL
);

CREATE TABLE command_history (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  lesson_id   TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  seq         INTEGER NOT NULL,
  command_json TEXT NOT NULL,
  inverse_json TEXT,
  source      TEXT NOT NULL CHECK (source IN ('voice','pen','ui')),
  status      TEXT NOT NULL CHECK (status IN ('applied','undone')),
  executed_at TEXT NOT NULL,
  UNIQUE (lesson_id, seq)
);

CREATE TABLE metrics_events (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  lesson_id   TEXT,
  event_type  TEXT NOT NULL,
  value_ms    INTEGER,
  detail_json TEXT,
  created_at  TEXT NOT NULL
);
```

| Rule | Detail |
|---|---|
| Timestamps | UTC ISO-8601 text |
| Migrations | `schema_migrations` table supports future migration |
| Retention | Keep the latest 20 autosave snapshots per lesson `[RECOMMENDED DEFAULT]` |
| Soft delete | Lessons soft-deleted for 7 days before purge `[RECOMMENDED DEFAULT]` |
| Writes | Wrapped in transactions; WAL mode enabled |
| Voice data | No audio or transcript content stored unless needed for metrics `[OPEN QUESTION]` whether transcripts are stored |

## 26. UX/UI Requirements

| ID | Requirement | Priority |
|---|---|---|
| UX-01 | Fullscreen layout dominated by the board | P0 |
| UX-02 | Prominent microphone button, at least 96×96 px, always visible | P0 |
| UX-03 | Status indicator showing Listening / Processing / Validating / Executing / Idle | P0 |
| UX-04 | Transcription strip showing the latest transcript and result | P0 |
| UX-05 | Large, always-visible Undo and Redo buttons | P0 |
| UX-06 | Pen/select tool toggle | P0 |
| UX-07 | Minimum text size on the board readable from the back of a classroom (default heading ≥ 64 px, text ≥ 36 px on 1920×1080) `[RECOMMENDED DEFAULT]` | P0 |
| UX-08 | Controls usable with pen pointer (target sizes ≥ 48 px) since the display is not touch | P0 |
| UX-09 | No settings menus during teaching; configuration is in a separate screen | P0 |
| UX-10 | Each action shows loading state, error state and success feedback consistently | P0 |
| UX-11 | Lesson controls (new, open, save, rename, delete, export) in a collapsible panel | P1 |

**Consistent UX rules:** validation errors shown inline in the status area with plain language; loading indicators appear within 200 ms of an action; success is signaled by a brief highlight of the affected element; errors persist until dismissed or superseded.

## 27. Error Handling

| Failure | Teacher-facing message | System behavior |
|---|---|---|
| Whisper failure / empty audio | "I couldn't understand the audio. Please try again." | Delete audio; no AI call; return to idle |
| AI failure (all providers) | "Unable to understand the command. Please try again." | Show Retry; board and pen stay functional |
| Invalid command | "That command can't be applied." with reason | Reject; no state/history change |
| Ambiguous command | "Which object would you like me to [action]?" | Await selection; no state change |
| Missing target | "Select an object first, then try again." | Reject; no state change |
| Network failure | "No internet connection. Voice commands are unavailable; drawing still works." | Skip AI; retry on demand |
| Rendering failure | "Display problem. Recovering the board." | Rebuild view from last valid state; log |
| Database failure | "Couldn't save your lesson. Your board is still open." | Keep in-memory state; retry; offer export; never silent |
| Confirmation timeout | "Cancelled." | No state change |

## 28. Security & Privacy

| ID | Requirement | Priority |
|---|---|---|
| SEC-01 | API keys never in source control; loaded from environment variables or OS credential store | P0 |
| SEC-02 | Keys never written to logs, error messages or exports | P0 |
| SEC-03 | Raw audio deleted after transcription (also on error, crash recovery clears temp audio at startup) | P0 |
| SEC-04 | All AI traffic over TLS 1.2+ | P0 |
| SEC-05 | Only transcript text and a minimal board context summary sent to AI providers | P0 |
| SEC-06 | AI output treated as untrusted input; strict validation; no `eval`/`exec` | P0 |
| SEC-07 | Local SQLite file stored in the user's profile directory with OS-level file permissions; encryption at rest `[OPEN QUESTION]` | P1 |
| SEC-08 | No collection of personal data beyond lesson content; no student data | P0 |
| SEC-09 | Privacy disclosure that transcripts are sent to Gemini/Groq | P1 |

## 29. Performance Requirements

**Voice-command latency target `[LOCKED]`:** under 3 seconds from the teacher finishing speaking to the command executed on the board, under normal network and hardware conditions.

| Stage | Budget (p50 target) |
|---|---|
| Whisper inference | ≤ 1.0 s `[RECOMMENDED DEFAULT]` |
| Network + AI response | ≤ 1.5 s |
| JSON parse + validation | ≤ 50 ms |
| Execution + state update | ≤ 50 ms |
| Render | ≤ 100 ms |
| Overhead / queueing | ≤ 300 ms |

| ID | Requirement |
|---|---|
| PERF-01 | p50 end-to-end latency < 3.0 s; p95 < 5.0 s for the standard command set |
| PERF-02 | Validation + execution < 100 ms per command (excluding render) |
| PERF-03 | Application cold start < 10 s including Whisper model load `[RECOMMENDED DEFAULT]` |
| PERF-04 | UI remains responsive (no frame stall > 100 ms) during Whisper and AI calls; heavy work off the UI thread |
| PERF-05 | Canvas supports at least 200 elements without perceptible lag |
| PERF-06 | Autosave does not block the UI |

Latency sources: Whisper inference, network, AI response, JSON parsing, validation, rendering. Mitigations: preload Whisper at startup, pick a small English model, keep prompts short, reuse HTTP connections.

## 30. Command Queue

| ID | Requirement | Priority |
|---|---|---|
| Q-01 | New commands arriving during processing are placed in a FIFO queue `[LOCKED]` | P0 |
| Q-02 | Only one command is validated and executed at a time | P0 |
| Q-03 | Context snapshot is taken at dequeue time, not at utterance time, so each command sees the latest state | P0 |
| Q-04 | Queue depth shown to the teacher when > 1 | P1 |
| Q-05 | Maximum queue length 5; further commands rejected with "Please wait" `[RECOMMENDED DEFAULT]` | P1 |
| Q-06 | A command awaiting confirmation or clarification blocks the queue; queued commands wait | P0 |
| Q-07 | Pen drawing commits are also serialized through the same engine | P0 |
| Q-08 | A failed command does not clear the queue | P0 |

## 31. Undo/Redo

| Rule | Behavior |
|---|---|
| Recording | Every valid state-changing command is recorded with its inverse |
| Invalid commands | Never recorded |
| Undo | Reverses the most recent applied command; marks it `undone` |
| Redo | Reapplies the most recently undone command |
| New command after undo | Clears the redo stack |
| Multiple undos | Supported, back to the start of the lesson session |
| Failed command | No history change |
| Destructive command | Recorded after confirmation; undo restores deleted/cleared elements with original IDs |
| `undo`/`redo` themselves | Not added to the history stack |
| Non-undoable | `save_lesson`, `new_lesson` |
| Persistence across reopen | History persisted; undo availability after reopening `[OPEN QUESTION]` |
| Depth | 100 steps `[RECOMMENDED DEFAULT]` |

## 32. Testing Strategy

**Unit tests (P0)**
- Command schema validation; each parameter validator; target validation; board state transitions; undo/redo; SQLite operations (CRUD, migration, transactions); ID generation determinism; coordinate/bounds logic.

**Integration tests (P0)**
- Whisper → AI (recorded fixture audio); AI → Validator (recorded AI responses); Validator → Board; Board → SQLite; Pen input → Engine.

**Failure tests (P0)**
- Malformed JSON; missing target; invalid target; unsupported command; network failure; AI timeout; Gemini→Groq fallback; database failure; renderer failure; ambiguous command; destructive confirmation (confirm and cancel); queue overflow; extra fields in parameters.

**Determinism tests (P0):** run the same command sequence 100 times on the same initial state and assert identical resulting state.

**End-to-end test (P0):** execute the exact success scenario from Section 8 with scripted audio fixtures, and again live with a human speaker.

**Performance tests (P0):** measure stage-by-stage latency over at least 100 commands on the HP EliteBook.

**Classroom simulation (P1):** noisy environment, accents, 30-minute session.

## 33. Analytics & Metrics

Metrics are collected locally (no third-party analytics) `[RECOMMENDED DEFAULT]`.

| Metric | Target | Measurement |
|---|---|---|
| Voice command success rate | ≥ 90% | Commands executed without retry ÷ voice commands attempted |
| Deterministic validation success rate | ≥ 95% of AI outputs | Valid outputs ÷ AI outputs received |
| Invalid command rejection rate | Tracked; investigate if > 5% | Rejections ÷ AI outputs |
| Average command latency | < 3.0 s p50 | Timestamp from speech end to render |
| Clarification rate | < 10% | Clarifications ÷ commands |
| AI regeneration rate | < 5% | Regenerations ÷ AI calls |
| Teacher correction rate | < 10% | Undo or repeat within 10 s ÷ commands |
| Undo rate | Tracked | Undos ÷ commands |
| Manual vs voice interaction | Tracked | Pen commits vs voice commands |
| Lesson save success rate | ≥ 99.9% | Successful saves ÷ save attempts |
| Application crash rate | < 1 per 100 session hours | Crash logs |
| Fallback activation rate | Tracked | Groq uses ÷ AI calls |

## 34. Acceptance Criteria

The MVP is complete only when all of the following are verified:

- [ ] 1. Teacher can activate push-to-talk.
- [ ] 2. Whisper transcribes speech locally.
- [ ] 3. Transcription is visible.
- [ ] 4. Gemini interprets supported natural-language commands.
- [ ] 5. AI returns strict structured commands.
- [ ] 6. Invalid AI output is rejected.
- [ ] 7. Deterministic validation occurs before execution.
- [ ] 8. AI cannot directly modify board state.
- [ ] 9. Teacher can create headings.
- [ ] 10. Teacher can create text.
- [ ] 11. Teacher can create shapes.
- [ ] 12. Teacher can move items.
- [ ] 13. Teacher can resize items.
- [ ] 14. Teacher can change colors.
- [ ] 15. Teacher can delete items.
- [ ] 16. Teacher can clear the board with confirmation.
- [ ] 17. Teacher can undo and redo.
- [ ] 18. Teacher can manually draw with the Smart Pen.
- [ ] 19. Manual drawings receive unique IDs.
- [ ] 20. Board state is stored in SQLite.
- [ ] 21. Lessons can be saved and reopened.
- [ ] 22. Auto-save works.
- [ ] 23. Manual save works.
- [ ] 24. Export works according to the selected format.
- [ ] 25. Gemini fallback to Groq works.
- [ ] 26. AI/network failures do not crash the application.
- [ ] 27. Commands are processed sequentially.
- [ ] 28. Ambiguous commands trigger clarification.
- [ ] 29. Destructive commands require confirmation.
- [ ] 30. Average latency is below 3 seconds under normal conditions.
- [ ] 31. The complete MVP success scenario works reliably.

## 35. Risks & Mitigations

Score = Likelihood × Impact (High = 3, Medium = 2, Low = 1).

| ID | Risk | Likelihood | Impact | Score | Mitigation | Fallback | Owner |
|---|---|---|---|---|---|---|---|
| R-01 | Whisper latency exceeds budget on HP EliteBook | Medium | High | 6 | Benchmark models early; use smaller English model; preload at startup | Reduce model size; accept longer latency for P1 | Backend Dev |
| R-02 | AI response latency | Medium | High | 6 | Short prompts; connection reuse; strict timeouts | Fall back to Groq | Backend Dev |
| R-03 | Internet dependency | Medium | High | 6 | Keep board/pen functional offline; clear errors | Retry button; manual controls | Backend Dev |
| R-04 | Smart Pen incompatibility | Medium | High | 6 | Verify pen as HID early (Phase 3 spike) | Use mouse/stylus input | Frontend Dev |
| R-05 | PyQt rendering performance | Low | Medium | 2 | Cache rendering; limit element count | Simplify rendering of strokes | Frontend Dev |
| R-06 | AI hallucination | Medium | High | 6 | Closed command set; strict validation | Reject and request clarification | Backend Dev |
| R-07 | Malformed JSON | Medium | Medium | 4 | JSON mode; regeneration; fallback provider | Show error | Backend Dev |
| R-08 | Board state synchronization | Low | High | 3 | Single-writer engine; queue | Reload last saved state | Backend Dev |
| R-09 | Command history complexity | Medium | Medium | 4 | Inverse operations tested per command | Snapshot-based undo | Backend Dev |
| R-10 | Teachers prefer manual interaction | Medium | Medium | 4 | Pilot with teachers; measure voice vs pen use | Pen-first positioning | Owner |
| R-11 | Voice commands feel unnatural | Medium | Medium | 4 | Test varied phrasing; display transcript | Improve prompts | Owner |
| R-12 | Command set increases complexity | Low | Medium | 2 | Hold the 12-command limit | Defer features | Owner |
| R-13 | Classroom noise degrades recognition | High | Medium | 6 | Recommend directional/headset mic; show transcript | Re-record prompt | QA |
| R-14 | Incorrect target resolution | Medium | High | 6 | Clarify instead of guess; selection highlight | Undo | Backend Dev |
| R-15 | Accidental destructive commands | Medium | High | 6 | Confirmation + Undo | Restore from autosave | Backend Dev |
| R-16 | State corruption | Low | High | 3 | Atomic execution; transactions; snapshots | Restore from last snapshot | Backend Dev |
| R-17 | AI provider outage | Medium | High | 6 | Dual providers | Manual-only mode | Backend Dev |

## 36. Open Questions

| ID | Question | Status |
|---|---|---|
| OQ-01 | Exact Smart Pen protocol (HID/stylus vs vendor SDK; USB vs Bluetooth) | Open |
| OQ-02 | Exact Whisper model and size for the HP EliteBook | Open |
| OQ-03 | Export format(s) (recommended: PNG, then PDF) | Technical/Product Decision Required |
| OQ-04 | Exact SQLite schema (proposal in Section 25) | Open |
| OQ-05 | Exact board coordinate system and canvas size (proposed 1920×1080) | Open |
| OQ-06 | Supported shape types for `create_shape` (proposed rectangle, circle, line, arrow, triangle) | Open |
| OQ-07 | Color model (named palette vs hex vs both) | Open |
| OQ-08 | Exact confirmation UX (proposal in Section 20) | Open |
| OQ-09 | Gemini/Groq models, API configuration, rate limits, cost | Open |
| OQ-10 | HP EliteBook hardware constraints (CPU/GPU/RAM) | Open |
| OQ-11 | The success scenario creates an equation, but no `create_equation` command exists. Should equations be created via `create_text` with an equation flag, or should a command be added? | Product Decision Required |
| OQ-12 | Push-to-talk press-and-hold vs click-toggle | Open |
| OQ-13 | Internal pen-drawing operation outside the 12-command AI set: acceptable? | Open |
| OQ-14 | Are transcripts stored (for metrics) or discarded? | Open |
| OQ-15 | Does undo history persist after a lesson is reopened? | Open |
| OQ-16 | Does `delete lesson` need the same confirmation UX as the board commands? | Open |

## 37. Development Phases

**Phase 1 — Core Foundation (P0)**
- [ ] Project structure and repository setup
- [ ] Board state and element model
- [ ] Command schema and validators
- [ ] Deterministic validation engine
- [ ] Command history with inverse operations
- [ ] SQLite persistence layer
- Validation: unit tests for engine, history and persistence pass; determinism test passes.

**Phase 2 — Board UI (P0)**
- [ ] PyQt6 fullscreen board
- [ ] Rendering of text, headings, shapes
- [ ] Selection, move, resize, delete, color
- [ ] Undo/Redo buttons
- Validation: all board commands can be run from a developer console with correct visuals.

**Phase 3 — Pen (P0)**
- [ ] Smart Pen input spike (protocol)
- [ ] Freehand drawing and live rendering
- [ ] Drawing element IDs
- [ ] Board state integration
- Validation: drawing is selectable, movable, deletable, undoable.

**Phase 4 — Voice (P0)**
- [ ] Push-to-talk control
- [ ] Local Whisper integration
- [ ] Transcription display
- [ ] Voice status indicator; audio deletion
- Validation: transcription accuracy and latency measured on the HP EliteBook.

**Phase 5 — AI (P0)**
- [ ] `AIProvider` abstraction and Gemini integration
- [ ] Strict JSON output and context builder
- [ ] Groq fallback
- [ ] Regeneration and error handling
- Validation: 50-utterance fixture set produces ≥ 95% valid commands.

**Phase 6 — Safety & Reliability (P0)**
- [ ] Confirmation and clarification flows
- [ ] Command queue
- [ ] Failure handling for all cases in Section 27
- Validation: all failure tests pass.

**Phase 7 — Lessons (P0/P1)**
- [ ] Autosave and manual save
- [ ] Open, rename, delete
- [ ] Export
- Validation: save/reopen round trip preserves state exactly.

**Phase 8 — Testing (P0)**
- [ ] Full unit and integration suites
- [ ] End-to-end scenario
- [ ] Performance testing
- [ ] Classroom simulation
- Validation: all acceptance criteria in Section 34 checked.

## 38. Future Roadmap (not part of MVP acceptance)

- **Phase 2:** Arabic support; improved handwriting recognition; more board commands; multiple pages; better shape recognition; more export formats. (P3 for V1)
- **Phase 3:** AI lesson generation; student interaction; collaboration; LMS integrations; web/mobile clients. (P3 for V1)
- **Future hardware:** potential dedicated Smart Chalkboard hardware. (P3 for V1)

---

## Appendix A — Milestones

| Milestone | Description | Due Date | Status | Owner |
|---|---|---|---|---|
| Kickoff | Project start | 2026-10-03 | TODO | Mohamed |
| PRD Approved | PRD signed off | [TBD] | TODO | Mohamed |
| Phase 1–2 Done | Foundation and board UI | [TBD] | TODO | Backend Dev |
| Phase 3–4 Done | Pen and voice | [TBD] | TODO | Frontend Dev |
| Phase 5–6 Done | AI and safety | [TBD] | TODO | Backend Dev |
| Phase 7–8 Done | Lessons and testing | [TBD] | TODO | QA |
| Beta Launch | Classroom pilot | [TBD] | TODO | Mohamed |
| Public Launch | V1 release | [TBD] | TODO | Mohamed |

## Appendix B — Stakeholders and Approvals

| Name | Role | Involvement | Contact |
|---|---|---|---|
| Mohamed | Owner / PM | Decisions, approval | [TBD] |
| [TBD] | Engineering Lead | Architecture sign-off | [TBD] |

| Gate | Approver | Required By | Status |
|---|---|---|---|
| PRD approval | Product Owner + Engineering Lead | Before Phase 1 | Pending |

## Appendix C — References

Design files [TBD] · Repository [TBD] · API docs (Gemini, Groq) [TBD] · Staging [TBD] · CI/CD [TBD]

## Appendix D — Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| v1.0 | 2026-10-03 | Mohamed | Initial PRD created |
