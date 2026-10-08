# Data Model: Compact Control Layout

**Feature**: `004-compact-control-layout` | **Date**: 2026-10-04
**Sources**: `spec.md`, `research.md`

Board, Element, Command, History, Lesson, Viewport, WindowPreferences,
and all 003 presentation entities are UNCHANGED in behavior. This feature
retunes sizes and re-parents two controls.

## Retuned size tokens (`ui/theme.py` only)

- `MIC_DIAMETER`: 112 → 64 (circular mic; ≥44px target kept).
- `COMPACT_CONTROL_H` (new): 44 — Undo/Redo height and Window-button
  square size; minimum target 44px in both dimensions.
- `PILL_H` (new): 36 — status pill height; width fits text (no fixed width).
- Spacing, radii, fonts, and ALL colors unchanged.

## Control placement (layout facts, not new entities)

- Bottom bar order: mic, Undo, Redo (left group) → stretch → status
  pill (right). No equal-width stretching.
- Top strip order: "Heard:" label, transcript (stretch), result chip,
  Window button (rightmost, after chip).
- Transcript label: visible text = word-boundary elision + "…" of the
  full transcript; tooltip = full transcript. Recomputed on strip resize.

## State transitions

None added or altered: toggle, pill, chip, mic-state, undo/redo enable,
and dialog flows behave exactly as before; only geometry and transcript
shortening change.
