# Implementation Plan: Resizable Window Mode

**Branch**: `002-resizable-window-mode` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification + 2026-10-03 clarifications + user technical brief + constitution v1.0.0

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace the forced `showFullScreen()` with a fullscreen/windowed main
window (toggle button + F11, persisted mode/size/position), center a
uniform-scale letterboxed board view driven by a single invertible
viewport transform shared by paint/pen/selection, keep chrome in
non-overlapping layouts with 48px minima and an explicit high-contrast
stylesheet, fix text rendering via in-box wrapping plus a creation-time
fit gate, and cover it with pytest-qt tests. `core/` is untouched.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 (`QMainWindow` show states, `QShortcut` F11, `QSettings` IniFormat, `QFontMetrics`, stylesheets), pytest-qt (new), existing faster-whisper/Gemini/Groq untouched
**Storage**: Local settings store only (`window/mode`, `window/geometry`); lesson SQLite schema unchanged
**Testing**: pytest-qt with `QT_QPA_PLATFORM=offscreen` in CI + headless math tests; manual headed checklist in quickstart.md
**Target Platform**: Windows desktop (same HP EliteBook classroom machine)
**Project Type**: desktop-app (existing single project)
**Performance Goals**: resize repaint within one frame for ≤200 elements; settings I/O on close/startup only (zero impact on the 3 s voice budget)
**Constraints**: `core/` (board, schema, validators, engine, history) MUST NOT be modified; canvas stays 1920×1080; 960×540 window minimum; 48px control minima; ≥4.5:1 button contrast; text boxes immutable
**Scale/Scope**: one window, one board; out of scope: canvas-size changes, multi-monitor, multiple windows, zoom/pan

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — no AI paths touched; demo script fixtures unchanged. PASS.
- [x] II. Determinism — viewport is a pure function of (view, canvas) sizes; same sizes → same pixels; board state untouched. PASS.
- [x] III. Separation — all new code lives in `ui/` + one `app/` gate (`text_fit.py`); `core/` + `persistence/` unmodified (CI diff-guard task). PASS.
- [x] IV. Code quality — typed, small modules (`viewport.py`, `window_state.py`, `text_fit.py`), explicit stylesheet, no eval/exec. PASS.
- [x] V. Test-first — pytest-qt mapping/mode/resize tests + headless math/contrast tests before implementation; 001 suite must stay green. PASS.
- [x] VI. Security/privacy — QSettings holds geometry only; no keys, audio, transcripts, or lesson content. PASS.
- [x] VII. Reliability — resize/mode-switch cannot mutate state (paint + input are read-only over state; queue/engine paths unchanged); dialogs keep once-only outcomes. PASS.
- [x] VIII. Scope — no new AI commands, no canvas change, no out-of-scope items (zoom/pan, multi-window explicitly excluded). PASS.

Re-check after Phase 1 design (research/data-model/contracts/quickstart above): no new violations. Text-fit gate placed in `app/` (not `core/`) specifically to preserve III/VIII. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/002-resizable-window-mode/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── viewport-contract.md
│   ├── window-state-contract.md
│   ├── text-fit-contract.md
│   └── chrome-layout-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/
├── core/            # UNTOUCHED by this feature (diff-guard enforced)
├── persistence/     # UNTOUCHED by this feature
├── ui/
│   ├── viewport.py        # NEW: pure scale/offset + forward/inverse mapping
│   ├── window_state.py    # NEW: QSettings load/save, mode machine
│   ├── board_view.py      # MODIFY: use Viewport, wrap text in-box, letterbox
│   ├── main_window.py     # MODIFY: show states, F11 + toggle, layouts/minima,
│   │                      #   stylesheet, centered dialogs, recenter on move
│   ├── confirm_dialog.py  # MODIFY: parent-centering (behavior unchanged)
│   └── clarify_dialog.py  # MODIFY: parent-centering (behavior unchanged)
└── app/
    ├── text_fit.py  # NEW: QFontMetrics creation-time fit gate + message
    └── main.py      # MODIFY: restore-before-show, save-on-close, gate wiring

tests/
├── ui/              # NEW: mapping/mode/resize/text/contrast/chrome tests
└── (existing suites unchanged — 001 regression must stay green)
```

**Structure Decision**: Existing single-project layout extended in place.
New pure modules (`viewport.py`, `window_state.py`, `text_fit.py`) keep
Qt math testable headless; paint/input call sites share the one viewport
formula.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
