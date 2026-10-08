# Tasks: Tooltip Theme Styling

**Input**: Design documents from `/specs/011-tooltip-theme-styling/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Requested in the follow-up technical direction: generated-stylesheet assertions, proxy-style delay assertions, explicit tooltip contrast coverage, transcript-text preservation, and full regression coverage.
**Constraints**: Central-theme values only; dark non-white background; light text at least 16px; WCAG AA contrast; thin theme border; rounded corners; 6px vertical and 10px horizontal padding; 500ms delay; unchanged tooltip text; no new tooltips or features.
**Organization**: User-requested build order — tooltip tokens and QSS rule → application-level stylesheet and delay → contrast and stylesheet tests — grouped by user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the active feature workspace and pre-change verification baseline

- [X] T001 [P] Verify that the active branch is `011-tooltip-theme-styling` and that `.specify/feature.json` points to `specs/011-tooltip-theme-styling`
- [X] T002 [P] Record the pre-change baseline by running the full suite in `tests/` and the applicable coverage gates, without changing source or tests

**Checkpoint**: Workspace and baseline are known before any 011 edits.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Inventory existing tooltip text and styling behavior before changing shared theme code

**⚠️ CRITICAL**: No user-story work can begin until this phase is complete

- [X] T003 Inventory every existing tooltip text, current `QToolTip` stylesheet behavior, application stylesheet installation, and tooltip-related tests in `src/smartboard/ui/theme.py`, `src/smartboard/ui/main_window.py`, `src/smartboard/app/main.py`, `tests/ui/test_theme_tokens.py`, and `tests/ui/test_transcript_elision.py` without changing behavior

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Read every tooltip comfortably (Priority: P1) 🎯 MVP

**Goal**: Provide one central dark tooltip rule with readable text, border, corners, and padding

**Independent Test**: Inspect the generated stylesheet and rendered tooltips for background, text size and contrast, border, corners, padding, and unchanged text.

- [X] T004 [US1] Add tooltip padding and delay tokens and generate the central `QToolTip` rule from background, foreground, font-size, border, radius, and padding tokens in `src/smartboard/ui/theme.py`

**Checkpoint**: At this point, User Story 1 styling should be available for verification.

---

## Phase 4: User Story 2 - Avoid disruptive tooltip timing and placement (Priority: P1)

**Goal**: Apply application-level styling and native 500ms tooltip timing without custom hover behavior

**Independent Test**: Verify that separate tooltip windows receive the central rule, tooltips observe the required delay, native dismissal/placement remains unchanged, and transcript text remains complete.

- [X] T005 [US2] Implement the narrow tooltip-delay proxy style in `src/smartboard/ui/tooltip_style.py`, returning 500ms only for tooltip wake-up delay and delegating all other style behavior
- [X] T006 [US2] Install the proxy style once during startup while retaining application-level stylesheet application in `src/smartboard/app/main.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Keep one consistent tooltip theme (Priority: P2)

**Goal**: Prove that every tooltip uses central theme values and preserves existing text

**Independent Test**: Compare generated styling, delay behavior, contrast, and tooltip text against central theme values and existing transcript coverage.

- [X] T007 [US3] Verify central-theme sourcing and unchanged text by extending token and transcript coverage in `tests/ui/test_theme_tokens.py` and `tests/ui/test_transcript_elision.py`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Stylesheet, delay, contrast, and final verification

**Purpose**: Add the requested focused tests and retain full regression safety

- [X] T008 Add generated-stylesheet and proxy-style delay tests to `tests/ui/test_tooltip_theme.py`, asserting the `QToolTip` rule, token colors, preserved tooltip text, and 500ms delay behavior
- [X] T009 Add the explicit tooltip text/background contrast test to `tests/ui/test_theme_contrast.py`, then run the complete regression suite in `tests/` with applicable coverage gates and execute `specs/011-tooltip-theme-styling/quickstart.md`

**Checkpoint**: The feature is complete, tested, documented, and regression-free.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - BLOCKS application/delay work
- **User Story 2 (Phase 4)**: Depends on User Story 1 central rule
- **User Story 3 (Phase 5)**: Depends on User Stories 1-2
- **Final verification (Phase 6)**: Depends on all implementation and consistency behavior

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Requires User Story 1 central rule - independently testable after Phase 3
- **User Story 3 (P2)**: Requires User Stories 1-2 - independently testable after Phase 4

### Within Each User Story

- Theme tokens before stylesheet rule
- Stylesheet rule before application styling
- Application styling before delay installation
- Implementation before focused tests, per the requested build order
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run in parallel
- All other tasks are sequential because they share theme/UI/startup files, extend prior behavior, or validate prior work

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
5. Add focused verification → Full regression green
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
- Verify focused tests after implementation, per the requested build order
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, widget-level tooltip styling, custom hover timers, tooltip-text changes, new tooltips, and unrelated features
