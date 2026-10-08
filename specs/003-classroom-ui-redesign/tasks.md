# Tasks: Classroom UI Redesign

**Input**: Design documents from `/specs/003-classroom-ui-redesign/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: Theme/widget/regression/contrast tests are REQUIRED by the plan (constitution V); no-regression gate over the full pre-redesign suite.
**Constraints**: `core/`, `persistence/`, and `app/` logic MUST NOT change behavior (verified by diff-guard + full suite).

**Organization**: Ordered per user instruction — theme + contrast → board surface → control bar + mic → strip + chip → dialogs — grouped by spec user story so each story stays independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Icon assets, regression refs directory, behavior-change guardrails

- [X] T001 Vendor bundled SVG icon set (mic, undo, redo, window, check, alert, question, error, state dots) in `src/smartboard/ui/icons/` per `contracts/icons-contract.md`
- [X] T002 [P] Create `tests/ui/refs/` directory with `.gitkeep` and `--regen-refs` run convention documented in `tests/ui/test_regression.py` header
- [X] T003 [P] Extend behavior guard: fail if `core/`, `persistence/`, or `app/` logic changed vs `002-resizable-window-mode` (SVG/theme/widget-only diffs allowed) in `tests/contract/test_003_behavior_untouched.py`

**Checkpoint**: `pytest tests/contract -q` green; icons load without errors.

---

## Phase 2: Foundational — Theme Module + Contrast Test FIRST (Blocking Prerequisites)

**Purpose**: The single visual authority everything else builds on. Blocks all story phases.

**⚠️ CRITICAL**: Write T004–T005 FIRST and confirm they FAIL before implementing T006.

- [X] T004 Theme contract tests (every token present, `build_stylesheet()` contains all widget selectors, no visual literals outside `theme.py`) in `tests/ui/test_theme_tokens.py`
- [X] T005 [P] WCAG luminance tests (every `CONTRAST_PAIRS` entry ≥4.5:1 normal / ≥3:1 large text and controls; adding an unlisted pair fails) in `tests/ui/test_theme_contrast.py`
- [X] T006 Extend `src/smartboard/ui/theme.py` into the full token table (palette, state/outcome colors, type scale, spacing, radii, sizes, `CONTRAST_PAIRS`) with `build_stylesheet()` generating all application QSS (only AFTER T004–T005 fail)

**Checkpoint**: T004–T005 fail pre-implementation, then green with T006; no literals outside `theme.py`.

---

## Phase 3: User Story 1 - Board Surface (Priority: P1) 🎯 MVP

**Goal**: Distinct slate board surface with border/shadow, token fonts, selection outline + corner handles.

**Independent Test**: Offscreen grabs at 1366×768 and 1920×1080 show a centered lighter rounded surface with border, legible heading/body text, and handles on the selected element only.

- [X] T007 [P] [US1] Board surface tests (surface rect centered, border pixels sampled, heading ≥64px / body ≥36px measured, 4 corner handles on selected element, no handles elsewhere) in `tests/ui/test_board_surface.py`
- [X] T008 [P] [US1] Cached SVG icon loader with theme tinting and missing-file failure in `src/smartboard/ui/icons.py`
- [X] T009 [US1] Repaint `src/smartboard/ui/board_view.py` surface/border/shadow, token fonts via `font_for`, selection outline + square handles, highlight ring (mapping and text-wrap logic unchanged) — depends on T006

**Checkpoint**: Story 1 acceptance scenarios pass; paint stays a pure function of state + viewport + theme.

---

## Phase 4: User Story 3 - Control Bar + Microphone States (Priority: P1)

**Goal**: Circular stateful mic as primary control, icon secondary buttons, status pill with per-state color + icon.

**Independent Test**: All five mic appearances and all five pill states pairwise distinguishable; hover/pressed/disabled/focus treatments visible; Undo/Redo disable correctly on empty history.

- [X] T010 [P] [US3] Mic button tests (112px circle, 5 `voiceState` appearances, pulse animation runs only while listening, QSS hover/pressed/disabled/focus blocks present) in `tests/ui/test_mic_button.py`
- [X] T011 [P] [US3] Status pill tests (5 state triples incl. icon + text, never color alone) in `tests/ui/test_pill_chip.py`
- [X] T012 [US3] Implement `src/smartboard/ui/mic_button.py` (QPushButton subclass, `voiceState` property, `QPropertyAnimation` pulse, SVG icon tinted per state) — depends on T006
- [X] T013 [US3] Implement `src/smartboard/ui/status_pill.py` (theme triple widget driven by pipeline state strings; owns no state machine) — depends on T006
- [X] T014 [US3] Rewire `src/smartboard/ui/main_window.py` control bar (circular mic + icon Undo/Redo/Window buttons, pill widget, QSS application, Undo/Redo enabled refresh after every engine result, no emoji anywhere)

**Checkpoint**: Story 3 control-bar scenarios pass; buttons meet 48px minima and contrast gate.

---

## Phase 5: User Story 2 - Transcription Strip + Result Chip (Priority: P1)

**Goal**: "Heard:" label, large transcript or placeholder, outcome chip with color + icon + text.

**Independent Test**: One command per outcome class shows matching transcript + chip triple; empty state shows the placeholder.

- [X] T015 [P] [US2] Strip + chip tests (Heard label, ≥20px text, exact placeholder when empty, 4 outcome triples incl. icon + text) in `tests/ui/test_pill_chip.py` (extend)
- [X] T016 [US2] Implement `src/smartboard/ui/result_chip.py` (top-bar right chip; renders outcome triples from engine result dicts) and rewire the top strip in `src/smartboard/ui/main_window.py` (Heard label + transcript + chip layout)

**Checkpoint**: Story 2 acceptance scenarios pass; chip never signals by color alone.

---

## Phase 6: User Story 4 - Dialogs + Title (Priority: P2)

**Goal**: Same-theme dialogs with ≥48px buttons, exact window title, selection confidence kept.

**Independent Test**: Each dialog inspected for theme, button sizes, centering; title reads exactly "Smart Chalkboard".

- [X] T017 [P] [US4] Dialog tests (theme selectors applied, Cancel/Confirm ≥48px high, centered over parent, once-only outcomes preserved) in `tests/ui/test_themed_dialogs.py`
- [X] T018 [US4] Restyle `src/smartboard/ui/confirm_dialog.py` and `src/smartboard/ui/clarify_dialog.py` with the theme (large buttons; behavior and 30 s timeout unchanged) and set the window title to exactly "Smart Chalkboard" in `src/smartboard/ui/main_window.py`

**Checkpoint**: Story 4 acceptance scenarios pass; dialog behavior identical to pre-redesign.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Regression proof, reference shots, headed sign-off

- [X] T019 Run FULL suite green (`tests/` — new UI tests plus unchanged 001/002 suites) with the T003 behavior guard passing
- [X] T020 [P] Offscreen regression grabs at 1366×768 and 1920×1080 with structural assertions (surface/border/handles/chip/pill/buttons) in `tests/ui/test_regression.py`, references committed in `tests/ui/refs/`
- [X] T021 [P] Record headed verification outcomes (5-state distinguishability, chip-without-color reading, Undo/Redo 20-trial identification, font measurements, teacher trial) in `specs/003-classroom-ui-redesign/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all story phases; T004–T005 MUST fail before T006
- **Board Surface (Phase 3, US1)**: Depends on Foundational (needs tokens + icons)
- **Control Bar (Phase 4, US3)**: Depends on Foundational (needs tokens); independent of Phase 3 paint
- **Strip + Chip (Phase 5, US2)**: Depends on Foundational (needs tokens + pill pattern from Phase 4)
- **Dialogs (Phase 6, US4)**: Depends on Foundational (needs tokens + QSS)
- **Polish (Phase 7)**: Depends on all prior phases

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependencies on other stories
- **US3 (P1)**: After Foundational — independent of US1 paint work
- **US2 (P1)**: After Foundational; reuses pill triple pattern from US3
- **US4 (P2)**: After Foundational; outcome logic covered by existing 001/002 tests

