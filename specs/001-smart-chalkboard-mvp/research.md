# Research: Smart Chalkboard MVP

**Feature**: `001-smart-chalkboard-mvp` | **Date**: 2026-10-03
**Input**: User technical brief + `spec.md` + constitution v1.0.0 + PRD.md

## Decisions

### R-01: Python version and UI framework

- **Decision**: Python 3.11+, PyQt6 fullscreen desktop UI, `src/smartboard/` package layout with UI-independent `core/` + `persistence/`.
- **Rationale**: Matches locked stack and constitution principle III (core importable without UI). 3.11 gives `tomllib`, faster startup, and stable `pytest-qt` support on Windows.
- **Alternatives rejected**: Tkinter (weak canvas), Electron (breaks Python/Whisper locality and latency budget).

### R-02: Local Whisper model for HP EliteBook latency budget

- **Decision**: `faster-whisper` runtime, default model `small.en`, preloaded at startup off the UI thread; English-only; 15 s cap per utterance. If p50 transcription > 1.0 s on the EliteBook during Phase 4 benchmarks, drop to `base.en` (accuracy/latency tradeoff documented in metrics).
- **Rationale**: `small.en` is the largest English-only model plausibly inside the ≤1.0 s transcription slice of the 3 s budget; `faster-whisper` (CTranslate2) is 2–4× faster than reference Whisper on CPU. Preloading removes cold-start cost from the measured path.
- **Alternatives rejected**: Reference `openai-whisper` (slower on CPU), cloud STT (violates offline transcription + privacy rule), large models (blow the budget).
- **Validation**: Phase 4 measures 100 utterances on the EliteBook; model choice recorded in metrics.

### R-03: AI provider abstraction (Gemini primary, Groq fallback)

- **Decision**: `AIProvider.interpret(transcript, context) -> RawResponse` interface with `GeminiProvider` primary and `GroqProvider` fallback. Request provider structured/JSON mode where available. Policy: 1 regeneration on same provider for malformed JSON → fallback provider → teacher-facing error. First-attempt timeout 2.0 s (a 4 s timeout alone would exceed the 3 s target). Log provider name + error type only, never keys or content.
- **Rationale**: Satisfies AI-01…AI-07 and constitution VII (degrade to manual-only, never crash). One regeneration bounds latency while handling the top AI failure mode.
- **Alternatives rejected**: Single provider (no outage cover), unbounded retries (latency blowout), function-calling with side effects (violates AI isolation).

### R-04: API key handling

- **Decision**: Keys from environment variables only (`GEMINI_API_KEY`, `GROQ_API_KEY`), loaded at startup; fail-fast with a clear message if primary key missing. No keys in source, logs, errors, exports, or DB. OS credential store is a documented follow-up, env vars are the V1 contract.
- **Rationale**: Constitution VI + SEC-01/SEC-02. Env vars are CI-friendly (GitHub Actions secrets) and review-enforceable.

### R-05: SQLite persistence shape

- **Decision**: SQLite + WAL mode, transactional writes, `schema_migrations` table. Tables: `lessons`, `board_states` (JSON snapshots, `auto`/`manual`, keep latest 20 autosaves per lesson), `command_history` (`seq` per lesson, `source` in voice/pen/ui, `status` applied/undone, inverse JSON), `metrics_events` (latency stages, no audio/transcript content).
- **Rationale**: Locked stack; WAL keeps autosave off the critical path without blocking the UI thread. History persistence also resolves the deferred undo-after-reopen question: history IS persisted, undo survives reopen (up to 100 steps).
- **Alternatives rejected**: Raw JSON files (no atomic history/audit), ORM-heavy abstraction (unneeded complexity for single-user app).

### R-06: Threading and queue model

