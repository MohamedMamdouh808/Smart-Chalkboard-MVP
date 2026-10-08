# Implementation Plan: Manual Drawing

**Branch**: `008-manual-drawing` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification + 2026-10-04 clarifications + user technical brief + constitution v1.0.0
**Restoration record**: 2026-10-05

> **Restoration note:** The completed 008 plan was overwritten by a later
> `setup-plan` invocation. No committed copy existed in git history, so this
> file was regenerated from `spec.md`, `research.md`, `data-model.md`,
> `contracts/`, `tasks.md`, `quickstart.md`, the implemented source, and the
> recorded test results. No 008 specification or task was changed during
> restoration.

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement pointer-based freehand drawing as a first-class board element.
Capture tablet, mouse, and touch input through one mode-gated collector,
map every sample to canvas coordinates, group strokes within 1.5 seconds,
reduce near-duplicate samples, and commit each group through an internal
engine drawing operation with snapshot-based undo/redo. Committed drawings
support the existing voice move, resize, recolor, and confirmed-delete
operations, render through `QPainterPath`, persist inside lesson JSON, and
retain exact points across reopen. Selection uses six-unit stroke proximity
with outline and corner-handle adornments.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6 tablet/mouse/touch events, `QPainterPath`, existing viewport transform, deterministic `CommandEngine`, FIFO `CommandQueue`, existing SQLite board/history path
**Storage**: Existing lesson board JSON; drawings stored as schemaless element data, with no new tables or migration
**Testing**: `pytest`, `pytest-qt`, offscreen Qt, synthetic mouse/tablet/touch events, headless engine/integration tests, save/reopen round-trip tests
**Target Platform**: Windows desktop classroom machine
**Project Type**: desktop-app, existing single-project layout
**Performance Goals**: One live overlay path per frame; click-time-only linear hit testing; reduced point count for long sessions; engine validation and execution below the existing 100 ms command budget
**Constraints**: UI-independent core; plain point data across the UI/engine boundary; internal drawing operation only, never a thirteenth AI command; Select startup default; P/S shortcuts; 1.5-second grouping; six-unit hit tolerance; point-reduction distance near two canvas units; thin/medium/thick width setting, default medium; no width control on the main bar
**Scale/Scope**: One drawing element type, unified input, live/committed rendering, grouping, persistence, full-matrix verification, and existing command compatibility

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — Voice input produces command objects; pen input produces plain points. Only `CommandEngine.add_drawing` and the validated command paths mutate board state. PASS.
- [x] II. Determinism — Grouping input, clipped/reduced points, viewport-independent canvas coordinates, never-reused drawing IDs, snapshot inverses, and queue serialization produce repeatable drawings and history. PASS.
- [x] III. Separation — Point math, hit testing, grouping semantics, and engine operations remain Qt-independent. Widgets collect input, select through the engine, and render snapshots without business rules. PASS.
- [x] IV. Code quality — Small typed modules and helpers, explicit constants, local core imports where needed, no `eval` or `exec`, no untrusted dynamic imports. PASS.
- [x] V. Test-first — Twelve-case pytest/pytest-qt matrix plus mixed heading/drawing/voice coverage, failure paths, offline coverage, and a 95%-plus core coverage gate. PASS.
- [x] VI. Security/privacy — No audio capture, no credentials, no network dependency, local settings only for pen width and window geometry. PASS.
- [x] VII. Reliability — Atomic `add_drawing`, bounds validation, FIFO queue plus engine lock, no concurrent voice/pen writes, queued pen commits, group preservation across resize, exact undo/redo and reopen behavior. PASS.
- [x] VIII. Scope — Twelve locked AI commands remain unchanged; `add_drawing` is internal-only; handwriting recognition, conversion, partial erase, palm tuning, multi-pen, and voice pen remain excluded. PASS.

