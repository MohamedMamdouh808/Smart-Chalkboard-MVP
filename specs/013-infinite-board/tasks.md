# Tasks: Infinite Board

**Input**: Design documents from `/specs/013-infinite-board/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Included because the user explicitly requested pytest/pytest-qt coverage and the specification requires measurable acceptance testing.
**Organization**: Tasks are grouped by user story. The phase order follows the user-requested build sequence.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (for example, US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/smartboard/` and `tests/` at repository root
- UI tests use offscreen Qt through `pytest-qt`
- Core tests remain headless and PyQt-independent

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish governance, baseline, and the required build order before implementation.

- [X] T001 Record the required infinite-board constitution-amendment proposal in `specs/013-infinite-board/constitution-amendment-proposal.md`
- [X] T002 Verify Python 3.11, PyQt, pytest, pytest-qt, and SQLite prerequisites and record the baseline command/results in `specs/013-infinite-board/baseline.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build camera mathematics and the unbounded world model before any story-specific input, rendering, editing, voice, persistence, or performance work.

**CRITICAL**: No user-story work can begin until this phase is complete.

### Tests for foundation

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T003 [P] Add camera/transform round-trip, cursor-anchored zoom, limits, and history-invariance tests in `tests/unit/test_camera_transform.py`
- [X] T004 [P] Add unbounded creation/move/resize/drawing, minimum-size, numeric-guard, and canvas-free serialization tests in `tests/unit/test_infinite_world.py`
- [X] T005 [P] Add application-owned camera and camera-operation history-invariance tests in `tests/integration/test_camera_ownership.py`

### Implementation for foundation

- [X] T006 [P] Implement application-owned `CameraState`, validation, pan/zoom/reset/fit helpers, and visible-rectangle calculation in `src/smartboard/app/camera.py`
- [X] T007 [P] Implement Qt-agnostic world/screen transforms in `src/smartboard/ui/camera_transform.py`
- [X] T008 Remove canvas dimensions, clipping, bounded drawing bounds, canvas-aware restore, and canvas serialization in `src/smartboard/core/board.py`
- [X] T009 Replace canvas-bound validation with finite world-coordinate/dimension guards in `src/smartboard/core/validators.py`
- [X] T010 Remove canvas checks, canvas growth, canvas-proportional defaults, and drawing clipping from engine operations in `src/smartboard/core/engine.py`
- [X] T011 Remove canvas clamping and enforce finite unbounded gesture geometry in `src/smartboard/core/gesture.py`
- [X] T012 Revise retained `E_OUT_OF_BOUNDS` wording from page-edge language to numeric-range language in `src/smartboard/core/errors.py`
- [X] T013 Make `Orchestrator` own authoritative camera/view size and remove canvas-growth routing in `src/smartboard/app/orchestrator.py`

**Checkpoint**: Camera math and unbounded engine behavior are independently tested; camera operations do not mutate board state or history.

---

## Phase 3: User Story 1 - Navigate an unbounded board (Priority: P1) 🎯 MVP

**Goal**: Teachers can pan and zoom an edgeless board through every supported gesture, button, shortcut, indicator, fit-all behavior, grid, and viewport rendering path.

**Independent Test**: Drive pan/zoom gestures, shortcuts, buttons, indicators, fit-all, grid motion, culling, handle sizing, and history inspection without creating or editing content.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] Add wheel, Shift-wheel, Ctrl-wheel, Space-drag, middle-button drag, empty-space drag, pinch/native zoom, shortcuts, zoom indicator, fit-all, and history-invariance widget tests in `tests/ui/test_camera_input.py`
- [X] T015 [P] [US1] Add viewport culling, zoom-dependent grid, constant-screen handles/selection, and pointer-tolerance widget tests in `tests/ui/test_infinite_rendering.py`
- [X] T016 [P] [US1] Add camera JSON, transform invariant, pan/zoom/reset/fit, and no-board-mutation contract tests in `tests/contract/test_camera_transform_contract.py`

### Implementation for User Story 1

- [X] T017 [P] [US1] Create the shared read-only world-space element painting helper in `src/smartboard/ui/board_paint.py`
- [X] T018 [US1] Implement camera-aware input routing, gestures, transforms, culling, grid, screen-space adornments, and provisional-edit anchoring hooks in `src/smartboard/ui/board_view.py`
- [X] T019 [US1] Add zoom in/out/reset/fit controls, shortcuts, and zoom-percentage indicator wiring in `src/smartboard/ui/main_window.py`
- [X] T020 [US1] Apply authoritative camera updates, transient view-size tracking, and camera-aware rerendering in `src/smartboard/app/main.py`

**Checkpoint**: User Story 1 is fully navigable and independently testable; camera motion creates no board or history changes.

---

## Phase 4: User Story 3A - Draw, select, drag, and resize at any zoom (Priority: P2)

**Goal**: Pen drawing, selection, dragging, and resizing remain accurate in world coordinates from 10% through 400% zoom.

**Independent Test**: Draw and manipulate elements at representative pan/zoom extremes; verify stored world geometry, selection accuracy, fixed-corner resizes, and constant-screen handles.

### Tests for User Story 3A

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T021 [P] [US3] Add unbounded world drag/resize geometry and fixed-corner behavior tests in `tests/unit/test_world_gestures.py`
- [X] T022 [P] [US3] Add pen capture, selection, drag, resize, and constant-handle widget tests across zoom levels in `tests/ui/test_world_manipulation.py`

### Implementation for User Story 3A

- [X] T023 [US3] Convert pen capture/grouping to canonical world coordinates in `src/smartboard/ui/pen_input.py`
- [X] T024 [US3] Implement zoom-scaled pointer tolerance and world-space hit testing in `src/smartboard/core/hit_test.py`
- [X] T025 [US3] Route world-space selection, pen, drag, resize, hover, and commit payloads through the camera transform in `src/smartboard/ui/board_view.py`

**Checkpoint**: World-space drawing and direct manipulation work independently at all supported zoom levels.

---

## Phase 5: User Story 2 - Create and edit text directly on the board (Priority: P1)

**Goal**: Teachers can double-click to create provisional text and edit existing headings, text, and equations inline, with exact one-entry history behavior for accepted changes.

**Independent Test**: Double-click empty and occupied space; commit with Enter/outside click; cancel with Escape; clear existing text; verify content, validation, selection, one-step undo/redo, and zero history entries for discarded edits.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T026 [P] [US2] Add internal `edit_text` validation, target-kind checks, history, undo/redo, and public-schema rejection tests in `tests/unit/test_edit_text.py`
- [X] T027 [P] [US2] Add double-click creation, provisional overlay, Enter/Shift-Enter/Escape/outside-click, camera-following, commit, discard, and revert widget tests in `tests/ui/test_inline_text.py`

### Implementation for User Story 2

- [X] T028 [US2] Implement provisional text sessions, heading/text editor selection, screen-rectangle positioning, commit/cancel behavior, and camera-following in `src/smartboard/ui/text_overlay.py`
- [X] T029 [US2] Implement double-click creation/editing, overlay lifecycle, focus precedence, and world-anchored commit payloads in `src/smartboard/ui/board_view.py`
- [X] T030 [US2] Implement validated internal `edit_text` with swap-inverse history while rejecting it from public command validation in `src/smartboard/core/engine.py`
- [X] T031 [US2] Route accepted UI-origin text creation and internal text edits through queue/engine ownership in `src/smartboard/app/orchestrator.py`

**Checkpoint**: User Story 2 is fully writable inline and independently testable with exact history accounting.

---

## Phase 6: User Story 3B - Voice placement and AI context (Priority: P2)

**Goal**: Voice-created elements appear in the visible viewport, relative voice moves respect zoom, and AI context remains short, viewport-aware, and capped.

**Independent Test**: Issue creation and relative-move commands at different cameras/zooms; verify explicit positions are preserved, defaults are visible, distances scale correctly, context contains viewport/selection/visible/nearby elements, and no more than 50 summaries are sent.

### Tests for User Story 3B

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T032 [P] [US3] Add deterministic visible-area placement, collision scanning, fallback, and explicit-position preservation tests in `tests/unit/test_placement.py`
- [X] T033 [P] [US3] Add voice creation placement, zoom-scaled relative moves, normalized-history replay, and viewport-context integration tests in `tests/integration/test_voice_viewport.py`
- [X] T034 [P] [US3] Add viewport shape, 50-element cap, visibility ordering, no-canvas, least-exposure, and 12-command-lock contract tests in `tests/contract/test_infinite_prompt_contract.py`

### Implementation for User Story 3B

- [X] T035 [US3] Implement deterministic visible-viewport default placement in `src/smartboard/app/placement.py`
- [X] T036 [US3] Normalize missing creation positions and zoom-relative distances before queue/history submission in `src/smartboard/app/orchestrator.py`
- [X] T037 [US3] Replace canvas context with viewport bounds, selection, visible/nearby ordering, and 50-summary cap in `src/smartboard/ai/context_builder.py`
- [X] T038 [US3] Shorten prompt wording for unbounded world coordinates and viewport preference while preserving the locked command schema in `src/smartboard/ai/prompt.py`

**Checkpoint**: Voice behavior and AI context work independently without leaking camera state into validation or history.

---

## Phase 7: User Story 3C - Persistence, migration, and export (Priority: P2)

**Goal**: Camera state saves and restores with lessons, legacy lessons migrate without coordinate changes, and exports render content bounds at 100%.

**Independent Test**: Save/reopen new snapshots; reopen legacy bare-board and legacy canvas snapshots; verify unchanged coordinates, centered legacy viewing, camera restoration, content-bounds export, and valid empty-lesson export.

### Tests for User Story 3C

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T039 [P] [US3] Add new/legacy lesson-document serialization, camera defaults, centered legacy viewing, and coordinate-preservation tests in `tests/unit/test_lesson_document.py`
- [X] T040 [P] [US3] Add camera save/restore through SQLite snapshots and reopen behavior tests in `tests/integration/test_infinite_persistence.py`
- [X] T041 [P] [US3] Add content-union bounds, fixed margin, 100% rendering, shared-paint parity, and empty-lesson export tests in `tests/integration/test_infinite_export.py`

### Implementation for User Story 3C

- [X] T042 [US3] Implement lesson-document composition, validation, restoration, legacy normalization, and camera handling in `src/smartboard/app/lesson_document.py`
- [X] T043 [US3] Implement content-bounds calculation, fixed-margin export, 100% rendering, and shared-paint reuse in `src/smartboard/app/exporter.py`
- [X] T044 [US3] Implement valid empty-lesson export and export-failure behavior without board/history mutation in `src/smartboard/app/exporter.py`

**Checkpoint**: Lessons, migration, and export work independently and preserve world coordinates exactly.

---

## Phase 8: Polish and Performance

**Purpose**: Prove the required 200-element behavior, retire contradictory legacy expectations, and enforce the release gate.

- [X] T045 [P] Add 200-element viewport-filtering, pan/zoom smoke, AI/persistence/export bounded-growth performance tests in `tests/performance/test_infinite_board_performance.py`
- [X] T046 Update or retire obsolete finite-canvas expectations in `tests/unit/test_adaptive_canvas.py`, `tests/ui/test_viewport_math.py`, `tests/ui/test_coordinate_mapping.py`, `tests/ui/test_board_scaling.py`, `tests/ui/test_adaptive_canvas_layout.py`, `tests/integration/test_canvas_persistence.py`, `tests/integration/test_canvas_voice_pen_drag.py`, and `tests/performance/test_classroom_sim.py`
- [X] T047 Run the full pytest suite plus the 95% core-coverage gate and fix regressions across `tests/` and `src/smartboard/core/`
- [X] T048 Run type checking, lint, and formatting validation and fix findings across `src/smartboard/`

---

## Dependencies and Execution Order

### Required build chain

Follow the user-requested order exactly:

1. Phase 1: Setup
2. Phase 2: Foundational camera/transform and unbounded engine work
3. Phase 3: User Story 1 navigation input and rendering
4. Phase 4: User Story 3A pen/selection/drag/resize
5. Phase 5: User Story 2 inline text creation/editing
6. Phase 6: User Story 3B voice placement/AI context
7. Phase 7: User Story 3C persistence/migration/export
8. Phase 8: Polish and performance

Do not start a later phase until its predecessor checkpoint is green, even where files differ.

### User-story dependencies

- **User Story 1 (P1)**: Depends on Phase 2; MVP increment when combined with Setup and Foundation.
- **User Story 3A (P2)**: Depends on Phase 3 because manipulation must be verified through the finished navigation/rendering behavior.
- **User Story 2 (P1)**: Depends on Phase 4 under the requested build order because overlay anchoring and world gestures must already be stable.
- **User Story 3B (P2)**: Depends on Phase 5 because normalized voice commands may create and move inline-created text.
- **User Story 3C (P2)**: Depends on Phase 6 because saved lessons must include voice-created content and restored cameras.
- **Polish/performance**: Depends on all implementation phases.

### Within each phase

- Write fail-first tests before implementation.
- Implement shared helpers before their callers.
- Complete engine/model changes before UI integration that depends on them.
- Complete each checkpoint before advancing.

### Parallel opportunities

- T003, T004, and T005 use separate test files.
- T006 and T007 create separate camera/transform modules.
- T014, T015, and T016 use separate UI/contract test files.
- T021 and T022 use separate unit/widget test files.
- T026 and T027 use separate engine/widget test files.
- T032, T033, and T034 use separate unit/integration/contract test files.
- T039, T040, and T041 use separate unit/integration test files.
- T045 can be developed alongside T046 file retirement once implementation is functionally complete, but both must be green before T047.

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 tests together:
Task: "Add camera input widget tests in tests/ui/test_camera_input.py"
Task: "Add rendering/culling/grid/handle tests in tests/ui/test_infinite_rendering.py"
Task: "Add camera contract tests in tests/contract/test_camera_transform_contract.py"
```

---

## Implementation Strategy

### MVP first

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational camera and unbounded-engine work.
3. Complete Phase 3: User Story 1 navigation.
4. **STOP and VALIDATE**: Independently test edgeless pan/zoom, limits, grid, culling, handles, fit-all, and history invariance.
5. Demo the navigable infinite board before content workflows.

### Incremental delivery

1. Foundation plus US1 delivers navigation MVP.
2. Add US3A world drawing/manipulation.
3. Add US2 inline text creation/editing.
4. Add US3B voice placement/AI context.
5. Add US3C persistence/migration/export.
6. Finish with performance/polish and release validation.
7. Each increment preserves prior checkpoints without breaking earlier stories.

---

## Notes

- `[P]` tasks use different files and have no dependencies on incomplete tasks.
- `[US1]`, `[US2]`, and `[US3]` trace tasks to specification user stories.
- US3 is intentionally implemented in three ordered increments: manipulation, voice/AI, then persistence/export.
- Verify tests fail before implementing.
- Commit after each task or logical group.
- Stop at every checkpoint and validate independently.
- Avoid vague tasks, same-file conflicts, and out-of-order phase execution.
