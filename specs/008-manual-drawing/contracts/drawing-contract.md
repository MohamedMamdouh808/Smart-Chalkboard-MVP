# Drawing Contract

- Shape: `{id: drawing_NNN, strokes: [{points: [{x, y, pressure?}],
  width: 2|4|8, color}], bbox, z}`. Bbox derived from points.
- `move_item` translates every point; `resize_item` scales every point
  about the bbox origin; `change_color` recolors the element; all
  revalidate bounds/confirmation/history through existing engine paths.
- Hit-test: min point-to-segment distance ≤ 6 canvas units; z-order
  breaks ties; adornment = outline + corner handles over the bbox.
- Render: live stroke on the temporary overlay; committed drawings in
  the board pass in z-order via `QPainterPath`, round caps/joins,
  pressure-scaled width when pressure exists, element width otherwise.
- Points reduced at commit: drop samples < ~2 canvas units from the
  last kept point (endpoints always kept).
