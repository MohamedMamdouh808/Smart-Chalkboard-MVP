# Data Model: Resizable Window Mode

**Feature**: `002-resizable-window-mode` | **Date**: 2026-10-03
**Sources**: `spec.md`, clarify 2026-10-03, `research.md`

Board, Element, Command, History, and Lesson are UNCHANGED (engine
untouched). This feature adds three UI-layer entities only.

## WindowPreferences

- Fields: `mode: fullscreen | normal | maximized` (default `fullscreen`
  on fresh install), `geometry: bytes | null` (Qt geometry blob for
  size+position; null when never windowed), `last_saved_at: str | null`.
- Rules: written at close only; read before first paint; corrupt/missing
  → defaults; never stored in lesson data (FR-005 isolation).
- Lifecycle: close → save; startup → restore → show.

## Viewport

- Derived per paint/input event from `(view_w, view_h)` and the fixed
  canvas 1920×1080 — never stored.
- Fields: `scale: float = min(view_w/1920, view_h/1080)`,
  `ox: float = (view_w − 1920·scale)/2`,
  `oy: float = (view_h − 1080·scale)/2`.
- Rules: uniform scale (no distortion), centered (letterbox split evenly),
  invertible (`to_screen`/`to_canvas` exact inverses); one formula shared
  by paint, pen, mouse, and selection hit-test.
- Letterbox margins share the board background tone (no scrolling).

## TextLayout (render-time only)

- Rule: wrap inside the fixed element box; box size/coordinates immutable.
- Fit gate (app layer, creation path): `fits(text, box, font)` via font
  metrics → reject with "Text is too long for this element. Resize it or
  shorten the text." when false.
- Overflow rule: post-resize shortfall clips at the box edge in paint
  only; layout and coordinates unchanged.

## State transitions (window)

`fullscreen ⇄ normal ⇄ maximized` via toggle button or F11 at any time;
content and selection identical across transitions (verified by state
comparison). Dialogs: open → (parent resize/move) → recentered → single
outcome (accept/reject/timeout-as-cancel).
