# Quickstart: Resizable Window Mode

**Feature**: `002-resizable-window-mode` | **Date**: 2026-10-03

## Run windowed

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
py -3.11 -m smartboard.app.main
```

Press **F11** or the window toggle button to switch fullscreen ↔ window.
Close windowed → reopen → windowed at the same size and position (fresh
install starts fullscreen). Minimum window size is 960×540.

## Verify

```powershell
py -3.11 -m pytest tests/ui tests/unit -q   # viewport math, text-fit, contrast, chrome
py -3.11 -m pytest tests -q                 # full suite incl. 001 regression (engine untouched)
$env:QT_QPA_PLATFORM = "offscreen"; py -3.11 -m pytest tests/ui -q  # headless Qt
```

## Manual headed checklist (real display, fonts, pen)

Offscreen-verified 2026-10-03 (see `review-002.png`): layout order,
letterboxing, selection outline, pen stroke, styled buttons, windowed
1280×720 render. Remaining for a real display:

- [ ] F11 × 4 with content on board → state identical each time.
- [ ] Drag through 960×540 → 1280×720 → maximized → fullscreen; content
  undistorted, centered, controls readable, no overlap.
- [ ] Pen tap selects the intended element at three sizes.
- [ ] Resize mid-stroke and with a confirmation dialog open → stroke intact,
  dialog centered, outcome applied once.
- [ ] Heading text fully visible in its box (real Arial metrics); button
  labels high-contrast.
