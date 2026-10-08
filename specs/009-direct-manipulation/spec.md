# Feature Specification: Direct Manipulation

**Feature Branch**: `009-direct-manipulation`  
**Created**: 2026-10-05  
**Status**: Draft  
**Input**: User description: "Fix the drawing bounding box by computing it from all stroke points plus half the stroke width in a single function in the engine's drawing model, and invalidate and recompute it on every change; add a regression test using a multi-stroke drawing like a scribble beside a straight line. Add a hit-test routine for each element type in the UI-independent core. In the board widget add a Select-mode interaction state machine (idle, dragging, resizing) handling mouse, tablet and touch events through the existing screen-to-canvas transform; draw corner handles and the selection outline in paintEvent, and use setCursor for handle hover. During a gesture, render a transformed preview from the original geometry (translate for drag, scale about the fixed corner for resize) without touching board state. On release, send one move or resize operation with source "ui" to the engine, which validates bounds and minimum size, executes it, and records a single history entry with an inverse operation; Escape cancels. For drawings, scale all stroke points proportionally about the fixed corner and keep the stroke width unchanged. Test with pytest and pytest-qt: bounding box correctness, drag of each element type, corner resize with each of the four corners, bounds clamping, minimum size, one history entry per gesture and undo/redo, cancel with Escape, gestures at several window sizes, and a mixed scenario of voice-resize followed by a manual drag."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trust the selection outline (Priority: P1)

A teacher selects any heading, text, equation, shape, or drawing and immediately recognizes the selected object from its outline. The outline tightly surrounds all visible content, including both a loose scribble and a straight line belonging to the same drawing. A thin bar, cropped outline, or stale outline is never shown.

**Why this priority**: Selection is the prerequisite for every manual operation. An inaccurate outline makes teachers distrust dragging, resizing, and voice commands that use the selection.

**Independent Test**: Can be fully tested by selecting representative objects and comparing each outline against the corresponding rendered content, without dragging or resizing anything.

**Acceptance Scenarios**:

1. **Given** headings, text, an equation, a shape, and a drawing, **When** the teacher selects each object, **Then** its outline tightly encloses the complete visible object.
2. **Given** a drawing containing a scribble beside a straight line, **When** a stroke is added, moved, resized, undone, redone, or reopened, **Then** the drawing outline is recalculated and still encloses all ink.
3. **Given** a selected drawing, **When** the teacher reviews the outline, **Then** it never appears as a thin bar or only part of the drawing.

---

### User Story 2 - Drag an element directly (Priority: P1)

In Select mode, a teacher presses anywhere on a visible element and moves it across the canvas while watching it follow the pointer. Drawing selection also works near a stroke or inside its bounding box. The element remains fully visible and inside the canvas. Pressing empty space clears the selection.

**Why this priority**: Direct dragging is the fastest correction when an object is in the wrong place and reduces dependence on spoken positioning.

**Independent Test**: Can be fully tested by dragging each element type from a known starting rectangle to a known destination and inspecting the final position, bounds, and history.

**Acceptance Scenarios**:

1. **Given** Select mode and a visible element, **When** the teacher presses on any part of it and drags, **Then** the element follows the pointer with live visual feedback.
2. **Given** a drag toward a canvas edge, **When** continuing past the edge, **Then** the element remains completely inside the canvas.
3. **Given** an empty area of the board, **When** the teacher presses there, **Then** any active selection is cleared.
4. **Given** a completed drag, **When** the teacher uses Undo, **Then** the element returns to its pre-drag position; **When** the teacher uses Redo, **Then** the dragged position returns.

---

### User Story 3 - Resize from a corner handle (Priority: P1)

A teacher selects an object, sees square handles on its four corners, drags one corner, and watches the object resize around the opposite fixed corner. Drawings, shapes, and equations preserve their proportions by default; headings and text change their box while their text wraps inside it. Handles remain easy to grab on ordinary classroom displays.

**Why this priority**: Precise visual sizing is needed for readability and lesson layout, but manual resizing must not distort mathematical or drawn content by default.

**Independent Test**: Can be fully tested by resizing representative objects from each corner and checking their final dimensions, fixed opposite corner, wrapping behavior, bounds, and history.

**Acceptance Scenarios**:

1. **Given** a selected element, **When** the teacher looks at its selection, **Then** square handles appear on all four corners.
2. **Given** a selected drawing, shape, or equation, **When** the teacher drags any corner, **Then** the object resizes proportionally while the opposite corner remains fixed.
3. **Given** selected text or a heading, **When** the teacher drags a corner, **Then** its box changes and the text wraps inside the new box.
4. **Given** a resize below the permitted minimum or beyond the canvas, **When** the gesture is completed, **Then** the retained result respects the 24-canvas-unit minimum and canvas maximum.
5. **Given** a completed resize, **When** the teacher uses Undo, **Then** the prior dimensions return; **When** the teacher uses Redo, **Then** the resized dimensions return.

---

### Edge Cases

