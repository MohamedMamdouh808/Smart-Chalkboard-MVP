# Data Model: Smart Chalkboard MVP

**Feature**: `001-smart-chalkboard-mvp` | **Date**: 2026-10-03
**Sources**: `spec.md`, `research.md`, PRD Sections 17–20, 25, 31

## Entities

### Board

- Fields: `lesson_id: str`, `canvas: {width: 1920, height: 1080, unit: "px"}`,
  `elements: list[Element]`, `selected_element_id: str | None`, `version: int`.
- Rules: fixed single page; every element bbox wholly inside canvas;
  `selected_element_id` is null or references an existing element (deleting
  the selection clears it); new elements take top `z`; same valid command
  on same state → identical state (IDs, positions deterministic).

### Element

- Identity: `id: str` = `<type>_<NNN>` (zero-padded per-type counter),
  unique per lesson, never reused after deletion.
- Types: `heading | text | shape | drawing`. Equation content is a `text`
  element with `equation_style: true` (locked clarify decision).
- Common fields: `x, y, width, height` (canvas units, top-left origin),
  `color: str` (named palette or `#RRGGBB`), `z: int`.
- Type fields:
  - heading: `text` 1–200 chars.
  - text: `text` 1–2000 chars, optional `size`, `equation_style: bool`.
  - shape: `shape_type` in `rectangle|circle|line|arrow|triangle`,
    optional `position/size/color`.
  - drawing: `strokes: list[list[{x, y, pressure?}]]`, grouped per the
    1.5 s rule; selectable/movable/resizable/deletable/recolorable.
- Validation: text lengths trimmed; min size 24×24; scale factors
  0.25–4.0 ("bigger" ×1.25, "smaller" ×0.8); off-canvas results rejected,
  never clamped.

### Command (locked 12)

`create_heading | create_text | move_item | resize_item | delete_item |
clear_board | create_shape | change_color | undo | redo | save_lesson |
new_lesson`

- Schema: `{command, target_id: str | null, parameters: object, timestamp:
  ISO-8601 UTC Z}`. All four fields required, no extra top-level fields,
  strict types. Unknown parameter keys → rejection. AI timestamp is
  informational; engine assigns authoritative `seq`.
- Target resolution: target-requiring commands need an existing id or a
  contextual selection (`use_selection`-style flag + non-null
  `selected_element_id`); otherwise `E_TARGET_MISSING`/`E_AMBIGUOUS` with a
  clarification prompt. No guessing.
- Clarification envelope (not a command, never mutates):
  `{"clarification_needed": true, "question": "..."}`.
- Per-command params, confirm, undoability: see `contracts/command-schema.json`.
  `delete_item` + `clear_board` always confirm; `new_lesson` confirms when
  dirty; `undo`/`redo` move the history pointer and are never recorded;
  `save_lesson`/`new_lesson` are not undoable.

### Command history

- Record: every valid state-changing command with `seq` (per lesson),
  `command_json`, `inverse_json`, `source` (voice|pen|ui), `status`
  (applied|undone), `executed_at` (engine clock).
- Rules: invalid/cancelled/timed-out commands never recorded; new command
  after undo clears redo stack; depth 100; destructive commands recorded
  post-confirmation with original IDs restorable; history persisted in
  SQLite so undo survives lesson reopen.

### Lesson

- Fields: `id`, `title`, `created_at`, `updated_at`, `last_saved_at`,
  `deleted_at | null` (soft delete, 7-day purge default).
- Operations: new (confirm when dirty, offer save-first), open (latest
  saved state), rename, delete (explicit confirmation), manual save,
  autosave (~30 s when dirty + after destructive commands, background
  thread), export (V1: PNG image minimum).
- Retention: latest 20 autosave snapshots per lesson.

### Transcription (ephemeral)

- In-memory text of one utterance, shown for verification, deleted audio
  always; NOT persisted to SQLite; metrics carry counts/latencies only.

### Metrics (local only)

- `event_type` (command_attempt, validation_result, latency_stage,
  fallback_use, save_result…), `value_ms`, `detail_json` (no transcript,
  audio, keys, or lesson PII), `created_at`.

## SQLite schema (WAL, transactional writes, `schema_migrations`)

See `contracts/persistence-schema.sql`. Text timestamps are UTC ISO-8601.
`command_history(lesson_id, seq)` unique. `board_states(save_type)` in
`auto|manual`. `metrics_events` holds no content payloads.

## State transitions (engine pipeline, in order)

Receive → JSON/schema → supported-command → params → target → board-state
(capacity/bounds/history preconditions) → allowed-ops → destructive?
(confirm) → resolve defaults → reject (typed error, no mutation) or
execute atomically → update state → record history → emit render event →
autosave hook (background).

## Error codes

`E_SCHEMA | E_UNSUPPORTED_COMMAND | E_PARAM_INVALID | E_TARGET_MISSING |
E_TARGET_NOT_FOUND | E_OUT_OF_BOUNDS | E_NOTHING_TO_UNDO |
E_NOTHING_TO_REDO | E_CONFIRMATION_REQUIRED | E_AMBIGUOUS` — each with a
teacher-friendly message (see `contracts/error-codes.md`).
