# Feature Specification: Refine Layout Chrome

**Feature Branch**: `007-refine-layout-chrome`
**Created**: 2026-10-04
**Status**: Draft
**Input**: User description: "Refine the Smart Chalkboard layout without changing behavior, commands or data... (dev input fills bar free space with no width cap and 8px gaps, dark themed styling with always-visible text/cursor; slimmer 44px top bar with smaller transcript text, word ellipsis, tooltip, compact chip/Window; board uses full window width with ≤8px side margins and all remaining height with unchanged aspect mapping and slimmer bar padding; no overlap down to 960x540; all sizes from theme)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Type in a full-width dev input (Priority: P1)

A developer enables the developer setting and finds the transcript
input filling the entire free space between Redo and the status pill
(no width cap), about 44px high with an 8px gap on each side. It has a
dark themed background, light text at least 18px, the muted placeholder,
a visible focus outline, and typed text plus cursor always clearly
visible — no white default styling anywhere.

**Why this priority**: The input is the daily driver for AI-path
testing; it should use the room the compact bar freed.

**Independent Test**: Can be fully tested with the setting on by
measuring the input against its neighbors, typing text, focusing it,
and submitting through the unchanged path.

**Acceptance Scenarios**:

1. **Given** the developer setting on, **When** the bottom bar is
   measured, **Then** the input spans from 8px after Redo to 8px before
   the pill with no maximum width and is about 44px high.
2. **Given** the input focused with typed text, **When** viewed, **Then**
   the background is dark themed, the text and cursor are clearly
   visible, and a focus outline shows — with no white styling.
3. **Given** Enter pressed, **When** submitted, **Then** the text flows
   through the unchanged path and the box clears.

---

### User Story 2 - Read a slimmer top bar (Priority: P1)

The top bar is about 44px high: the "Heard:" label and transcript use a
smaller 18–20px font, vertically centered, with word-boundary "..."
shortening and full-text tooltip; the chip and Window button are compact
(32–36px high) and anchored right.

**Why this priority**: A shorter top bar returns the room to the board
where it matters most.

**Independent Test**: Can be fully tested by measuring bar/label/chip
heights, checking vertical centering, and exercising a long transcript.

**Acceptance Scenarios**:

1. **Given** the top bar, **When** measured, **Then** it is about 44px
   high with label and transcript in 18–20px text, vertically centered.
2. **Given** an overlong transcript, **When** viewed, **Then** it ends
   at a word boundary with "..." and the full text appears on hover.
3. **Given** the chip and Window button, **When** measured, **Then**
   each is 32–36px high and both stay anchored right and fully visible.

---

### User Story 3 - Teach on the largest possible board (Priority: P1)

The canvas spans the full window width with at most 8px margins on each
side and all remaining height between the bars, keeping the same
aspect-ratio-preserving, centered mapping; slimmer bar padding gives the
room back. Nothing overlaps the board down to 960×540, and logical
size, coordinates, selection, and pen mapping are unchanged.

**Why this priority**: Every reclaimed pixel goes to lesson content —
the point of all three layout features.

**Independent Test**: Can be fully tested by measuring margins and board
height at three window sizes and verifying mapping accuracy is
unchanged.

**Acceptance Scenarios**:

1. **Given** any supported window size, **When** the canvas is measured,
   **Then** side margins are at most 8px each and it fills all height
   between the bars with unchanged aspect mapping.
2. **Given** 960×540, **When** the full window is inspected, **Then** no
   control overlaps the board and pen taps still select exactly the
   intended element.

---

### Edge Cases

- What happens with a very narrow window and a long transcript? → The
  transcript yields (elides) while chip and Window button stay visible.
- What happens when the input text is very long? → The input scrolls
  internally; neighbors never shift and no overlap occurs.
- What happens with the developer setting off? → The middle stays empty
  and the bar matches the current compact layout exactly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dev input MUST fill the free bottom-bar space between
  Redo and the pill with no maximum width, about 44px high, with an 8px
  gap to each neighbor.
- **FR-002**: The input MUST use a dark themed background, light text at
  least 18px, the muted placeholder, and a visible focus outline, with
  typed text and cursor clearly visible at all times and no white
  default styling.
- **FR-003**: The top bar MUST be about 44px high with "Heard:" label
  and transcript in 18–20px vertically centered text, word-boundary
  "..." shortening, and full-text tooltip.
- **FR-004**: The chip and Window button MUST be 32–36px high, anchored
  right, and fully visible at every supported size.
- **FR-005**: The canvas MUST use the full window width with at most 8px
  side margins and all remaining bar-to-bar height, with the unchanged
  aspect-preserving centered mapping and slimmer bar padding.
- **FR-006**: Nothing MUST overlap the board down to 960×540; logical
  size, coordinates, selection, and pen mapping MUST be unchanged.
- **FR-007**: All sizes MUST come from the central theme; no behavior,
  commands, data, colors (beyond the existing tokens), or board
  rendering logic may change.

### Key Entities

- **Dev input (full-bleed)**: Flag-gated box spanning bar free space;
  same submit contract, roomier presentation.
- **Slim top bar**: 44px strip with smaller transcript text and compact
  right-anchored chip + Window button.
- **Maximized canvas area**: Full-width (≤8px margins), full-height
  board region under the unchanged mapping.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Input spans Redo+8px to pill−8px with no width cap in 10
  out of 10 inspections, at 44px height with visible text, cursor, and
  focus outline and zero white styling.
- **SC-002**: Top bar measures about 44px with 18–20px centered text;
  chip and Window button measure 32–36px and stay right-anchored.
- **SC-003**: Side margins measure at most 8px each and board height is
  strictly greater than before at the same window size.
- **SC-004**: 100 pen taps across three sizes select exactly the
  intended element (mapping unchanged).
- **SC-005**: Zero behavior regressions: the full pre-change suite
  passes with only layout-assertion updates where the refinement
  requires them.

## Assumptions

- "About" sizes allow whole-pixel rounding from theme tokens without
  changing targets or minima.
- Removing the 700px cap supersedes the prior cap; nothing else from
  the dev-input contract changes.
- Slimmer bar padding means reduced vertical chrome margins, never
  smaller than the control minima.
