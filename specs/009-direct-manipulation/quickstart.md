# Quickstart: Direct Manipulation

**Feature**: `009-direct-manipulation` | **Date**: 2026-10-05
**Status**: Implemented and verified offscreen on 2026-10-05: full suite
`366 passed, 4 skipped`; full-suite core coverage `97.24%` against the required `95%`.

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m smartboard.app.main
```

In Select mode:

1. Click an element and confirm its outline tightly surrounds all visible content.
2. Drag the element and confirm it remains completely inside the canvas.
3. Drag each corner handle and confirm the opposite corner remains fixed.
4. Press Escape during a gesture and confirm nothing changes.
5. Undo and redo accepted gestures and confirm complete reversal and restoration.

## Verify

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m pytest tests -q --cov=src/smartboard/core --cov-report=term-missing --cov-fail-under=95
```

The gesture-specific test matrix is in [contracts/test-matrix.md](contracts/test-matrix.md). Required coverage includes:

- width-8 scribble-plus-line bounding-box regression;
- per-type hit testing;
- dragging every element type;
- all four resize corners;
- bounds clamping and minimum size;
- one history entry per accepted gesture;
- Undo/Redo and Escape cancellation;
- gestures at four representative window sizes;
- voice resize followed by manual drag.

## Verification outcomes

- Automated gesture matrix passed offscreen, including synthetic mouse, tablet, and touch coverage at 960×540, 1280×720, 1920×1080, and 800×1000.
- Two historical no-change branch guards are skipped because their base branches have no unique snapshots; two pre-existing environment-dependent tests remain skipped.
- Ruff, Black, and mypy executables/modules were unavailable in the execution environment, so those checks could not be run here.

## Manual headed checklist

- [ ] Selection outlines visibly enclose headings, text, equations, shapes, and drawings.
- [ ] Drag and resize previews track the pointer smoothly.
- [ ] Handle hover changes the cursor.
- [ ] Cancelled gestures leave the board visually unchanged.

Headed checks were not performed in this offscreen-only execution environment.
