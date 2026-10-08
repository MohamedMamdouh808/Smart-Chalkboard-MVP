# Tasks: Manual Drawing

**Input**: Design documents from `/specs/008-manual-drawing/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: The 12-case matrix is REQUIRED by the plan (constitution V); written LAST per user order, plus a mixed heading/drawing/voice scenario.
**Constraints**: Engine stays UI-free (plain point data); no 13th AI command; Select default; 1.5 s grouping; 6-unit hit tolerance; no bar width control.

**Organization**: Ordered per user instruction — model → engine op → input + toggle → rendering → grouping → persistence → tests — grouped by spec user story so each story stays independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the seams the feature plugs into before changing them

- [X] T001 Verify engine extension points, viewport mapping, and snapshot path (read-only): `src/smartboard/core/engine.py`, `src/smartboard/ui/viewport.py`, `src/smartboard/persistence/lesson_repo.py`

**Checkpoint**: Extension points confirmed; no code changed.

---

## Phase 2: Foundational — Drawing Model (Blocking Prerequisites)

**Purpose**: The element every later phase operates on. BLOCKS all story phases.

- [X] T002 [US1] Implement the Drawing element shape in `src/smartboard/core/board.py` (id, strokes with points/width/color, bbox derived from points) with translate, scale-about-bbox-origin, and recolor helpers
- [X] T003 [US2] Implement 6-unit segment hit-testing in `src/smartboard/core/hit_test.py` (point-to-segment distance, z-order ties, bbox fast path)

**Checkpoint**: Drawings transform and pick correctly headless, independent of any UI.

---

## Phase 3: User Story 1 — AddDrawing Engine Op (Priority: P1)

**Goal**: Internal commit with snapshot inverse; undo removes, redo restores identically.

**Independent Test**: Commit → undo → redo round-trips byte-identical points without any UI (verified in Phase 8).

- [X] T004 [US1] Implement the internal `AddDrawing` engine operation with snapshot inverse in `src/smartboard/core/engine.py` (plain point data in; existing validators, history, and queue reused; never AI-addressable)

**Checkpoint**: Drawings commit, undo, and redo through the engine headless.

---

## Phase 4: User Stories 1–2 — Pointer Input + Toggle (Priority: P1)

**Goal**: One-pointer unified input with viewport mapping; Pen/Select toggle defaulting to Select.

**Independent Test**: Synthetic mouse/tablet events yield canvas-space points; toggle + shortcuts switch modes (verified in Phase 8).

- [X] T005 [US1] Implement unified pointer collection in `src/smartboard/ui/board_view.py` (`QTabletEvent` position/pressure, mouse press/move/release, touch; one active pointer; per-sample `to_canvas`; outside-start ignored, outside points clipped; `StrokeFinished` signal with canvas points)
- [X] T006 [US2] Implement the Pen/Select toggle in `src/smartboard/ui/main_window.py` (visible toggle button + P/S shortcuts, Select default, mode-gated board events)

**Checkpoint**: Strokes arrive as canvas data in Pen mode; clicks select in Select mode.

---

## Phase 5: Rendering — Live Overlay + Committed Paint (serves US1–US2)

**Goal**: Live ink on the overlay; committed drawings in z-order with pressure widths.

**Independent Test**: Overlay clears on commit; committed paths match points with round caps (verified in Phase 8).

- [X] T007 Implement overlay painting and committed `QPainterPath` rendering (round caps/joins, pressure-scaled width else element width 2/4/8) in `src/smartboard/ui/board_view.py`

**Checkpoint**: Live and committed ink both render correctly without touching state.

---

## Phase 6: Grouping + Persistence (serves US1, US5)

**Goal**: 1.5 s groups become one element; saves round-trip byte-identically.

**Independent Test**: Timing and round-trip cases (verified in Phase 8).

- [X] T008 [US1] Implement grouping + ~2-unit point reduction and the app commit call in `src/smartboard/ui/pen_input.py` and `src/smartboard/app/orchestrator.py` (1.5 s rule, endpoints kept, queued behind voice work, autosave on commit)
- [X] T009 [P] [US5] Verify JSON serialization needs no migration and add the round-trip case to `tests/integration/test_drawing_engine.py` (structure shared with Phase 8)

**Checkpoint**: Groups commit whole; lessons reopen identically.

---

## Phase 7: Verification — 12-Case Matrix + Mixed Scenario (Final)

**Purpose**: The requested tests LAST, including heading + drawing + voice moves/resizes

- [X] T010 Create input tests in `tests/ui/test_drawing_input.py` (cases 1–4, 7–8, 10–11: synthetic mouse/tablet, 3-size mapping, grouping timing, off-canvas, resize mid-stroke, single-pointer, proximity select)
- [X] T011 [P] Create engine tests in `tests/integration/test_drawing_engine.py` (cases 5–6, 9, 12: undo/redo round-trip, voice move/resize/recolor/confirmed-delete + undo, save/reopen identity, offline commit)
- [X] T012 Create the mixed scenario in `tests/e2e/test_drawing_voice_mix.py` (typed heading → pen drawing → voice move → voice resize → undo chain, all identities and points verified)
- [X] T013 Run the matrix plus the FULL suite green and record headed-check outcomes in `specs/008-manual-drawing/quickstart.md`

**Checkpoint**: All acceptance scenarios verified; no behavior regressions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — read-only verification
- **Model (Phase 2)**: Depends on Setup — BLOCKS all story phases (everything operates on it)
- **Engine op (Phase 3, US1)**: Depends on Phase 2 (commits model elements)
- **Input + toggle (Phase 4, US1–US2)**: Depends on Phases 2–3 (samples map to model; commits flow to the op)
- **Rendering (Phase 5)**: Depends on Phases 2–4 (paints model + live state)
- **Grouping + persistence (Phase 6)**: Depends on Phases 2–5
- **Verification (Phase 7)**: Depends on all implementation phases

### User Story Dependencies

- **US1 (P1)**: After Model — input, op, grouping, paint; no dependencies on other stories
- **US2 (P1)**: After Model + op — toggle and hit-test ride the same element
- **US3 (P1)**: After US1–US2 path exists (voice commands address committed drawings)
- **US4–US5 (P2)**: After US1 path exists (offline/queue/resize + save ride it)

### Within Each Phase

- Model before op (T002–T003 → T004); op before input (T004 → T005–T006)
- One writer at a time for `board_view.py` (T005 → T007 strictly sequential)
- Tests last: T010–T012 written after all implementation, then T013 full run

### Parallel Opportunities

- T009 round-trip case can draft alongside T008 (shared file — coordinate, or sequence it)
- T010 and T011 run in parallel (different files, implementation complete)
- All other tasks are sequential (model → op → input chain, shared `board_view.py`)

---

## Implementation Strategy

### MVP First (model + op + input)

1. Complete Phases 1–2 (verify + Drawing model with transforms + hit-test)
2. Complete Phases 3–4 (engine op + pointer input + toggle)
3. **STOP and VALIDATE**: draw → grouped element → undo, all headless-testable

### Incremental Delivery

1. Verify + model → transforms and picking proven
2. + Engine op → commit/undo/redo proven
3. + Input + toggle → live strokes in Pen mode (MVP core!)
4. + Rendering → overlay + committed paint
5. + Grouping + persistence → whole sketches, exact reopen
6. + Verification → 12-case matrix + mixed scenario green, full suite green

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to spec user story for traceability (US1–US5)
- Model rule: bbox derived from points; translate/scale/recolor are pure point operations
- Engine rule: `AddDrawing` is internal-only (never in the 12-command schema); snapshot inverse; queue + history reused
- Commit after each task or logical group; stop at any checkpoint to validate independently
- Avoid: multi-pointer, 13th commands, bar width controls, mapping changes, behavior changes of any kind
