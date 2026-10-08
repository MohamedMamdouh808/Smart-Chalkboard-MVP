# Data Model: Manual Drawing

**Feature**: `008-manual-drawing` | **Date**: 2026-10-04
**Sources**: `spec.md`, clarify 2026-10-04, `research.md`

Board, Command, History, Lesson, and the engine pipeline are UNCHANGED
in shape; drawings ride them as a new element type.

## Drawing element

- Identity: `id = drawing_NNN`, unique per lesson, never reused
  (existing ID generator).
- Fields: `strokes: [{points: [{x, y, pressure?}], width: 2|4|8,
  color: str}]`, `bbox {x, y, w, h}` derived from points (min/max),
  standard `z` ordering with all other elements.
- Width: one of thin 2 / medium 4 (default) / thick 8 canvas units,
  fixed per element, chosen in settings (clarify lock — no bar control).
- Color: palette color active at stroke start; explicit recolor changes
  the whole element.

## Pending stroke (never stored)

- Fields: ordered canvas-space points + source pointer id; lives in the
  view/app layer from press to release/group-close. Never in board
  state, history, saves, or exports.

## Grouping + commit

- Open group accumulates strokes while each new stroke starts within
  1.5 s (LOCKED) of the previous pen-up with no selection/command
  between; otherwise the group closes and commits as one internal
  `AddDrawing` operation with a snapshot inverse (undo removes, redo
  restores identically).
- Resize scales points about the bbox origin; move translates them;
  both revalidate bounds through existing validators.

## Selection (drawings)

- Hit: min point-to-segment distance ≤ 6 canvas units (brief value,
  supersedes the spec's ~12 default); ties broken by z-order.
- Adornment: existing outline + corner handles over the bbox.

## State transitions

`press → samples → release → StrokeFinished → group open/close →
AddDrawing → history → autosave`. Voice commands interleave only via
the queue; resizes only change the viewport under live samples.
