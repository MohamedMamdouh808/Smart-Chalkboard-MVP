# Tasks: Adaptive Canvas Layout

**Input**: Design documents from `/specs/012-adaptive-canvas-layout/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Requested in the follow-up technical direction: canvas growth, element stability, uniform mapping, multi-size coordinates, edge bounds, legacy reopening, save/reopen identity, history invariance, window-margin layout, and full regression coverage.
**Constraints**: Stored per-lesson dimensions; grow-only non-history behavior; uniform undistorted mapping; minimum canvas/window bounds; legacy migration; twelve locked AI commands unchanged; listed exclusions remain excluded.
**Organization**: User-requested build order — canvas state and growth operation with tests first → hardcoded-size replacement → widget scale and mapping → default placement and sizes → lesson migration and export → layout and mixed voice/pen/drag tests — grouped by user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the active feature workspace and pre-change verification baseline

- [X] T001 [P] Verify that the active branch is `012-adaptive-canvas-layout` and that `.specify/feature.json` points to `specs/012-adaptive-canvas-layout`
- [X] T002 [P] Record the pre-change baseline by running the full suite in `tests/` and the applicable coverage gates, without changing source or tests

**Checkpoint**: Workspace and baseline are known before any 012 edits.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Inventory fixed-canvas assumptions before changing shared geometry code

**⚠️ CRITICAL**: No user-story work can begin until this phase is complete

- [X] T003 Inventory every hardcoded 1920/1080 use and canvas-sensitive test in `src/smartboard/core/board.py`, `src/smartboard/core/validators.py`, `src/smartboard/core/engine.py`, `src/smartboard/core/gesture.py`, `src/smartboard/ui/viewport.py`, `src/smartboard/ui/board_view.py`, `src/smartboard/app/exporter.py`, and `src/smartboard/ai/context_builder.py` without changing behavior

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Use the full classroom window (Priority: P1) 🎯 MVP

**Goal**: Store adaptive canvas dimensions and grow them monotonically without history effects

**Independent Test**: Verify stored dimensions, grow-only behavior, minimum/legacy handling, version updates, and history invariance without rendering any particular window size.

### Canvas state and growth operation

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T004 [US1] Add failing canvas-state and growth tests to `tests/unit/test_adaptive_canvas.py` for stored dimensions, minimum/new-board defaults, legacy migration defaults, grow-only increases, invalid dimensions, version updates, and zero history entries
- [X] T005 [US1] Implement stored canvas fields, serialization/restoration, minimum/legacy constants, and the validated non-history `grow_canvas` operation in `src/smartboard/core/board.py` and `src/smartboard/core/engine.py`
- [X] T006 [US1] Run the new US1 tests plus affected existing board/engine tests in `tests/unit/test_adaptive_canvas.py`, `tests/unit/test_drawing_model.py`, and `tests/unit/test_history.py`, then fix only 012 regressions

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Keep every element stable while resizing (Priority: P1)

**Goal**: Replace fixed-canvas geometry, mapping, and placement with stored-canvas behavior while preserving absolute coordinates

**Independent Test**: Resize through representative sizes and verify exact element coordinates, undistorted rendering, consistent pointer/command mapping, bounded placement, and history invariance.

### Stored-dimension geometry replacement

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [US2] Add failing stored-dimension geometry tests to `tests/unit/test_adaptive_canvas.py` for clipping, drawing bounds, bounds validation, drag clamping, resize clamping, and right/bottom-edge behavior
- [X] T008 [US2] Replace fixed-canvas geometry with stored dimensions in `src/smartboard/core/board.py`, `src/smartboard/core/validators.py`, `src/smartboard/core/engine.py`, and `src/smartboard/core/gesture.py`

### Widget scale and coordinate mapping

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [US2] Add failing mapping tests to `tests/ui/test_adaptive_canvas_layout.py` for capped uniform scale, centering only during downscaling, exact screen/canvas inverses, pen/selection/drag/resize coordinates, and several window sizes
- [X] T010 [US2] Implement explicit-canvas viewport mapping, stored-canvas rendering/mapping, and available-area growth signaling in `src/smartboard/ui/viewport.py` and `src/smartboard/ui/board_view.py`

### Default placement and sizes

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [US2] Add failing default-placement tests to `tests/unit/test_adaptive_canvas.py` for canvas-proportionate origins, legacy-size maximums, small-canvas validity, and large-canvas bounds
- [X] T012 [US2] Implement canvas-proportionate default placement and bounded default sizes in `src/smartboard/core/engine.py`
- [X] T013 [US2] Run the new US2 tests plus affected existing viewport, gesture, input, and engine tests in `tests/unit/test_adaptive_canvas.py`, `tests/ui/test_adaptive_canvas_layout.py`, `tests/ui/test_viewport_math.py`, and `tests/integration/test_drawing_engine.py`, then fix only 012 regressions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Preserve lessons, exports, and command determinism (Priority: P2)

**Goal**: Persist, reopen, export, and interpret lessons using stored canvas dimensions

**Independent Test**: Save, reopen, migrate, export, and replay identical commands against identical stored states without moving elements or changing history semantics.

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [US3] Add failing persistence tests to `tests/integration/test_canvas_persistence.py` for saved canvas JSON, legacy reopening, save/reopen identity, stored-canvas exports, AI-context dimensions, and history invariance
- [X] T015 [US3] Implement board restoration/migration, stored-canvas exports, AI-context dimensions, and locked growth routing in `src/smartboard/core/board.py`, `src/smartboard/app/exporter.py`, `src/smartboard/ai/context_builder.py`, `src/smartboard/app/orchestrator.py`, and `src/smartboard/app/main.py`
- [X] T016 [US3] Run the new US3 tests plus affected existing persistence, export, context, and lesson tests in `tests/integration/test_canvas_persistence.py`, `tests/integration/test_lessons.py`, and `tests/integration/test_ai_intent_live.py`, then fix only 012 regressions

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Layout and mixed-behavior verification

**Purpose**: Prove window layout and combined voice/pen/drag behavior on adaptive canvases

- [X] T017 Add layout and mixed-behavior tests to `tests/ui/test_adaptive_canvas_layout.py` and `tests/e2e/test_canvas_voice_pen_drag.py` for window-minus-margins board width at 959×566, repeated resizes, voice commands, pen drawing, and manual dragging across representative sizes
- [X] T018 Resolve layout/mixed-behavior failures in the applicable files among `src/smartboard/ui/board_view.py`, `src/smartboard/ui/main_window.py`, `src/smartboard/app/main.py`, `src/smartboard/core/engine.py`, and `src/smartboard/ai/context_builder.py`, without adding canvas controls, pages, zoom, pan, or stretching
- [X] T019 Run the complete regression suite in `tests/` with applicable coverage gates, then execute the automated verification steps in `specs/012-adaptive-canvas-layout/quickstart.md` and record the outcomes there

**Checkpoint**: The feature is complete, tested, documented, and regression-free.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - BLOCKS geometry/mapping work
- **User Story 2 (Phase 4)**: Depends on User Story 1 stored canvas and growth behavior
- **User Story 3 (Phase 5)**: Depends on User Stories 1-2
- **Final verification (Phase 6)**: Depends on all implementation and persistence behavior

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Requires User Story 1 canvas state/growth - independently testable after Phase 3
- **User Story 3 (P2)**: Requires User Stories 1-2 - independently testable after Phase 4

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Stored state before geometry replacement
- Geometry replacement before mapping
- Mapping before default placement
- Placement before persistence/export behavior
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run in parallel
- All other tasks are sequential because they share core/UI/app files, extend prior behavior, or validate prior work

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
5. Add layout/mixed verification → Full regression green
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
- Avoid: vague tasks, same file conflicts, fixed-canvas assumptions, element rewrites on resize, history entries for growth, new AI commands, canvas controls, pages, zoom, pan, and stretching
