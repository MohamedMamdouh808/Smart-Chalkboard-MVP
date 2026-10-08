# Research: Dev Input Bottom Bar

**Feature**: `006-dev-input-bottom-bar` | **Date**: 2026-10-04
**Input**: spec + user technical brief (remove from top bar, insert in
bottom-bar `QHBoxLayout` with stretch, `setMaximumWidth(700)`, centered,
flag-tied visibility, theme sizes/fonts, pytest-qt tests at 3 sizes)

No NEEDS CLARIFICATION: the brief prescribes the exact mechanism.

## Decisions

### R-01: Reparent, don't rebuild

- **Decision**: Construct the existing `QLineEdit` in the bottom-bar
  layout (between the stretch-adjacent Redo button and the status pill)
  and delete it from the top strip — one widget, moved. Submit callback,
  placeholder, tooltip, and clear-after-submit wiring move with it
  untouched.
- **Rationale**: Spec FR-003 (identical submit behavior); a rebuild
  risks dropping a signal connection.
- **Alternatives rejected**: Second input + hide one (two sources of
  truth for one transcript).

### R-02: Stretch with 700px cap, centered

- **Decision**: `bar.addWidget(dev_input, stretch=1)` plus
  `dev_input.setMaximumWidth(700)`; centering comes free because the
  existing stretch spacer already centers free space between the group
  and the pill — the capped input sits inside the stretched cell, and
  the cell's extra room splits evenly on both sides.
- **Rationale**: User-brief directive; reuses the 004 stretch instead of
  new spacer math.
- **Alternatives rejected**: Fixed 700px width (overflows the middle at
  960×540); manual centering offsets (fights the layout on resize).

### R-03: Flag check untouched, theme tokens for size/font

- **Decision**: Keep `SMARTBOARD_DEV_INPUT == "1"` as the single
  visibility condition (evaluated at construction, as now). Height and
  font from theme: fixed height token (44px compact control) and the
  ≥18px button font token; placeholder string unchanged.
- **Rationale**: Spec FR-002/FR-004; identical gating semantics, themed
  presentation.
- **Alternatives rejected**: New flag or setting (gratuitous migration);
  hard-coded sizes (theme-rule violation).

### R-04: Disabled-while-processing via existing wiring

- **Decision**: The existing submit/delivery path already disables
  meaningfully: set `dev_input.setEnabled(False)` on submit and
  re-enable on result delivery in the same callback that refreshes the
  board — no new state, same pattern as Undo/Redo enable refresh.
- **Rationale**: Spec FR-005 with zero new machinery.
- **Alternatives rejected**: Separate busy flag (duplicates delivery
  state that already exists).

### R-05: Layout tests at three sizes

- **Decision**: pytest-qt offscreen at 960×540, 1366×768, 1920×1080:
  input visible iff flag on (monkeypatched env + rebuild window);
  input rect disjoint from mic/Undo/Redo/pill rects; input width ≤ 700;
  top strip contains exactly Heard/transcript/chip/Window (no input);
  board-view height equals the flag-off height at the same size.
- **Rationale**: User-brief directive; geometric assertions, no font
  dependence.
- **Alternatives rejected**: Screenshot comparison (existing refs cover
  visuals; geometry needs numbers).