- What happens when the pointer starts on overlapping elements? The existing topmost/board-order rule selects the upper object.
- What happens when a drag reaches the canvas edge? Live feedback stays clamped; the committed result lies completely inside the canvas.
- What happens when a resize would violate minimum size or leave the canvas? The committed result uses the nearest valid geometry permitted by validation.
- What happens when another command is being processed? The manual gesture waits behind it and never changes board state concurrently.
- What happens when Escape is pressed during a drag or resize? The gesture cancels, board state and history remain unchanged, and the prior selection remains available.
- What happens when the window is resized during a gesture? Existing screen-to-canvas mapping continues to govern gesture geometry.
- What happens in Pen mode? Drawing behavior is unchanged; drag and resize gestures are unavailable while drawing.
- What happens after a gesture? The manipulated object remains selected so repeated voice or manual operations can address it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Selection outlines MUST tightly cover the entire visible extent of every heading, text object, equation, shape, and drawing.
- **FR-002**: Every drawing bounding box MUST account for all points in all strokes plus half the stroke width and MUST be recalculated whenever the drawing changes through stroke addition, move, resize, undo, redo, or reopening.
- **FR-003**: Pressing any visible part of an element in Select mode MUST select that element; drawing selection MUST also work within a small stroke tolerance or inside its bounding box.
- **FR-004**: Pressing empty board space in Select mode MUST clear the active selection.
- **FR-005**: A dragged element MUST follow the pointer with live feedback and remain fully inside canvas bounds throughout the gesture.
- **FR-006**: A selected element MUST display square handles on all four corners.
- **FR-007**: Dragging a corner MUST resize the element while keeping the diagonally opposite corner fixed.
- **FR-008**: Corner resizing MUST preserve proportions by default for drawings, shapes, and equations.
- **FR-009**: Corner resizing for text and headings MUST change their containing box and wrap their text within it.
- **FR-010**: Manual resizing MUST enforce a minimum element size of 24 canvas units and MUST NOT exceed the canvas.
- **FR-011**: The pointer MUST provide a visible cursor change when hovering over a resize handle, while each handle MUST offer at least a 24-screen-pixel interaction target.
- **FR-012**: Gesture previews MUST NOT change board state; a cancelled gesture, including Escape, MUST leave board state and history unchanged.
- **FR-013**: Each completed manual drag or resize MUST produce exactly one move or resize history entry, reversible by one Undo and reappliable by one Redo.
- **FR-014**: Manual operations MUST use the same validated `move_item` and `resize_item` operations as voice commands and MUST NOT introduce new AI-addressable commands.
- **FR-015**: Gestures MUST wait behind any command already being processed and MUST never change board state concurrently with another operation.
- **FR-016**: Voice commands MUST continue to operate on manually selected, dragged, and resized elements; the manipulated object MUST remain selected after the gesture.
- **FR-017**: Dragging, resizing, selection, handles, and cursor behavior MUST work at different window sizes through the existing screen-to-canvas mapping.
- **FR-018**: Select-mode gestures MUST NOT alter Pen-mode drawing behavior.
- **FR-019**: Out of scope: rotation, multi-select, snapping and guides, copy and paste, and layering controls.

### Key Entities *(include if feature involves data)*

- **Element selection**: The currently selected board object and its exact rectangular extent, used by both manual gestures and selection-based voice commands.
- **Drawing bounding geometry**: All stroke points plus half the stroke width, recalculated after every drawing-affecting change.
- **Hit-test result**: The element identified from a Select-mode pointer action, including stroke-proximity and bounding-box alternatives for drawings.
- **Corner handle**: One of four interactive selection corners with a smaller visual square and a larger pointer target.
- **Drag gesture**: A pointer press, live translation preview, cancellation option, and at most one committed move.
- **Resize gesture**: A corner press, live proportional or box-resize preview, cancellation option, and at most one committed resize.
- **Gesture history entry**: The single reversible record created when a gesture is accepted, with an inverse operation for Undo and forward restoration for Redo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Teachers select the intended heading, text object, equation, shape, or drawing on the first attempt in at least 95 of 100 selection trials.
- **SC-002**: Every tested selection outline completely encloses its rendered object, including multi-stroke test drawings; no thin-bar or partial outline is observed.
- **SC-003**: Teachers successfully drag each element type to an intended on-canvas destination and have it remain fully visible.
- **SC-004**: Teachers successfully resize representative objects from all four corners while retaining the expected fixed opposite corner, minimum size, canvas containment, and default proportions where applicable.
- **SC-005**: Every accepted drag or resize is reversed by one Undo, restored by one Redo, and cancelled gestures leave board state and history unchanged in every cancellation trial.
- **SC-006**: At least 9 out of 10 first-time teachers can select, drag, resize, cancel, undo, and redo an element without guidance.
- **SC-007**: Voice move and resize commands continue to succeed on manually dragged and resized elements in every mixed voice/manual trial.

## Assumptions

- Existing topmost/board-order selection behavior continues when pointer actions overlap multiple eligible elements.
- The existing six-canvas-unit drawing-selection tolerance remains appropriate unless future classroom testing requires adjustment.
- Standard directional resize cursors may represent handle hover; exact cursor styling remains a presentation choice.
- The existing canvas remains fixed at 1920 by 1080 canvas units, with 24 canvas units as the universal minimum element dimension.
- Selection after a gesture remains on the manipulated object, consistent with current engine selection behavior.
- No AI command-schema change is required because manual gestures reuse existing validated operations as internal UI-sourced operations.
