# Research: Infinite Board

**Feature**: `013-infinite-board`
**Date**: 2026-10-08
**Status**: All Phase 0 technical unknowns resolved; three reversible UI defaults are recorded as assumptions pending final product confirmation.

## 1. Camera ownership and lesson JSON shape

- **Decision**: Add `CameraState(pan_x, pan_y, zoom)` in the application layer (`src/smartboard/app/camera.py`). `CommandEngine` and `Board` never receive camera objects. Lesson snapshots use the existing bare-board shape plus a sibling `camera` object:
  ```json
  {
    "lesson_id": "lesson_001",
    "version": 7,
    "elements": [],
    "selected_element_id": null,
    "camera": {"pan_x": 0.0, "pan_y": 0.0, "zoom": 1.0}
  }
  ```
- **Rationale**: This preserves the constitution’s UI-independent core and single-writer engine. Camera motion remains application view state; SQLite needs no schema migration because snapshots remain opaque JSON.
- **Alternatives considered**:
  - Store camera inside `Board`: rejected because it would mix transient view state into engine-owned board state and history snapshots.
  - Store camera only in OS/window settings: rejected because lessons must reopen with their saved camera and legacy snapshots must migrate deterministically.
  - Create a new SQLite table/column: rejected as unnecessary indirection for an opaque snapshot payload.

## 2. Camera coordinates and transform semantics

- **Decision**: `pan_x` and `pan_y` are the world coordinates visible at screen origin `(0, 0)`:
  ```text
  screen = (world - pan) * zoom
  world = screen / zoom + pan
  ```
  Limits: `0.10 <= zoom <= 4.00`; pan and world geometry use finite floats bounded by `MAX_WORLD_COORD = 1_000_000.0`.
- **Rationale**: Origin-anchored pan makes zoom-about-cursor exact with one closed-form update:
  ```text
  world_anchor = screen / old_zoom + old_pan
  new_zoom = clamp(old_zoom * factor)
  new_pan = world_anchor - screen / new_zoom
  ```
  It also makes the visible world rectangle trivial:
  ```text
  visible = (pan_x, pan_y, view_width / zoom, view_height / zoom)
  ```
- **Alternatives considered**:
  - Center-anchored camera: rejected because every viewport resize would change the stored pan semantics and complicate cursor-anchored zoom.
  - Separate scale/offset object in `BoardView` only: rejected because placement, AI context, persistence, and export need the same canonical math.

## 3. Removing finite-canvas bounds while retaining sanity checks

- **Decision**:
  - Delete canvas dimensions, `clip_point`, `fits_canvas`, `bbox_inside_canvas`, `grow_canvas`, and canvas-growth signals.
  - Keep `MIN_SIZE = 24`, resize scale range, text-length limits, color/shape enums, and other deterministic validation.
  - Add finite numeric guards:
    ```text
    MAX_WORLD_COORD = 1_000_000.0
    MAX_WORLD_SIZE = 1_000_000.0
    ```
  - Geometry outside those finite limits fails with the retained typed code `E_OUT_OF_BOUNDS`, but its teacher-facing message must change from board-edge language to numeric-range language.
- **Rationale**: “Infinite” means no page edge, not unbounded floats or unbounded image allocations. A finite guard preserves determinism, JSON safety, and export sanity without reintroducing spatial clipping.
- **Alternatives considered**:
  - Unlimited IEEE doubles: rejected because extreme values can break JSON serialization, transforms, painting, and exports.
  - Keep canvas fields but ignore them: rejected because dead bounded-canvas state would invite regressions and contradict the feature.
  - Introduce a new error code for numeric limits: rejected because the existing typed taxonomy already has a suitable out-of-range code; only its message needs modernization.

## 4. Deterministic voice placement without giving the engine camera state

- **Decision**: The orchestrator normalizes creation payloads before queueing:
  - Explicit AI/user positions are preserved unchanged.
  - Missing positions are replaced with an explicit world position from a pure application-layer placement function using the current visible rectangle.
  - Relative voice distances are converted from zoom-relative input into explicit world distances before execution:
    ```text
    world_distance = base_distance / zoom
    ```
  - The history record contains the normalized explicit command, so replay remains deterministic without camera context.
- **Rationale**: This satisfies both the world-scaled voice requirement and constitution determinism. The engine still sees a self-contained command; camera state never enters validation, history, or board content.
- **Alternatives considered**:
  - Pass camera/viewport into `CommandEngine.execute`: rejected because it would leak view state into validation/history and make replay camera-dependent.
  - Keep legacy canvas-proportional defaults: rejected because they are meaningless in an unbounded world.
  - Store unnormalized relative commands plus zoom in history: rejected because redo/replay would depend on transient camera state.

