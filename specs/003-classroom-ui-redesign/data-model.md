# Data Model: Classroom UI Redesign

**Feature**: `003-classroom-ui-redesign` | **Date**: 2026-10-03
**Sources**: `spec.md`, `research.md`

Board, Element, Command, History, Lesson, Viewport, and WindowPreferences
are UNCHANGED. This feature adds presentation-only entities; no stored
lesson or engine data changes shape.

## ThemeTokens

- Single source (`ui/theme.py`): palette (window bg, board surface,
  border, shadow, text, muted, per-state colors, per-outcome colors),
  typography (one sans family; transcript/status ≥20px, buttons ≥18px,
  board heading 64px / body 36px at full canvas scale), spacing, radii
  (board 24px, controls 8px), target sizes (mic 112px circle, secondary
  ≥48px, dialog buttons ≥48px high).
- Rules: every widget reads tokens; `build_stylesheet()` is the only QSS
  producer; contrast pairs declared alongside tokens for the luminance
  test. No visual literals outside this module.

## VoiceState (presentation mapping, not a new state machine)

- Keys: `idle|listening|processing|validating|executing` (mic + pill) and
  outcomes `done|needs_confirmation|needs_clarification|error` (chip).
- Each maps to exactly one `(label, color token, icon name)` triple;
  color is never the sole carrier.
- Source of truth stays the pipeline (`orchestrator.status`, engine
  result dicts); widgets render, never decide.

## BoardSurface (paint-time derivation)

- Rounded rect = canvas rect in screen space + 24px radius, 2px border,
  layered soft shadow; selection adornment = outline + 4 square corner
  handles on the selected element rect; highlight ring on the affected
  element. All derived per paint from state + viewport; nothing stored.

## State transitions (visual only)

Mic/pill appearances switch on pipeline state changes; chip updates on
each voice result; Undo/Redo enabled styling follows history
can-undo/can-redo; dialogs inherit the theme with ≥48px buttons. No
board-state transition is added or altered.
