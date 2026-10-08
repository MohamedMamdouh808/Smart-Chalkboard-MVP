# Geometry Contract

## Canonical drawing bounds

- `drawing_bbox` is the sole function for deriving drawing bounds from:
  - all points in all strokes; and
  - half the drawing’s nominal stroke width.
- It must expand each point extremum by half the stroke width before applying:
  - the 24-canvas-unit minimum; and
  - canvas containment.
- Existing callers and affected tests must be updated to the revised signature.
- The width-8 scribble-plus-straight-line regression must equal:
  - `(96, 106, 728, 118)`.
- Pressure-specific rendered width does not alter the canonical nominal-width envelope.

## Mandatory recalculation

The canonical function must be used after every drawing-affecting path:

- stroke-group creation;
- drawing move;
- drawing resize;
- undo;
- redo;
- restoration from persisted lesson JSON.

Restored or legacy snapshots must have their bounds refreshed from stored points before selection, hit-testing, rendering, or gesture use.

## Drag preview and commit geometry

- Store the press point’s offset from the element origin.
- Candidate position:
  - `x = original_x + pointer_delta_x`;
  - `y = original_y + pointer_delta_y`.
- Clamp the candidate so the complete original width and height remain inside the canvas.
- Quantize the committed position to integer canvas coordinates.
- Drawing points translate by the committed delta.

## Resize preview and commit geometry

- The pressed corner is active; the diagonally opposite corner is fixed.
- For drawings, shapes, and equations:
  - derive candidate dimensions from pointer displacement relative to the fixed corner;
  - preserve the original width-to-height ratio by default.
- For headings and text:
  - derive candidate width and height independently;
  - retain existing box-based text wrapping after commit.
- Enforce dimensions of at least 24 canvas units.
- Clamp candidate geometry so it remains inside the canvas while retaining the fixed corner.
- Quantize committed dimensions and origin to integer canvas coordinates.
- Scale drawing points proportionally about the fixed corner.
- Retain each stroke’s stored width.
- Recalculate the drawing bounds after point scaling.

## Invalid geometry

- A release with no movement is a click selection, not a gesture commit.
- A release whose geometry cannot be made valid under minimum-size and canvas-containment rules cancels without:
  - state mutation;
  - version increment;
  - history entry.