## 5. Visible-area placement policy

- **Decision**: Use a deterministic world-space scan:
  1. Start at the visible rectangle’s top-left plus a fixed margin.
  2. Use fixed default sizes: heading `800×96`, text `600×120`, equation `320×80`, default shape `200×200`.
  3. Sort visible elements by `(y, x)` and move the candidate below the first intersecting element plus a fixed gap.
  4. Accept the first non-overlapping candidate; if the visible area is full, place below the lowest visible element as the specified “when possible” fallback.
- **Rationale**: The behavior is predictable, testable, zoom-independent in world space, and directly implements “near top-left, below nearby content when possible.”
- **Alternatives considered**:
  - Retain global bottom stacking: rejected because new voice elements could appear far outside the viewport.
  - Random/nearest-empty-space search: rejected for nondeterminism and implementation complexity.
  - Camera-relative screen placement without world conversion: rejected because stored coordinates must remain world units.

## 6. Internal text operations and history semantics

- **Decision**:
  - Double-click on empty space creates a provisional overlay only; committing valid text issues one public `create_text` operation through the queue/engine.
  - Cancelling an empty new-text overlay discards the provisional state and creates no engine entry.
  - Editing existing heading/text/equation calls a new internal `CommandEngine.edit_text`, which validates target and text and records one swap-inverse history entry.
  - Clearing existing text and committing/cancelling reverts to prior content with no history entry.
  - `edit_text` remains absent from `COMMANDS`, prompt text, AI parser acceptance, and public `execute`; this follows the existing internal `add_drawing` precedent, not a 13th AI command.
- **Rationale**: Provisional creation preserves the spec’s exact history accounting: one entry for accepted creation, zero entries for discarded empties. Snapshot inverses reuse proven undo/redo machinery.
- **Alternatives considered**:
  - Commit placeholder text immediately then delete on Escape: rejected because it would leave history side effects for a discarded action.
  - Record internal edits as public `create_text`: rejected because that would misrepresent history and redo semantics.
  - Expose `edit_text` to AI: rejected because it would violate the locked 12-command contract.

## 7. Input architecture and gesture precedence

- **Decision**:
  - `BoardView` emits view intents; `Orchestrator` owns/applies/clamps camera state and re-renders with the updated camera.
  - Precedence while Space is held: Space+drag pans in both Select and Pen modes without changing the active mode; releasing Space returns pointer behavior to the active mode.
  - Middle-button drag always pans.
  - Select-mode empty-space drag pans; empty-space click without movement only clears selection.
  - Wheel without modifiers pans; `Shift+wheel` pans horizontally; `Ctrl+wheel` zooms about the cursor.
  - Support both Qt pinch gestures and native trackpad zoom events, normalized into the same cursor-anchored zoom operation.
  - Text-overlay focus takes precedence over Space-pan so typing spaces does not move the camera.
- **Rationale**: Centralizing camera ownership prevents widget/application divergence. The precedence rules preserve existing pen behavior while making navigation available everywhere.
- **Alternatives considered**:
  - Let the widget mutate authoritative camera directly: rejected because persistence, AI placement, and export need one application-owned source.
  - Disable Space-pan in Pen mode: rejected as the current default because the spec describes Space-dragging as mode-preserving navigation; this remains reversible if product confirmation chooses otherwise.
  - Support only native gestures or only `QPinchGesture`: rejected because trackpads and touchscreens may deliver different Qt event types across platforms.

## 8. Rendering, culling, grid, and constant-size affordances

- **Decision**:
  - Paint world content under a camera transform:
    ```text
    translate(-pan_x * zoom, -pan_y * zoom)
    scale(zoom, zoom)
    ```
  - Prefilter elements by world-rectangle/viewport intersection before painting; retain linear culling for the required 200-element target rather than adding a spatial index.
  - Draw the dot grid in screen space from a fixed world lattice with power-of-two zoom-dependent spacing, keeping on-screen dot pitch in a comfortable range and dot radius constant in screen pixels.
  - Reset the transform before painting selection outlines, handles, and highlight rings so stroke widths and handle sizes remain constant in screen space.
  - Extract read-only element painting into a shared UI-layer helper used by both `BoardView` and PNG export.
  - Scale pointer hit tolerance as `screen_tolerance / zoom` so selection remains usable at 10% and precise at 400%.
