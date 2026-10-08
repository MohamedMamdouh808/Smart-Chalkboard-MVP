# Feature Specification: Infinite Board

**Feature Branch**: `013-infinite-board`  
**Created**: 2026-10-08  
**Status**: Draft  
**Input**: User description: "Replace the fixed canvas with an infinite, pannable and zoomable board like Figma. The board fills the whole area between the top bar and bottom bar with no visible page edge. World model: elements live in an unbounded world coordinate space with the origin at (0,0); the camera (pan offset and zoom level) is view state, not board content. Panning: hold Space and drag, drag with the middle mouse button, scroll with the mouse wheel or touchpad (vertical and Shift+wheel for horizontal), and in Select mode dragging on empty space pans the board. Zoom: Ctrl+wheel and pinch zoom around the pointer position, zoom buttons or shortcuts Ctrl+Plus, Ctrl+Minus, Ctrl+0 to reset to 100%, and a small zoom percentage indicator; zoom range 10% to 400%. A "Fit all" shortcut (Shift+1) frames all elements. The board shows a subtle dot grid that pans and zooms with the camera. Creating text directly: in Select mode, double-clicking empty board space creates a text element at that point and enters inline editing; Enter or clicking outside commits, Escape on an empty new element discards it. Double-clicking an existing text, heading or equation edits it in place. These UI actions go through the deterministic engine as UI-originated operations (create_text and an internal edit_text), are validated, and create one Undo history entry each. Voice commands work on the infinite board: new elements created by voice are placed in the currently visible area (near its top-left with margins, below existing elements there when possible) so they are always visible; the AI context contains the visible viewport bounds in world coordinates, the selected element and the elements visible or near it. move_item and resize_item have no canvas bounds limit, and "move left", "move up" and similar relative moves use world units scaled to the current zoom. Pen drawing works at any zoom and pan, storing stroke points in world coordinates with a stroke width that is constant in world units. Selection, drag and corner-resize handles keep a constant on-screen size at any zoom. Camera changes (pan and zoom) are never commands and never create Undo history entries, but the last camera position and zoom are saved with the lesson and restored on reopen. Lessons saved on the old fixed canvas open with their elements at the same coordinates, centered in view at 100% zoom. Export renders all content (the bounding box of all elements plus a margin) at 100%. Performance: panning and zooming stay smooth with at least 200 elements, drawing only elements visible in the viewport. Out of scope: multiple pages, multi-select, rotation, snapping and guides, minimap, collaboration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate an unbounded board (Priority: P1)

A teacher pans and zooms freely across an edgeless board. Panning works by holding Space and dragging, dragging with the middle mouse button, scrolling with the wheel or touchpad, and dragging empty space in Select mode. Zooming works with Ctrl+wheel and pinch gestures around the pointer, zoom buttons and shortcuts, reset to 100%, a visible zoom percentage, fit-all framing, and a subtle dot grid that moves with the camera.

**Why this priority**: Free navigation is the defining capability of the infinite board; without reliable pan and zoom, unbounded content cannot be taught from.

**Independent Test**: Can be fully tested by panning and zooming through representative gestures, shortcuts, buttons, and indicators, verifying camera behavior, zoom limits, grid motion, performance, and history invariance—without creating or editing content.

**Acceptance Scenarios**:

1. **Given** any board content, **When** the teacher holds Space and drags, drags with the middle mouse button, scrolls vertically or horizontally, or drags empty space in Select mode, **Then** the view pans while content coordinates remain unchanged.
2. **Given** any zoom level, **When** the teacher uses Ctrl+wheel, pinch zoom, zoom buttons, or zoom shortcuts, **Then** the view zooms around the pointer within 10% to 400%, with reset returning exactly to 100%.
3. **Given** scattered elements, **When** the teacher uses Fit all, **Then** every element becomes framed in view.
4. **Given** any camera position or zoom, **When** history is inspected, **Then** camera changes have created no Undo entries.

---

### User Story 2 - Create and edit text directly on the board (Priority: P1)

