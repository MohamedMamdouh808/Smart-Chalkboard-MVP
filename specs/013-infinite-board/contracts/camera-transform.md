# Contract: Camera and World/Screen Transforms

## Camera JSON

```json
{
  "pan_x": 120.0,
  "pan_y": -40.0,
  "zoom": 1.5
}
```

Validation:

- `pan_x` and `pan_y` are finite numbers within `±1_000_000.0`.
- `zoom` is a finite number in `[0.10, 4.00]`.
- Invalid camera snapshots normalize to the nearest valid value; invalid types fall back to `0.0, 0.0, 1.0`.

## Transform invariants

For screen origin `(0, 0)`:

```text
screen = (world - pan) * zoom
world = screen / zoom + pan
```

Required properties:

1. `screen_to_world(world_to_screen(point)) == point` within floating-point tolerance.
2. `world_to_screen(screen_to_world(pixel)) == pixel` within floating-point tolerance.
3. Zoom-about-cursor leaves the world coordinate beneath the cursor unchanged.
4. Panning changes only camera state; element coordinates, board version, selection, and history remain unchanged.
5. Reset returns zoom exactly to `1.0`.
6. Fit-all frames every element’s canonical world bounds.

## Camera operation contract

| Operation | Input | Result |
|---|---|---|
| Pan by screen pixels | `dx`, `dy` | `pan += (dx / zoom, dy / zoom)` |
| Zoom about cursor | screen point, factor | Clamped zoom; pan adjusted to preserve cursor world anchor |
| Reset | none | `zoom = 1.0`; pan unchanged |
| Fit all with content | world bounds + view size | Zoom clamped to `[0.10, 4.00]`; all bounds visible |
| Fit all without content | none | Sensible default view; no content/history changes |

No camera operation may:

- mutate board elements;
- increment board version;
- append history;
- alter selection;
- supply camera state to engine validation.
