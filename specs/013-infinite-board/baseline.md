# Baseline: Infinite Board

**Feature**: `013-infinite-board`
**Date**: 2026-10-08

## Environment

- `py -3.11`
- `$env:PYTHONPATH = "src;C:\sblibs"`
- `$env:QT_QPA_PLATFORM = "offscreen"` for automated tests

## Baseline result

Command:

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m pytest tests -q
```

Result:

- Exit code: `0`
- Collected tests: `413`
- Outcome: `409 passed, 4 skipped`
- Core coverage gate before changes: `97.08%` against required `95%`

This baseline preserves the finite/adaptive-canvas behavior that `013-infinite-board` intentionally replaces. Obsolete canvas-bound expectations are retired in Phase 8 after infinite-board behavior is green.