A teacher double-clicks empty board space to create and immediately edit a text element, committing with Enter or by clicking outside, or discarding an empty new element with Escape. Double-clicking existing text, headings, or equations edits that content in place. Each accepted creation or edit is validated and reversible with one Undo.

**Why this priority**: Direct text entry removes the friction of dialog-driven creation and makes the infinite board immediately writable.

**Independent Test**: Can be fully tested by double-clicking empty and occupied board space, committing and cancelling edits, and verifying content, validation, selection, and one-step Undo/Redo.

**Acceptance Scenarios**:

1. **Given** Select mode and empty board space, **When** the teacher double-clicks there, **Then** a new text element appears at that point and enters inline editing.
2. **Given** an active new-text edit, **When** the teacher presses Enter or clicks outside with content present, **Then** the text commits as one Undo entry.
3. **Given** an active new-text edit with no content, **When** the teacher presses Escape, **Then** the element is discarded with no board change or history entry.
4. **Given** existing text, a heading, or an equation, **When** the teacher double-clicks it, **Then** its content becomes editable in place and commits as one Undo entry.

---

### User Story 3 - Command, draw, and reopen across the infinite board (Priority: P2)

A teacher uses voice commands, pen drawing, selection, dragging, and resizing anywhere in world coordinates. Voice-created elements appear visibly, relative moves respect zoom, drawings store world coordinates, handles stay usable at every zoom, camera position persists with lessons, legacy lessons reopen centered, and exports render all content.

**Why this priority**: The infinite board must remain fully commandable, drawable, persistent, and exportable—not merely viewable.

**Independent Test**: Can be fully tested by issuing voice commands, drawing at extremes of pan/zoom, manipulating distant content, saving/reopening lessons, reopening legacy lessons, and exporting content bounds.

**Acceptance Scenarios**:

1. **Given** any camera position, **When** a voice command creates content, **Then** the new element appears visibly near the viewport’s top-left, below nearby visible content when possible.
2. **Given** any zoom level, **When** the teacher says “move left” or “move up,” **Then** the element moves by zoom-scaled world units with no canvas-bounds rejection.
3. **Given** any pan or zoom, **When** the teacher draws, **Then** stroke points and stroke widths are stored in constant world units.
4. **Given** any zoom level, **When** an element is selected, dragged, or resized, **Then** its handles retain constant on-screen size and gestures remain accurate.
5. **Given** a saved lesson, **When** it reopens, **Then** the last camera position and zoom are restored; legacy fixed-canvas lessons reopen with unchanged coordinates, centered at 100% zoom.
6. **Given** a finished lesson, **When** it is exported, **Then** the export renders all content bounds plus a margin at 100%.

---

### Edge Cases

