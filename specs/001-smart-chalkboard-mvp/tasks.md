# Tasks: Smart Chalkboard MVP — Voice and Pen Classroom Board

**Input**: Design documents from `/specs/001-smart-chalkboard-mvp/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Engine tests are MANDATORY and test-first per constitution V. UI/integration/E2E tests listed per phase.

**Organization**: Phases follow the requested build order (foundation → UI → pen → voice → AI → safety → lessons → testing). Engine phases put tests BEFORE implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding, CI gates, repo hygiene

- [X] T001 Create package layout `src/smartboard/{core,persistence,voice,ai,app,ui}/` + `tests/{unit,contract,integration,e2e,performance,fixtures/audio,fixtures/ai_responses}/` + `.github/workflows/ci.yml` stub
- [X] T002 [P] Configure `pyproject.toml` (Python 3.11+, PyQt6, faster-whisper, google-generativeai, groq, pytest, pytest-qt, pytest-cov, ruff/black, mypy) in `pyproject.toml`
- [X] T003 [P] Configure lint/format/type gates + GitHub Actions CI (typecheck + lint + format check + tests + ≥95% coverage gate on `core/`) in `.github/workflows/ci.yml`, `.pre-commit-config.yaml`
- [X] T004 [P] Add recorded-fixture scaffolding: sample WAV + AI JSON samples (valid/malformed/ambiguous/unsupported) in `tests/fixtures/audio/`, `tests/fixtures/ai_responses/`

**Checkpoint**: `pytest --collect-only` runs; CI workflow lints an empty package green.

---

## Phase 2: Core Foundation — TESTS FIRST, then engine (Blocking Prerequisites)

**Purpose**: UI-independent deterministic engine; sole writer to board state. Constitution principles I, II, III, V, VII.

**⚠️ CRITICAL**: No UI/pen/voice/AI work can begin until this phase is complete. Tests MUST be written and FAIL before implementation.

### Tests for Core Foundation (write FIRST ⚠️)

- [X] T005 [P] [US1] Schema tests for all 12 commands incl. equation-via-`create_text`, shape enum (5 locked), palette+hex, extra-field rejection in `tests/unit/test_command_schema.py`
- [X] T006 [P] [US1] Param validator tests (text lengths, scale 0.25–4.0, ×1.25/×0.8 mappings, bounds/min-size, no-room) in `tests/unit/test_validators.py`
- [X] T007 [P] [US2] Target/selection tests (explicit id, `use_selection`, missing→`E_TARGET_MISSING`, unknown→`E_TARGET_NOT_FOUND`, ambiguity→`E_AMBIGUOUS`, no-guess rule) in `tests/unit/test_target_resolution.py`
- [X] T008 [P] [US4] History tests (record + inverse, undo/redo pointer, redo-clear, depth 100, undo/redo unrecorded, save/new unrecorded, cancel unrecorded) in `tests/unit/test_history.py`
- [X] T009 [P] [US4] Engine rejection tests (every `E_*` code; state+history byte-identical after reject/cancel/timeout) in `tests/unit/test_engine_rejections.py`
- [X] T010 [P] Determinism tests (100× same-sequence identical-state incl. IDs/positions) in `tests/unit/test_determinism.py`
- [X] T011 [P] Persistence contract tests (migrations, lessons CRUD, snapshots, history seq/status, WAL, transactional rollback on DB failure) in `tests/unit/test_persistence.py`

### Implementation for Core Foundation (only AFTER tests T005–T011 fail)

- [X] T012 [P] [US1] Implement `src/smartboard/core/element_ids.py`, `src/smartboard/core/board.py` (Board/Element, 1920×1080 bounds, selection, z-order, deterministic IDs)
- [X] T013 [P] [US1] Implement `src/smartboard/core/command_schema.py`, `src/smartboard/core/validators.py` (12 commands, shape/color/enum rules per `contracts/command-schema.json`)
- [X] T014 [US1] Implement `src/smartboard/core/engine.py` (14-step pipeline, atomic apply, typed `EngineResult`, confirm/clarify signals) — depends on T012, T013
- [X] T015 [US4] Implement `src/smartboard/core/history.py` (inverses, pointer, depth 100, persistence hook) — depends on T014
- [X] T016 [US4] Implement `src/smartboard/core/errors.py` (all `E_*` codes + teacher messages per `contracts/error-codes.md`)
- [X] T017 Implement `src/smartboard/persistence/sqlite.py`, `src/smartboard/persistence/migrations.py`, `src/smartboard/persistence/{lesson_repo,history_repo,metrics}.py` per `contracts/persistence-schema.sql` (WAL, transactions; transcripts never stored)
- [X] T018 [P] UI-independence guard test (import `smartboard.core` + `smartboard.persistence` with PyQt6 blocked) in `tests/contract/test_core_has_no_ui_imports.py`

**Checkpoint**: `pytest tests/unit tests/contract -q` green with ≥95% coverage on `core/`; engine test-first evidence recorded.

---

## Phase 3: Board UI (PyQt6 shell, read-only renderer)

**Purpose**: Fullscreen board, selection, status/transcription, dialogs. No business logic in widgets.

- [X] T019 [P] [US1] pytest-qt scaffold for renderer (state-in → pixels-out, 100 ms render budget) in `tests/integration/test_renderer.py`
- [X] T020 [US1] Implement `src/smartboard/ui/main_window.py` (fullscreen, ≥96×96 mic button, status bar Listening/Processing/Validating/Executing/Idle, transcription strip, Undo/Redo buttons, pen/select toggle)
- [X] T021 [US1] Implement `src/smartboard/ui/board_view.py` (read-only canvas, aspect-preserving scale, heading/text/equation-style/shape/drawing render, selection outline, highlight of affected element)
- [X] T022 [US2] Implement selection model in `src/smartboard/ui/selection.py` (pen/mouse select, exposes `selected_element_id`, clears on delete)
- [X] T023 [US4] Implement `src/smartboard/ui/confirm_dialog.py` (modal, large Cancel/Confirm, 30 s timeout = cancel) + `src/smartboard/ui/clarify_dialog.py` ("Which object…?" + select-to-resolve)

**Checkpoint**: Board renders all 5 element types from engine state; dialogs operable with pen pointer; no widget mutates state directly.

---

## Phase 4: Pen (HID/stylus, offline-first)

**Purpose**: US3 — drawings as first-class undoable elements through the same engine.

- [X] T024 [P] [US3] Pen-commit tests (unique never-reused IDs, 1.5 s grouping, move/resize/recolor/delete via commands, undo restores) in `tests/integration/test_pen_engine.py`
- [X] T025 [US3] Implement `src/smartboard/ui/pen_input.py` (`QTabletEvent`/mouse fallback, live preview <50 ms, pen-up grouping) + internal `add_drawing` commit path in `src/smartboard/app/orchestrator.py` (NOT a 13th AI command)
- [X] T026 [US3] Verify pen works with loopback-disabled network (manual-only mode drill) in `tests/integration/test_offline_pen.py`

**Checkpoint**: Drawings selectable/movable/deletable/undoable with unique IDs; pen works with no network.

---

## Phase 5: Voice (push-to-talk + local transcription)

**Purpose**: US1/US2 capture — press-and-hold, English, on-screen transcription, audio deleted.

- [X] T027 [P] [US1] Recorder tests (hold-to-record/release-to-submit, 15 s cap, empty/silence → retry message, no AI call) in `tests/integration/test_recorder.py`
- [X] T028 [P] [US6] Whisper fixture tests (recorded audio → expected text; failure/empty → friendly message; audio file deleted incl. on failure) in `tests/integration/test_whisper_fixtures.py`
- [X] T029 [US1] Implement `src/smartboard/voice/recorder.py`, `src/smartboard/voice/whisper_service.py` (faster-whisper `small.en` preloaded off UI thread, `base.en` fallback), `src/smartboard/voice/audio_cleanup.py` (delete + startup temp sweep) + `src/smartboard/ui/mic_button.py` wiring
- [X] T030 Measure 100-utterance Whisper latency on HP EliteBook; record model decision in `tests/performance/test_whisper_latency.py`

**Checkpoint**: Transcription visible ≤1.0 s p50 slice; audio never retained; empty audio never reaches AI.

---

## Phase 6: AI Intent (provider abstraction + fallback)

**Purpose**: Text + board context → strict JSON only. No side effects.

- [X] T031 [P] [US1] AI contract tests (valid/invalid/ambiguous/unsupported fixtures → schema pass/fail; malformed → 1 regen → fallback → error) in `tests/contract/test_aiprovider_contract.py`
- [X] T032 [P] [US6] Fallback tests (timeout>2.0 s, network error, 5xx, rate-limit → Groq; both-down → clear error + Retry, board/pen intact) in `tests/integration/test_ai_fallback.py`
- [X] T033 Implement `src/smartboard/ai/provider_iface.py`, `src/smartboard/ai/context_builder.py` (transcript + element summaries + selection + 12 schemas only), `src/smartboard/ai/gemini.py`, `src/smartboard/ai/groq.py`, `src/smartboard/ai/fallback_policy.py` per `contracts/aiprovider-interface.md` (env keys, JSON mode, log provider+type only)
- [X] T034 50-utterance fixture validation (≥95% valid commands) in `tests/integration/test_ai_accuracy.py`

**Checkpoint**: AI returns data only; every output validated as untrusted; fallback path never exceeds design without a clear message.

---

## Phase 7: Safety & Reliability (queue, confirm/clarify wiring, failure drills)

**Purpose**: US4/US6 — atomic sequential execution, no-guess behavior, graceful degradation.

- [X] T035 [P] [US4] Queue tests (FIFO order, one-at-a-time, dequeue-time snapshot, cap 5 → "Please wait", confirm blocks queue, failure never clears queue) in `tests/integration/test_command_queue.py`
- [X] T036 [P] [US4] Confirmation/clarification flow tests (confirm/cancel/timeout paths; ambiguous → question + selection resolve; rejections leave state+history identical) in `tests/integration/test_confirm_clarify_flows.py`
- [X] T037 [US6] Failure-matrix tests (Whisper fail, AI all-down, network loss, DB fail, renderer fail, save fail — each with exact teacher message + preserved board + retry) in `tests/integration/test_failure_matrix.py`
- [X] T038 Implement `src/smartboard/app/command_queue.py`, `src/smartboard/app/session.py`, `src/smartboard/app/workers.py` (Whisper/AI/autosave off UI thread; single executor owning the only writer)
- [X] T039 Wire status machine + error surfacing (loading ≤200 ms, errors persist to dismiss, success highlight) in `src/smartboard/ui/status_bar.py`

**Checkpoint**: All failure tests green; queue + confirm/clarify behave per FR-008/FR-009/FR-014.

---

## Phase 8: Lessons (new/open/rename/delete/save/autosave/export)

**Purpose**: US5 — teacher work survives sessions.

- [X] T040 [P] [US5] Lesson tests (new/open/rename/delete+confirm, manual save, autosave cadence without UI block, save-fail message + in-memory preserve + export fallback, reopen restores IDs/positions/history) in `tests/integration/test_lessons.py`
- [X] T041 [US5] Implement `src/smartboard/app/lesson_service.py` (dirty tracking, save-first offer on new, 30 s autosave, post-destructive save) + `src/smartboard/ui/lesson_panel.py` (collapsible) + PNG export in `src/smartboard/app/exporter.py`
- [X] T042 [US5] 50× save/reopen round-trip identity test in `tests/integration/test_save_reopen_identity.py`

**Checkpoint**: Zero-loss round trips; history (undo) survives reopen; export produces a shareable file.

---

## Phase 9: Testing & Acceptance (gates, E2E, performance)

**Purpose**: Prove MVP acceptance; lock quality gates.

- [X] T043 [US1–US4] Newton's Second Law E2E with fixtures (heading → equation → ×1.25 resize → pen drawing → confirmed delete → Undo restores original ID) in `tests/e2e/test_newton_scenario.py`
- [X] T044 Live-speaker E2E repeat of T043 (human mic, same assertions) in `tests/e2e/test_newton_live.py`
- [X] T045 [P] 100-command latency harness with stage breakdown (Whisper/AI/validate/execute/render) + budgets enforced in `tests/performance/test_latency_budget.py`
- [X] T046 [P] Determinism + coverage gate run (100× identical-state + `--cov-fail-under=95` on `core/`) in CI `ci.yml`
- [X] T047 [P] Classroom simulation (noise/accents, 30-min session script, correction-rate metrics) in `tests/performance/test_classroom_sim.py`
- [X] T048 Docs + `quickstart.md` validation (fresh-venv setup → run → E2E green) and metrics-target review (SC-002…SC-007)

**Checkpoint**: All acceptance criteria (spec SC-001…SC-007) verified; MVP demo-ready.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Core Foundation (Phase 2)**: Depends on Setup — BLOCKS all later phases; tests T005–T011 MUST fail before T012–T018
- **Board UI (Phase 3)**: Depends on Phase 2 (renders engine state only)
- **Pen (Phase 4)**: Depends on Phases 2–3 (commits through engine, renders on board)
- **Voice (Phase 5)**: Depends on Phase 2 (transcription feeds engine-bound pipeline)
- **AI (Phase 6)**: Depends on Phases 2 + 5 (text + context → JSON → engine)
- **Safety & Reliability (Phase 7)**: Depends on Phases 2–6 (wires queue + dialogs + failure paths)
- **Lessons (Phase 8)**: Depends on Phases 2 + 7 (persistence + queue/atomicity)
- **Testing & Acceptance (Phase 9)**: Depends on all prior phases

### Within Each Phase

- Engine phases: tests FIRST, confirm FAIL, then implement (T005–T011 → T012–T018)
- All phases: contract/fixture tests before adapters; core before wiring; story complete before next priority

### Parallel Opportunities

- All [P] tests within a phase can run in parallel (different files)
- T005–T011, T012–T013, T016–T017 file groups are parallel-safe
- Phases 3–6 can overlap once Phase 2 interfaces (`engine.py`, `history.py`, error codes) are frozen, but each still verifies against the engine independently

---

## Implementation Strategy

### MVP First (engine + US1 slice)

1. Complete Phase 1 (Setup) + Phase 2 (Core Foundation test-first)
2. Complete Phase 3 (Board UI read-only) — engine drivable from console
3. **STOP and VALIDATE**: 12-command validation + determinism + coverage gate green

### Incremental Delivery

1. Setup + Foundation → engine proven headless
2. + Board UI → visible board, console-driven commands
3. + Pen → drawable, undoable, offline-capable
4. + Voice → push-to-talk with transcription display
5. + AI → strict JSON with fallback
6. + Safety → queue + confirm/clarify + failure matrix
7. + Lessons → save/reopen/export
8. + Testing → Newton E2E + latency + classroom sim (MVP!)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to spec user story for traceability (US1–US6)
- Engine rule: `core/` + `persistence/` importable without PyQt6 — enforced by T018 and CI
- Verify engine tests fail before implementing (T005–T011 red → T012–T018 green)
- Commit after each task or logical group; stop at any checkpoint to validate independently
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence, any 13th AI command
