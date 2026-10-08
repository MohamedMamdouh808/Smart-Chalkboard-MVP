# Research: Adaptive Canvas Layout

**Feature**: `012-adaptive-canvas-layout` | **Date**: 2026-10-07
**Input**: Approved `spec.md`, follow-up technical direction, constitution v1.0.0, existing board/viewport/engine/persistence implementation

No NEEDS CLARIFICATION remains. The specification fixes layout, stability, storage, determinism, history, legacy, export, and exclusions; the technical direction fixes stored fields, growth semantics, mapping, migration, and tests.

## Decisions

### R-01: Store per-lesson canvas dimensions in the UI-independent core

- **Decision**: Add `canvas_width` and `canvas_height` to `Board`, include them in board state/save JSON/AI context, migrate missing values to 1920×1080, and default new in-memory boards to the 960×540 minimum until the UI reports a larger available area.
- **Rationale**: Canvas size governs validation, placement, mapping, context, export, and determinism, so it must be authoritative state rather than a UI constant.
- **Alternatives rejected**: Keeping fixed 1920×1080 behavior; storing canvas size only in window settings, which would not travel with lessons, snapshots, exports, or AI context.

### R-02: Grow canvas size through a non-history engine operation

- **Decision**: Add internal `grow_canvas(width, height)` that validates dimensions, increases each stored dimension independently, bumps board version on actual growth, and records no history entry or history hook.
- **Rationale**: Growth is deterministic window-derived state maintenance, not a reversible user command; versioning lets the UI refresh and later saves persist the larger canvas.
- **Alternatives rejected**: A public AI-addressable canvas command; silent widget mutation; recording growth as Undo history.

### R-03: Replace fixed-canvas uses with stored dimensions

- **Decision**: Pass stored dimensions explicitly to clipping, drawing bounds, bounds checks, drag/resize clamping, default placement, and export. Retain legacy 1920×1080 constants only for migration/default compatibility and add minimum-canvas constants.
- **Rationale**: This removes fixed-canvas behavior while preserving reopening of old lessons and explicit compatibility in tests.
- **Alternatives rejected**: Global mutable canvas settings, which would break determinism and per-lesson storage; leaving compatibility fallbacks scattered through widgets.

### R-04: Use capped uniform viewport mapping with centering

- **Decision**: Compute `scale = min(1, view_w / canvas_w, view_h / canvas_h)` with top-left origin at scale 1 and centered offsets only when downscaling. Use the same viewport for painting, pen input, selection, dragging, resizing, and hit-testing.
- **Rationale**: This gives undistorted 1:1 rendering whenever the window is large enough and uniform fit without clipping when it is smaller.
- **Alternatives rejected**: Aspect-ratio letterboxing at all sizes; non-uniform stretching; separate mappings for input and rendering.

### R-05: Emit canvas growth from the widget and apply it through the engine

- **Decision**: `BoardView` emits available-area size on show/resize; the app calls the internal engine growth path only when available dimensions exceed stored dimensions. UI thread and queue writer paths serialize through the existing engine lock.
- **Rationale**: The widget reports layout facts without mutating state; the engine remains the sole writer and growth never races voice/manual commands.
- **Alternatives rejected**: Direct board mutation from resize events; treating growth as a queued user command with history.

### R-06: Scale default placement proportionally with maximums

- **Decision**: Derive default x from canvas width, retain the established top margin/slot behavior, and cap default heading/text/shape dimensions at their legacy sizes so large canvases do not create oversized elements.
- **Rationale**: Preserves familiar placement at legacy size while keeping defaults usable on both minimum and very large canvases.
- **Alternatives rejected**: Fixed 160/800 defaults on all canvases, which would crowd small canvases or look arbitrary on large ones; unbounded proportional defaults, which would create huge elements.

### R-07: Migrate, save, export, and contextualize the stored size

- **Decision**: Board restoration defaults missing canvas data to 1920×1080 without moving elements; saved JSON includes canvas size; exports derive dimensions from stored state with legacy fallback; AI context includes stored canvas dimensions.
- **Rationale**: This preserves old lessons byte-for-byte in coordinates while making new validation, placement, rendering, and exports deterministic.
- **Alternatives rejected**: Rescaling legacy elements to a new canvas; omitting canvas size from AI context, which would make identical commands state-dependent.

### R-08: Test growth, stability, mapping, bounds, legacy, persistence, history, and layout

- **Decision**: Use `pytest`/`pytest-qt` synthetic resizes and stored-state fixtures for growth/no-shrink behavior, element stability, downscale mapping, multi-size coordinates, right/bottom bounds, legacy reopening, save/reopen identity, history invariance, and window-minus-margins board width.
- **Rationale**: Synthetic layout tests are repeatable in CI and directly encode the technical matrix without display hardware.
- **Alternatives rejected**: Manual headed-only resize verification; display-server-dependent fullscreen assertions.

## Performance notes

- Growth checks are constant-time integer comparisons.
- Viewport math remains per-event pure arithmetic.
- Canvas growth does not copy, transform, save, or re-render elements beyond normal refresh.
