# Implementation Plan: Direct Manipulation

**Branch**: `009-direct-manipulation` | **Date**: 2026-10-05 | **Spec**: [spec.md](spec.md)
**Input**: Approved feature specification from `/specs/009-direct-manipulation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Fix drawing bounding boxes by deriving them from all stroke points plus half the nominal stroke width, then add UI-independent hit testing and Select-mode drag/resize gestures. The widget tracks `idle`, `dragging`, and `resizing`, renders non-mutating previews from gesture snapshots, and releases exactly one queued `move_item` or `resize_item` operation with source `"ui"`. Drawings preserve stroke widths, proportions, bounds, history semantics, voice compatibility, and Pen-mode behavior.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 mouse/tablet/touch events and painting, existing `Viewport`, deterministic `CommandEngine`, FIFO `CommandQueue`, existing SQLite board/history path
**Storage**: Existing lesson board JSON and existing history records; no schema migration
**Testing**: `pytest`, `pytest-qt`, offscreen Qt, synthetic pointer/keyboard events, headless core tests, persistence round-trip tests
**Target Platform**: Windows desktop classroom machine
**Project Type**: desktop-app, existing single-project layout
**Performance Goals**: Event-driven hit-testing and gesture math; drawing-box work linear in stored points; one engine validation/execution per accepted gesture within the existing 100 ms command budget; no per-frame board writes
**Constraints**: UI-independent core geometry; internal manual operations only; twelve locked AI commands unchanged; Select startup default; six-unit drawing tolerance; 24-canvas-unit minimum; full canvas containment; 24-screen-pixel handle targets; one history entry per accepted gesture; no state/history change on cancellation; Pen-mode isolation; rotation, multi-select, snapping/guides, copy/paste, and layering controls excluded
**Scale/Scope**: Headings, text, equations, shapes, and drawings; all four resize corners; four representative window sizes; mixed voice/manual operation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — Voice input still produces command objects. Manual gestures produce standard or internal manual operations. Only the engine mutates board state. PASS.
- [x] II. Determinism — Canonical bounds, pure preview math, integer commit quantization, existing ID/history sequencing, and FIFO queue order preserve repeatable results. PASS.
- [x] III. Separation — Bounding, hit-testing, handle geometry, preview transforms, validation, and history remain Qt-independent. The widget manages interaction state, pointer capture, painting, and cursors only. PASS.
- [x] IV. Code quality — Typed core helpers, small gesture module, existing command schema unchanged for voice, no `eval`/`exec`, no untrusted dynamic behavior. PASS.
- [x] V. Test-first — Required regression, hit-test, gesture, history, cancellation, size-matrix, and mixed-scenario tests precede implementation; full suite and 95%-plus core coverage remain gates. PASS.
- [x] VI. Security/privacy — No audio, credentials, network, exports, or new persistence flows. PASS.
- [x] VII. Reliability — Atomic engine commits, validation before mutation, FIFO plus engine-lock serialization, queued UI operations, unchanged rendering on cancellation or failure. PASS.
- [x] VIII. Scope — Existing twelve voice commands remain the only AI-addressable operations; manual resize metadata is internal-only; all stated exclusions remain excluded. PASS.

Re-check after Phase 1 design (`research.md`, `data-model.md`, `contracts/`, `quickstart.md` above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/009-direct-manipulation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── geometry-contract.md
│   ├── hit-test-contract.md
│   ├── gesture-contract.md
│   ├── history-contract.md
│   └── test-matrix.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/core/board.py          # MODIFY: canonical half-width drawing bounds and recalculation helper
src/smartboard/core/hit_test.py       # EXTEND: per-type hit routines and expanded handle detection
src/smartboard/core/gesture.py       # NEW: Qt-independent drag/resize previews, anchors, clamping, aspect policy
src/smartboard/core/engine.py         # MODIFY: bound refresh on drawing paths; internal fixed-corner manual resize
src/smartboard/core/validators.py     # UNCHANGED: public move/resize schema remains voice-compatible
src/smartboard/ui/board_view.py       # MODIFY: idle/dragging/resizing, synthetic-event-compatible input, preview, cursors
src/smartboard/ui/theme.py            # UNCHANGED: existing selection/handle tokens reused
src/smartboard/app/orchestrator.py    # EXTEND: route one UI-sourced manual operation through queue and engine lock
src/smartboard/app/main.py            # EXTEND: gesture result handling, refresh, errors, pending/blocked behavior
```

**Structure Decision**: Extend the existing single-project layout in place. Geometry and selection rules live in `core/`; interaction state and presentation live in `BoardView`; commit sequencing lives in the existing queue/orchestrator path.

## Implementation flow

Follow the user-approved delivery order:

1. **Bounding box first**
   - Add the failing width-8 scribble-plus-line regression.
   - Revise the sole `drawing_bbox` calculation to inflate all point extrema by half the nominal stroke width.
   - Refresh bounds on creation, move, resize, undo, redo, and persistence restoration.
   - Update existing callers and assertions affected by the corrected box.

2. **Hit testing**
   - Add failing per-type and per-shape-primitive hit tests.
   - Implement rectangle, ellipse, segment-proximity, polygon, drawing-proximity, and bounding-box routines.
   - Add viewport-scale-aware handle detection.
   - Preserve topmost selection, empty-space deselection, and no-history selection behavior.

3. **Drag with preview and commit**
   - Add failing drag tests for every element type.
   - Implement press selection, movement threshold, clamped translation preview, and one queued `move_item` commit.
   - Keep previews and board state separate throughout pointer motion.
   - Verify full-suite and coverage gates before proceeding.

4. **Corner handles and resize**
   - Add failing tests for all four corners, aspect preservation, text-box wrapping, minimum size, and canvas clamping.
   - Render selected corner handles and hover cursors.
   - Scale drawing points about the fixed corner while retaining stored stroke widths.
   - Commit one queued `resize_item` operation without changing the public voice schema.

5. **History integration and cancellation**
   - Verify exactly one applied history entry per accepted gesture.
   - Verify complete Undo/Redo restoration, including drawing points and bounds.
   - Verify Escape, mode-change, invalid, rejected, blocked, and queue-full paths leave state, version, and history unchanged.

6. **Mixed voice/manual verification**
   - Add the failing voice-resize-then-manual-drag scenario.
   - Confirm shared operations, selection retention, bounds, history order, and Pen-mode isolation.
   - Run the full test suite and core-coverage gate.
   - Leave optional real-display checks in `quickstart.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
