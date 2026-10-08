# Tasks: Resizable Window Mode

**Input**: Design documents from `/specs/002-resizable-window-mode/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: pytest-qt + headless math tests are REQUIRED by the plan (constitution V); mapping tests come FIRST per user order.
**Constraints**: `src/smartboard/core/` and `src/smartboard/persistence/` MUST NOT be modified (verified by T-task diff-guard).

**Organization**: Ordered per user instruction — mapping tests → scalable view → mode toggle → persistence → clipping/styling fixes — grouped by spec user story so each story stays independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test tooling and guardrails for the UI-layer change

- [X] T001 Install pytest-qt for py-3.11 and set `QT_QPA_PLATFORM=offscreen` for CI runs in `.github/workflows/ci.yml`
- [X] T002 [P] Create `tests/ui/` package scaffold with offscreen `qapp` fixture in `tests/ui/conftest.py`
- [X] T003 [P] Add core-untouched diff-guard (fail if `src/smartboard/core/` or `src/smartboard/persistence/` changed vs `001-smart-chalkboard-mvp`) in `tests/contract/test_002_core_untouched.py`

**Checkpoint**: `pytest tests/ui tests/contract -q` collects; 001 suite still green.

---

## Phase 2: Foundational — Coordinate Mapping Tests FIRST (Blocking Prerequisites)

**Purpose**: The single-source viewport contract proven before any widget changes. Blocks all later phases.

**⚠️ CRITICAL**: Write T004–T007 FIRST and confirm they FAIL before implementing T008.

- [X] T004 [P] [US2] Viewport math tests (uniform scale, centered offsets, letterbox rule, exact forward/inverse round-trip <0.5 units at 960×540, 1280×720, 1920×1080, portrait 800×1000) in `tests/ui/test_viewport_math.py`
- [X] T005 [P] [US2] Pen/mouse mapping tests (tap-to-canvas at three sizes selects exactly the intended element; mid-stroke viewport swap commits matching coordinates) in `tests/ui/test_coordinate_mapping.py`
- [X] T006 [P] [US1] Mode-switch tests (F11/button × 4 toggles, board state + selection byte-identical each time) in `tests/ui/test_mode_switching.py`
- [X] T007 [P] [US4] Resize-during-activity tests (resize mid-command, mid-stroke, open dialog → no lost input, dialog centered, outcome applied once) in `tests/ui/test_resize_safety.py`
- [X] T008 Implement pure viewport module per `contracts/viewport-contract.md` in `src/smartboard/ui/viewport.py` (only AFTER T004–T005 fail)

**Checkpoint**: T004–T007 fail pre-implementation (test-first evidence), then go green with T008.

---

## Phase 3: User Story 2 - Scalable Board View (Priority: P1) 🎯 MVP

**Goal**: Board view scales the fixed 1920×1080 canvas with the shared viewport; saves/exports identical at any size.

**Independent Test**: Resize through 960×540 → 1280×720 → fullscreen; content undistorted/centered; save/export byte-identical across sizes.

- [X] T009 [P] [US2] Viewport-driven paint tests (letterbox margins, aspect preservation every ratio, 200-element repaint within one frame) in `tests/ui/test_board_scaling.py`
- [X] T010 [P] [US2] Size-independence tests (save snapshot + export at three window sizes → identical bytes) in `tests/ui/test_size_independence.py`
- [X] T011 [US2] Rewire `src/smartboard/ui/board_view.py` to `Viewport` (replace local scale math; paint via forward map; pen/mouse/selection via inverse map; letterbox in background tone)
- [X] T012 [US2] Add viewport-swap-safe stroke commit path in `src/smartboard/ui/pen_input.py` (samples map through live viewport; commit stores canvas coords)

**Checkpoint**: Story 2 acceptance scenarios pass; paint and hit-test share one formula.

---

## Phase 4: User Story 1 - Window Mode Toggle (Priority: P1)

**Goal**: Fullscreen ↔ window at any time via button + F11 with zero content change.

**Independent Test**: 4 alternating toggles with content on board; state comparison identical each time.

- [X] T013 [US1] Implement mode machine in `src/smartboard/ui/main_window.py` (showNormal/showMaximized/showFullScreen, toggle button, F11 shortcut, 960×540 minimum, dialogs recenter on move/resize)
- [X] T014 [US1] Wire toggle into `src/smartboard/app/main.py` (startup per restored preference; Esc keeps existing behavior)

**Checkpoint**: US1 acceptance scenarios pass; toggle works mid-lesson and mid-dialog.

---

## Phase 5: Window Geometry Persistence (supports US1 P1)

**Goal**: Reopen in closing mode, size, and position; fresh install starts fullscreen.

**Independent Test**: 10 alternating fullscreen/windowed closes reopen correctly with geometry restored.

- [X] T015 [P] Geometry persistence tests (save-on-close, restore-before-first-paint, corrupt/missing → fullscreen default, never touches lesson data) in `tests/ui/test_window_persistence.py`
- [X] T016 Implement `src/smartboard/ui/window_state.py` (settings keys `window/mode`, `window/geometry` per `contracts/window-state-contract.md`) and hook save/restore in `src/smartboard/app/main.py`

**Checkpoint**: SC-007 trials pass; lesson files untouched by geometry changes.

---

## Phase 6: User Story 3 - Clipping and Styling Fixes (Priority: P1)

**Goal**: Unclipped wrapped text and readable high-contrast controls at every size.

**Independent Test**: At 960×540 every label readable, 48px targets, no chrome/board overlap, full heading visible.

- [X] T017 [P] [US3] Text-fit tests (wrap inside fixed box; over-long creation rejected with exact message; post-resize shortfall clips at edge; coordinates unchanged) in `tests/ui/test_text_fit.py`
- [X] T018 [P] [US3] Contrast + chrome tests (luminance ≥4.5:1 on declared hexes; all targets ≥48px; no overlap at 960×540) in `tests/ui/test_chrome_contrast.py`
- [X] T019 [US3] Implement creation-time fit gate in `src/smartboard/app/text_fit.py` (font-metrics check, exact rejection message) and wire before queueing in `src/smartboard/app/main.py`
- [X] T020 [US3] Fix `src/smartboard/ui/board_view.py` text paint (word-wrap inside element rect; edge-clip only on post-resize shortfall)
- [X] T021 [US3] Fix stylesheets in `src/smartboard/ui/main_window.py` (explicit text + background colors meeting `contracts/chrome-layout-contract.md` palette; 48px minima; layout order strip → board → bar)

**Checkpoint**: US3 acceptance scenarios + SC-004/SC-005 pass.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Regression, docs, and headed verification

- [X] T022 Run full suite (`tests/` incl. 001 regression + new `tests/ui/`) green with no `core/`/`persistence/` diff in `tests/contract/test_002_core_untouched.py`
- [X] T023 [P] Update manual headed checklist results in `specs/002-resizable-window-mode/quickstart.md` (real display, fonts, pen at three sizes)
- [X] T024 [P] Offscreen review screenshot (Newton board at 1280×720 windowed) saved for visual confirmation in `specs/002-resizable-window-mode/review-002.png`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all story phases; T004–T007 MUST fail before T008
- **Scalable View (Phase 3, US2)**: Depends on Foundational — viewport proven first
- **Mode Toggle (Phase 4, US1)**: Depends on Phase 3 (toggles a correctly scaling view)
- **Persistence (Phase 5, US1)**: Depends on Phase 4 (persists the toggled states)
- **Clipping/Styling (Phase 6, US3)**: Depends on Phase 3 (paints into the scaled view); needs T019 gate before T020 paint
- **Polish (Phase 7)**: Depends on all prior phases

### User Story Dependencies

- **US2 (P1)**: After Foundational — no dependencies on other stories
- **US1 (P1)**: Depends on US2 view work (toggle needs something correct to toggle)
- **US3 (P1)**: Depends on US2 view work; independent of US1 toggle mechanics
- **US4 (P2)**: Covered by Foundational T007 tests + Phase 3–4 implementation; verified in Polish

### Within Each Phase

- Tests FIRST, confirm FAIL, then implement (T004–T007 → T008; T009–T010 → T011–T012; T015 → T016; T017–T018 → T019–T021)
- `core/` + `persistence/` never modified — T003/T022 enforce

### Parallel Opportunities

- All [P] tests within a phase run in parallel (different files)
- T001–T003 mutually parallel; T004–T007 mutually parallel; T009–T010, T015, T017–T018 parallel-safe
- Phase 6 test-writing can start once Phase 2 viewport math is frozen

---

## Implementation Strategy

### MVP First (US2 scalable view)

1. Complete Phase 1 (Setup) + Phase 2 (mapping tests-first + Viewport)
2. Complete Phase 3 (scalable view + size-independence)
3. **STOP and VALIDATE**: resize across sizes with identical saves/exports

### Incremental Delivery

1. Setup + Foundational → viewport contract proven
2. + Scalable view → correct at every size (MVP core!)
3. + Mode toggle → F11/button switching
4. + Persistence → reopen where you left off
5. + Clipping/styling → readable everywhere
6. + Polish → full suite green, headed checklist signed

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to spec user story for traceability (US1–US4)
- Engine rule: `core/` + `persistence/` importable and UNCHANGED — enforced by T003 and T022
- Verify mapping tests fail before implementing (T004–T007 red → T008 green)
- Commit after each task or logical group; stop at any checkpoint to validate independently
- Avoid: duplicated scale math outside `viewport.py`, new AI commands, canvas-size changes, zoom/pan
