# Implementation Plan: Classroom UI Redesign

**Branch**: `003-classroom-ui-redesign` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification + user technical brief + constitution v1.0.0

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Rebuild the Smart Chalkboard chrome around one theme module (tokens +
generated QSS): QPainter board surface with border/shadow, stateful
circular mic button with pulse animation, SVG-icon secondary buttons,
status pill + result chip driven by existing pipeline state, themed
dialogs, exact window title, and offscreen visual-regression plus
token-contrast tests. Zero board-behavior, command, or data changes.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 (`QPainter`, `QPropertyAnimation`, `QIcon`/SVG, QSS), pytest-qt (existing); engine/voice/AI/persistence untouched
**Storage**: None (reference PNGs in `tests/ui/refs/` are committed test assets, not app data)
**Testing**: pytest-qt offscreen grabs at 1366×768 + 1920×1080 (structural assertions + ≤0.5% diff gate), headless luminance tests, full pre-redesign suite as no-regression gate
**Target Platform**: Windows desktop (same classroom machine)
**Project Type**: desktop-app (existing single project)
**Performance Goals**: QSS applied once at startup; pulse animation ~1 Hz on one small widget; repaint cost unchanged (same element count, one extra surface rect + handles)
**Constraints**: `core/`, `persistence/`, engine results, queue, history, viewport math, window geometry all UNCHANGED; no new commands/features; no light theme; no user theming; no emoji in chrome
**Scale/Scope**: One window, same canvas/board; visual layer only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — no AI paths touched. PASS.
- [x] II. Determinism — paint is a pure function of (state, viewport, theme); same inputs → same pixels. PASS.
- [x] III. Separation — all work in `ui/` (+ icons assets); `core/` + `persistence/` + `app/` logic unmodified (diff-guard extended). PASS.
- [x] IV. Code quality — typed small widgets, one token source, no literals elsewhere, no eval/exec. PASS.
- [x] V. Test-first — theme/widget/regression/contrast tests before implementation; full suite must pass unchanged. PASS.
- [x] VI. Security/privacy — icons are local SVGs; no network, keys, audio, or content changes. PASS.
- [x] VII. Reliability — no state-writing paths touched; dialogs keep once-only outcomes; animation confined to mic widget. PASS.
- [x] VIII. Scope — pure restyle; excluded items (features, commands, light/custom themes) explicitly untouched. PASS.

Re-check after Phase 1 design (research/data-model/contracts/quickstart above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/003-classroom-ui-redesign/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── theme-contract.md
│   ├── widgets-contract.md
│   ├── icons-contract.md
│   └── regression-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/ui/
├── theme.py         # EXTEND: full token table + build_stylesheet() + CONTRAST_PAIRS
├── icons/           # NEW: bundled SVGs (mic, undo, redo, window, check, alert,
│                    #   question, error, state dots)
├── icons.py         # NEW: cached QIcon loader with theme tinting
├── mic_button.py    # NEW: circular QPushButton, voiceState property, pulse
├── status_pill.py   # NEW: state triple widget (itself theme-driven)
├── result_chip.py   # NEW: Heard label + transcript + outcome triple
├── board_view.py    # MODIFY: surface/border/shadow, token fonts, handles
├── main_window.py   # MODIFY: strip+chip top, mic+pill bar bottom, title,
│                    #   undo/redo enable refresh, QSS application
├── confirm_dialog.py# MODIFY: theme + ≥48px buttons (behavior unchanged)
└── clarify_dialog.py# MODIFY: theme + ≥48px buttons (behavior unchanged)

tests/ui/
├── test_theme_contrast.py   # NEW: luminance gate over CONTRAST_PAIRS
├── test_mic_button.py       # NEW: 5 states, pulse, sizes, QSS states
├── test_pill_chip.py        # NEW: triples incl. no-color-alone check
├── test_board_surface.py    # NEW: surface/border/handles pixel assertions
├── test_regression.py       # NEW: offscreen grabs, 2 sizes, diff gate + refs
└── refs/                    # NEW: reference PNGs (explicit regen only)
```

**Structure Decision**: Existing single-project layout extended in place.
Theme + icons are additive modules; widgets are modified, never forked;
`app/` orchestration and everything below it is untouched.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
