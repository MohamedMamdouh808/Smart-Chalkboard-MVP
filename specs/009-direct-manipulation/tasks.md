# Tasks: Direct Manipulation

**Input**: Design documents from `/specs/009-direct-manipulation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Requested in the specification and explicitly required test-first by the user: write each part’s tests before its implementation and confirm failure first.
**Constraints**: UI-independent core geometry; no thirteenth AI command; public voice-command schema unchanged; Select startup default; six-unit drawing tolerance; 24-canvas-unit minimum; full canvas containment; 24-screen-pixel handle targets; one history entry per accepted gesture; Pen-mode isolation.
**Organization**: User-requested delivery order — bounding box → hit testing → drag → handles/resize → history/cancellation → mixed voice/manual verification — with tests before implementation for every part.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the active feature workspace and pre-change test baseline

- [X] T001 [P] Verify that the active branch is `009-direct-manipulation` and that `.specify/feature.json` points to `specs/009-direct-manipulation`
- [X] T002 [P] Record the pre-change baseline by running the full suite in `tests/` and the core coverage gate for `src/smartboard/core/`, without changing source or tests

**Checkpoint**: Workspace and baseline are known before any 009 edits.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Confirm shared engine, queue, viewport, and widget seams before user-story work

**⚠️ CRITICAL**: No user-story work can begin until this phase is complete

- [X] T003 [P] Verify existing queue, engine-lock, manual-operation, history, and selection seams in `src/smartboard/app/command_queue.py`, `src/smartboard/app/orchestrator.py`, and `src/smartboard/core/engine.py` without changing behavior
- [X] T004 [P] Verify existing viewport mapping, pointer handling, selection painting, handle tokens, and mode behavior in `src/smartboard/ui/viewport.py`, `src/smartboard/ui/board_view.py`, `src/smartboard/ui/theme.py`, and `src/smartboard/ui/main_window.py` without changing behavior

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Trust the selection outline (Priority: P1) 🎯 MVP

**Goal**: Correct drawing bounds and dependable per-type hit testing with accurate selection outlines and handles

**Independent Test**: Select headings, text, equations, shapes, and multi-stroke drawings and verify each outline encloses all visible content; no dragging or resizing is required.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [P] [US1] Add failing canonical bounding-box tests to `tests/unit/test_direct_manipulation_geometry.py`, including the width-8 scribble-plus-line expectation `(96, 106, 728, 118)` and recalculation after creation, move, resize, undo, redo, and persistence restoration
- [X] T006 [P] [US1] Add failing per-type hit tests to `tests/unit/test_direct_manipulation_hit_testing.py` for headings, text, equations, rectangles, circles, lines, arrows, triangles, drawings, topmost overlap, malformed elements, empty space, and viewport-scale-aware handle detection
- [X] T007 [P] [US1] Add failing selection-presentation tests to `tests/ui/test_direct_manipulation_selection.py` for tight outlines around every element type, four corner handles on the selected element only, and immediate empty-space deselection

### Implementation for User Story 1

- [X] T008 [US1] Revise canonical drawing bounds and refresh behavior in `src/smartboard/core/board.py` and `src/smartboard/core/engine.py`, expanding point extrema by half the nominal stroke width and recalculating after creation, move, resize, undo, redo, and persistence restoration
- [X] T009 [US1] Implement per-type hit routines, shape-primitive handling, drawing proximity/box selection, expanded handle detection, and topmost dispatch in `src/smartboard/core/hit_test.py`, and use the canonical drawing bounds for selected-drawing outlines in `src/smartboard/ui/board_view.py`
- [X] T010 [US1] Run the new US1 tests plus affected existing drawing, hit-test, and selection tests in `tests/unit/test_direct_manipulation_geometry.py`, `tests/unit/test_direct_manipulation_hit_testing.py`, `tests/ui/test_direct_manipulation_selection.py`, `tests/unit/test_drawing_model.py`, `tests/integration/test_drawing_engine.py`, and `tests/ui/test_board_surface.py`, then fix only 009 regressions

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Drag an element directly (Priority: P1)

**Goal**: Select-mode dragging with non-mutating live previews and exactly one queued move commit

**Independent Test**: Drag headings, text, equations, shapes, and drawings to known destinations, verify canvas clamping, and verify one history entry with complete Undo/Redo.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US2] Add failing Qt-independent drag-geometry tests to `tests/unit/test_direct_manipulation_gesture_geometry.py` for grab offsets, translation, canvas clamping, integer commit quantization, and preview/state separation
- [X] T012 [P] [US2] Add failing synthetic drag tests to `tests/ui/test_direct_manipulation_drag.py` for mouse, tablet, and touch dragging of every element type, edge clamping, empty-space behavior, preview-only pointer motion, and one queued `move_item` commit

### Implementation for User Story 2

- [X] T013 [US2] Implement Qt-independent drag candidates, clamped translation, commit quantization, and preview geometry in `src/smartboard/core/gesture.py`
- [X] T014 [US2] Implement Select-mode press selection, idle/dragging transitions, movement threshold, snapshot previews, suppressed underlying rendering, and gesture signals in `src/smartboard/ui/board_view.py`
- [X] T015 [US2] Route valid drag releases through one FIFO-queued standard `move_item` operation with source `"ui"` in `src/smartboard/app/orchestrator.py` and `src/smartboard/app/main.py`
- [X] T016 [US2] Run the new US2 tests plus affected queue, selection, and viewport tests in `tests/unit/test_direct_manipulation_gesture_geometry.py`, `tests/ui/test_direct_manipulation_drag.py`, `tests/integration/test_command_queue.py`, and `tests/ui/test_coordinate_mapping.py`, then fix only 009 regressions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Resize from a corner handle (Priority: P1)

**Goal**: Four-corner resizing around a fixed opposite corner with proportion-aware previews and exactly one queued resize commit

**Independent Test**: Resize representative objects from `nw`, `ne`, `sw`, and `se`, verify fixed corners, proportions, text wrapping, minimum size, canvas containment, cursors, and history behavior.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US3] Add failing Qt-independent resize-geometry tests to `tests/unit/test_direct_manipulation_gesture_geometry.py` for all four fixed-corner anchors, proportion preservation for drawings/shapes/equations, independent text/heading boxes, minimum size, canvas clamping, integer quantization, and unchanged drawing stroke widths
- [X] T018 [P] [US3] Add failing synthetic resize tests to `tests/ui/test_direct_manipulation_resize.py` for all four corners, visible handles, diagonal hover cursors, live previews, text wrapping, edge/minimum behavior, and one queued `resize_item` commit

### Implementation for User Story 3

- [X] T019 [US3] Implement Qt-independent fixed-corner resize candidates, aspect policy, clamping, quantization, proportional drawing-point transforms, and preview geometry in `src/smartboard/core/gesture.py`
- [X] T020 [US3] Implement handle rendering, expanded handle interaction, hover cursors, idle/resizing transitions, snapshot previews, and resize-release signaling in `src/smartboard/ui/board_view.py`
- [X] T021 [US3] Implement internal fixed-corner manual resize execution in `src/smartboard/core/engine.py` and route one FIFO-queued existing `resize_item` operation with source `"ui"` through `src/smartboard/app/orchestrator.py` and `src/smartboard/app/main.py`
- [X] T022 [US3] Run the new US3 tests plus affected engine, rendering, text, and viewport tests in `tests/unit/test_direct_manipulation_gesture_geometry.py`, `tests/ui/test_direct_manipulation_resize.py`, `tests/integration/test_drawing_engine.py`, and `tests/ui/test_text_fit.py`, then fix only 009 regressions

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: History integration and cancellation

**Purpose**: Prove atomic history behavior and non-mutating cancellation across accepted and rejected gestures

- [X] T023 [P] Add failing history-accounting tests to `tests/integration/test_direct_manipulation_history.py` proving one applied entry per accepted drag/resize, complete Undo/Redo restoration, retained selection, FIFO ordering, and no concurrent engine writes
- [X] T024 [P] Add failing cancellation tests to `tests/ui/test_direct_manipulation_gesture_cancel.py` proving Escape, mode change, no-movement release, invalid geometry, rejected validation, blocked queue, and full-queue outcomes leave board state, version, and history unchanged
- [X] T025 Finalize successful and unsuccessful gesture completion in `src/smartboard/app/orchestrator.py`, `src/smartboard/app/main.py`, and `src/smartboard/ui/board_view.py`, including preview cleanup, unchanged-board refresh, error reporting, retained selection, and deferred/blocked queue behavior without duplicate commits
- [X] T026 Run the history/cancellation tests plus affected queue and engine tests in `tests/integration/test_direct_manipulation_history.py`, `tests/ui/test_direct_manipulation_gesture_cancel.py`, `tests/integration/test_command_queue.py`, and `tests/unit/test_history.py`, then fix only 009 regressions

**Checkpoint**: Accepted gestures have exactly one reversible history entry; every cancellation path is side-effect-free.

---

## Phase 7: Mixed voice/manual verification and polish

**Purpose**: Prove manual gestures coexist with voice operations and leave the suite green

- [X] T027 Add a failing voice-resize-then-manual-drag scenario to `tests/e2e/test_voice_manual_direct_manipulation.py` covering shared operations, transformed drawing points, recalculated bounds, selection retention, history order, Pen-mode isolation, and representative window sizes
- [X] T028 Resolve failures exposed by the mixed scenario in the applicable files among `src/smartboard/core/board.py`, `src/smartboard/core/hit_test.py`, `src/smartboard/core/gesture.py`, `src/smartboard/core/engine.py`, `src/smartboard/ui/board_view.py`, `src/smartboard/app/orchestrator.py`, and `src/smartboard/app/main.py`, without changing the public voice-command schema or adding an AI command
- [X] T029 Run the complete regression suite in `tests/` and the core coverage gate for `src/smartboard/core/`, requiring all tests to pass and coverage to remain at or above 95%
- [X] T030 Execute the manual and automated verification steps in `specs/009-direct-manipulation/quickstart.md` and record the headed-check outcomes there

**Checkpoint**: The feature is complete, tested, documented, and regression-free.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion; BLOCKS drag and resize work
- **User Story 2 (Phase 4)**: Depends on User Story 1 geometry and selection; BLOCKS resize-commit work
- **User Story 3 (Phase 5)**: Depends on User Story 2 gesture and commit infrastructure
- **History/cancellation (Phase 6)**: Depends on User Stories 1-3
- **Mixed verification/polish (Phase 7)**: Depends on all implementation and history behavior

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Requires User Story 1 bounds and selection - independently testable after Phase 3
- **User Story 3 (P1)**: Requires User Story 2 gesture/commit behavior - independently testable after Phase 4

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Geometry/selection behavior before widget behavior
- Core implementation before integration
- Widget behavior before application commit behavior
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run in parallel
- T003 and T004 can run in parallel
- T005, T006, and T007 can run in parallel
- T011 and T012 can run in parallel
- T017 and T018 can run in parallel
- T023 and T024 can run in parallel
- All other tasks are sequential because they share source files, extend prior behavior, or validate prior work

---

## Parallel Example: User Story 1

```text
# Launch all tests for User Story 1 together:
Task: "Add failing canonical bounding-box tests in `tests/unit/test_direct_manipulation_geometry.py`"
Task: "Add failing per-type hit tests in `tests/unit/test_direct_manipulation_hit_testing.py`"
Task: "Add failing selection-presentation tests in `tests/ui/test_direct_manipulation_selection.py`"
```

---

## Parallel Example: User Story 2

```text
# Launch all tests for User Story 2 together:
Task: "Add failing Qt-independent drag-geometry tests in `tests/unit/test_direct_manipulation_gesture_geometry.py`"
Task: "Add failing synthetic drag tests in `tests/ui/test_direct_manipulation_drag.py`"
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
5. Add history/cancellation → Verify atomic behavior
6. Add mixed voice/manual verification → Full regression green
7. Each story adds value without breaking previous stories

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
- Avoid: vague tasks, same file conflicts, public schema changes, new AI commands, board writes during previews, and implementation before tests
