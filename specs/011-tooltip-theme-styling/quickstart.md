# Quickstart: Tooltip Theme Styling

**Feature**: `011-tooltip-theme-styling` | **Date**: 2026-10-06
**Status**: Implemented and verified offscreen on 2026-10-06: full suite
`388 passed, 4 skipped`; full-suite core coverage `97.24%` against the required `95%`.

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
py -3.11 -m smartboard.app.main
```

In the classroom app:

1. Hover over controls and confirm tooltips use the dark theme, readable text, border, rounded corners, and comfortable padding.
2. Confirm tooltips appear after a brief intentional hover and do not obscure controls unnecessarily.
3. Confirm the transcript tooltip still contains the complete transcript.

## Verify

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m pytest tests/ui/test_tooltip_theme.py tests/ui/test_theme_contrast.py tests/ui/test_transcript_elision.py -q
py -3.11 -m pytest tests -q --cov=src/smartboard/core --cov-report=term-missing --cov-fail-under=95
```

The tooltip-specific test matrix is in [contracts/test-matrix.md](contracts/test-matrix.md). Required coverage includes:

- generated stylesheet rule and token colors;
- 500ms style-hint delay;
- tooltip text/background contrast;
- unchanged transcript tooltip text.

## Manual headed checklist

- [ ] Tooltips are readable and visually consistent.
- [ ] Tooltips appear after intentional hovers without obscuring controls unnecessarily.
- [ ] The transcript tooltip contains the complete text.

Automated offscreen verification is complete, including generated-stylesheet,
delay-hint, contrast, tooltip-text, and full-regression coverage. Headed
checks were not performed in this offscreen-only execution environment.
