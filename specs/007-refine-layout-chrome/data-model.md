# Data Model: Refine Layout Chrome

**Feature**: `007-refine-layout-chrome` | **Date**: 2026-10-04
**Sources**: `spec.md`, `research.md`

No board, command, history, theme-color, or font-family entities change.
This feature adds size tokens and restyles two bars.

## New size tokens (`ui/theme.py`, additive)

- `STRIP_H = 44` (top bar height), `FONT_STRIP = 18` (Heard/transcript),
  `CHIP_H = 34` (chip and Window button height, 32–36 band),
  `BOARD_MARGIN = 8` (window side margins + layout padding),
  `BAR_PAD_V = 6` (slimmer vertical chrome padding).
- Existing tokens (mic 64, compact 44, pill 36, transcript 24 elsewhere,
  palette, radii) unchanged.

## Restyled facts

- Dev input: full-gap fill, 44px, dark bg, ≥18px light text, muted
  placeholder, focus outline — all from the extended QSS block.
- Top bar: 44px, 18px vertically centered Heard/transcript with
  ellipsis + tooltip, 34px right-anchored chip + Window button.
- Board cell: full width minus ≤8px margins, full inter-bar height;
  mapping rule identical.

## State transitions

None added or altered.
