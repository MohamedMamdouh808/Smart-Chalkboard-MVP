# Quickstart: Infinite Board

**Feature**: `013-infinite-board`
**Date**: 2026-10-08

## 1. Environment

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m pytest tests -q
```

Use offscreen Qt for automated widget tests. Omit `QT_QPA_PLATFORM=offscreen` only for a visible manual run.

## 2. Camera and transform checks

Verify:

- World/screen round-trips at zoom `0.10`, `1.00`, and `4.00` with representative pan offsets.
- Cursor-anchored zoom preserves the world coordinate beneath the cursor.
- Pan/reset/fit-all operations leave board version, elements, selection, and history unchanged.
- Invalid camera values normalize to finite values and zoom remains within range.

## 3. Engine and world-coordinate checks

Verify:

- Creation, movement, resizing, drawing, and text edits succeed across negative and distant world coordinates.
- Minimum-size validation remains enforced.
- Non-finite or out-of-range geometry is rejected without state/history changes.
- No canvas fields appear in new board snapshots.
- Double-click creation and existing-text edits each produce exactly one history entry.
- Discarded or reverted edits produce no history entries.
- `edit_text` is unavailable through public AI command validation.

## 4. Input and rendering checks

Verify:

- Wheel pans, `Shift+wheel` pans horizontally, and `Ctrl+wheel` zooms about the cursor.
- Space+drag pans without changing Pen/Select mode.
- Middle-button drag pans.
- Select-mode empty drag pans without creating content.
- Pinch/native zoom input uses the same cursor-anchored zoom path.
- Only viewport-intersecting elements are painted.
- Grid spacing responds to zoom while dot size stays constant on screen.
- Handles and selection outlines remain constant on screen from 10% through 400%.

## 5. Voice, persistence, migration, and export checks

Verify:

- Voice-created elements appear in the visible rectangle near its top-left.
- Relative voice moves use the active zoom.
- AI context contains viewport bounds, selection, and no more than 50 compact visible/nearby elements.
- Camera saves and restores with lessons.
- Legacy snapshots preserve coordinates and reopen centered at 100%.
- Export renders content bounds plus margin at 100%.
- Empty lessons export a valid image.

## 6. Performance check

Create 200 representative elements across visible and offscreen world regions, then verify:

- Viewport filtering paints only intersecting elements.
- Pan/zoom smoke operations complete within the generous automated performance budget.
- No unbounded AI context, history, persistence, or export growth occurs.

## 7. Release gate

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m pytest tests -q --cov=src/smartboard/core --cov-report=term --cov-fail-under=95
```

The infinite-board implementation must preserve the existing 95% core-coverage gate and update or retire obsolete canvas-bound expectations.
