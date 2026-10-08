# Quickstart: Manual Drawing

**Feature**: `008-manual-drawing` | **Date**: 2026-10-04
**Verified**: 2026-10-04 — 12-case matrix green; full suite green
(289 passed, 2 skipped); core coverage gate holds at 98.24%; refs
regenerated for the Pen toggle and inspected.

Later same-day fixes, all covered by tests: stroke recoloring now rewrites
every stored stroke colour (undo/redo restores them), ~2-unit point
reduction runs at commit, pen commits go through the queue and an engine
lock so they can never interleave with a voice command, selection goes
through the engine instead of touching board state directly, and pen width
is a persisted thin/medium/thick setting with no toolbar control.

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
py -3.11 -m smartboard.app.main
```

Press **P** (or the Pen toggle) and draw with mouse or pen; press **S**
to select. Strokes within 1.5 s group into one undoable drawing.
Voice/dev commands work on drawings by selection or ID.

## Verify

```powershell
py -3.11 -m pytest tests/ui/test_drawing_input.py tests/integration/test_drawing_engine.py -q
py -3.11 -m pytest tests -q   # full suite incl. no-regression gate
```

## Manual headed checklist (real display + pen if available)

- [ ] Live stroke follows the pointer with no visible lag.
- [ ] Pen pressure visibly varies stroke width; mouse draws uniform width.
- [ ] Grouped sketch undoes in one step; voice resize keeps proportions.
- [ ] Offline drawing, save/reopen, and resize-mid-stroke all intact.
