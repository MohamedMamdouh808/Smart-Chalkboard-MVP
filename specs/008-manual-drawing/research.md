# Research: Manual Drawing

**Feature**: `008-manual-drawing` | **Date**: 2026-10-04
**Input**: spec + 2026-10-04 clarifications + user technical brief
(QTabletEvent/QMouseEvent/QTouchEvent, single active pointer, viewport
transform, StrokeFinished signal, internal AddDrawing + inverse, Drawing
element shape, segment hit-test at 6 units, overlay + QPainterPath
render, point reduction, JSON serialization, pytest/pytest-qt matrix)

No NEEDS CLARIFICATION: the brief prescribes each mechanism; two values
supersede older defaults (tolerance 6 units, see R-05).

## Decisions

### R-01: One unified pointer path, single active pointer

- **Decision**: `BoardView` handles `tabletEvent` (position + pressure),
  mouse press/move/release, and touch events through one collector that
  accepts exactly one active pointer (by pointer id); a second contact
  while one is down is ignored. Every sample converts screen→canvas via
  `Viewport.to_canvas` at sample time. No pen-protocol dependency; mouse
  works with no pen present.
- **Rationale**: Spec FR-001/FR-009; one-pointer rule kills
  multi-touch/palm streaks without any tuning UI.
- **Alternatives rejected**: Per-device handlers with separate state
  (drift between paths); multi-pointer (explicitly out of scope).

### R-02: Mode-gated events, Select default

- **Decision**: `MainWindow` owns the Pen/Select toggle (button + P/S
  shortcuts, Select default per clarify). BoardView exposes
  `set_mode()`; in Pen mode press-drag paints the live stroke, in
  Select mode clicks hit-test (existing box test first, then
  stroke-distance per R-05).
- **Rationale**: Spec FR-002 + clarify lock; Select-default means stray
  contact can never draw.
- **Alternatives rejected**: Modeless draw-near-content (ambiguous with
  selection); Pen default (rejected in clarify).

### R-03: StrokeFinished → grouped AddDrawing through the engine

- **Decision**: On release, BoardView emits `StrokeFinished(list of
  canvas-space `{x, y, pressure?}` points). The app layer groups per the
  1.5 s rule (existing `StrokeGrouper` semantics) and commits via an
  internal `AddDrawing` engine operation with a stored inverse (element
  snapshot) — undo removes, redo restores byte-identically. Pending
  strokes live in the view/app layer, never in board state, so resizes
  and queued voice commands cannot lose or corrupt them.
- **Rationale**: Spec FR-003/FR-004/FR-009; engine stays UI-free (plain
  point data in, validated element out).
- **Alternatives rejected**: Direct board mutation from the view
  (violates single-writer + determinism gates).

### R-04: Drawing element behavior = element behavior

- **Decision**: `Drawing {id, strokes[{points[{x,y,pressure?}], width,
  color}], bbox}`; bbox derived from points. Engine `move_item`
  translates all points, `resize_item` scales them about the bbox
  origin, `change_color` recolors, `delete_item` confirms — all through
  the existing validators (bounds, confirmation, history). New
  voice-created elements append; strokes are never rewritten.
- **Rationale**: Spec FR-005/FR-006; zero new command surface.
- **Alternatives rejected**: Drawings as second-class overlays (breaks
  undo/voice/save uniformity).

### R-05: 6-unit segment hit-test (brief supersedes spec default)

- **Decision**: Selection hit = minimum distance from tap point to any
  stroke segment ≤ 6 canvas units; outline + handles over the element
  bbox. The spec's "~12 units" assumption is superseded by the brief's
  explicit 6 units (tighter = fewer accidental picks next to text).
- **Rationale**: User-brief directive; exact, testable, recorded here
  so the older default cannot resurface.
- **Alternatives rejected**: Bbox-only picking (selects empty space
  inside loops); 12 units (spec default, explicitly replaced).

### R-06: Overlay live paint, QPainterPath committed paint

- **Decision**: In-progress stroke paints on a temporary overlay layer
  (cleared on commit/cancel); committed drawings paint in the normal
  board pass in z-order via `QPainterPath` with round caps/joins,
  pressure-scaled width when pressure is present, element width
  otherwise (thin 2 / medium 4 default / thick 8).
- **Rationale**: Spec FR-002/FR-010; overlay keeps uncommitted ink out
  of state snapshots and exports.
- **Alternatives rejected**: Painting live ink into board state (would
  leak into saves/exports/undo).

### R-07: Distance-threshold point reduction + JSON storage

- **Decision**: Drop samples closer than ~2 canvas units to the last
  kept point (keeps endpoints); drawings serialize inside the existing
  board JSON (`strokes`, `width`, `color`); save/reopen round-trips
  byte-identically (existing snapshot path, no schema migration — the
  element dict is schemaless extra data today).
- **Rationale**: User-brief directive; small JSON without visible
  quality loss.
- **Alternatives rejected**: Raw sample streams (JSON bloat on fast
  machines); Douglas-Peucker (overkill vs a threshold for classroom
  sketching).

### R-08: pytest + pytest-qt matrix with synthetic events

- **Decision**: `QTest.mousePress/Move/Release` + constructed
  `QTabletEvent`s, mapping checks at 3 sizes, grouping-timer tests
  (real 1.5 s clock, short suite), undo/redo round-trips, voice-style
  move/resize/recolor/delete on drawings, off-canvas strokes, resize
  mid-stroke, save/reopen round-trip — all headless offscreen, no
  hardware.
- **Rationale**: User-brief directive; every spec acceptance maps to a
  test.
- **Alternatives rejected**: Hardware-only testing (unrepeatable in CI).

## Performance notes

- Live overlay repaint is one path per frame; hit-test is linear in
  segments but only runs on clicks, not on move — no per-frame cost.
- Point reduction bounds JSON and repaint work for long sessions.
