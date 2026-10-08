# Widgets Contract

## MicButton (`ui/mic_button.py`, `QPushButton` subclass)

- Fixed 112px circle; `voiceState` property in
  `idle|listening|processing|validating|executing`; per-state ring/fill
  painted in `paintEvent`; `QPropertyAnimation` on `pulse` (~1 Hz) only
  while `listening` (static ring under reduced motion).
- Hover/pressed/disabled/focus treatments from generated QSS.

## StatusPill + ResultChip

- Pill: current pipeline state as (color, icon, text); chip (top bar
  right): `Heard:` label + transcript (≥20px; placeholder "Hold the mic
  and speak a command" when empty) + outcome triple for
  `done|needs_confirmation|needs_clarification|error`.
- Both render triples handed down from pipeline state/results; they own
  no state machine. Color is never the sole signal.

## BoardView additions

- Paints surface (shadow → fill → border, 24px radius), elements
  (unchanged mapping), selection outline + 4 square corner handles,
  highlight ring. Fonts from tokens (heading 64 / body 36 at scale 1).

## Dialogs + title

- Confirm/clarify dialogs share the theme; Cancel/Confirm ≥48px high,
  centered (002 behavior kept). Window title exactly `"Smart Chalkboard"`.
- Undo/Redo show disabled styling iff history cannot undo/redo; main
  window refreshes their enabled state after every engine result.
