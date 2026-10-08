# Data Model: Dev Input Bottom Bar

**Feature**: `006-dev-input-bottom-bar` | **Date**: 2026-10-04
**Sources**: `spec.md`, `research.md`

No board, command, history, or theme-token entities change. One widget
changes parent; one layout gains a stretched, capped child.

## DevInput (moved, not remade)

- Same `QLineEdit`: placeholder "Dev transcript — type a command and
  press Enter", Enter submits transcript → clears, full-text tooltip
  behavior unchanged, visible iff `SMARTBOARD_DEV_INPUT == "1"`.
- New home: bottom-bar `QHBoxLayout` between Redo and the status pill,
  `stretch=1`, `setMaximumWidth(700)`, fixed height = 44px compact
  token, ≥18px theme font, visible focus outline from the button-focus
  styling language.
- Disabled (subtle, theme-consistent) from submit until result delivery.

## Bar layouts after the move

- Bottom: mic, Undo, Redo, dev-input (stretch 1, ≤700px, centered),
  status pill. Flag off: mic, Undo, Redo, stretch, pill — identical to
  the current bar.
- Top: "Heard:" label, transcript (stretch), result chip, Window button
  — transcript keeps the freed room.

## State transitions

None added or altered: submit → disabled → result → enabled + cleared;
flag evaluation at construction only.
