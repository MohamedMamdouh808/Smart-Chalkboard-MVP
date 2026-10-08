# Implementation Plan: Adaptive Canvas Layout

**Branch**: `012-adaptive-canvas-layout` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)
**Input**: Approved feature specification plus user-supplied core, engine, mapping, migration, export, and test directives

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Store per-lesson canvas dimensions in the UI-independent core, grow them monotonically through a non-history engine operation, replace fixed-canvas geometry with stored dimensions, map all input/output through a capped uniform viewport, migrate legacy lessons to 1920×1080, and verify growth, stability, mapping, bounds, persistence, history, and layout behavior.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 layout/painting/events, deterministic `CommandEngine`, FIFO `CommandQueue`, existing SQLite board/history path
**Storage**: Existing lesson board JSON; canvas dimensions included; no schema migration
**Testing**: `pytest`, `pytest-qt`, offscreen Qt, synthetic resizes, stored-state fixtures, save/reopen round trips
**Target Platform**: Windows desktop classroom machine
**Project Type**: desktop-app, existing single-project layout
**Performance Goals**: Constant-time growth checks; per-event pure viewport arithmetic; one engine validation per actual growth; no element copying/transforming on resize
**Constraints**: Stored per-lesson dimensions; grow-only behavior; uniform undistorted mapping; 24-unit minimum element size; 960×540 minimum canvas and window bounds; legacy 1920×1080 migration; no history for window-driven growth; twelve locked AI commands unchanged; user-selected sizes, pages, infinite canvas, zoom/pan, and non-uniform stretching excluded
**Scale/Scope**: All element types; representative window sizes including fullscreen and smaller-than-canvas layouts; legacy, saved, and exported lessons

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — Canvas growth and mapping produce state through the engine; AI output remains a structured command and only the engine mutates state. PASS.
- [x] II. Determinism — Stored canvas size makes validation, placement, mapping, export, and AI context repeatable for identical states. PASS.
- [x] III. Separation — Canvas geometry, validation, growth, and persistence remain Qt-independent; widgets report layout facts and render snapshots. PASS.
- [x] IV. Code quality — Typed small core/UI/app changes, explicit canvas parameters, no visual/business literals outside their authorities, no `eval`/`exec`. PASS.
- [x] V. Test-first — Growth, stability, mapping, bounds, legacy, persistence, history, layout, and regression tests precede and verify engine changes. PASS.
- [x] VI. Security/privacy — No credentials, audio, uploads, exports of sensitive data, or logging changes. PASS.
- [x] VII. Reliability — Atomic growth, validation before mutation, engine-lock serialization, FIFO behavior, offline/manual continuity, and no history pollution. PASS.
- [x] VIII. Scope — No new AI-addressable command, schema change, page/canvas control, zoom/pan, or unrelated feature; one governance exception below. CONDITIONAL PASS.

Re-check after Phase 1 design (`research.md`, `data-model.md`, `contracts/`, `quickstart.md` above): no new violations. One Complexity Tracking entry is required.

## Project Structure

### Documentation (this feature)

```text
specs/012-adaptive-canvas-layout/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── canvas-state-contract.md
│   ├── mapping-contract.md
│   ├── growth-contract.md
│   ├── persistence-export-contract.md
│   └── test-matrix.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/core/board.py              # MODIFY: stored canvas fields, explicit geometry, migration/restore
src/smartboard/core/validators.py         # MODIFY: explicit-canvas bounds validation
src/smartboard/core/engine.py             # MODIFY: internal grow_canvas, stored-canvas validation/placement
src/smartboard/core/gesture.py            # MODIFY: explicit-canvas drag/resize clamping
src/smartboard/ui/viewport.py             # MODIFY: explicit canvas dimensions and capped uniform mapping
src/smartboard/ui/board_view.py           # MODIFY: stored-canvas rendering/mapping and available-area signal
src/smartboard/ui/main_window.py          # VERIFY: free-area layout and minimum window behavior
src/smartboard/app/orchestrator.py        # EXTEND: locked internal canvas-growth routing
src/smartboard/app/main.py                # MODIFY: first-open growth, resize growth, refresh behavior
src/smartboard/app/exporter.py            # MODIFY: derive export dimensions from stored canvas
src/smartboard/ai/context_builder.py      # MODIFY: include stored canvas dimensions
src/smartboard/persistence/*.py           # UNCHANGED: existing JSON snapshot schema carries canvas data
tests/unit/test_adaptive_canvas.py        # NEW: state, growth, validation, mapping, migration coverage
tests/ui/test_adaptive_canvas_layout.py   # NEW: synthetic resize, surface, mapping, and margin coverage
tests/integration/test_canvas_persistence.py # NEW: save/reopen, legacy, export, history coverage
```

**Structure Decision**: Extend the existing single-project layout in place. Canvas authority lives in `core/`; layout facts and rendering live in `ui/`; sequencing and persistence reuse the existing app paths.

## Implementation flow

1. **Canvas state and geometry**
   - Add stored dimensions, minimum/legacy constants, board serialization/restoration, and canvas-aware clipping/bounds helpers.
   - Migrate missing canvas data to legacy size without touching elements.
   - Update all fixed-canvas call sites and affected unit assertions.

2. **Growth and command behavior**
   - Add validated grow-only engine behavior with version updates and no history/hook records.
   - Route UI-reported available area through the engine lock only when it exceeds stored size.
   - Replace validation, drag/resize clamping, and default placement with stored dimensions and proportional bounded defaults.
   - Include canvas size in AI context and derive export dimensions from stored state.

3. **Mapping and layout**
   - Implement capped uniform viewport mapping with centering only during downscaling.
   - Use stored canvas dimensions for painting, input, selection, gestures, and layout rectangles.
   - Emit available-area growth intents from show/resize without moving elements.
   - Verify existing free-area layout and minimum-window behavior.

4. **Verification**
   - Add growth/no-shrink, stability, downscale, mapping, edge-bounds, legacy, save/reopen, history, and window-margin tests.
   - Update existing viewport/board/engine/gesture/persistence/export/context tests affected by stored dimensions.
   - Retain the full regression suite and applicable coverage gates.
   - Leave optional real-display checks in `quickstart.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Additional Constraints fixed-size canvas | Approved 012 explicitly replaces global fixed 1920×1080 behavior with per-lesson stored adaptive dimensions, while retaining single-page, non-infinite, undistorted behavior | A MINOR constitution amendment should update the canvas constraint; retaining the old global fixed canvas would make the approved feature impossible |
