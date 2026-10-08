# Quickstart: Compact Control Layout

**Feature**: `004-compact-control-layout` | **Date**: 2026-10-04

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
py -3.11 -m smartboard.app.main
```

Bottom-left: 64px mic, compact Undo/Redo. Top-right: result chip with the
Window button beside it (tooltip "Window", F11 still works). Bottom-right:
compact status pill. Long transcripts shorten with "…" — hover for the
full text.

## Verify

```powershell
py -3.11 -m pytest tests/ui -q                     # layout, elision, minima
py -3.11 -m pytest tests -q                        # full suite incl. no-regression
$env:QT_QPA_PLATFORM = "offscreen"; py -3.11 -m pytest tests/ui -q  # headless
```

## Manual headed checklist (real display)

Offscreen-verified 2026-10-04 (`tests/ui/refs/window-1366x768.png`,
`window-1920x1080.png` inspected): compact mic/Undo/Redo bottom-left,
Window icon button beside Done chip, compact pill bottom-right, empty
middle, taller board, word-boundary elision with tooltip. (Offscreen
shots show tofu glyphs — the runner ships no fonts; real text verified
on hardware below.)
Remaining for a real display:

- [ ] Mic/Undo/Redo order, sizes, and 44px targets at 960×540.
- [ ] Window button beside chip; tooltip + accessible name read "Window".
- [ ] Pill shows all five states compactly at bottom right.
- [ ] Overlong transcript shortens at a word boundary with "…"; tooltip
  shows the full text; chip + Window button never clipped.
- [ ] Board visibly taller than before at the same window size.
