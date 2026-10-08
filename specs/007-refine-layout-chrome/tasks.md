# Tasks: Refine Layout Chrome

**Input**: Design documents from `/specs/007-refine-layout-chrome/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Layout tests REQUIRED by the plan run LAST per user order; full suite closes.
**Constraints**: Additive tokens only; QLineEdit visuals exclusively from QSS; mapping byte-identical; no behavior changes.

**Organization**: Ordered per user instruction — tokens → input style/stretch → top bar → board/margins → tests — grouped by spec user story so each story stays independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the starting geometry before refinement

- [X] T001 Record current strip height, bar height, board heights, and input width cap at 1366×768 in `specs/007-refine-layout-chrome/baselines.md` (read-only; no code changes)

**Checkpoint**: Refinement targets have a measured baseline.

---

## Phase 2: Foundational — Theme Tokens (Blocking Prerequisites)

**Purpose**: Additive size tokens + QLineEdit QSS block. BLOCKS all story phases.

- [X] T002 Add tokens (`STRIP_H`, `FONT_STRIP`, `CHIP_H`, `BOARD_MARGIN`, `BAR_PAD_V`), the `QLineEdit` stylesheet block, and the input text/background contrast pair in `src/smartboard/ui/theme.py` (existing values untouched)

**Checkpoint**: Tokens render in QSS; contrast gate still green.

---

## Phase 3: User Story 1 - Dev Input Full-Bleed (Priority: P1)

**Goal**: Uncapped stretched input with themed dark styling and always-visible text/cursor.

**Independent Test**: Gap fill, 44px height, 8px gaps, dark styling, focus outline, submit-clears (verified in Phase 6).

- [X] T003 [US1] Uncap and stretch the dev input in `src/smartboard/ui/main_window.py` (remove `setMaximumWidth`, keep stretch + centering, 44px height, 8px gaps to neighbors, placeholder kept)
- [X] T004 [US1] Move input visuals into the theme in `src/smartboard/ui/main_window.py` (drop inline input visuals; rely on the QSS block + placeholder string only)

**Checkpoint**: Input fills the gap with zero white styling; behavior identical.

---

## Phase 4: User Story 2 - Slim Top Bar (Priority: P1)

**Goal**: 44px strip, smaller centered transcript text, compact right-anchored chip + Window.

**Independent Test**: Heights, centering, ellipsis, chip anchoring at three sizes (verified in Phase 6).

- [X] T005 [US2] Compact the top strip in `src/smartboard/ui/main_window.py` (44px height, 18px Heard/transcript vertically centered, elision + tooltip kept, 34px chip + Window button right-anchored)

**Checkpoint**: Strip slimmer; transcript keeps the freed room.

---

## Phase 5: User Story 3 - Maximized Board (Priority: P1)

**Goal**: Full-width (≤8px margins), full-height canvas area under the identical mapping.

**Independent Test**: Margins, board height gain, mapping accuracy unchanged (verified in Phase 6).

- [X] T006 [US3] Apply token margins and slim bar padding in `src/smartboard/ui/main_window.py` (≤8px side margins, slim vertical chrome padding; viewport/paint code untouched)

**Checkpoint**: Board strictly larger at the same window size; mapping identical.

---

## Phase 6: Verification — Layout Tests + Regression (Final)

**Purpose**: The requested tests LAST: fill, contrast, width-rule, then the full suite

- [X] T007 Create layout tests in `tests/ui/test_chrome_refine.py` (input gap fill both sides, input-text contrast ≥4.5:1, aspect-conditional board-width rule, disjointness at 960×540/1366×768/1920×1080)
- [X] T008 Run the new tests plus the FULL suite green, regenerate refs only if visuals intentionally moved, and record headed-check outcomes in `specs/007-refine-layout-chrome/quickstart.md`

**Checkpoint**: All acceptance scenarios verified; no behavior regressions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — read-only baseline
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all story phases (tokens first)
- **Input (Phase 3, US1)**: Depends on Foundational (styles the new tokens)
- **Top bar (Phase 4, US2)**: Depends on Foundational (independent of US1 paint)
- **Board (Phase 5, US3)**: Depends on Phases 3–4 (measures the freed room)
- **Verification (Phase 6)**: Depends on all implementation phases

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependencies on other stories
- **US2 (P1)**: After Foundational — independent of US1 input work
- **US3 (P1)**: After US1–US2 chrome work (board gains their room)
- **US4 (edge coverage)**: Covered by the same move + Phase 6 geometry tests

### Within Each Phase

- Tokens before widgets (T002 → T003–T006)
- One writer at a time for `main_window.py` (T003 → T004 → T005 → T006 strictly sequential)
- Tests last: T007 written after all implementation, then T008 full run

### Parallel Opportunities

- None — every task touches `theme.py`, `main_window.py`, or tests observing them. Strictly sequential.

---

## Implementation Strategy

### MVP First (tokens + input)

1. Complete Phases 1–2 (baseline + tokens/QSS block)
2. Complete Phase 3 (full-bleed themed input)
3. **STOP and VALIDATE**: gap fill, dark styling, submit-clears

### Incremental Delivery

1. Baseline + tokens → sizes centralized, QSS extended
2. + Input restyle → full-gap dark input (MVP core!)
3. + Slim strip → 44px bar, compact chip/Window
4. + Board margins → largest canvas yet
5. + Verification → geometry tests green, full suite green, headed sign-off

---

## Notes

- No [Story]-less test split is needed: verification maps per story (T007 covers US1–US3).
- Layout rule: no size/color/font literals outside `ui/theme.py`.
- Behavior rule: mapping, submit flow, flag gating, and bar/strip order byte-identical in effect.
- Commit after each task; stop at any checkpoint to validate independently.
- Avoid: token value edits (additive only), inline input visuals, mapping changes, behavior changes of any kind
