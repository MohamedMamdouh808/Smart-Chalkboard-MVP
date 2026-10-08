# Data Model: Adaptive Canvas Layout

**Feature**: `012-adaptive-canvas-layout` | **Date**: 2026-10-07
**Sources**: Approved `spec.md`, follow-up technical direction, `research.md`, constitution v1.0.0

Element identity, command payloads, history entries, lesson tables, and provider behavior remain unchanged in shape. This feature adds stored canvas dimensions and canvas-aware geometry; it does not add AI commands, pages, zoom, pan, or user canvas controls.

## Stored canvas size

- `canvas_width`, `canvas_height`: integer logical dimensions owned by `Board`.
- Minimum new/in-memory size: `960 × 540`.
- Legacy migration size: `1920 × 1080`.
- Each dimension grows independently to the maximum available board area observed.
- Stored dimensions never shrink automatically.
- Existing element coordinates are never rewritten because the canvas changed.

## Board state and context

- `Board.to_dict()` canvas object reports stored width/height.
- Saved board JSON includes the same canvas object.
- AI context includes stored canvas width/height alongside existing element summaries and selection.
- Board restoration copies lesson ID, canvas size, elements, selection, and version.
- Snapshots lacking canvas data migrate to legacy size without moving elements.

## Growth operation

- `grow_canvas(width, height)` is internal and never AI-addressable.
- Inputs are validated as integer dimensions at or above the canvas minimum.
- A request at or below stored size is a successful no-op.
- Actual growth updates stored dimensions and board version.
- Growth creates no history entry, history-hook record, confirmation, or clarification.

## Display mapping

- Available board-widget width/height determines display geometry.
- `scale = min(1, view_w / canvas_w, view_h / canvas_h)`.
- At scale 1, canvas origin is at the widget’s top-left drawing origin.
- When downscaling, the canvas is centered with offsets on both axes.
- The same mapping converts screen input to canvas coordinates and canvas geometry to screen output.
- Painting, pen sampling, selection, hit-testing, drag previews, resize previews, and cursors all use this mapping.

## Default placement policy

- Default horizontal origin derives from canvas width while preserving the legacy 160-unit origin at 1920 width.
- Default vertical origin retains the established top margin and slot behavior.
- Default heading/text/shape dimensions retain legacy sizes as maximums.
- Smaller canvases receive proportionally smaller defaults within minimum-size validation.
- Large canvases do not create unbounded default elements.

## State transitions

```text
new lesson -> minimum canvas -> first available area -> grow if larger
larger window -> available area exceeds stored size -> grow, no history
smaller window -> stored size retained -> uniform downscale/center
legacy reopen -> missing canvas migrates to 1920x1080
save -> stored canvas persists
export -> stored canvas dimensions used
```

## Entity-to-story mapping

- US1 full-window layout: board area, stored canvas size, display mapping, default placement bounds.
- US2 element stability: absolute coordinates, uniform mapping, resize behavior, history invariance.
- US3 lessons/exports/determinism: stored canvas persistence, legacy migration, export dimensions, AI context.