Re-check after Phase 1 design (`research.md`, `data-model.md`, `contracts/`, `quickstart.md` above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/008-manual-drawing/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── input-contract.md
│   ├── drawing-contract.md
│   ├── persistence-contract.md
│   └── test-matrix.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/core/board.py               # ADD: widths, reduction distance, point/bbox/translate/scale helpers
src/smartboard/core/engine.py              # ADD: internal add_drawing and select; EXTEND: drawing move/resize/recolor
src/smartboard/core/hit_test.py            # NEW: segment hit testing and topmost selection
src/smartboard/ui/board_view.py            # MODIFY: unified input, selection click, adornments, live/committed paint
src/smartboard/ui/pen_input.py             # EXTEND: canvas mapping and 1.5-second grouping
src/smartboard/ui/main_window.py           # MODIFY: Pen/Select toggle, shortcuts, Select default
src/smartboard/ui/window_state.py          # EXTEND: thin/medium/thick pen-width setting
src/smartboard/app/command_queue.py        # EXTEND: locking, peek, identity-tagged submit_and_run
src/smartboard/app/orchestrator.py         # MODIFY: queue-routed pen dispatch under engine lock
src/smartboard/app/main.py                 # MODIFY: grouping timers, queued commits, engine selection, width wiring

tests/unit/test_drawing_model.py           # NEW/EXTEND: bbox, transforms, reduction, stroke recolor, select
tests/ui/test_drawing_input.py             # NEW: synthetic input, mapping, grouping-off-canvas, resize, selection
tests/integration/test_drawing_engine.py   # NEW/EXTEND: undo/redo, voice operations, persistence, queue behavior
tests/integration/test_pen_engine.py       # NEW/EXTEND: IDs, offline commit, grouping semantics
tests/e2e/test_drawing_voice_mix.py        # NEW: heading, drawing, voice operations, and undo chain
tests/ui/test_window_persistence.py        # EXTEND: pen-width setting behavior and absence of bar control
tests/ui/refs/window-1366x768.png          # REGENERATED
tests/ui/refs/window-1920x1080.png         # REGENERATED
```

**Structure Decision**: Extend the existing single-project layout in place.
Core geometry and engine behavior stay Qt-independent. All drawing state
changes enter through the engine; the UI contributes only canvas samples,
mode/selection intents, and rendering. Persistence reuses the existing
board JSON and history-hook notification path.

## Implementation flow

1. **Model and selection geometry**
   - Store a drawing as ordered stroke point lists with per-stroke width and color.
   - Derive its bounding box from all valid points, enforce the 24-unit minimum, and clamp it into the 1920×1080 canvas.
   - Retain endpoints while reducing samples nearer than approximately two canvas units to the last retained sample.
   - Select drawings by minimum point-to-segment distance within six units and resolve ties by z-order.

2. **Internal commit and command compatibility**
   - Clip pen samples to the canvas and normalize invalid samples out without rejecting the entire stroke.
   - Validate width, derive a unique never-reused drawing ID, validate the final bounding box, increment board version, record history, and invoke the history hook identically to other state changes.
   - Translate every stored point on `move_item`; scale every stored point about the bounding-box origin on `resize_item`; rewrite every stored stroke color on `change_color`.
   - Preserve pre- and post-operation snapshots so undo and redo restore byte-identical point data and stroke colors.
   - Provide an internal, non-history selection operation so view clicks cannot directly assign board selection.

3. **Input, modes, and grouping**
   - Handle tablet position/pressure, mouse press/move/release, and touch through one one-pointer collector.
   - Convert every sample with the viewport current at sample time; ignore presses starting outside the board and clip later points to the edge.
   - Start in Select; change modes only through the toggle or P/S; reset active pointer and live ink on mode changes.
   - Emit canvas-space `StrokeFinished` samples; append strokes to the active 1.5-second group unless selection or another command intervenes.
   - Route grouped commits through the FIFO queue and engine lock, retry blocked work through the pending-commit path, and refresh only from engine results.

4. **Rendering and user preference**
   - Paint in-progress ink on a temporary overlay cleared after release or commit.
   - Paint committed drawings in z-order with `QPainterPath`, round caps/joins, stored stroke widths, and pressure-scaled widths when pressure is available.
   - Draw only the selected element’s outline and four corner handles; preserve highlight rendering separately.
   - Persist pen width as thin/medium/thick with medium default; initialize both live and committed strokes from settings without adding a toolbar control.

5. **Verification**
   - Cover all twelve manual-drawing cases: synthetic mouse/tablet input, three window mappings, grouping boundaries, undo/redo identity, voice operations, off-canvas handling, resize during a stroke, persistence identity, one-pointer behavior, drawing selection, and offline operation.
   - Cover mixed heading/drawing/voice behavior and queue serialization under voice load.
   - Require the full regression suite and core coverage gate before accepting the feature.
   - Recorded outcome: `289 passed, 2 skipped`; core coverage `98.24%` against the required `95%`.
   - Visual references were regenerated and inspected; optional real-display/manual pen checks remain available in `quickstart.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
