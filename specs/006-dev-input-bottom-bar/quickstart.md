# Quickstart: Dev Input Bottom Bar

**Feature**: `006-dev-input-bottom-bar` | **Date**: 2026-10-04
**Verified**: 2026-10-04 — layout tests green at 3 sizes; full suite
green (241 passed); core coverage gate holds.

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:SMARTBOARD_DEV_INPUT = "1"
py -3.11 -m smartboard.app.main
```

Type in the bottom-bar input (between Redo and the status pill, ≤700px);
Enter submits through the unchanged AI path and clears. Without the
flag, the bar is exactly as before.

## Verify

```powershell
py -3.11 -m pytest tests/ui/test_dev_input_bar.py -q
py -3.11 -m pytest tests -q   # full suite incl. no-regression gate
```

## Manual headed checklist (real display)

- [ ] Input centered ≤700px in the bar middle at three sizes.
- [ ] Flag off: bar identical to before; top strip has transcript room.
- [ ] Disabled state visible while a command processes.
