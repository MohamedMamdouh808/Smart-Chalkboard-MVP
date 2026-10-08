# Contract: Voice Placement and AI Context

## Normalized voice creation

Before queueing, the application layer converts viewport-dependent voice input into explicit world coordinates.

| Provider payload | Application behavior |
|---|---|
| Creation with explicit `position` | Preserve position unchanged |
| Creation without `position` | Insert deterministic visible-area world position |
| Relative move with named distance | Convert using that distance’s world base divided by active zoom |
| Relative move with numeric distance | Convert numeric screen-relative distance into world distance using active zoom |
| Absolute move/resize | Preserve unchanged |

The normalized payload recorded in history must replay deterministically without camera context.

## Default placement algorithm

1. Candidate starts at visible top-left plus fixed margins.
2. Fixed default sizes apply by element kind.
3. Visible elements are scanned in `(y, x)` order.
4. The candidate moves below the first intersecting element plus a fixed gap.
5. The first non-overlapping candidate is used.
6. If no visible gap exists, the candidate goes below the lowest visible element.

Explicit positions bypass this algorithm.

## AI context shape

```json
{
  "transcript": "add a title",
  "viewport": {"x": 0.0, "y": 0.0, "width": 960.0, "height": 540.0, "zoom": 1.0},
  "selected_element_id": "text_001",
  "elements": [
    {"id": "text_001", "type": "text", "label": "F = ma", "x": 160.0, "y": 200.0}
  ],
  "commands": ["create_heading", "create_text"]
}
```

Rules:

- No canvas dimensions are sent.
- At most 50 element summaries are sent.
- Visible elements come before nearby elements.
- Nearby means intersecting the viewport expanded by one viewport dimension.
- No stroke arrays, audio, secrets, or full board state are included.
- The prompt remains short and preserves the locked 12-command allowlist.
