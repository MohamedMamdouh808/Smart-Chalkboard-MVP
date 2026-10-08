# Implementation Plan: Infinite Board

**Branch**: `013-infinite-board` | **Date**: 2026-10-08 | **Spec**: [specs/013-infinite-board/spec.md](spec.md)
**Input**: Feature specification from `/specs/013-infinite-board/spec.md`

## Summary

Replace the bounded adaptive canvas with an unbounded world-coordinate board and an application-owned camera. Elements retain world coordinates; `CameraState(pan_x, pan_y, zoom)` controls only the view. The engine loses canvas dimensions and spatial bounds checks but retains minimum-size and finite numeric validation. The UI implements cursor-anchored pan/zoom, viewport culling, a zoom-dependent dot grid, constant-screen handles, double-click inline text editing, voice placement in the visible viewport, viewport-aware AI context, camera persistence, legacy migration, and content-bounds export.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: PyQt6, pytest, pytest-qt, pytest-cov
**Storage**: Existing SQLite persistence with opaque lesson JSON; no database schema migration
**Testing**: `pytest`, `pytest-qt`, offscreen Qt widget tests, integration tests, performance smoke tests
**Target Platform**: Windows desktop classroom application
**Project Type**: Desktop application
**Performance Goals**:
- Preserve validation plus execution under 100 ms per command.
- Support smooth pan/zoom with at least 200 elements.
- Paint only viewport-intersecting elements.
- Send at most 50 compact element summaries to AI providers.
**Constraints**:
- No new AI-addressable command; the public schema remains the existing 12 commands.
- Internal `edit_text` must be unavailable through public AI validation.
- Camera changes must not mutate board state, version, selection, or history.
- Core engine and persistence must remain importable without PyQt6.
- Core validation/history coverage must remain at or above 95%.
- Offline manual pen behavior must remain intact.
**Scale/Scope**:
- One active classroom board at a time.
- Unbounded world coordinates bounded only by finite numeric sanity limits.
- 200-element interactive performance target.
- Out of scope: pages, multi-select, rotation, snapping/guides, minimap, collaboration.

## Constitution Check

*GATE: Passed initial check before Phase 0 research; re-checked after Phase 1 design.*

### I. AI Isolation

**Pass.**

- AI remains limited to producing one structured command from the existing 12-command schema.
- Viewport-aware placement and zoom-relative move normalization occur in deterministic orchestrator code before queue submission.
- Normalized explicit commands—not camera objects—are validated, executed, and recorded.
- Internal `edit_text` is callable only from trusted UI/application code and is rejected by public command-shape validation.

### II. Determinism

**Pass.**

- Identical normalized commands applied to identical board states produce identical board states.
- History stores normalized explicit world coordinates and distances, eliminating camera dependence during undo/redo.
- Camera operations are excluded from board state, version sequencing, and history.
- Finite numeric guards prevent non-finite or pathological world values.

### III. Separation of Concerns

**Pass.**

- `Board` and `CommandEngine` remain UI-independent and camera-unaware.
- `CameraState`, transforms, placement policy, lesson documents, and AI-context shaping live outside core validation/execution.
- `BoardView` handles input events, coordinate conversion, provisional overlay editing, and read-only rendering; it does not implement board mutation rules.
- Shared export painting must remain read-only.

### IV. Code Quality and Maintainability

**Pass.**

- New modules remain small and single-purpose:
  - camera state and transforms;
  - visible-area placement;
  - lesson-document migration;
  - read-only shared board painting;
  - inline editing overlay behavior.
- Complete type hints and existing lint/format/type expectations apply.
- Dead canvas-growth code, clipping helpers, bounds checks, and obsolete tests must be removed rather than left dormant.

### V. Test-First Discipline

**Pass.**

- Core engine changes require fail-first tests.
- Requested pytest/pytest-qt coverage includes transforms, input handling, history invariance, persistence, migration, export, and performance.
- Failure-path coverage must include malformed input, unsupported commands, invalid targets, numeric-range violations, ambiguous voice input, queue behavior, persistence/export failures, renderer failures, confirmation flows, and queue overflow where applicable.
- Obsolete canvas-bound tests must be updated or retired; contradictory expectations must not be preserved.

### VI. Security and Privacy

**Pass.**

- AI context becomes shorter and viewport-scoped.
- At most 50 compact summaries are transmitted.
- Stroke-point arrays, audio, credentials, and full board dumps remain excluded.
- Existing secret-handling and untrusted-AI validation rules remain unchanged.

### VII. Reliability and Offline Pen Continuity

**Pass.**

