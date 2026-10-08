# Tasks: Voice Microphone Command

**Input**: Design documents from `/specs/010-voice-microphone-command/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Requested in the specification and follow-up technical direction: fake doubles, real fixture transcription, bounds, silence, unavailable-microphone, queueing, no-disk-audio, readiness, metrics, and full regression coverage.
**Constraints**: Memory-only audio; English-only transcription; 0.4-second minimum; 15-second maximum; existing pipeline/queue/history/status behavior; twelve locked AI commands unchanged; listed exclusions remain excluded.
**Organization**: User-requested build order — model-loader worker → recorder → transcription worker → microphone hold/release and statuses → existing AI-path wiring → error cases and tests — grouped by user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the active feature workspace and pre-change verification baseline

- [X] T001 [P] Verify that the active branch is `010-voice-microphone-command` and that `.specify/feature.json` points to `specs/010-voice-microphone-command`
- [X] T002 [P] Record the pre-change baseline by running the full suite in `tests/` and the applicable core coverage gate for `src/smartboard/core/`, without changing source or tests

**Checkpoint**: Workspace and baseline are known before any 010 edits.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Provide configuration, dependency, and fake-test seams before voice work

**⚠️ CRITICAL**: No user-story work can begin until this phase is complete

- [X] T003 Add the missing `sounddevice` runtime dependency in `pyproject.toml` without importing it from untestable modules
- [X] T004 Add failing configuration tests to `tests/unit/test_voice_config.py` for `base.en`/`cpu` defaults and `WHISPER_MODEL`/`WHISPER_DEVICE` overrides
- [X] T005 Implement environment-backed transcription configuration in `src/smartboard/voice/voice_config.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Speak a board command (Priority: P1) 🎯 MVP

**Goal**: Press-hold capture, local transcription, and shared AI-pipeline execution for one spoken command

**Independent Test**: Submit a fake transcript through the same developer-text path and verify the resulting board state, statuses, result, queue behavior, and history.

### Model-loader worker

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [US1] Add failing model-loader tests to `tests/integration/test_voice_microphone.py` proving one background load, `base.en`/`cpu`/`int8` construction, reuse of the loaded model, and loading-state signaling
- [X] T007 [US1] Implement the background model-loader worker and readiness signals in `src/smartboard/voice/voice_worker.py`

### Recorder

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [US1] Add failing recorder tests to `tests/integration/test_voice_microphone.py` proving 16 kHz mono float32 in-memory buffering, 15-second cutoff, injected missing/denied-microphone errors, and no filesystem writes
- [X] T009 [US1] Implement press-hold sounddevice capture and injectable fake-backend behavior in `src/smartboard/voice/recorder.py`

### Transcription worker

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [US1] Add failing transcription-worker tests to `tests/integration/test_voice_microphone.py` proving direct NumPy-array transcription with English, beam size 1, VAD filtering, duration measurement, memory-only disposal, and QThread signal delivery
- [X] T011 [US1] Implement the NumPy transcription path, worker transcription job, duration measurement, and disposal behavior in `src/smartboard/voice/whisper_service.py` and `src/smartboard/voice/voice_worker.py`

### Microphone hold/release and statuses

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [US1] Add failing microphone-behavior tests to `tests/ui/test_microphone_button_voice.py` proving press-hold start, release-to-stop, Listening during capture, Processing during transcription, transcript display, and unchanged unrelated button behavior
- [X] T013 [US1] Implement press-hold behavior, loading/ready presentation, and status propagation in `src/smartboard/ui/mic_button.py` and `src/smartboard/ui/main_window.py`

### Existing AI-path wiring

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [US1] Add failing pipeline-wiring tests to `tests/integration/test_voice_microphone.py` proving finished transcripts enter the same developer-text submission function and receive identical validation, queueing, execution, status, result, and history behavior
- [X] T015 [US1] Wire finished voice transcripts through the existing developer-text submission path in `src/smartboard/app/main.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Trust unsuccessful or unavailable voice input (Priority: P1)

**Goal**: Predictable privacy-preserving failures with no board, state, history, disk, upload, or AI side effects

**Independent Test**: Exercise too-short audio, silence, transcription failure, missing microphone, and denied access, verifying exact messages and unchanged application state.

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T016 [US2] Add failing error-path tests to `tests/integration/test_voice_microphone.py` for sub-0.4-second recordings, silent/unintelligible audio, transcription errors, missing microphones, denied access, and filesystem-absence assertions
- [X] T017 [US2] Harden duration gating, exact failure messages, error disposal, unavailable-microphone handling, and non-submission behavior in `src/smartboard/voice/recorder.py`, `src/smartboard/voice/whisper_service.py`, `src/smartboard/voice/voice_worker.py`, and `src/smartboard/app/main.py`
- [X] T018 [US2] Run the new US2 tests plus affected existing voice and queue tests in `tests/integration/test_voice_microphone.py` and `tests/integration/test_voice.py`, then fix only 010 regressions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Start the first voice command without a cold-start delay (Priority: P2)

**Goal**: Background preparation with explicit microphone readiness before first use

**Independent Test**: Launch the application flow, verify loading text during preload and immediate first-command behavior after readiness, without blocking startup interaction.

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T019 [US3] Add failing readiness tests to `tests/ui/test_microphone_button_voice.py` proving `Loading voice model...` during preload, readiness transition, first-command availability, and nonblocking startup interaction
- [X] T020 [US3] Implement startup preload wiring and readiness presentation in `src/smartboard/app/main.py`, `src/smartboard/voice/voice_worker.py`, and `src/smartboard/ui/mic_button.py`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Fixture, metrics, and final verification

**Purpose**: Prove real transcription, performance telemetry, and regression safety

- [X] T021 Add the approved recorded command fixture at `tests/fixtures/audio/command.wav`, add the narrow `.gitignore` fixture exception in `.gitignore`, and add one real `base.en` transcription test to `tests/integration/test_voice_microphone.py`
- [X] T022 Add transcription-duration metric tests and implementation in `tests/integration/test_voice_microphone.py` and `src/smartboard/voice/voice_worker.py`, recording only duration milliseconds plus model/device/result metadata
- [X] T023 Run the complete regression suite in `tests/` and the applicable coverage gates, then execute the automated verification steps in `specs/010-voice-microphone-command/quickstart.md` and record the outcomes there

**Checkpoint**: The feature is complete, tested, documented, and regression-free.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - BLOCKS error-path and readiness work
- **User Story 2 (Phase 4)**: Depends on User Story 1 capture/transcription behavior
- **User Story 3 (Phase 5)**: Depends on User Story 1 loader/worker behavior
- **Final verification (Phase 6)**: Depends on all implementation and error behavior

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Requires User Story 1 capture/transcription - independently testable after Phase 3
- **User Story 3 (P2)**: Requires User Story 1 loader/worker - independently testable after Phase 3

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Configuration before loader
- Loader before recorder
- Recorder before transcription worker
- Worker before microphone behavior
- Microphone behavior before pipeline wiring
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run in parallel
- All other tasks are sequential because they share voice/UI/app files, extend prior behavior, or validate prior work

---

## Parallel Example: Setup

```text
# Launch setup checks together:
Task: "Verify active branch and feature pointer in `.specify/feature.json`"
Task: "Record baseline suite and coverage results for `tests/`"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add fixture, metrics, and final verification → Full regression green
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: Prepares User Story 2 tests without implementing shared behavior
   - Developer C: Prepares User Story 3 tests without implementing shared behavior
3. Stories complete and integrate in the required sequential order

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, disk-backed audio, parallel AI pipelines, schema changes, new AI commands, and implementation before tests
