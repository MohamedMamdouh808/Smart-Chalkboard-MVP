# Text-Fit Contract

- Wrap: heading/text render with word-wrap INSIDE the fixed element box.
  Box size and coordinates never change to fit text (clarify 2026-10-03).
- Creation gate (app layer, before queueing): font-metrics check against
  the default box; failure rejects with exactly:
  `Text is too long for this element. Resize it or shorten the text.`
- Post-resize shortfall: paint clips at the box edge; layout, coordinates,
  history, saves, and exports unchanged.
- Engine (`core/` validators, schema, execution) is NOT modified by this
  feature; the gate is additive in the app layer only.
