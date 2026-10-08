# Transcript Contract

- Visible text: the full transcript shortened at the last word boundary
  that fits the label width, plus "…". NEVER cut mid-word (unless a
  single word exceeds the whole width and no boundary exists).
- Tooltip: `setToolTip(fullTranscript)` on every update — the complete
  text is always one hover away.
- Recompute on every strip resize (the available width changes with the
  window and with chip/Window-button geometry).
- The result chip and Window button MUST remain fully visible and
  operable at every size down to 960×540; the transcript yields space,
  never them.
- Two-line wrap is acceptable ONLY if the theme reserves strip height
  for it; the default stays single-line elision per spec assumption.
