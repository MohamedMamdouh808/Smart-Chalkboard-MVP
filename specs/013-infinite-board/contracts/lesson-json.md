# Contract: Lesson JSON, Migration, and Export

## New lesson snapshot

```json
{
  "lesson_id": "lesson_001",
  "version": 7,
  "elements": [],
  "selected_element_id": null,
  "camera": {"pan_x": 0.0, "pan_y": 0.0, "zoom": 1.0}
}
```

Rules:

- Board content and camera are siblings in one opaque snapshot.
- Element coordinates are authoritative world coordinates.
- No canvas width/height fields are written.
- Saving serializes the latest application-owned camera.
- Reopening restores both board content and camera.

## Backward-compatible loader

| Snapshot shape | Board result | Camera result |
|---|---|---|
| New `elements` + `camera` | Restore elements/selection/version unchanged | Restore saved camera |
| Legacy bare board without `canvas` | Restore coordinates unchanged | Origin at 100% zoom |
| Legacy board with `canvas` dimensions | Ignore canvas dimensions; preserve coordinates | 100% camera centered on legacy canvas rectangle |
| Missing/corrupt camera | Restore board if valid | Default camera |

Migration must not:

- translate, scale, clamp, or round stored element coordinates;
- invent content bounds;
- create history entries;
- alter SQLite schema.

## Export contract

- Export calculates the union of canonical world bounds for all elements.
- A fixed 48-unit margin is added around content bounds.
- Rendering occurs at exactly 100% zoom.
- An empty lesson exports a valid fixed 960×540 image.
- Export is a read-only application handoff and creates no board/history changes.
