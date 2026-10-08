# Implementation Plan: Tooltip Theme Styling

**Branch**: `011-tooltip-theme-styling` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)
**Input**: Approved feature specification plus user-supplied stylesheet, application-styling, delay, and test directives

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Style every tooltip through one central QSS rule using theme tokens, apply the generated stylesheet at `QApplication` level, set the 500ms tooltip delay through a narrow proxy style, and verify the rule, delay, contrast, and unchanged transcript text with `pytest`/`pytest-qt`.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 QSS, `QApplication`, `QProxyStyle`, existing theme tokens, existing transcript/UI infrastructure
**Storage**: None; no schema, settings, asset, or tooltip-text changes
**Testing**: `pytest`, `pytest-qt`, offscreen Qt, generated-stylesheet assertions, style-hint assertions, contrast assertions, existing transcript-tooltip coverage
**Target Platform**: Windows desktop classroom machine
**Project Type**: desktop-app, existing single-project layout
**Performance Goals**: Stylesheet generation remains startup-only; one delegated style hint; no additional timers, paint passes, layout work, or state changes
**Constraints**: Central-theme values only; dark non-white background; light text at least 16px; WCAG AA contrast; thin theme border; rounded corners; 6px vertical and 10px horizontal padding; 500ms delay; unchanged tooltip text; no new tooltips or features
**Scale/Scope**: All existing tooltips; one stylesheet rule; one style-hint override; focused contrast/delay/text tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — No AI, board-state, validation, execution, history, or persistence paths are touched. PASS.
- [x] II. Determinism — Stylesheet generation and style-hint behavior are deterministic; no command/state behavior changes. PASS.
- [x] III. Separation — Presentation remains in theme/UI startup code; core logic is untouched and no business rules enter widgets. PASS.
- [x] IV. Code quality — Typed small theme/style modules, central tokens, no visual literals outside theme, no `eval`/`exec`, no untrusted dynamic behavior. PASS.
- [x] V. Test-first — Stylesheet, delay, contrast, transcript-preservation, and full-regression tests precede and verify implementation. PASS.
- [x] VI. Security/privacy — No credentials, audio, uploads, exports, logs, or sensitive data changes. PASS.
- [x] VII. Reliability — Existing atomic engine, queue, manual-mode, and failure behavior are untouched; styling cannot change board state or history. PASS.
- [x] VIII. Scope — No new tooltips, commands, schema changes, features, or behavior changes. PASS.

Re-check after Phase 1 design (`research.md`, `data-model.md`, `contracts/`, `quickstart.md` above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/011-tooltip-theme-styling/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── stylesheet-contract.md
│   ├── style-delay-contract.md
│   ├── text-placement-contract.md
│   └── test-matrix.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/ui/theme.py                # MODIFY: tooltip tokens and central QToolTip rule
src/smartboard/ui/tooltip_style.py        # NEW: narrow QProxyStyle tooltip-delay hint
src/smartboard/app/main.py                # MODIFY: install proxy style; retain app-level stylesheet
tests/ui/test_tooltip_theme.py            # NEW: QSS token, delay-hint, and text-preservation tests
tests/ui/test_theme_contrast.py           # EXTEND: explicit tooltip text/background contrast test
tests/ui/test_transcript_elision.py       # UNCHANGED: existing full-transcript tooltip coverage
```

**Structure Decision**: Extend the existing single-project layout in place. Theme values and stylesheet generation stay in `theme.py`; Qt style behavior stays in a small UI module; application startup retains the existing application-level stylesheet behavior.

## Implementation flow

1. **Theme tokens and stylesheet**
   - Add tooltip padding and delay tokens to the central theme.
   - Generate one `QToolTip` rule from background, foreground, font-size, border, radius, and padding tokens.
   - Preserve all existing tooltip text.

2. **Application styling and delay**
   - Retain application-level stylesheet application so separate tooltip windows receive the rule.
   - Install a narrow proxy style that returns 500ms for tooltip wake-up delay and delegates all other behavior.
   - Preserve native tooltip timing, dismissal, and placement.

3. **Verification**
   - Add stylesheet-rule/token tests, proxy-style delay tests, explicit tooltip contrast tests, and transcript-text coverage.
   - Retain the full regression suite and applicable coverage gates.
   - Leave optional real-display checks in `quickstart.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