- **Decision**: Single FIFO `CommandQueue` (max 5 waiting, "Please wait" beyond that), one validator/executor (single writer) on a worker thread; Whisper, AI calls, and autosave run on background `QThreadPool`/worker threads; UI receives state-change events only. Context snapshot is taken at dequeue time. A command awaiting confirmation/clarification blocks the queue.
- **Rationale**: Constitution VII (atomic, sequential, one-at-a-time) plus PERF-04 (no frame stall > 100 ms). Single writer eliminates board-state races.
- **Alternatives rejected**: Direct UI-thread execution (freezes board during Whisper/AI), multi-executor parallelism (breaks determinism).

### R-07: Smart Pen input path

- **Decision**: Treat pen as standard HID/stylus (`QTabletEvent` / mouse-fallback) — no vendor SDK in V1. Stroke grouping: strokes within 1.5 s with no intervening selection/command form one `drawing` element. Pen-up commits go through the same engine as an internal `add_drawing` operation (not a 13th AI command). Live preview renders locally < 50 ms; commit is serialized through the queue.
- **Rationale**: PRD recommended default; keeps pen working offline and undoable with zero AI surface expansion.
- **Alternatives rejected**: Vendor SDK first (integration risk, hardware lock-in).

### R-08: Equation representation (resolves OQ-11)

- **Decision** (locked in clarify 2026-10-03): equations are equation-styled `text` elements via `create_text`. Renderer draws them with a distinct equation style (larger serif/monospace treatment; full LaTeX engine is out of scope). No `create_equation` command.
- **Rationale**: Preserves the 12-command lock and unblocks the acceptance scenario.

### R-09: Shapes, colors, confirmation, push-to-talk (clarify locks)

- **Decision**: Shapes exactly `rectangle/circle/line/arrow/triangle`. Colors: named palette of 8–10 plus `#RRGGBB` hex. Confirmation: modal, large pen-usable Cancel/Confirm, 30 s timeout = cancel. Push-to-talk: press-and-hold, release submits, 15 s cap, no toggle in V1.
- **Rationale**: Direct clarify outcomes 2026-10-03; each rejection returns the supported set and a teacher-friendly message.

### R-10: Transcripts and export (deferred clarify items — plan defaults)

- **Decision**: Transcripts are shown on screen and kept in memory for the session only; they are NOT persisted to SQLite and audio is always deleted (spec FR-015). Metrics record counts/latencies, never transcript text or audio. Export V1 minimum is a PNG board image (PDF follow-up). Lesson delete uses the same explicit-confirmation pattern.
- **Rationale**: Least-exposure privacy posture; PNG is the smallest verifiable shareable artifact. If the second clarify pass decides otherwise, only `persistence/` and export tasks change — engine untouched.

### R-11: Testing and CI

- **Decision**: `pytest` + `pytest-qt` (UI), `pytest-cov` (≥95% gate on validation/history), recorded fixtures for Whisper audio and AI JSON responses (no network in tests), determinism suite (100× same-sequence identical-state), Newton's Second Law E2E, latency harness (100 commands, stage breakdown). GitHub Actions: type check + lint + format check + full test suite + coverage gate; merges blocked on failure.
- **Rationale**: Constitution V (test-first, failure paths, E2E) made executable.

## Latency budget (p50, normal conditions)

| Stage | Budget |
|---|---|
| Whisper inference | ≤ 1.0 s |
| Network + AI response | ≤ 1.5 s (first attempt timeout 2.0 s; fallback path exempt from 3 s target) |
| JSON parse + validation | ≤ 50 ms |
| Execution + state update | ≤ 50 ms |
| Render | ≤ 100 ms |
| Overhead / queueing | ≤ 300 ms |
| **Total** | **< 3.0 s** |

## Risks carried into design

- Whisper `small.en` may still exceed 1.0 s on the EliteBook → mitigated by preload + `base.en` fallback (R-02).
- AI p95 will exceed 3 s on fallback path → accepted; target applies to primary path (documented in plan).
- Pen HID quirks on Windows → Phase 3 spike verifies `QTabletEvent` before pen UI work.
