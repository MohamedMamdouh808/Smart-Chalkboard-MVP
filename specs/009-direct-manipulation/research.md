# Research: Direct Manipulation

**Feature**: `009-direct-manipulation` | **Date**: 2026-10-05
**Input**: Approved `spec.md`, constitution v1.0.0, existing 008 manual-drawing implementation

No NEEDS CLARIFICATION remains. The approved specification fixes the geometry rule, interaction model, preview/commit separation, history behavior, compatibility constraints, and exclusions.

## Decisions

### R-01: Expand the canonical drawing bounding box by half the stroke width

- **Decision**: Change `drawing_bbox` to accept stroke geometry plus the drawing’s nominal stroke width, expand the minimum and maximum x/y extents by half that width, enforce the 24-unit minimum afterward, and clamp the resulting box into the canvas. Use this same function for creation, move, resize, undo, redo, persistence restoration, and rendering/selection consumers.
- **Regression anchor**: A width-8 drawing containing scribble points around `(100,140)` through `(260,120)` plus a horizontal line from `(500,220)` to `(820,220)` must produce `(96,106,728,118)` rather than the old point-only `(100,110,720,110)`.
- **Rationale**: One canonical function prevents state, selection, hit-testing, and painting from diverging. Expanding before minimum-size handling avoids thin-line degeneration.
- **Alternatives rejected**: A render-only ink envelope, which would leave engine state and selection inconsistent; padding only the final width/height, which would be asymmetric for diagonal or off-center strokes.

### R-02: Add UI-independent hit-test routines by element type

- **Decision**: Keep PyQt out of `core/hit_test.py` and add:
  - rectangle containment for headings, text, equations, and rectangular shapes;
  - ellipse containment for circles;
  - segment proximity for lines and arrows;
  - polygon containment for triangles;
  - stroke-segment proximity or bounding-box containment for drawings;
  - a central `select_at` dispatcher preserving topmost/z-order behavior and empty-space deselection.
- **Rationale**: “Any visible part” requires shape-aware geometry, especially for thin lines and arrows. Pure core functions remain headless-testable and keep the UI from owning selection rules.
- **Alternatives rejected**: Bounding-box-only selection, which accepts large empty areas in diagonal or triangular shapes; Qt path-based hit-testing, which would violate UI-independent-core separation.

### R-03: Keep the gesture state machine in the widget, geometry in the core

- **Decision**: Implement `idle`, `dragging`, and `resizing` in `BoardView`, while moving target geometry, handle detection, clamping, aspect handling, and preview transforms into a Qt-independent core gesture helper.
- **Press behavior**: A Select-mode press checks the selected element’s handles first, then dispatches by element type. A stroke-proximity/bbox press selects a drawing; other presses use type-specific hit behavior; empty space clears selection.
- **Drag discrimination**: Remaining below a small canvas movement threshold keeps the interaction in the press-candidate/equivalent-to-click path; crossing it transitions to `dragging` or `resizing`.
- **Pointer coverage**: Reuse the existing mouse, tablet, and touch entry points and convert every sample with the viewport current at sample time.
- **Pen isolation**: Pen-mode collection, single-pointer handling, and `StrokeFinished` behavior remain unchanged.
- **Rationale**: This preserves the requested widget state machine without putting business/geometry rules into Qt event handlers.
- **Alternatives rejected**: Geometry calculations inside event handlers, which would be untestable headlessly and risk duplicating engine rules; a separate native gesture recognizer, which would bypass the existing viewport and pointer infrastructure.

### R-04: Use expanded but visually smaller resize handles

- **Decision**: Continue drawing 14-unit corner squares, but calculate handle interaction using the larger of the visual square and a square equivalent to 24 screen pixels. Use diagonal resize cursors appropriate to each corner and restore the arrow cursor elsewhere.
- **Rationale**: Classroom touch/mouse targets need to be easier to acquire than the small visual affordance, while the board should not become visually cluttered with oversized handles.
- **Alternatives rejected**: Enlarging the painted handles to the full interaction area; a fixed canvas-unit hit area, which would shrink below 24 screen pixels at small window scales.

### R-05: Preview from a snapshot; never mutate board state mid-gesture

- **Decision**: Store the original element snapshot at gesture start. Render the underlying committed element suppressed and the transformed snapshot in its place. Escape, mode change, failed validation, queue blockage, or release without movement clears the preview without writing state or history.
- **Rationale**: Atomicity requires users to see a proposed result while the engine remains the only writer of actual results.
- **Alternatives rejected**: Temporarily mutating and restoring board state, which would expose invalid intermediate states to persistence, history, rendering, and concurrent voice commands.

### R-06: Commit exactly one existing engine operation per gesture

- **Decision**:
  - Drag: queue one standard `move_item` payload with source `"ui"`.
  - Resize: queue one internal manual-resize payload whose recorded history command remains the existing `resize_item`.
  - Pass the fixed opposite corner as engine-method metadata rather than expanding the public voice-command schema.
  - Route both through the existing FIFO queue and engine lock.
- **Rationale**: This gives one Undo/Redo entry, preserves voice-schema compatibility, avoids a thirteenth AI command, and prevents concurrent engine writes.
- **Alternatives rejected**: Separate move plus resize commands for corner changes, which would require two Undo operations; extending the public `resize_item` schema with anchor fields, which would alter the locked voice-command surface.

### R-07: Preserve proportions selectively and retain drawing stroke width

- **Decision**:
  - Preserve proportions by default when resizing drawings, shapes, and equations.
  - Resize headings/text boxes independently and let existing rendering wrap their text.
  - Scale drawing point coordinates about the fixed corner while retaining every stroke’s stored width.
  - Clamp live and committed geometry to the 24-unit minimum and full canvas containment.
- **Rationale**: Mathematical and drawn content should not be distorted by corner gestures, while text layout needs flexible boxes. Stored stroke width is a style property, not a spatial coordinate.
- **Alternatives rejected**: Uniform free resize for all types, which would distort equations and drawings; scaling stroke widths with geometry, contrary to the approved behavior.

### R-08: Test with synthetic events across window sizes plus engine tests

- **Decision**: Use `pytest` and `pytest-qt` synthetic mouse/tablet/touch events at the established 960×540, 1280×720, 1920×1080, and 800×1000 sizes. Add model tests for the scribble-plus-line regression, per-type hit tests, all four corners, clamping/minimum behavior, single-history commit and Undo/Redo, Escape cancellation, and a voice-resize-then-manual-drag scenario. Retain the full-suite and 95%-plus core-coverage gates.
- **Rationale**: Synthetic events are repeatable in CI and directly cover the requested matrix without pen hardware.
- **Alternatives rejected**: Hardware-only or headed-only gesture testing, which is neither repeatable nor suitable as a merge gate.

## Performance notes

- Hit-testing remains event-driven, not per-frame.
- Bounding-box recalculation is linear in the drawing’s stored points and occurs only on drawing-affecting operations.
- Gesture previews transform a view-local snapshot rather than copying board state or issuing engine writes during pointer motion.
