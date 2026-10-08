# Chrome-Layout Contract

- Order top→bottom: transcription strip, board view (stretch), control
  bar (mic, Undo, Redo, status). Board letterboxes INSIDE its view, so
  chrome can never overlap board content.
- Minimums: every control ≥ 48px in its smallest dimension; window
  minimum 960×540 keeps all chrome visible with no scrolling.
- Palette (explicit stylesheet, text + background declared together):
  text `#F5F5F5` on surfaces `#2a2a44`/`#22223a` — contrast ≥ 4.5:1,
  enforced by a luminance unit test on the declared hex values.
- Dialogs: parented to the main window (centered by default), recentered
  on parent move/resize while open; exactly one outcome per opening.
