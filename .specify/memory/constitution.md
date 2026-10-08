<!-- Sync Impact Report:
Version change: 0.0.0 (template, unratified) → 1.0.0 (initial ratification)
List of modified principles:
- [PRINCIPLE_1_NAME] → I. AI Isolation (AI Never Controls the Board) [ADDED]
- [PRINCIPLE_2_NAME] → II. Determinism [ADDED]
- [PRINCIPLE_3_NAME] → III. Separation of Concerns (UI-Independent Core) [ADDED]
- [PRINCIPLE_4_NAME] → IV. Code Quality and Maintainability [ADDED]
- [PRINCIPLE_5_NAME] → V. Test-First Discipline + VI. Security and Privacy + VII. Reliability + VIII. Scope Discipline [ADDED - expanded from 5 template slots to 8 principles per user input]
Added sections:
- Additional Constraints (technology stack, 12-command lock, performance budgets)
- Development Workflow (TDD gates, CI, review, compliance)
Removed sections: none (template placeholders replaced)
Templates requiring updates:
- .specify/templates/plan-template.md — ✅ checked, no update required (generic Constitution Check gate remains compatible)
- .specify/templates/spec-template.md — ✅ checked, no update required (aligns; scope discipline reinforces FR/SC rigor)
- .specify/templates/tasks-template.md — ✅ checked, no update required (test-first tasks already supported; constitution mandates test-first for engine)
- .specify/templates/commands/*.md — ✅ checked, no files found, nothing to update
- README.md, docs/quickstart.md — ⚠ pending (files do not exist; create when scaffolding and reference this constitution)
- AGENTS.md — ⚠ pending (currently placeholder SPECKIT block only; add constitution reference on next scaffolding pass)
Follow-up TODOs: none — all placeholders resolved. Ratification date set to 2026-10-03 (initial adoption).
-->

# Smart Chalkboard Constitution

## Core Principles

### I. AI Isolation (AI Never Controls the Board)

AI MUST never directly mutate board state, call UI methods, touch SQLite,
or execute code. AI output is limited to producing a single structured
command object (`command`, `target_id`, `parameters`, `timestamp`).
Only the deterministic validation and execution engine may mutate board
state, and every AI-generated or pen-generated change MUST pass through
that engine. Any path that bypasses validation MUST be rejected in review.

Rationale: Unchecked AI output is unpredictable. A single-writer engine
guarantees every board change is validated, reversible where applicable,
and auditable.

### II. Determinism

Identical valid commands applied to identical board states MUST produce
identical resulting states, including identical element IDs and positions.
State transitions MUST contain no randomness, no network access, and no
wall-clock dependency. AI-supplied timestamps are informational only; the
engine owns authoritative ordering and history sequencing.

Rationale: Determinism makes behavior predictable for teachers, makes the
100-run identical-state test meaningful, and makes bugs reproducible.

### III. Separation of Concerns (UI-Independent Core)

Core logic — board model, command schema, validation, execution engine,
history (undo/redo), and persistence — MUST be independent of PyQt6 and
importable without any UI. UI widgets MUST NOT contain business rules;
they emit intents and render state only. The renderer MUST be a read-only
consumer of board state.

Rationale: Testability and reliability. The engine can be unit-tested,
fuzzed, and verified headless; UI failures can never corrupt state.

### IV. Code Quality and Maintainability

All Python code MUST carry complete type hints. Linting and formatting
MUST be enforced in CI and MUST block merges on failure. Modules MUST be
small and single-purpose. Business logic MUST NOT live in UI widgets.
Dead code, `eval`, `exec`, dynamic imports of untrusted strings, and
untyped public APIs are prohibited.

Rationale: Small, typed, lint-clean modules keep the safety-critical
engine reviewable and prevent validation logic from leaking into the UI.

### V. Test-First Discipline (NON-NEGOTIABLE)

Engine development MUST follow test-first: tests written, confirmed to
fail, then implementation. Validation and history modules MUST maintain
minimum 95% line coverage. Mandatory failure-path tests MUST cover at
minimum: malformed JSON, unsupported command, invalid target, missing
target, provider failure and fallback, database failure, renderer
failure, ambiguity/clarification, confirmation confirm and cancel, and
queue overflow. An end-to-end test of the Newton's Second Law scenario
(PRD Section 8: heading → equation → resize → pen drawing → confirmed
delete → undo) MUST pass before MVP acceptance.

Rationale: The engine is the sole state writer; only test-first with
explicit failure coverage proves rejections leave state and history
untouched.

### VI. Security and Privacy

API keys MUST never be committed to source control; they MUST be loaded
from environment variables or the OS credential store, and MUST never
appear in logs, errors, or exports. Raw audio MUST be deleted immediately
after transcription, including on failure, with temp-audio sweep at
startup. AI output MUST be treated as untrusted input and strictly
validated. `eval`/`exec` are forbidden. Only transcript text plus a
minimal board-context summary may be sent to providers, over TLS 1.2+.

Rationale: Classroom audio and credentials are sensitive; least-exposure
plus untrusted-AI handling bounds the blast radius of prompt injection.

### VII. Reliability and Offline Pen Continuity

Command execution MUST be atomic: a command fully applies or does not
apply. Commands MUST be processed sequentially through a single FIFO
queue with one command validated and executed at a time. Rejected,
cancelled, or timed-out commands MUST never change board state or history.
Manual Smart Pen drawing MUST keep working with full local state,
history, and persistence when AI or network is down; AI/network failure
MUST degrade to manual-only mode with a clear message and retry, never a
crash or state loss.

Rationale: Teachers cannot afford lost boards mid-lesson. Atomicity plus
a single queue plus offline-capable pen use makes failures recoverable.

### VIII. Scope Discipline

Only the 12 locked commands (`create_heading`, `create_text`, `move_item`,
`resize_item`, `delete_item`, `clear_board`, `create_shape`,
`change_color`, `undo`, `redo`, `save_lesson`, `new_lesson`) may be
AI-addressable in V1. No additional AI-addressable commands and no
features outside the MVP scope (multi-page, infinite canvas, non-English,
continuous listening, collaboration, LMS, AI lesson generation) may be
added without a constitution amendment. Pen-stroke commit is an internal
operation through the same engine, not a 13th AI command.

Rationale: A closed command set is what makes validation exhaustive and
latency predictable; scope creep reintroduces the unpredictability this
constitution exists to prevent.

## Additional Constraints

Technology stack is LOCKED for V1: Python application logic, PyQt6 UI,
local Whisper STT (English, push-to-talk only), Gemini primary with Groq
fallback via a swappable `AIProvider` interface, SQLite persistence
(WAL mode, transactional writes). Board canvas is fixed-size single-page
(default 1920x1080); every element bounding box MUST lie wholly inside
the canvas. Voice-command latency target: p50 < 3.0 s end-to-end under
normal conditions; validation plus execution < 100 ms per command.
Destructive commands (`delete_item`, `clear_board`, `new_lesson` with
unsaved changes) MUST require explicit confirmation. Ambiguous commands
MUST request clarification and MUST NOT guess. Rejection errors MUST use
typed codes (e.g., `E_SCHEMA`, `E_UNSUPPORTED_COMMAND`,
`E_PARAM_INVALID`, `E_TARGET_MISSING`, `E_TARGET_NOT_FOUND`,
`E_OUT_OF_BOUNDS`, `E_NOTHING_TO_UNDO`, `E_NOTHING_TO_REDO`,
`E_CONFIRMATION_REQUIRED`, `E_AMBIGUOUS`) with teacher-friendly messages.

## Development Workflow

All feature work MUST pass a Constitution Check gate before implementation
planning and re-check after design. Engine changes REQUIRE test-first
evidence, coverage report for validation/history, and a determinism run.
CI MUST enforce type checking, lint, format, full unit plus failure-path
suites, and the Newton's Second Law end-to-end test. Reviews MUST verify:
no direct state mutation outside the engine, no business logic in
widgets, no new AI-addressable commands, no secrets in code, and no
`eval`/`exec`. Violations MUST either be fixed or recorded in plan.md
Complexity Tracking with justification; unjustified violations block merge.

## Governance

This constitution supersedes all other practices, PRD interpretations,
and template defaults on conflict. Amendments REQUIRE a documented
proposal, version bump, and migration note in the Sync Impact Report.
Versioning follows semantic versioning: MAJOR for incompatible
governance or principle removals/redefinitions, MINOR for new principles
or materially expanded guidance, PATCH for clarifications and wording.
Compliance review is mandatory on every PR and plan; `AGENTS.md` and
runtime guidance MUST reference this file as the source of truth.

**Version**: 1.0.0 | **Ratified**: 2026-10-03 | **Last Amended**: 2026-10-03
