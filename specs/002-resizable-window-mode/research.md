# Research: Resizable Window Mode

**Feature**: `002-resizable-window-mode` | **Date**: 2026-10-03
**Input**: spec + 2026-10-03 clarifications + user technical brief (UI-layer only, engine untouched)

No NEEDS CLARIFICATION remains: the brief prescribes the stack touchpoints
and clarify locked letterboxing, geometry restore, and text-wrap rules.

## Decisions

### R-01: Window state machine (no forced fullscreen)

- **Decision**: `QMainWindow` starts per restored preference; `showNormal()`,
  `showMaximized()`, `showFullScreen()` only. Toggle button + F11
  (`QShortcut`) switch fullscreen ↔ last normal state at any time.
  Minimum size 960×540 via `setMinimumSize`. Mode, size, and position
  persist at close and restore before first paint (fresh install →
  fullscreen).
- **Rationale**: Directly implements FR-001/FR-002/FR-003 with stock Qt
  semantics (minimize/maximize/move come free with a normal window).
- **Alternatives rejected**: Manual frameless chrome (reimplements OS
  behavior, breaks pen-as-pointer hit areas); separate fullscreen widget
  (duplicates layout, risks divergence).

### R-02: QSettings for geometry persistence

- **Decision**: `QSettings(IniFormat, "SmartChalkboard", "SmartChalkboard")`:
  keys `window/mode` (`fullscreen|normal|maximized`), `window/geometry`
  (`saveGeometry` blob), fresh install → fullscreen. Written on close,
  read before first show; corrupt/missing values fall back to defaults.
- **Rationale**: User-brief directive; per-user, no lesson data mixed in,
  survives updates.
- **Alternatives rejected**: JSON in lesson DB (mixes chrome with lesson
  content, violates FR-005 size-independence).

### R-03: Single-source viewport transform (the safety core)

- **Decision**: New `ui/viewport.py` (Qt-agnostic pure math):
  `Viewport.from_sizes(view_w, view_h)` → uniform `scale =
  min(view_w/1920, view_h/1080)`, centered offsets `ox, oy` (letterbox
  margins share the board background). Forward `to_screen(x, y)` for
  painting; inverse `to_canvas(px, py)` for ALL pen/mouse/selection input.
  BoardView paints with this transform; pen and click handlers convert
  through its inverse — never duplicating the formula. Recomputed on
  every resize; mid-stroke samples each map through the then-current
  viewport and the committed stroke stores canvas coordinates, so a
  mid-stroke resize cannot skew the element.
- **Rationale**: FR-004/FR-006/FR-011 hinge on one formula used both ways;
  purity makes it headless-testable at many sizes (no Qt needed).
- **Alternatives rejected**: Per-call-site scale math (drift between
  paint and hit-test — the exact bug class FR-006 forbids).

### R-04: Text fit without touching the engine

- **Decision**: Text wraps inside the fixed element box (`drawText` with
  word-wrap in the element rect; box/coordinates immutable). Creation-time
  fit gate lives in the app layer (`app/text_fit.py`, `QFontMetrics`-based):
  text that cannot fit the default box is rejected BEFORE queueing with
  "Text is too long for this element. Resize it or shorten the text."
  Post-resize overflow clips at the box edge (render only, no layout
  change). `core/` (schema, validators, engine, history) is not modified.
- **Rationale**: Honors both FR-008 and the user's "engine untouched"
  constraint; validation location is the only sane seam (engine owns
  state rules, but box sizes are fixed constants shared read-only).
- **Alternatives rejected**: Engine validator change (violates the
  explicit constraint); auto-grow (breaks FR-005 byte-identical exports).

### R-05: Chrome layout that cannot overlap the board

- **Decision**: `QVBoxLayout`: transcription strip (fixed height, 48px
  minimum targets) + `BoardView` (stretch=1) + control-bar `QHBoxLayout`
  with `setMinimumHeight` and per-button `setMinimumSize(…, 48)`.
  Letterboxing happens INSIDE BoardView, so chrome can never cover board
  content at any window size ≥ 960×540.
- **Rationale**: FR-007 by construction instead of by careful pixels.
- **Alternatives rejected**: Overlay/floating controls (overlap risk at
  minimum size).

### R-06: Button contrast via explicit stylesheet

- **Decision**: Explicit button stylesheet declaring both `color` (near-
  white text) and `background` (dark slate) plus a distinct focus/hover
  treatment; verified against the 4.5:1 requirement with a luminance
  computation test on the declared hex values (no eyeballing).
- **Rationale**: FR-009 made deterministic; the previous bug was inherited
  ambient styling with unreadable combinations.
- **Alternatives rejected**: OS-theme inheritance (unverifiable, varies
  per machine).

### R-07: Dialogs centered, once-only outcomes

- **Decision**: `ConfirmDialog`/`ClarifyDialog` constructed with the main
  window as parent (Qt centers on parent by default); recenter on parent
  move/resize via `move()` to parent center while open. Outcome path
  unchanged (accept → confirmed execute; reject/timeout → cancel once);
  resize cannot re-trigger the outcome because the dialog owns exactly one
  accept/reject signal connection.
- **Rationale**: FR-010/FR-011 with zero engine involvement.
- **Alternatives rejected**: Custom positioning math (fights window
  manager); non-modal dialogs (breaks queue-blocking semantics).

### R-08: Testing with pytest-qt (offscreen in CI)

- **Decision**: Install `pytest-qt`; new `tests/ui/` suite runs with
  `QT_QPA_PLATFORM=offscreen` in CI: coordinate-mapping property tests
  (round-trip screen→canvas→screen at 960×540, 1280×720, 1920×1080,
  portrait 800×1000), mode-switch tests (F11/button, 4 toggles, state
  identical), resize-mid-stroke test (viewport swap between samples,
  committed coords match drawn shape), text-wrap/clip tests, contrast
  luminance test, 48px-minimum layout test. Live headed pass remains a
  manual checklist item in quickstart.
- **Rationale**: User-brief directive; offscreen keeps CI green without a
  display while still exercising real Qt paint/input paths.
- **Alternatives rejected**: Pure-math tests only (would miss Qt event/
  layout integration); headed-only CI (no Windows display runner).

## Performance notes

- Repaint on resize stays within a single frame for ≤200 elements (paint
  work is linear text/shape draws; no layout recomputation beyond the
  viewport).
- Geometry save/restore is O(1) QSettings I/O on close/startup only —
  never in the command path, so the 3 s voice budget is unaffected.
