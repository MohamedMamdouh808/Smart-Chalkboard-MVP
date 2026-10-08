# Quickstart: Refine Layout Chrome

**Feature**: `007-refine-layout-chrome` | **Date**: 2026-10-04
**Verified**: 2026-10-04 — layout tests green at 3 sizes; full suite
green (248 passed); core coverage gate holds.

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:SMARTBOARD_DEV_INPUT = "1"
py -3.11 -m smartboard.app.main
```

Slim 44px strip with smaller transcript text, compact chip + Window
button, full-gap dev input in the bar, and the largest board yet.

## Verify

```powershell
py -3.11 -m pytest tests/ui/test_chrome_refine.py -q
py -3.11 -m pytest tests -q   # full suite incl. no-regression gate
```

## Manual headed checklist (real display)

- [ ] Strip reads 44px; transcript vertically centered and readable.
- [ ] Dev input fills the bar gap with visible text, cursor, and focus.
- [ ] Board touches ≤8px side margins and fills inter-bar height.
