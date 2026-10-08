# Data Model: Infinite Board

**Feature**: `013-infinite-board`
**Date**: 2026-10-08

## 1. Board

Retained engine-owned board content, without canvas dimensions.

| Field | Type | Constraints |
|---|---|---|
| `lesson_id` | `str` | Required, non-empty lesson identifier. |
| `elements` | `list[Element]` | Ordered content; z-order remains list order plus `z`. |
| `selected_element_id` | `str \| None` | Transient selection; must reference an existing element when non-null. |
| `version` | `int` | Monotonic board version; increments on every accepted board mutation. |

State transitions:

- Accepted command/internal operation → mutate elements/selection → increment `version` → append one history entry, except camera motion, selection changes, provisional overlay edits, and other explicitly non-history actions.
- Undo/redo → apply stored inverse/forward snapshot → increment `version`.
- Camera operations → no board transition, no version change, no history entry.

Serialization:

- New board payload contains `lesson_id`, `version`, `elements`, and `selected_element_id`.
- No `canvas`, `canvas_width`, or `canvas_height` fields are emitted.
- Deserialization ignores legacy canvas fields.

## 2. Element

All geometry remains in unbounded world units.

| Field | Type | Constraints |
|---|---|---|
| `id` | `str` | Required deterministic engine-issued ID. |
| `type` | `str` | `heading`, `text`, `shape`, or `drawing`. |
| `x`, `y` | `float`/`int` | Finite world coordinates within `±MAX_WORLD_COORD`. |
| `width`, `height` | `float`/`int` | `>= MIN_SIZE`; finite and `<= MAX_WORLD_SIZE`. |
| `color` | `str` | Existing named-color or `#RRGGBB` validation. |
| `z` | `int` | Existing stacking order. |
| `extra` | `object` | Type-specific payload, including text/shape/drawing data. |
| Text content | `str` | Heading: 1–200 characters; text/equation: 1–2000 characters. |

Drawing-specific rules:

- `strokes[].points[].x/y` are finite world coordinates.
- Stored stroke `width` is constant in world units.
- Canonical drawing bounds are derived from all points plus half stroke width, expanded to `MIN_SIZE`, and never clamped to a canvas.
- Pressure remains optional per-point metadata.

Validation transitions:

- Creation/move/resize/text edits validate finite numeric range and minimum size.
- Out-of-range geometry fails with retained `E_OUT_OF_BOUNDS`; the message must describe numeric range, not a page edge.
- Rejected operations leave board state, version, selection, and history unchanged.

## 3. CameraState

Application-owned transient view state, persisted only as lesson metadata.

| Field | Type | Constraints |
|---|---|---|
| `pan_x` | `float` | Finite world x visible at screen origin. |
| `pan_y` | `float` | Finite world y visible at screen origin. |
| `zoom` | `float` | `0.10 <= zoom <= 4.00`; `1.0` means 100%. |

Derived transient data, never persisted directly:

| Field | Meaning |
|---|---|
| `view_width`, `view_height` | Current widget dimensions in screen pixels. |
| `visible_rect` | `(pan_x, pan_y, view_width / zoom, view_height / zoom)`. |
| `screen_point` | `(world - pan) * zoom`. |
| `world_point` | `screen / zoom + pan`. |

State transitions:

- Pan, zoom-about-cursor, reset, and fit-all update camera only.
- Camera updates never mutate `Board`, `version`, or history.
- Widget dimensions update the derived visible rectangle but are not saved.
- Closing/autosaving serializes the latest camera alongside board content.

## 4. LessonDocument

Application-level lesson envelope stored as opaque JSON in `board_states.state_json`.

| Field | Type | Constraints |
|---|---|---|
| `lesson_id` | `str` | Required. |
| `version` | `int` | Board version at save time. |
| `elements` | `list` | Board element payloads. |
| `selected_element_id` | `str \| None` | Selection at save time. |
| `camera` | `CameraSnapshot` | `pan_x`, `pan_y`, `zoom`. |

Migration rules:

- New document → validate board and camera, then restore both.
- Legacy bare-board document → preserve elements/selection/version; camera defaults to origin at 100%.
- Legacy document with canvas dimensions → preserve coordinates; derive an initial 100% camera that centers the old canvas rectangle in the current view.
- Unknown lesson/camera fields are ignored unless they affect coordinate or camera interpretation.
- No SQLite schema migration is required.

## 5. VisibleViewport

Read-only derived query used by placement, AI context, rendering, and export planning.

| Field | Type | Meaning |
|---|---|---|
| `x`, `y` | `float` | Visible world origin. |
| `width`, `height` | `float` | Visible world size. |
| `zoom` | `float` | Active zoom factor. |
| `visible_ids` | `list[str]` | Deterministic IDs intersecting the viewport. |
| `nearby_ids` | `list[str]` | Deterministic IDs in the expanded viewport margin. |

It has no lifecycle or persistence; it is recomputed from camera, widget size, and board elements.

## 6. VoicePlacementRequest

Transient application-layer normalization input.

| Field | Type | Meaning |
|---|---|---|
| `command_payload` | `object` | Parsed provider payload before queueing. |
| `viewport` | `VisibleViewport` | Placement/search context. |
| `zoom` | `float` | Relative-distance scaling input. |
| `normalized_payload` | `object` | Explicit world-coordinate payload submitted to history/queue. |

Rules:

- Explicit positions are never replaced.
- Missing creation positions receive deterministic visible-area coordinates.
- Relative distances are converted to explicit world distances using current zoom.
- Normalized payloads are self-contained and replayable without camera state.

## 7. TextEditSession

Transient UI-layer editing state; never persisted and never part of board history until committed.

| Field | Type | Meaning |
|---|---|---|
| `mode` | `new \| existing` | Whether the overlay edits provisional or stored text. |
| `element_id` | `str \| None` | Existing target ID; null for provisional creation. |
| `kind` | `heading \| text` | Heading uses single-line editing; text/equation uses multiline editing. |
| `world_anchor` | `point` | Creation point or existing element rectangle. |
| `original_text` | `str` | Stored text for existing elements; empty for new elements. |
| `current_text` | `str` | Live overlay text. |

Transitions:

- `new + commit(non-empty)` → one `create_text` history entry.
- `new + cancel/empty` → no board/history change.
- `existing + commit(changed non-empty)` → one internal `edit_text` history entry.
- `existing + cancel/empty` → revert to original text with no history change.

## 8. AIContext

Least-exposure deterministic context sent to providers.

| Field | Type | Meaning |
|---|---|---|
| `transcript` | `str` | Verbatim teacher transcript. |
| `viewport` | `object` | Visible world bounds plus zoom. |
| `selected_element_id` | `str \| None` | Current selection. |
| `elements` | `list` | Compact visible/nearby element summaries. |
| `commands` | `list[str]` | Locked 12-command allowlist. |

Rules:

- Maximum `MAX_AI_ELEMENTS = 50`.
- Visible elements precede nearby elements.
- Nearby means intersecting the viewport expanded by one viewport width/height.
- No stroke-point arrays, audio, credentials, or full board contents are included.
- Camera pan/zoom are represented only through derived world bounds and zoom.
