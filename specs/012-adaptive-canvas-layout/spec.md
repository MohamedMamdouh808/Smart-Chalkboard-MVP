# Feature Specification: Adaptive Canvas Layout

**Feature Branch**: `012-adaptive-canvas-layout`  
**Created**: 2026-10-07  
**Status**: Draft  
**Input**: User description: "Make the Smart Chalkboard board fill the entire free area of the window, full width and full height between the top bar and bottom bar with at most an 8px margin, instead of a fixed 16:9 canvas. Replace the fixed 1920x1080 canvas with an adaptive canvas whose logical size follows the board area at 1:1 scale (one canvas unit equals one screen pixel at the base scale), so text, drawings and shapes are never stretched or distorted. Elements keep their absolute canvas coordinates, and a window resize never moves, rescales or deletes elements. Each lesson stores its canvas size, which grows to the largest board area the lesson has had and never shrinks automatically; the engine validates bounds, drag and resize clamping, default placement and export against this stored canvas size, and the canvas size is part of the board state and the AI context so the same command on the same state gives the same result. Enlarging the window or entering fullscreen grows the canvas and reveals new empty space on the right and bottom; the origin stays at the top-left. If the window is smaller than the stored canvas size, the whole canvas is scaled down uniformly to fit, centered, so no element is clipped or hidden; letterboxing appears only in that case. Pen drawing, selection, dragging, corner resizing and voice commands work at every window size through the same screen-to-canvas mapping, which includes the uniform scale. A canvas size change from resizing the window is not a user command and does not create an Undo history entry. Existing lessons saved on the 1920x1080 canvas open with that size as their stored canvas size and their elements keep their coordinates. Minimum window size stays 960x540 and the default canvas size for a new lesson is the board area at first open, with a minimum of 960x540. Exports use the stored canvas size. Out of scope: user-selectable canvas sizes, multiple pages, infinite canvas, zoom and pan, non-uniform stretching."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use the full classroom window (Priority: P1)

A teacher opens the board at any supported window size and sees it fill the available area between the top and bottom bars, with only a small margin. Text, drawings, and shapes retain their natural proportions and are never stretched to fit an artificial canvas shape.

**Why this priority**: Classroom displays and window sizes vary; using the available space without distortion is the central visible improvement.

**Independent Test**: Can be fully tested by opening representative window sizes and fullscreen, then checking board coverage, margins, proportions, and the absence of distortion—without creating or moving content.

**Acceptance Scenarios**:

1. **Given** any supported window size, **When** the board is displayed, **Then** it fills the full available width and height between the bars with no more than an 8-pixel margin.
2. **Given** headings, text, drawings, and shapes, **When** the window changes size or shape, **Then** every object retains its natural proportions and is never stretched.
3. **Given** a larger window or fullscreen, **When** the board grows, **Then** new empty space appears on the right and bottom while the origin remains at the top-left.

---

### User Story 2 - Keep every element stable while resizing (Priority: P1)

A teacher resizes the window during a lesson without losing work. Existing elements retain their absolute positions, sizes, and content; drawing, selection, dragging, resizing, and voice commands continue to work through the same coordinate mapping at every size.

**Why this priority**: Lessons must survive ordinary window management; moving or losing content during a resize would be unacceptable.

**Independent Test**: Can be fully tested by placing content, resizing through representative sizes, and verifying coordinates, interaction accuracy, command behavior, and history behavior.

**Acceptance Scenarios**:

1. **Given** existing elements, **When** the window is resized, **Then** no element moves, rescales, disappears, or changes content.
2. **Given** any supported window size, **When** the teacher draws, selects, drags, resizes, or issues voice commands, **Then** pointer and command coordinates behave consistently through the same mapping.
3. **Given** a window resize, **When** history is inspected, **Then** the canvas-size change has created no Undo entry.
4. **Given** a window smaller than the stored lesson canvas, **When** the lesson is displayed, **Then** the whole canvas is uniformly scaled to fit and centered, with no clipped or hidden elements.

---

### User Story 3 - Preserve lessons, exports, and command determinism (Priority: P2)

A teacher reopens older and newer lessons with confidence. Each lesson remembers the largest canvas it has used, exports at that stored size, and produces deterministic command results from identical board states.

**Why this priority**: Stored lessons and exports are durable work products; changing their coordinates or command behavior would erode trust.

**Independent Test**: Can be fully tested by reopening legacy lessons, enlarging and shrinking windows, exporting lessons, and replaying identical commands against identical states.

**Acceptance Scenarios**:

