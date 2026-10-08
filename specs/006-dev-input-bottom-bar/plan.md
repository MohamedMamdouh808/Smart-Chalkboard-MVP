# Implementation Plan: Dev Input Bottom Bar

**Branch**: `006-dev-input-bottom-bar` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification + user technical brief + constitution v1.0.0

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Reparent the developer transcript input from the top strip to the
bottom-bar middle (stretch, 700px cap, centered, theme sizes), keeping
flag gating, submit behavior, and processing-disabled state — verified
by pytest-qt layout tests at three sizes. Zero behavior, AI-flow, or
mic changes.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 layouts only (`QHBoxLayout` stretch,
`setMaximumWidth`, `setVisible`) — engine/AI/persistence untouched
**Storage**: None (no new assets, settings, or keys)
**Testing**: pytest-qt offscreen at 960×540, 1366×768, 1920×1080 (flag
on/off, disjointness, width cap, board-geometry identity); full suite
as no-regression gate
**Target Platform**: Windows desktop (same classroom machine)
**Project Type**: desktop-app (existing single project)
**Performance Goals**: No new paint or layout passes; elision behavior
unchanged; zero command-path impact
**Constraints**: Same widget moved (not rebuilt); flag semantics
identical; theme-only sizes; board geometry identical on/off
**Scale/Scope**: One input widget, two layouts; layout-only change

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — transcript path untouched; only a widget parent changes. PASS.
- [x] II. Determinism — layout is a pure function of flag + size + tokens. PASS.
- [x] III. Separation — all work in `ui/main_window.py` (+ tests); logic layers unmodified. PASS.
- [x] IV. Code quality — one small move, tokens stay the sole size source, no eval/exec. PASS.
- [x] V. Test-first — layout tests before the move; full suite must pass unchanged. PASS.
- [x] VI. Security/privacy — dev-only visibility unchanged; no new data flows. PASS.
- [x] VII. Reliability — submit/disable/enable wiring moves with the widget, unchanged. PASS.
- [x] VIII. Scope — pure reparenting within the specced bounds; excluded items untouched. PASS.

Re-check after Phase 1 design (research/data-model/contracts/quickstart above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/006-dev-input-bottom-bar/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── move-contract.md
│   └── layout-tests.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/ui/main_window.py   # MODIFY: move dev_input to bar (stretch, cap, theme sizes)
tests/ui/test_dev_input_bar.py     # NEW: on/off, disjointness, cap, board identity, submit/disable
```

**Structure Decision**: Two-file change. The widget and its wiring move
together; everything else (engine, AI, theme, board, dialogs) is
untouched.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
