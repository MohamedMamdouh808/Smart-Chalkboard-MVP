# Chrome Geometry Contract

- Strip: minimum height `STRIP_H` (44px); Heard + transcript at
  `FONT_STRIP` (18px), vertically centered; transcript elides with
  tooltip (unchanged rule); chip + Window button `CHIP_H` (34px),
  right-anchored, fully visible ≥960×540.
- Bar: dev input fills the Redo→pill gap (no width cap), 44px,
  8px gaps to neighbors; bar vertical padding `BAR_PAD_V`.
- Board cell: window width minus at most 2×`BOARD_MARGIN` (8px each
  side), full inter-bar height; viewport mapping rule byte-identical —
  the canvas only ever scales larger.
- Disjointness at 960×540, 1366×768, 1920×1080 (all chrome pairs).
