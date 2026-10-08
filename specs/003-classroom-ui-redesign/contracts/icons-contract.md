# Icons Contract

- Location: `src/smartboard/ui/icons/` (bundled SVGs, stroke-style like
  Lucide/Material Symbols): `mic, undo, redo, window, check, alert,
  question, error, dot-idle, dot-processing, dot-validating,
  dot-executing`.
- Loading: `ui/icons.py` caches and returns `QIcon`s; strokes tinted at
  load to the theme text color. Missing file → build-time test failure,
  never a silent fallback.
- Rule: NO emoji in chrome (buttons, pill, chip, dialogs). Text labels
  always accompany icons.
