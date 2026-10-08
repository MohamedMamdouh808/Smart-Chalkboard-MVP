# Text and Placement Contract

## Text preservation

- Every existing tooltip retains byte-identical text.
- The transcript tooltip retains the complete transcript, including when visible text is elided.
- Styling changes must not add, remove, reorder, or shorten tooltip text.

## Placement behavior

- Native Qt tooltip timing, dismissal, and placement behavior remain unchanged.
- Compact themed padding minimizes unnecessary coverage without custom positioning logic.
- No new tooltips and no unrelated application behavior are introduced.
