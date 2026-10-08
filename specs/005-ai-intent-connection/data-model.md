# Data Model: AI Intent Connection

**Feature**: `005-ai-intent-connection` | **Date**: 2026-10-04
**Sources**: `spec.md`, `research.md`, `001` data-model/contracts

Board, Element, Command, History, Lesson, and the engine pipeline are
UNCHANGED. This feature adds intent-layer data shapes only.

## AIConfig

- Fields: `provider: str` (`groq` in V1; unknown → fail fast),
  `groq_api_key: str | None` (never logged/displayed),
  `groq_model: str` (default from `.env.example`, e.g.
  `llama-3.1-8b-instant`), `timeout_s: float = 4.0`, `max_regens: int = 1`.
- Source: `.env` via dotenv; `.env.example` committed with placeholders.

## RawResponse

- Fields: `raw_text: str` — exactly what the provider returned, nothing
  else. Parsed as JSON by the app layer, then validated by the engine as
  untrusted input. Providers MUST NOT return anything but the raw text.

## BoardContext (prompt input, least exposure)

- Fields: `transcript: str`; `elements: [{id, type, label, x, y}]`
  (short labels, no full content dumps); `selected_element_id: str |
  None`; `commands: [12 schemas]` (compacted).
- Rules: no audio, no keys, no full lesson content, no metrics.

## ClarificationResponse (display-only envelope)

- Shape: `{"clarification_needed": true, "question": "..."}`. Rendered
  as the teacher-facing question; never mutates state, never recorded.

## Outcome mapping (existing engine results → chip)

- `ok` → Done; `needs_confirmation` → Needs confirmation;
  `needs_clarification`/`E_AMBIGUOUS` → Needs clarification; anything
  else → Error with the exact regeneration-exhausted or outage message.
  Wiring only — the mapping table from 001 is unchanged.

## State transitions

`transcript → prompt → raw_text → parse → engine validate/execute →
board + history → chip/transcript display`. Any step may short-circuit
to a teacher-facing error with zero mutation; retry re-enters at the
transcript with identical semantics (no duplicate applies — a command
executes at most once per confirmation).
