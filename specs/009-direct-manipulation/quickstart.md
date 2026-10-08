# Quickstart: Direct Manipulation

**Feature**: `009-direct-manipulation` | **Date**: 2026-10-05
**Status**: Planned implementation; no code changes are included in this planning pass.

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
py -3.11 -m pytest tests/unit tests/contract -q --cov=src/smartboard/core --cov-report=term-missing --cov-fail-under=95
py -3.11 -m pytest tests -q
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

## Manual headed checklist

- [ ] Selection outlines visibly enclose headings, text, equations, shapes, and drawings.
- [ ] Drag and resize previews track the pointer smoothly.
- [ ] Handle hover changes the cursor.
- [ ] Cancelled gestures leave the board visually unchanged.