- Engine operations remain atomic and FIFO-serialized under the existing engine lock.
- Rejected numeric-range operations leave state and history untouched.
- Camera updates are non-history view operations and cannot corrupt board state.
- Pen input remains locally committable without AI/network availability.

### VIII. Scope Discipline and Fixed-Canvas Constraint

**Conditional pass; merge blocked pending a ratified constitution amendment.**

The requested feature intentionally expands V1 scope from a fixed-size canvas to an infinite board. That expansion is justified by explicit product direction, but it conflicts with:

- Principle VIII’s prohibition on adding infinite canvas without amendment.
- The Additional Constraints requirement that the board be fixed-size and that every element lie wholly inside the canvas.

The design minimizes the constitutional impact:

- No 13th AI-addressable command is added.
- `create_text` is already an approved command.
- `edit_text` follows the approved internal-operation precedent used by pen commits.
- Stored coordinates remain authoritative.
- Legacy lessons migrate without coordinate changes.

The implementation PR must include a constitution amendment and cannot merge before ratification.

## Project Structure

### Documentation (this feature)

```text
specs/013-infinite-board/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── ai-context.md
│   ├── camera-transform.md
│   ├── lesson-json.md
│   └── ui-input-rendering.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/
├── ai/
│   ├── context_builder.py
│   └── prompt.py
├── app/
│   ├── camera.py
│   ├── command_queue.py
│   ├── exporter.py
│   ├── lesson_document.py
│   ├── lesson_service.py
│   ├── main.py
│   ├── orchestrator.py
│   └── placement.py
├── core/
│   ├── board.py
│   ├── command_schema.py
│   ├── engine.py
│   ├── errors.py
│   ├── gesture.py
│   ├── hit_test.py
│   └── validators.py
├── persistence/
│   ├── history_repo.py
│   ├── lesson_repo.py
│   └── migrations.py
├── ui/
│   ├── board_paint.py
│   ├── board_view.py
│   ├── camera_transform.py
│   ├── main_window.py
│   ├── pen_input.py
│   └── text_overlay.py
└── voice/

tests/
├── contract/
├── e2e/
├── fixtures/
├── integration/
├── performance/
├── ui/
└── unit/
```

**Structure Decision**: Retain the existing single-project desktop layout. Add application-layer camera, placement, lesson-document, transform, overlay, and shared-painting modules. Remove canvas-specific core/UI pathways rather than preserving parallel finite/infinite implementations.

## Design

### 1. Application-owned camera

Create `src/smartboard/app/camera.py` with:

- `CameraState(pan_x=0.0, pan_y=0.0, zoom=1.0)`.
- `MIN_ZOOM = 0.10`, `MAX_ZOOM = 4.00`.
- Finite numeric validation and normalization.
- `pan_by_screen`, `zoom_about_cursor`, `reset_zoom`, and `fit_camera_for_bounds`.
- `visible_world_rect(camera, view_width, view_height)`.

Create Qt-agnostic `src/smartboard/ui/camera_transform.py` implementing:

```text
screen = (world - pan) * zoom
world = screen / zoom + pan
```

`Orchestrator` owns the authoritative camera and transient view size. `BoardView` retains a render/input copy, emits view intents, and receives authoritative camera updates from the application layer.

Remove:

- `CommandEngine.grow_canvas`.
- `Orchestrator.grow_canvas`.
- `BoardView.CanvasResized` canvas-growth behavior.
- Minimum/legacy canvas constants from active board state.

Replace canvas-growth signaling with view-size notification used only for derived viewport calculation.

### 2. Unbounded core model

Update `src/smartboard/core/board.py`:

- Remove `canvas_width`, `canvas_height`, minimum/legacy canvas constants, clipping, canvas-bounded bbox calculation, and canvas-aware restore logic.
- Preserve element IDs, coordinates, colors, stacking, selection, versioning, and drawing-point data.
- Recompute drawing bounds in unbounded world space.
- Ignore legacy canvas fields during deserialization.

Update `src/smartboard/core/validators.py` and `engine.py`:

- Remove `fits_canvas` and canvas-based create/move/resize/drawing checks.
- Retain `MIN_SIZE`, resize-scale limits, text limits, color/shape validation, and deterministic command handling.
- Add `MAX_WORLD_COORD = 1_000_000.0` and `MAX_WORLD_SIZE = 1_000_000.0`.
- Retain `E_OUT_OF_BOUNDS` as the numeric-range error while revising its teacher-facing wording.
- Replace canvas-proportional default placement with explicit-position handling plus a deterministic direct-engine fallback.
- Update gesture helpers to remove canvas clamping and enforce finite numeric limits.

### 3. Input handling

Update `BoardView` to:

