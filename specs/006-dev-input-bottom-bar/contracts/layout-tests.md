# Layout Tests Contract

pytest-qt offscreen at 960×540, 1366×768, 1920×1080 (flag on via
monkeypatched env + rebuilt window, and flag off):

- Flag on: input visible; input rect disjoint from mic/Undo/Redo/pill
  rects; input width ≤ 700; top strip has no input child.
- Flag off: input hidden (`isVisible() is False`); bar control order,
  sizes, and positions match the pre-move layout.
- Both: board-view height equals the flag-off height at the same size;
  submit still clears; disabled state appears while processing.
