# Mapping Contract

## Viewport formula

- Viewport construction requires explicit view width/height and stored canvas width/height.
- Scale is `min(1, view_w / canvas_w, view_h / canvas_h)`.
- Offsets center the canvas when downscaling; at scale 1 the canvas origin coincides with the board drawing origin.
- Invalid view or canvas dimensions use safe non-negative defaults without raising during rendering.

## Shared geometry

- Painting, pen sampling, selection, hit-testing, drag previews, resize previews, cursors, and layout rectangles use the same viewport.
- Screen-to-canvas conversion is the exact inverse of canvas-to-screen conversion.
- No element, stroke, font, or shape geometry is stretched; only uniform display scale may be below 1.
- Letterboxing appears only when the available area is smaller than the stored canvas.

## Board-area layout

- The board widget fills its available layout area subject to existing chrome and the small-margin rule.
- Resize and show events report available widget dimensions without moving elements.
