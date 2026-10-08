# Layout Tests Contract

pytest-qt offscreen at 960×540, 1366×768, 1920×1080 (flag on):

- Input fill: input right edge within 8px + pill padding of the pill's
  left edge AND input left edge within 8px + of Redo's right edge (fills
  the gap, both sides).
- Input contrast: input text color vs input background ≥4.5:1 (token
  pair, computed — not eyeballed).
- Board width rule: board-view width equals window width minus margins
  (≤16px total) WHEN width binds first under the aspect rule; when
  height binds, the canvas stays centered with symmetric pillar margins
  (assert the rule branch actually taken, not a fixed width).
- Regression: all prior layout assertions keep passing with only the
  sizes this feature intentionally moves.