- **Rationale**: World-space painting preserves zoom behavior; screen-space adornments preserve Figma-like handle usability. Linear culling is sufficient and avoids premature indexing complexity.
- **Alternatives considered**:
  - Paint handles in world space: rejected because handles would become unusably small at 10% and oversized at 400%.
  - Full-scene spatial index: rejected as unnecessary for 200 elements and an added invalidation risk.
  - Fixed world grid spacing: rejected because dots would collapse into noise when zoomed out or disappear visually when zoomed in.
  - Duplicate painting code in exporter: rejected because exporter and interactive rendering would diverge.

## 9. Inline editor control choice

- **Decision**:
  - Heading: `QLineEdit`.
  - Text and equation: `QPlainTextEdit`.
  - Enter commits; `Shift+Enter` inserts a newline in multiline editing; Escape cancels.
  - The overlay is positioned from the element’s current screen rectangle and follows camera changes while open.
- **Rationale**: Single-line headings get native Enter-to-commit behavior, while wrapped text/equations retain multiline editing. Camera-following preserves the world anchor during navigation.
- **Alternatives considered**:
  - `QLineEdit` for everything: rejected because it would lose multiline text behavior.
  - `QPlainTextEdit` for everything: rejected because headings do not need multiline editing affordances.
  - Modal dialog editing: rejected because it breaks direct in-place editing and world anchoring.

## 10. AI context limits and prompt wording

- **Decision**:
  - Replace canvas dimensions with `viewport: {x, y, width, height, zoom}`.
  - Send selected element plus visible and nearby elements, capped at `MAX_AI_ELEMENTS = 50`.
  - Nearby means intersecting the visible rectangle expanded by one viewport width/height in each direction, ordered by visibility then distance.
  - Keep the prompt short: unbounded-world coordinate guidance, viewport bounds, compact element lines, transcript, and existing command/clarification rules.
  - Preserve least-exposure summaries; do not send full stroke-point arrays or audio.
- **Rationale**: Voice placement and relative-move reasoning require viewport awareness, but unbounded boards could otherwise send unbounded context. A deterministic cap preserves latency, privacy, and testability.
- **Alternatives considered**:
  - Send all elements: rejected for unbounded prompt growth and privacy/latency exposure.
  - Send only strictly visible elements: rejected because commands may refer to just-offscreen nearby content.
  - Send camera pan/zoom without world bounds: rejected because providers reason more reliably with explicit world bounds.

## 11. Migration, persistence, and export

- **Decision**:
  - `Board.from_dict` ignores legacy `canvas` data and preserves element coordinates exactly.
  - A lesson-document loader normalizes:
    - New snapshots with sibling `camera`.
    - Legacy bare-board snapshots with default camera at origin/100%.
    - Legacy snapshots containing canvas dimensions with a centered 100% camera derived from the old canvas size and current view size.
  - Drawing bounds are recomputed in unbounded world space without clamping.
  - Export computes the union of canonical world bounds, adds a fixed 48-unit margin, renders at 100%, and produces a fixed 960×540 empty-lesson image.
- **Rationale**: Coordinates remain authoritative while only the viewing model changes. Centering legacy lessons preserves their visual composition without moving content.
- **Alternatives considered**:
  - Migrate legacy coordinates into a new origin scheme: rejected because it would alter saved lessons.
  - Preserve canvas fields in new snapshots: rejected because bounded-canvas state must be removed.
  - Export the current viewport instead of content bounds: rejected because the spec explicitly requires content-bounds export.

## 12. Test strategy

- **Decision**: Follow the user-requested pytest/pytest-qt coverage:
  - Pure unit tests for transforms, placement, lesson documents, numeric guards, AI context caps, and engine behavior.
  - `pytest-qt`/offscreen widget tests for wheel, Space, middle-button, pinch-normalized zoom, double-click creation/editing, overlay commit/discard, drag/resize across zoom, constant handle size, culling, grid smoke behavior, camera persistence, fit-all, and history invariance.
  - Integration tests for voice placement/context, migration, export, and a 200-element performance check.
  - Update or retire obsolete canvas-bound tests rather than preserving contradictory expectations.
- **Rationale**: The requested behaviors span pure math, deterministic engine rules, Qt event handling, and persistence; each layer needs the appropriate test harness.
- **Alternatives considered**:
  - Widget-only testing: rejected because engine determinism and math deserve fast headless tests.
  - Unit-only testing: rejected because Qt event routing and overlay behavior cannot be proven without widgets.
  - Preserve all legacy canvas-bound tests unchanged: rejected because they assert behavior this feature intentionally removes.
