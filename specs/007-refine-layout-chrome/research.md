# Research: Refine Layout Chrome

**Feature**: `007-refine-layout-chrome` | **Date**: 2026-10-04
**Input**: spec + user technical brief (theme tokens, explicit QLineEdit
stylesheet, stretch-1 uncapped input, slimmer strip, expanding board
view with token margin, pytest-qt tests at 3 sizes)

No NEEDS CLARIFICATION: every mechanism is prescribed.

## Decisions

### R-01: New theme tokens, nothing else retuned

- **Decision**: Add `STRIP_H=44`, `CHIP_H`/`WINDOW_BTN_H` in 32–36
  (`CHIP_H=34`), `BOARD_MARGIN=8`, `BAR_PAD_V` slimmed (6px vertical
  chrome padding); existing colors, fonts (transcript 18–20 via new
  `FONT_STRIP=18`), icons, and radii untouched.
- **Rationale**: Spec FR-007 (theme-only sizes); additive tokens keep
  every prior assertion addressable.
- **Alternatives rejected**: Editing existing token values in place
  (would silently move 004-era minima the suite still pins).

### R-02: Explicit QLineEdit stylesheet kills platform defaults

- **Decision**: Extend the generated QSS with a `QLineEdit` block:
  background, color, `placeholder-text-color`, border, `:focus` border,
  padding, font-size — all from tokens. The dev input then carries no
  inline visuals beyond its placeholder string.
- **Rationale**: User-brief directive; the 003 session proved
  platform-default styling leaks wherever QSS is silent.
- **Alternatives rejected**: Per-widget inline stylesheet (re-split
  authority the theme just unified).

### R-03: Uncapped stretch input, slimmer bars

- **Decision**: `bar.addWidget(dev_input, stretch=1)` (alignment
  centered), `setMaximumWidth` REMOVED; strip minimum height → 44px
  token; bar vertical padding → slim token. The input's 44px height is
  unchanged, so bar height is still mic-driven.
- **Rationale**: Spec FR-001/FR-005; removing the cap supersedes the 006
  contract by explicit user order.
- **Alternatives rejected**: Keeping the cap (contradicts the brief).

### R-04: Board expands via layout, mapping untouched

- **Decision**: No viewport or paint change: the board view already
  fills its layout cell (`stretch=1`) and recomputes scale/offset from
  widget size every paint. Slimmer chrome + ≤8px layout margins enlarge
  the cell, so the canvas scales up automatically. Root/central layout
  margins set from `BOARD_MARGIN` (8px).
- **Rationale**: Spec FR-005/FR-006 — room gain with zero mapping risk.
- **Alternatives rejected**: Touching viewport math (unneeded risk for
  an unchanged contract).

### R-05: Tests assert fill, contrast, and width rule

- **Decision**: pytest-qt at 960×540, 1366×768, 1920×1080: input right
  edge within 8px+ of the pill's left edge (fills the gap), input text
  color vs background ≥4.5:1 via the token pair, and board-view width
  equals window width minus 2× margin whenever the aspect ratio lets
  width bind first (width-bound sizes), else height-bound with centered
  pillar margins — asserting the rule, not a fixed outcome.
- **Rationale**: User-brief directive; aspect-conditional assertions
  stay green on any display shape.
- **Alternatives rejected**: Fixed-pixel expectations (brittle across
  chrome heights); screenshot diffs (existing refs cover visuals).