1. **Given** a lesson previously saved at 1920 by 1080, **When** it reopens, **Then** its stored canvas size is 1920 by 1080 and all elements retain their coordinates.
2. **Given** an enlarged window, **When** the lesson grows, **Then** its stored canvas size increases to the larger board area and never shrinks automatically afterward.
3. **Given** identical board states including canvas size, **When** the same command is applied, **Then** the result is identical, including validation, placement, and export behavior.
4. **Given** a finished lesson, **When** it is exported, **Then** the export uses the lesson’s stored canvas size.

---

### Edge Cases

- What happens when the window is smaller than the stored canvas? The canvas scales uniformly, centers, and letterboxes only as needed; nothing is clipped or hidden.
- What happens when the window grows and then shrinks? The stored canvas remains at its largest size; display scaling handles the smaller window without moving content.
- What happens to a brand-new lesson? Its initial canvas is the board area at first open, never smaller than 960 by 540.
- What happens when the window is at its 960-by-540 minimum? The board still fills the available area subject to the same mapping and margin rules.
- What happens to Undo history during window resizing? Canvas-size changes never create history entries.
- What happens to exports? They always use the stored lesson canvas size.
- What happens to user-selected canvas sizes, pages, infinite canvas, zoom, pan, or stretching? All remain explicitly out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The board MUST fill the full available window width and height between the top and bottom bars, with no more than an 8-pixel margin.
- **FR-002**: The logical canvas size MUST follow the available board area at one canvas unit per screen pixel at the base scale.
- **FR-003**: Text, drawings, and shapes MUST never be stretched or distorted by window size or shape.
- **FR-004**: Window resizing MUST NOT move, rescale, delete, or otherwise alter existing elements.
- **FR-005**: Each lesson MUST store its canvas size as the largest board area it has had; the stored size MUST NOT shrink automatically.
- **FR-006**: Bounds validation, drag clamping, resize clamping, default placement, and export MUST use the lesson’s stored canvas size.
- **FR-007**: Stored canvas size MUST be part of board state and AI context so identical commands on identical states produce identical results.
- **FR-008**: Canvas growth MUST reveal new empty space on the right and bottom while retaining the origin at the top-left.
- **FR-009**: When the window is smaller than the stored canvas, the entire canvas MUST scale uniformly to fit and center, with letterboxing only in that case and no clipped or hidden elements.
- **FR-010**: Pen drawing, selection, dragging, corner resizing, and voice commands MUST work at every window size through the same mapping, including any uniform display scale.
- **FR-011**: A window-driven canvas-size change MUST NOT be treated as a user command and MUST NOT create an Undo history entry.
- **FR-012**: Lessons saved on the legacy 1920-by-1080 canvas MUST reopen with that stored size and unchanged element coordinates.
- **FR-013**: Minimum window size MUST remain 960 by 540; a new lesson MUST default to its first-open board area, never below 960 by 540.
- **FR-014**: Exports MUST use the stored lesson canvas size.
- **FR-015**: Out of scope: user-selectable canvas sizes, multiple pages, infinite canvas, zoom and pan, and non-uniform stretching.

### Key Entities *(include if feature involves data)*

- **Board area**: The available window region between the top and bottom bars, filled subject to the small-margin rule.
- **Stored canvas size**: Each lesson’s largest-used logical width and height, used for validation, placement, context, and export.
- **Element coordinates**: Absolute positions and dimensions that remain stable across window resizes.
- **Display mapping**: The reversible relationship between screen pixels and canvas units, including uniform downscaling when required.
- **Legacy lesson size**: The 1920-by-1080 canvas assigned when reopening lessons saved before adaptive canvases.
- **Exported lesson image**: The lesson rendered at its stored canvas size.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At every tested window size and fullscreen state, the board fills the available area within the permitted margin and shows no distorted text, drawings, or shapes.
- **SC-002**: Across repeated resize trials, 100% of existing elements retain their exact coordinates, dimensions, and content.
- **SC-003**: Pointer, drawing, selection, drag, resize, and voice-command accuracy remain correct at every tested window size.
- **SC-004**: Stored canvas sizes grow when windows enlarge, never shrink automatically, and exports always match the stored size.
- **SC-005**: Legacy lessons reopen with a 1920-by-1080 stored canvas and unchanged coordinates in every reopen trial.
- **SC-006**: Window resizes create zero Undo history entries in every resize trial.
- **SC-007**: At least 9 out of 10 teachers can resize, reopen, and export lessons without guidance or lost work.

## Assumptions

- The top and bottom bars retain their existing purposes and approximate layout; only the board area becomes adaptive.
- “At most an 8-pixel margin” permits a smaller margin where layout requires it.
- “Base scale” means one canvas unit equals one screen pixel before any required uniform downscaling.
- Uniform downscaling is used only when the available board area is smaller than the stored lesson canvas.
- The existing 960-by-540 minimum window size continues to bound supported layouts.
- No user-facing control for selecting canvas size is required.
