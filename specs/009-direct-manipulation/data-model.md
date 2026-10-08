# Data Model: Direct Manipulation

**Feature**: `009-direct-manipulation` | **Date**: 2026-10-05
**Sources**: Approved `spec.md`, `research.md`, constitution v1.0.0

The board, command, history, lesson, queue, and persistence shapes remain
unchanged. This feature adds gesture-selection geometry and a transient
gesture state; it does not add stored element fields or AI commands.

## Element geometry

- Authoritative geometry remains integer canvas-space:
  - `x`, `y`, `width`, `height`
  - canvas bounds `0 <= x`, `0 <= y`, `x + width <= 1920`, `y + height <= 1080`
  - universal minimum dimension: 24 canvas units
- Drawings additionally carry:
  - all stroke point lists;
  - one nominal stroke width;
  - point coordinates that move or scale with the element;
  - a bounding box recalculated from points plus half the nominal width.
- Stored stroke widths remain unchanged by manual resizing.
- Existing topmost/z-order behavior remains authoritative for overlapping elements.

## Drawing bounding geometry

Fields used by the canonical calculation:

- `stroke_points`: every retained point from every stroke;
- `nominal_stroke_width`: one width shared by the drawing element;
- `half_width`: nominal width divided by two;
- `raw_min_x`, `raw_max_x`, `raw_min_y`, `raw_max_y`: point extrema;
- `expanded_min_x`, `expanded_max_x`, `expanded_min_y`, `expanded_max_y`: extrema extended by `half_width`;
- `bounds`: expanded extrema enlarged to at least 24 units, centered when necessary, and clamped into the canvas.

The regression contract anchors width-8 scribble-plus-line geometry at:

```text
(96, 106, 728, 118)
```

## Hit-test outcome

Each pointer evaluation produces:

- `target_element_id`: selected object or `None` for empty space;
- `corner`: `nw`, `ne`, `sw`, or `se` when a selected element’s handle is pressed, otherwise `None`;
- `canvas_point`: pointer location after viewport conversion;
- `viewport_scale`: window-size-dependent scale used for handle-target expansion;
- `selection_after_press`: newly selected object, or `None` when empty space was pressed.

Type-specific rules:

- heading, text, equation, and rectangular shapes: authoritative rectangle containment;
- circle: normalized ellipse containment;
- line and arrow: segment proximity within drawing tolerance;
- triangle: polygon containment;
- drawing: stroke-segment proximity within six canvas units, or bounding-box containment.

## Corner handles

Each selected element has four interactive corners:

- `nw`, `ne`, `sw`, `se`;
- the pressed corner is active;
- the diagonally opposite corner is fixed;
- visual size remains the current 14-unit square;
- interaction size is the larger of the visual square and a 24-screen-pixel square;
- hover uses the diagonal resize cursor appropriate to the active/fixed diagonal.

## Gesture snapshot and preview

A gesture captures a transient, non-persistent snapshot:

- `gesture_state`: `idle`, `dragging`, or `resizing`;
- `pointer_key`: the active mouse, tablet, or touch pointer;
- `element_id`: gesture target;
- `original_geometry`: pre-gesture rectangle;
- `original_points`: copied drawing point lists when applicable;
- `grab_offset`: pointer position relative to the element origin for drags;
- `active_corner` and `fixed_corner`: corner pair for resizes;
- `preserve_aspect`: true for drawings, shapes, and equations; false for headings and text;
- `preview_geometry`: clamped candidate rectangle;
- `preview_points`: drawing points transformed only for display;
- `cancelled`: true when Escape, mode change, invalid geometry, or failed commit clears the gesture.

Previews never enter `Board`, history, persistence, autosave, or command payloads.

## Gesture commit

A completed gesture produces one commit intent:

- drag: standard `move_item` with explicit integer position;
- resize: existing `resize_item` dimensions plus engine-method-only fixed-corner metadata;
- `target_id`: manipulated element;
- `source`: `"ui"`;
- timestamp: existing informational command-timestamp shape;
- queue: existing FIFO `submit_and_run`;
- history: exactly one reversible entry with an inverse;
- engine selection: manipulated element remains selected.

Rejected, blocked, full-queue, unchanged, or cancelled gestures produce:

- no element mutation;
- no board-version increment;
- no history-record increment;
- retained or explicitly refreshed original rendering.

## State transitions

```text
idle press-select/handle-press
  -> active press candidate
  -> dragging after movement threshold
  -> resizing after movement threshold
  -> release with movement and valid geometry -> one queued commit -> idle
  -> release without movement -> click selection -> idle
  -> Escape/mode change/invalid commit -> cancelled preview -> idle
```

## Entity-to-story mapping

- US1 selection outlines: element geometry, drawing bounding geometry, hit-test outcome, corner handles.
- US2 dragging: gesture snapshot, drag preview, `move_item` commit, empty-space deselection.
- US3 resizing: corner handles, fixed-corner resize preview, `resize_item` commit, aspect policy, minimum/canvas validation, text-box wrapping.
