# Layout Contract

## Bottom bar (one `QHBoxLayout`)

Order: mic (64px circle) → Undo (44px high) → Redo (44px high) →
stretch spacer → status pill (36px high, width fits text). Every control
≥44px in both dimensions. Widgets MUST NOT stretch to equal widths; the
middle stays empty.

## Top strip (one `QHBoxLayout`)

Order: "Heard:" label → transcript label (stretch) → result chip →
Window button (44px icon-only, tooltip + accessibleName "Window", F11
binding kept).

## Board gain

At any window size the board view is strictly taller than the pre-change
layout (same window size), because chrome consumes less vertical room.
Canvas size (1920×1080), aspect ratio, and letterboxing are unchanged —
the viewport simply computes a larger scale.

## No-overlap rule

At 960×540, 1366×768, and 1920×1080, all pairwise widget rectangles in
both bars are disjoint, and chip + Window button are fully inside the
strip rect.
