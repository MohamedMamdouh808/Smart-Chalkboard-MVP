# Quickstart: Classroom UI Redesign

**Feature**: `003-classroom-ui-redesign` | **Date**: 2026-10-03

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
py -3.11 -m smartboard.app.main
```

Click the circular mic to step the scripted demo; watch the status pill,
result chip, and per-state mic ring. F11 toggles fullscreen; Esc closes.

## Verify

```powershell
py -3.11 -m pytest tests/ui -q                 # theme, widgets, regression
py -3.11 -m pytest tests -q                     # full suite incl. no-regression gate
$env:QT_QPA_PLATFORM = "offscreen"; py -3.11 -m pytest tests/ui -q  # headless
py -3.11 -m pytest tests/ui --regen-refs -q      # regenerate reference PNGs (explicit only)
```

## Manual headed checklist (real display)

Offscreen-verified 2026-10-04 (`tests/ui/refs/window-1366x768.png`,
`window-1920x1080.png` inspected): distinct surface with border/shadow,
strip with Heard + transcript + Done chip, circular mic with icon ring,
icon Undo/Redo/Window buttons, single status pill, selection outline
with corner handles, highlight ring. (Offscreen shots show tofu glyphs —
the runner ships no fonts; real text verified on hardware below.)
Remaining for a real display:

- [ ] All 5 mic states + 5 pill states pairwise distinguishable side by side.
- [ ] Chip outcomes readable with color ignored (icons + text carry it).
- [ ] Undo/Redo disabled treatment correct on empty vs non-empty history.
- [ ] Heading/body sizes measured ≥64/≥36 at full canvas scale.
- [ ] 9/10 first-time teachers complete speak → confirm → undo unaided.
