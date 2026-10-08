# Research: Compact Control Layout

**Feature**: `004-compact-control-layout` | **Date**: 2026-10-04
**Input**: spec + user technical brief (theme size tokens, QHBoxLayout
left-group/stretch/pill, Window button after chip, elidedText + tooltip,
pytest-qt layout tests at three sizes)

No NEEDS CLARIFICATION: the brief prescribes each mechanism; the spec
locks sizes, order, and minima.

## Decisions

### R-01: Theme size tokens (no other value changes)

- **Decision**: Retune only size tokens in `ui/theme.py`: mic diameter
  112→64, compact control height 44, pill height 36, keep 48px-era minima
  where the spec still requires ≥44px targets; spacing tokens reused
  unchanged. No color, font, radius, or icon changes.
- **Rationale**: Spec FR-010 (all sizes from the central theme) with
  FR-011's ban on new colors; one-token change propagates to every
  consumer and test.
- **Alternatives rejected**: Hard-coded per-widget sizes (reintroduces
  the drift the theme exists to prevent).

### R-02: Bottom bar as left-group + stretch + pill

- **Decision**: Rebuild the bar as one `QHBoxLayout`: left group (mic,
  Undo, Redo in that order), an expanding stretch spacer, status pill
  right-anchored. No equal-width stretching; the middle stays empty and
  the board view (stretch=1 above) absorbs the freed vertical room.
- **Rationale**: Spec FR-001/FR-007 by construction; the existing
  vertical layout already gives reclaimed height to the board.
- **Alternatives rejected**: Fixed-position widgets (breaks at 960×540);
  spacer widgets with fixed widths (same result, more code).

### R-03: Window button after the result chip

- **Decision**: Move the existing Window toggle (same widget behavior,
  icon, F11 binding) into the top strip layout immediately after the
  result chip: 44px icon-only button, tooltip + accessibleName "Window".
- **Rationale**: Spec FR-004/FR-005; top-right placement keeps it beside
  the outcome it often follows (e.g., Done → present fullscreen).
- **Alternatives rejected**: Menu/overflow entry (hides a P1 control);
  duplicating the button (two sources of truth for one mode).

### R-04: Elided transcript with full-text tooltip

- **Decision**: `QFontMetrics.elidedText(text, ElideRight, availableWidth)`
  on the transcript label (word-boundary-safe: Qt elides at character
  level, so pre-truncate to the last space before the width, then append
  "…"), full text in `setToolTip`. Recompute on strip resizes via
  `resizeEvent`. Two-line wrap stays available only if the theme ever
  reserves strip height — default stays single-line per spec assumption.
- **Rationale**: Spec FR-008 exactly; tooltip preserves the complete
  transcript for verification.
- **Alternatives rejected**: Character-level cut without ellipsis
  (repeats the reported bug); marquee scrolling (motion during teaching,
  accessibility harm).

### R-05: Layout tests at three sizes

- **Decision**: pytest-qt offscreen at 960×540, 1366×768, 1920×1080:
  assert left-group order (mic.x < undo.x < redo.x), pill right-anchored
  (pill.right ≈ bar.right), pairwise widget-rectangle disjointness (no
  overlaps), chip + Window button fully inside the strip, and board-view
  height strictly greater than the pre-change layout at the same window
  size (compare against recorded baseline constant from 003 refs run).
- **Rationale**: User-brief directive; geometric assertions, immune to
  font-rendering noise.
- **Alternatives rejected**: Screenshot-only checks (already covered by
  003 regression refs; geometry needs numbers, not pixels).

## Performance notes

- Elision recompute is O(text length) on strip resize only — negligible
  against paint; no command-path impact, 3 s voice budget unaffected.
