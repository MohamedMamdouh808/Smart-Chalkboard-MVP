# Implementation Plan: Compact Control Layout

**Branch**: `004-compact-control-layout` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification + user technical brief + constitution v1.0.0

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Retune theme size tokens (64px mic, 44px compact controls, 36px pill),
rebuild the bottom bar as left-group + stretch + pill, move the Window
button beside the result chip, and shorten transcripts with
word-boundary ellipsis plus full-text tooltips — all verified by
pytest-qt layout tests at three sizes. Zero behavior, command, data, or
board-rendering changes.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 (`QHBoxLayout` stretch, `QFontMetrics.elidedText`, tooltip, accessibleName) — engine/voice/AI/persistence untouched
**Storage**: None (no new assets; no settings changes)
**Testing**: pytest-qt offscreen at 960×540, 1366×768, 1920×1080 (order, disjointness, board-height gain, elision/tooltip); full suite as no-regression gate
**Target Platform**: Windows desktop (same classroom machine)
**Project Type**: desktop-app (existing single project)
**Performance Goals**: Elision recompute O(text) on strip resize only; layout pass unchanged in kind; zero command-path impact
**Constraints**: `core/`, `persistence/`, `app/` logic, board rendering, colors, fonts, icons UNCHANGED; 44px minima; chip + Window button always visible ≥960×540
**Scale/Scope**: Same single window/board; layout-only change

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — no AI paths touched. PASS.
- [x] II. Determinism — layout is a pure function of window size + tokens; same sizes → same chrome. PASS.
- [x] III. Separation — all work in `ui/` theme + `main_window` layout (+ tests); logic layers unmodified. PASS.
- [x] IV. Code quality — typed small edits, tokens stay the sole size source, no eval/exec. PASS.
- [x] V. Test-first — layout/elision tests before implementation; full suite must pass unchanged. PASS.
- [x] VI. Security/privacy — tooltips show only the already-visible transcript; no new data flows. PASS.
- [x] VII. Reliability — no state-writing paths touched; F11/pill/chip/undo-redo wiring unchanged. PASS.
- [x] VIII. Scope — pure layout restyle within the specced bounds; excluded items untouched. PASS.

Re-check after Phase 1 design (research/data-model/contracts/quickstart above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/004-compact-control-layout/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── layout-contract.md
│   └── transcript-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/ui/
├── theme.py         # MODIFY: size tokens only (mic 64, compact 44, pill 36)
├── main_window.py   # MODIFY: bar/strip layouts, Window move, elision+tooltip
├── mic_button.py    # MODIFY: read diameter from theme (no fixed literal)
├── status_pill.py   # MODIFY: read pill height from theme (width fits text)
└── (board_view, dialogs, icons, viewport, window_state untouched)

tests/ui/
├── test_compact_layout.py   # NEW: order/sizes/disjointness/board-gain, 3 sizes
└── test_transcript_elision.py  # NEW: word-boundary ellipsis, tooltip, chip visibility
```

**Structure Decision**: Existing single-project layout edited in place.
Theme tokens stay the sole size source; layouts reference tokens;
`app/` orchestration and everything below it is untouched.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