### Within Each Phase

- Tests FIRST, confirm FAIL, then implement (T004–T005 → T006; T007 → T009; T010–T011 → T012–T014; T015 → T016; T017 → T018)
- `core/` + `persistence/` + `app/` logic never modified — T003/T019 enforce

### Parallel Opportunities

- All [P] tests within a phase run in parallel (different files)
- T001–T003 mutually parallel; T004–T005 parallel; T007–T008 parallel; T010–T011 parallel
- Phase 4 and Phase 3 implementation can overlap once tokens (T006) are frozen

---

## Implementation Strategy

### MVP First (US1 board surface)

1. Complete Phase 1 (Setup) + Phase 2 (theme test-first)
2. Complete Phase 3 (board surface + icons)
3. **STOP and VALIDATE**: offscreen grabs show a distinct readable surface at both sizes

### Incremental Delivery

1. Setup + Foundational → single visual authority proven
2. + Board surface → legible distinct board (MVP core!)
3. + Control bar → stateful mic, pill, icon buttons
4. + Strip + chip → heard/outcome visibility
5. + Dialogs → themed confirmations
6. + Polish → full suite green, refs committed, headed sign-off

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to spec user story for traceability (US1–US4)
- Theme rule: no color/size/font literals outside `ui/theme.py` — enforced by T004 and review
- Verify theme tests fail before implementing (T004–T005 red → T006 green)
- Commit after each task or logical group; stop at any checkpoint to validate independently
- Avoid: new features/commands, light theme, user theming, emoji, behavior changes of any kind
