# Hit-Test Contract

## Selection dispatch

- Select-mode pointer handling must evaluate the selected element’s handles before element bodies.
- Otherwise, selection must dispatch by element type:
  - heading: rectangle containment;
  - text: rectangle containment;
  - equation: rectangle containment;
  - shape: rendered-primitive geometry;
  - drawing: stroke-segment proximity or bounding-box containment.
- Overlapping candidates resolve through existing topmost/z-order behavior.
- Pointer actions outside every candidate return no target and clear selection.
- Malformed elements are skipped without raising.

## Shape primitives

- Rectangle: authoritative rectangle containment.
- Circle: normalized ellipse containment.
- Line and arrow: segment proximity within the established six-canvas-unit drawing tolerance.
- Triangle: polygon containment.
- Unknown shape subtypes fall back to authoritative rectangle containment without changing creation validation.

## Drawing selection

- A drawing is selected when the pointer is:
  - within six canvas units of any stroke segment; or
  - inside its recalculated bounding box.
- Bounding-box selection must use the half-stroke-width-expanded bounds.
- Empty areas inside concave ink do not defeat bounding-box selection.

## Handle detection

- Handles exist only for the currently selected element.
- Visual size remains the current 14-unit corner square.
- Interaction size is the larger of:
  - the visual square; and
  - a square equivalent to 24 screen pixels at the current viewport scale.
- A press inside an expanded handle selects that corner and begins resize candidacy.
- Hovering over a handle shows the diagonal resize cursor appropriate to its corner.
- Leaving handles restores the normal Select-mode cursor.

## Selection side effects

- Pressing a valid target updates engine selection immediately.
- Empty-space presses clear engine selection immediately.
- Selection changes alone:
  - create no history entry;
  - increment no board version;
  - invoke no history hook.