- What happens at extreme pan positions? Elements retain world coordinates and remain editable, selectable, and commandable.
- What happens at 10% or 400% zoom? Gestures, handles, drawing, and voice behavior remain accurate within the zoom limits.
- What happens when Fit all is used with no elements? The camera takes a sensible default view without creating content or history.
- What happens when inline editing is cancelled with existing content? Prior content is preserved without a spurious history entry.
- What happens when voice interpretation is ambiguous? Existing clarification behavior applies without guessing.
- What happens when the camera moves during a queued command? Camera state never enters command validation, history, or board content.
- What happens when reopening lessons saved under fixed or adaptive canvases? Element coordinates are preserved; only the viewing model changes.
- What happens when exporting an empty lesson? Export produces a valid empty rendering without inventing content bounds.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The board MUST fill the area between the top and bottom bars with no visible page edge.
- **FR-002**: Elements MUST live in unbounded world coordinates with the origin at (0,0); camera pan and zoom MUST be view state, never board content.
- **FR-003**: Panning MUST work by holding Space and dragging, middle-mouse dragging, vertical and Shift-modified horizontal wheel scrolling, and Select-mode empty-space dragging.
- **FR-004**: Zooming MUST work by Ctrl+wheel and pinch gestures around the pointer, zoom buttons, Ctrl+Plus, Ctrl+Minus, reset to 100% with Ctrl+0, and Fit all with Shift+1.
- **FR-005**: Zoom MUST remain within 10% to 400%, with a visible zoom percentage indicator.
- **FR-006**: The board MUST display a subtle dot grid that pans and zooms with the camera.
- **FR-007**: Double-clicking empty board space in Select mode MUST create a text element at that point and enter inline editing.
- **FR-008**: Enter or clicking outside MUST commit inline text; Escape on an empty new element MUST discard it without board or history changes.
- **FR-009**: Double-clicking existing text, headings, or equations MUST edit that content in place.
- **FR-010**: UI text creation and edits MUST pass through deterministic engine validation as UI-originated operations and create exactly one Undo entry each.
- **FR-011**: Voice-created elements MUST appear visibly near the viewport top-left, below nearby visible content when possible.
- **FR-012**: AI context MUST include visible viewport bounds in world coordinates, the selected element, and visible or nearby elements.
- **FR-013**: `move_item` and `resize_item` MUST have no canvas-bounds limit; relative voice moves MUST use zoom-scaled world units.
- **FR-014**: Pen strokes MUST store world-coordinate points with constant world-unit widths at any pan or zoom.
- **FR-015**: Selection outlines, drag behavior, and corner handles MUST retain constant on-screen size and accuracy at any zoom.
- **FR-016**: Camera changes MUST never create Undo history entries; the last camera position and zoom MUST save with the lesson and restore on reopen.
- **FR-017**: Legacy fixed-canvas lessons MUST reopen with unchanged coordinates, centered at 100% zoom.
- **FR-018**: Exports MUST render all element bounds plus a margin at 100%.
- **FR-019**: Panning and zooming MUST remain smooth with at least 200 elements by drawing only viewport-visible elements.
- **FR-020**: Out of scope: multiple pages, multi-select, rotation, snapping and guides, minimap, and collaboration.

### Key Entities *(include if feature involves data)*

- **World coordinates**: The unbounded coordinate space where all element geometry permanently lives.
- **Camera**: Pan offset plus zoom level; transient view state saved for reopening but excluded from board content and history.
- **Visible viewport**: The world-coordinate rectangle currently displayed, used for voice placement and AI context.
- **Dot grid**: The subtle camera-following background pattern.
- **Inline text edit**: A temporary editing state committed as validated text or discarded without side effects.
- **Voice placement**: Visible-area positioning for voice-created elements.
- **Content export**: All element bounds plus a margin rendered at 100%.
- **Legacy lesson view**: Unchanged fixed-canvas coordinates centered at 100% zoom.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Teachers pan and zoom using every supported gesture, button, and shortcut without content Coordinate changes in every navigation trial.
- **SC-002**: Zoom remains within 10% to 400% in every zoom trial, reset returns exactly to 100%, and the indicator always matches the active zoom.
- **SC-003**: Teachers create, commit, cancel, and edit text directly with the required Undo behavior in at least 9 out of 10 trials.
- **SC-004**: Voice-created elements are visible without manual navigation in every placement trial, and relative moves use the active zoom correctly.
- **SC-005**: Drawing, selection, dragging, resizing, handles, camera persistence, legacy reopening, and exports behave correctly at representative pan/zoom extremes.
- **SC-006**: Panning and zooming remain smooth with at least 200 elements, with only visible elements drawn.
- **SC-007**: Camera changes create zero Undo entries in every navigation trial.

## Assumptions

- “Like Figma” describes edgeless pan/zoom navigation and constant-size affordances, not feature parity with that product.
- Space-held dragging, middle-mouse dragging, wheel scrolling, and empty-space dragging coexist without changing Pen-mode drawing.
- “Below existing elements there when possible” means voice placement prefers visible empty space beneath nearby content but never overlaps illegibly when avoidable.
- “Zoom-scaled world units” means the same spoken distance covers proportionally more world space at lower zoom and less at higher zoom.
- “Constant on-screen size” permits standard pixel rounding but not zoom-dependent handle scaling.
- A margin around exported content bounds is a fixed presentation margin, not user-configurable cropping.
- This feature supersedes fixed/adaptive page-canvas constraints for navigation, validation, and export; stored element coordinates remain authoritative.