- Convert every pointer, pen, hover, selection, drag, resize, and overlay coordinate through the canonical camera transform.
- Implement wheel pan, `Shift+wheel` horizontal pan, and `Ctrl+wheel` cursor-anchored zoom.
- Implement Space-held panning without changing Pen/Select mode.
- Implement middle-button panning.
- Pan on Select-mode empty-space drag while preserving click-to-deselect.
- Normalize Qt pinch and native trackpad zoom events into the same zoom-about-cursor operation.
- Prevent Space-pan while the text overlay has focus.
- Emit camera intents without mutating board state or history.

### 4. Selection, drawing, drag, and resize at any zoom

- Use world coordinates for pen capture, selection, hit testing, drag origins, resize geometry, and committed board operations.
- Scale pointer tolerance as screen tolerance divided by zoom.
- Preserve world-unit stroke widths.
- Preserve fixed-corner resize behavior without canvas clamping.
- Paint selection outlines, handles, and highlight rings in screen space at constant size.

### 5. Inline text creation and editing

Add UI-layer provisional editing:

- Double-click empty space opens a provisional overlay anchored to the clicked world coordinate.
- Double-click existing heading/text/equation opens an overlay with existing content.
- Heading uses `QLineEdit`; text/equation uses `QPlainTextEdit`.
- Enter commits; multiline editing uses `Shift+Enter` for newline; Escape cancels.
- Clicking outside commits valid text.
- Empty new text is discarded without engine/history effects.
- Clearing existing text reverts without history effects.

Add application/engine behavior:

- Accepted new text travels as one public UI-origin `create_text` operation.
- Accepted existing-text edits call internal `CommandEngine.edit_text`.
- `edit_text` validates target kind and text, stores a swap-inverse snapshot, and records one history entry.
- Public schema, prompt, parser, and AI command validation continue to reject `edit_text`.

### 6. Voice placement and AI context

Add `src/smartboard/app/placement.py` with a pure deterministic placement function.

Before queueing a voice command, the orchestrator must:

- preserve explicit positions;
- supply a visible-area position when absent;
- convert relative distances into explicit world distances using active zoom;
- submit and record the normalized self-contained command.

Update AI context to include:

- visible world bounds and zoom;
- selected element;
- compact visible elements first;
- compact nearby elements second;
- no more than 50 summaries.

Update the prompt to describe unbounded world coordinates and visible-viewport preference while remaining short and preserving the 12-command lock.

### 7. Persistence, migration, and export

Add `src/smartboard/app/lesson_document.py` to:

- serialize board content plus camera;
- restore board content plus camera;
- normalize legacy bare-board snapshots;
- center legacy canvas snapshots at 100% without moving coordinates;
- ignore obsolete canvas fields.

Extract read-only painting into `src/smartboard/ui/board_paint.py` for shared interactive and export rendering.

Update export to:

- union canonical world bounds;
- add a fixed 48-unit margin;
- render at 100%;
- return a valid fixed image for empty lessons;
- perform no board/history mutation.

No SQLite schema change is required.

### 8. Test implementation

Implement the user-requested coverage in the corresponding harnesses:

- Unit: transforms, camera normalization, unbounded engine behavior, text edits, placement, AI caps, lesson documents, migration.
- Widget/offscreen: wheel, Space, middle-button, pinch normalization, double-click creation/editing, overlay behavior, drag/resize, handles, culling, grid, persistence, fit-all, history invariance.
- Integration: voice placement, AI context, legacy migration, camera save/restore, export, 200-element performance.
- Contract: UI-independent core, unchanged 12-command schema, prompt behavior, lesson JSON compatibility, rendering/history behavior.
- Update or retire obsolete finite-canvas tests.

## Open Product Confirmations

The specification already supports these defaults; final product confirmation remains advisable because the user explicitly asked for confirmation:

1. Space+drag pans in both Pen and Select modes while Space is held.
2. The dot grid is enabled by default with no separate visibility toggle.
3. There is no separate recenter button; `Shift+1`/Fit all provides recentering.

These are reversible UI defaults and do not block task decomposition.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Infinite board despite V1 fixed-canvas scope | Explicit product direction requires an edgeless pannable/zoomable board. | Retaining finite canvas bounds cannot satisfy pan/zoom, world coordinates, unbounded moves/resizes, or content-bounds export. |
| Internal `edit_text` engine operation alongside 12 locked AI commands | In-place editing needs validated reversible engine handling without becoming AI-addressable. | Recording edits as new creations or exposing text mutation to AI would corrupt history semantics or violate the command lock. |
| Shared UI-layer painting helper for interactive rendering and export | Interactive and exported output must not diverge. | Duplicating painting logic would create inconsistent text, shape, drawing, selection, and export behavior. |
