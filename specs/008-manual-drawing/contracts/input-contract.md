# Input Contract

- `BoardView` handles `QTabletEvent` (position + pressure), `QMouseEvent`
  press/move/release, and `QTouchEvent` through ONE collector; exactly
  ONE active pointer (by id) — further contacts ignored while down.
- Every sample converts screen→canvas via `Viewport.to_canvas` at sample
  time; samples starting outside the board are ignored; outside points
  clip to the canvas edge.
- Modes (owned by `MainWindow`, default Select): Pen → press-drag paints
  the live stroke; Select → click hit-tests (box first, then 6-unit
  stroke distance). Toggle button + P/S shortcuts.
- On release the view emits `StrokeFinished(list[{x, y, pressure?}])`
  (canvas space). The app layer groups (1.5 s, no interruption) and
  commits internal `AddDrawing` through the engine — never an
  AI-addressable command; pen input keeps working with no network.
