# Tasks: Dev Input Bottom Bar

**Input**: Design documents from `/specs/006-dev-input-bottom-bar/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Layout tests REQUIRED by the plan run LAST per user order; full suite closes.
**Constraints**: Same widget moved (not rebuilt); flag semantics identical; theme-only sizes; board geometry identical on/off.

**Organization**: Ordered per user instruction — move widget → theme sizing + disabled state → layout tests — grouped by spec user story so each story stays independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the starting point before the move

- [X] T001 Verify the current dev input lives in the top strip with flag gating and submit-and-clear wiring intact in `src/smartboard/ui/main_window.py` (read-only; no changes)

**Checkpoint**: Move prerequisites confirmed (widget, flag, wiring all present).

---

## Phase 2: User Story 1 - Move the Widget (Priority: P1)

**Goal**: Same input, new home: bottom-bar middle with stretch, 700px cap, centered.

**Independent Test**: Flag on shows the working input between Redo and the pill; flag off shows the exact current bar (verified in Phase 5).

- [X] T002 [US1] Move `dev_input` in `src/smartboard/ui/main_window.py` from the top-strip layout to the bottom-bar `QHBoxLayout` between Redo and the status pill with `stretch=1`, `setMaximumWidth(700)`, keeping flag check, placeholder, tooltip, and submit-and-clear wiring byte-identical

**Checkpoint**: Input submits and clears from its new home; top strip has no input.

---

## Phase 3: User Stories 1–2 - Theme Sizing + Disabled State (Priority: P1)

**Goal**: 44px themed input with focus outline and processing-disabled behavior.

**Independent Test**: Height/font/focus match theme; input disables on submit and re-enables on delivery (verified in Phase 5).

- [X] T003 [US1] Apply theme sizing to the moved input in `src/smartboard/ui/main_window.py` (44px height, ≥18px font, placeholder, visible focus outline from theme tokens; no hard-coded sizes)
- [X] T004 [US2] Wire the processing-disabled state in `src/smartboard/app/main.py` (`setEnabled(False)` on submit, re-enable on result delivery reusing the button-disabled visual language)

**Checkpoint**: Input looks themed and behaves busy-aware; no AI-flow changes.

---

## Phase 4: Verification — Layout Tests + Regression (Final)

**Purpose**: The requested tests LAST: geometry, gating, behavior, then the full suite

- [X] T005 Create layout tests in `tests/ui/test_dev_input_bar.py` (flag on/off visibility, bar order, ≤700px width, pairwise disjointness at 960×540/1366×768/1920×1080, board-height identity on/off, submit-clears, disabled-while-processing)
- [X] T006 Run the new tests plus the FULL suite green and record headed-check outcomes in `specs/006-dev-input-bottom-bar/quickstart.md`

**Checkpoint**: All acceptance scenarios verified; no behavior regressions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — read-only verification
- **Move (Phase 2, US1)**: Depends on Setup — BLOCKS sizing/tests (nothing to size or test before it moves)
- **Sizing + disabled (Phase 3, US1–US2)**: Depends on Phase 2 (styles the moved widget; wires the live path)
- **Verification (Phase 4)**: Depends on all implementation phases

### User Story Dependencies

- **US1 (P1)**: After Setup — move first, then size; no dependencies on other stories
- **US2 (P1)**: After US1 move (flag-off identity and disabled state need the widget placed)
- **US3 (P2)**: Covered by the same move + Phase 4 geometry tests; no separate implementation

### Within Each Phase

- Move before style (T002 → T003); style before verification (T003–T004 → T005–T006)
- `main.py` edits sequential (T004 wiring follows the T002 move)

### Parallel Opportunities

- None — every task touches `main_window.py`, its wiring, or tests observing them. Strictly sequential.

---

## Implementation Strategy

### MVP First (move only)

1. Complete Phases 1–2 (verify + move with existing sizing)
2. **STOP and VALIDATE**: input works from the bar middle, flag off identical

### Incremental Delivery

1. Verify + move → same widget, new home
2. + Theme sizing → 44px themed input
3. + Disabled state → busy-aware, no flow changes
4. + Verification → geometry tests green, full suite green, headed sign-off

---

## Notes

- No [Story]-less test phase split is needed: verification maps per story (T005 covers US1–US3).
- Layout rule: no size/font literals outside `ui/theme.py`.
- Behavior rule: submit/clear/tooltip/flag semantics byte-identical; board geometry identical on/off.
- Commit after each task; stop at any checkpoint to validate independently.
- Avoid: rebuilt widgets, new flags, AI-flow edits, mic changes, behavior changes of any kind
