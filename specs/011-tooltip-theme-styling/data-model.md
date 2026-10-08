# Data Model: Tooltip Theme Styling

**Feature**: `011-tooltip-theme-styling` | **Date**: 2026-10-06
**Sources**: Approved `spec.md`, follow-up technical direction, `research.md`, constitution v1.0.0

Board, command, history, lesson, queue, provider, persistence, and tooltip-text shapes remain unchanged. This feature adds shared tooltip presentation values, application styling behavior, and tooltip tests; it does not add tooltips, commands, stored data, or application behavior.

## Tooltip appearance

- `background`: existing dark `BUTTON_BG`.
- `foreground`: existing light `TEXT`.
- `font_size`: existing `FONT_BUTTON`, at least 16 pixels.
- `border`: 1px using existing `BUTTON_BORDER`.
- `corner_radius`: existing `CONTROL_RADIUS`.
- `vertical_padding`: tooltip-specific `TOOLTIP_PAD_V`, 6 pixels.
- `horizontal_padding`: tooltip-specific `TOOLTIP_PAD_H`, 10 pixels.
- `delay_ms`: tooltip-specific `TOOLTIP_WAKEUP_DELAY_MS`, 500 milliseconds.
- All values originate in the central theme module.

## Tooltip behavior

- Application-level generated QSS reaches tooltip popups as separate top-level windows.
- A narrow proxy style returns 500ms for tooltip wake-up delay and delegates all other behavior.
- Native tooltip timing, dismissal, and placement behavior remain unchanged.
- Existing tooltip text, including the complete transcript, remains byte-identical.

## Theme and test relationships

- The generated stylesheet contains one authoritative `QToolTip` rule using the tooltip appearance tokens.
- The explicit tooltip contrast test uses the existing normal-text WCAG AA threshold.
- The proxy-style test verifies the delay without timing-dependent hover behavior.
- The existing transcript-tooltip test verifies full-text preservation.

## Entity-to-story mapping

- US1 readable tooltips: tooltip appearance, central theme source, contrast behavior.
- US2 timing and placement: tooltip delay, native placement, transcript preservation.
- US3 consistent theme: one generated rule and theme-sourced values everywhere.
