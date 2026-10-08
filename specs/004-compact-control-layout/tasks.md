# Tasks: Compact Control Layout

**Input**: Design documents from `/specs/004-compact-control-layout/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Layout/elision tests are REQUIRED by the plan and run LAST per user order (Phase 6), after all implementation.
**Constraints**: `core/`, `persistence/`, `app/` logic, board rendering, colors, fonts, icons UNCHANGED; sizes from theme only.

**Organization**: Execution follows the requested order — theme tokens → bottom bar → Window move → transcript eliding → layout tests — grouped by spec user story so each story stays independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Record the pre-change baseline the board-gain test compares against

- [X] T001 Measure pre-change board-view heights at 960x540, 1366x768 and 1920x1080 and record them in `specs/004-compact-control-layout/baselines.md`

**Checkpoint**: Baseline heights recorded; implementation has a comparison target.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Central size tokens everything else reads. BLOCKS all story phases.

- [X] T002 Retune size tokens in `src/smartboard/ui/theme.py` (MIC_DIAMETER 64, new COMPACT_CONTROL_H 44, new PILL_H 36; colors, fonts, radii, spacing unchanged)

**Checkpoint**: Tokens updated; no widget or behavior changes yet.

---

## Phase 3: User Story 1 - Compact bottom-left controls (Priority: P1)

**Goal**: Mic, Undo, Redo grouped compactly bottom-left in that order with 44px minima.

**Independent Test**: Order/sizes/targets measured at three window sizes; pen/mouse/keyboard operation of each control (verified in Phase 6).

- [X] T003 [US1] Size the mic from the theme token in `src/smartboard/ui/mic_button.py` (fixed 64px circle, keep icons, ring, pulse, and state appearances)
- [X] T004 [US1] Rebuild the bottom bar in `src/smartboard/ui/main_window.py` as left group (mic, Undo, Redo) + stretch spacer + right-anchored pill; Undo/Redo 44px high from theme; no equal-width stretching

**Checkpoint**: Bottom bar compact with empty middle; pill still functional at right.

---

## Phase 4: User Story 2 - Window toggle beside the result chip (Priority: P1)

**Goal**: Compact Window control top-right after the chip with tooltip/accessible name and F11 intact.

**Independent Test**: Location/tooltip/name read at three sizes; toggle via control and F11 with unchanged content (verified in Phase 6).

- [X] T005 [US2] Move the Window toggle in `src/smartboard/ui/main_window.py` to the top strip immediately after the result chip as a 44px icon-only button with tooltip and accessibleName "Window"; keep the F11 binding and toggle behavior

**Checkpoint**: No Window control remains in the bottom bar; F11 works in both modes.

---

## Phase 5: User Story 3 - Compact status pill and larger board (Priority: P1)

**Goal**: 36px pill fitting its text at bottom right; taller board view with identical canvas mapping.

**Independent Test**: Pill height/contents measured in all five states; board height exceeds the Phase 1 baseline at the same window size (verified in Phase 6).

- [X] T006 [US3] Apply the compact pill height from the theme in `src/smartboard/ui/status_pill.py` (36px high, width fitting text; keep dot, icon, and text for all five states)

**Checkpoint**: Pill compact; bar shorter; board view absorbs the freed height.

---

## Phase 6: User Story 4 - Readable long transcripts (Priority: P2)

**Goal**: Word-boundary ellipsis with full-text tooltip; chip and Window button always visible.

**Independent Test**: Overlong transcript at 960x540 shortens at a word boundary with tooltip; chip/Window fully visible (verified in Phase 7).

- [X] T007 [US4] Implement transcript elision in `src/smartboard/ui/main_window.py` (word-boundary ellipsis plus "...", full text in tooltip, recompute on strip resize; transcript yields space, chip and Window button never do)

**Checkpoint**: No mid-word truncation at any supported size.

---

## Phase 7: Layout Verification & Polish (Final)

**Purpose**: The requested layout tests LAST, then full regression and docs

- [X] T008 Create layout tests in `tests/ui/test_compact_layout.py` (US1-US3: left-group order, mic 64px, Undo/Redo 44px, pill 36px right-anchored, pairwise widget disjointness, chip + Window fully in strip, board height above Phase 1 baseline — at 960x540, 1366x768, 1920x1080)
- [X] T009 [P] Create elision tests in `tests/ui/test_transcript_elision.py` (US4: word-boundary "...", full tooltip, chip + Window visible at 960x540)
- [X] T010 Run the new layout tests plus the FULL suite green and record headed-check outcomes in `specs/004-compact-control-layout/quickstart.md`

**Checkpoint**: All acceptance scenarios verified; no behavior regressions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all story phases (tokens first)
- **US1 bottom bar (Phase 3)**: Depends on Foundational
- **US2 Window move (Phase 4)**: Depends on Phase 3 (same file `main_window.py`; bar must exist first)
- **US3 pill (Phase 5)**: Depends on Phases 3–4 (pill lives in the rebuilt bar)
- **US4 eliding (Phase 6)**: Depends on Phases 3–4 (strip holds chip + Window button)
- **Verification (Phase 7)**: Depends on all implementation phases

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependencies on other stories
- **US2 (P1)**: Depends on US1 bar work (moves a control out of it)
- **US3 (P1)**: Depends on US1 bar work (pill anchors in it); independent of US2 mechanics
- **US4 (P2)**: Depends on US1/US2 strip-bar work (elision shares the strip with chip + Window)

### Within Each Phase

- Tokens before widgets (T002 → T003–T007)
- One writer at a time for `main_window.py` (T004 → T005 → T007 strictly sequential)
- Tests last: T008–T009 written after all implementation, then T010 full run

### Parallel Opportunities

- T008 and T009 run in parallel (different test files, implementation complete)
- T001 (baseline docs) and T002 (theme tokens) can overlap (different files, no dependency)
- All other tasks are sequential (shared `main_window.py` or token dependencies)

---

## Implementation Strategy

### MVP First (US1 compact bar)

1. Complete Phase 1 (baseline) + Phase 2 (tokens)
2. Complete Phase 3 (compact bottom bar)
3. **STOP and VALIDATE**: order/sizes/targets correct, states preserved

### Incremental Delivery

1. Baseline + tokens → sizes centralized
2. + Bottom bar → compact left group, empty middle (MVP core!)
3. + Window move → shorter bar, chip-adjacent toggle
4. + Compact pill → 36px status, taller board
5. + Eliding → readable long transcripts
6. + Verification → layout tests green, full suite green, headed sign-off

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to spec user story for traceability (US1–US4)
- Layout rule: no size/color/font literals outside `ui/theme.py`
- Behavior rule: `core/` + `persistence/` + `app/` logic, board rendering, colors, fonts, icons never modified
- Commit after each task or logical group; stop at any checkpoint to validate independently
- Avoid: equal-width stretching, mid-word truncation, new features/colors, behavior changes of any kind
