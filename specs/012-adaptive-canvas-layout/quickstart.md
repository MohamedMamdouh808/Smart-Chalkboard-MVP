# Quickstart: Adaptive Canvas Layout

**Feature**: `012-adaptive-canvas-layout` | **Date**: 2026-10-07
**Status**: Implemented and verified offscreen on 2026-10-07: full suite
`409 passed, 4 skipped`; full-suite core coverage `97.08%` against the required `95%`.

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
py -3.11 -m smartboard.app.main
```

In the classroom app:

1. Open representative window sizes and fullscreen, confirming the board fills the available area without distortion.
2. Place content, resize repeatedly, and confirm coordinates, content, and history behavior remain stable.
3. Reopen a legacy lesson and confirm its 1920-by-1080 canvas and unchanged coordinates.
4. Export a lesson and confirm the export uses the stored canvas size.

## Verify

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m pytest tests/unit/test_adaptive_canvas.py tests/ui/test_adaptive_canvas_layout.py tests/integration/test_canvas_persistence.py -q
py -3.11 -m pytest tests -q --cov=src/smartboard/core --cov-report=term-missing --cov-fail-under=95
```

The canvas-specific test matrix is in [contracts/test-matrix.md](contracts/test-matrix.md). Required coverage includes:

- canvas growth without shrinkage;
- element stability across resizes;
- uniform downscale mapping;
- multi-size coordinates;
- right/bottom bounds;
- legacy reopening;
- save/reopen identity;
- history invariance;
- window-minus-margins board width.

## Manual headed checklist

- [ ] The board fills supported window sizes without distortion.
- [ ] Resizing never moves or loses lesson content.
- [ ] Legacy lessons reopen and export at the expected canvas size.

Automated offscreen verification is complete, including growth, stability,
downscale mapping, multi-size coordinates, edge bounds, legacy reopening,
save/reopen identity, history invariance, and window-margin layout coverage.
Headed checks were not performed in this offscreen-only execution environment;
the two historical no-change branch guards and two pre-existing environment
skips account for the 4 skipped tests.
