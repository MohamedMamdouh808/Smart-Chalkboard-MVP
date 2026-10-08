# Implementation Plan: Refine Layout Chrome

**Branch**: `007-refine-layout-chrome` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification + user technical brief + constitution v1.0.0

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add theme size tokens, extend the generated QSS with an explicit
QLineEdit block, slim the strip and bar chrome, uncap the dev input to
fill its gap, and let the untouched viewport scale the board into the
freed room — proven by aspect-aware pytest-qt layout tests at three
sizes.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 layouts + QSS only — engine/AI/mapping/persistence untouched
**Storage**: None (no new assets, settings, or keys)
**Testing**: pytest-qt offscreen at 960×540, 1366×768, 1920×1080 (fill, contrast, width-rule); full suite as no-regression gate
**Target Platform**: Windows desktop (same classroom machine)
**Project Type**: desktop-app (existing single project)
**Performance Goals**: No new paint/layout passes; elision rule unchanged; zero command-path impact
**Constraints**: Additive tokens only; QLineEdit visuals exclusively from QSS; board mapping byte-identical; 44px/44px/34px/8px targets
**Scale/Scope**: Chrome restyle + layout margins; nothing else moves

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — no AI paths touched. PASS.
- [x] II. Determinism — layout is a pure function of flag + size + tokens. PASS.
- [x] III. Separation — all work in `ui/` theme + `main_window` (+ tests); logic layers unmodified. PASS.
- [x] IV. Code quality — additive tokens, one QSS block, no literals elsewhere, no eval/exec. PASS.
- [x] V. Test-first — layout tests before implementation; full suite must pass with only intended assertion moves. PASS.
- [x] VI. Security/privacy — no new data flows; dev-only gating unchanged. PASS.
- [x] VII. Reliability — no state paths touched; submit/disable wiring unchanged. PASS.
- [x] VIII. Scope — pure chrome refinement within the specced bounds; excluded items untouched. PASS.

Re-check after Phase 1 design (research/data-model/contracts/quickstart above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/007-refine-layout-chrome/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── tokens-styles.md
│   ├── chrome-geometry.md
│   └── layout-tests.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/ui/theme.py        # MODIFY: additive tokens + QLineEdit QSS + contrast pair
src/smartboard/ui/main_window.py  # MODIFY: strip/bar heights, input uncapped, margins/padding
tests/ui/test_chrome_refine.py    # NEW: fill/contrast/width-rule at 3 sizes
```

**Structure Decision**: Three-file change. Tokens stay additive (no
existing value moves); the QSS block absorbs the input's inline
visuals; everything else (engine, AI, viewport, board paint, dialogs)
is untouched.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
