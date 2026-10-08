# Viewport Contract

Canvas is fixed: 1920×1080, origin top-left. For a view of `view_w × view_h`:

```
scale = min(view_w / 1920, view_h / 1080)
ox    = (view_w - 1920 * scale) / 2
oy    = (view_h - 1080 * scale) / 2
```

- Forward (paint): `sx = x * scale + ox`, `sy = y * scale + oy`.
- Inverse (pen/mouse/selection): `x = (sx - ox) / scale`,
  `y = (sy - oy) / scale`. Exact inverse; round-trip error < 0.5 canvas
  units at every supported size.
- Letterbox: margins `(ox, oy)` filled with the board background tone;
  whole canvas always visible, never distorted, never cropped — EVERY
  aspect ratio, no exceptions (clarify 2026-10-03).
- Mid-stroke resize: each sample maps through the viewport current at
  sample time; committed strokes store canvas coordinates, so the element
  matches what the teacher drew.
- Single source: `ui/viewport.py`. Paint, pen, click, and hit-test MUST
  NOT reimplement this formula.
