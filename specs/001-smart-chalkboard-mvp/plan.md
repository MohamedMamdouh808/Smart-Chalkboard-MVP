# Implementation Plan: Smart Chalkboard MVP — Voice and Pen Classroom Board

**Branch**: `001-smart-chalkboard-mvp` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-smart-chalkboard-mvp/spec.md` + user technical brief + constitution v1.0.0

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

A fullscreen PyQt6 classroom board where press-and-hold voice (local
Whisper → Gemini/Groq `AIProvider` → strict JSON) and HID pen drawing both
funnel through one deterministic validation/execution engine (single FIFO
queue, atomic applies, typed errors, confirmation/clarification, undo/redo
history) persisted in SQLite (WAL). Primary requirement is the Newton's
Second Law E2E (heading → equation-as-styled-text → resize → pen drawing →
confirmed delete → undo) under 3 s p50, with pen fully usable offline.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6, faster-whisper (`small.en`, `base.en` fallback), google-generativeai (Gemini), groq SDK, pytest, pytest-qt, pytest-cov
**Storage**: SQLite (WAL, transactional, migrations table; JSON board snapshots; history + metrics tables)
**Testing**: pytest + pytest-qt + recorded audio/AI fixtures + determinism (100×) + Newton E2E + 100-command latency harness
**Target Platform**: Windows desktop (HP EliteBook), fullscreen non-touch display, HID/stylus pen, microphone
**Project Type**: desktop-app (single project)
**Performance Goals**: voice p50 < 3.0 s / p95 < 5 s; validation+execution < 100 ms; render < 100 ms; Whisper ≤ 1.0 s; AI ≤ 1.5 s primary path; 200 elements no lag
**Constraints**: 12-command lock; engine UI-independent (no PyQt6 in core); type hints everywhere; CI lint/format/type/test gates; no eval/exec; keys from env only; audio deleted post-transcription; atomic FIFO single-writer; pen works offline
**Scale/Scope**: single teacher, single lesson open, 100-step history, queue cap 5, 20 autosaves/lesson, 30 s autosave cadence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — `ai/` returns data only; only `core/engine.py` mutates `Board`; pen via internal op through same engine. No UI/AI/DB writes to state. PASS.
- [x] II. Determinism — no randomness/network/clock in transitions; AI timestamps informational; 100× determinism test required. PASS.
- [x] III. Separation — `core/` + `persistence/` importable without PyQt6 (CI import test); widgets emit intents + render only. PASS.
- [x] IV. Code quality — type hints, ruff/black (or configured equivalents), single-purpose modules, no logic in widgets, no eval/exec. PASS.
- [x] V. Test-first — engine test-first, ≥95% on validation/history, all listed failure paths, Newton E2E gate. PASS.
- [x] VI. Security/privacy — env keys, TLS 1.2+, audio deleted (+startup sweep), AI output untrusted,最小 context only. PASS.
- [x] VII. Reliability — atomic applies, FIFO single executor, rejections never mutate, offline pen continuity. PASS.
- [x] VIII. Scope — 12 locked commands (equation via `create_text`); no 13th command; out-of-scope items excluded. PASS.

Re-check after Phase 1 design (research/data-model/contracts/quickstart above): no new violations; pen `add_drawing` confirmed internal-only; transcript non-persistence and PNG-minimum export recorded as plan defaults pending second clarify pass. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/001-smart-chalkboard-mvp/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── command-schema.json
│   ├── aiprovider-interface.md
│   ├── engine-api.md
│   ├── persistence-schema.sql
│   ├── error-codes.md
│   └── acceptance-scenario.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── smartboard/
    ├── core/            # UI-independent: board, element_ids, commands,
    │                    # command_schema, validators, engine, history, errors
    ├── persistence/     # sqlite, migrations, lesson_repo, history_repo, metrics
    ├── voice/           # recorder (push-to-talk), whisper_service, audio_cleanup
    ├── ai/              # provider_iface, context_builder, gemini, groq, fallback_policy
    ├── app/             # session, command_queue, orchestrator, workers (threads), config
    └── ui/              # main_window, board_view (read-only), controls, mic_button,
                         # status_bar, transcription_strip, confirm_dialog, clarify_dialog,
                         # lesson_panel, pen_input (HID/stylus)

tests/
├── unit/                # core + persistence (test-first, ≥95% gate)
├── contract/            # schema/AI-shape/persistence contract tests
├── integration/         # voice→AI→engine→board→sqlite, pen→engine, fallback, queue
├── e2e/                 # Newton scenario (scripted + live), failure drills
├── performance/         # 100-command latency breakdown (EliteBook)
└── fixtures/
    ├── audio/           # recorded utterances incl. silence/edge cases
    └── ai_responses/    # valid, malformed, ambiguous, unsupported samples

.github/workflows/ci.yml # typecheck + lint + format + tests + coverage gate
```

**Structure Decision**: Single-project desktop-app layout. `core/` is the
safety-critical, UI-free engine package (unit-testable headless);
`persistence/voice/ai/app/` are adapters; `ui/` is a thin PyQt6 shell.
Heavy work (Whisper, AI, autosave) runs on worker threads; the queue owns
the only writer to `Board`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
