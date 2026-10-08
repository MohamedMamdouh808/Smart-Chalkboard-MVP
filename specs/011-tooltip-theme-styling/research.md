# Research: Tooltip Theme Styling

**Feature**: `011-tooltip-theme-styling` | **Date**: 2026-10-06
**Input**: Approved `spec.md`, follow-up technical direction, constitution v1.0.0, existing theme/UI implementation

No NEEDS CLARIFICATION remains. The specification fixes appearance, timing, placement, text preservation, and theme sourcing; the technical direction fixes the stylesheet, application-level styling, delay mechanism, and tests.

## Decisions

### R-01: Extend the central QToolTip rule with tooltip-specific theme tokens

- **Decision**: Add `TOOLTIP_PAD_V`, `TOOLTIP_PAD_H`, and `TOOLTIP_WAKEUP_DELAY_MS` to `theme.py`, then generate one `QToolTip` rule using:
  - `BUTTON_BG` background;
  - `TEXT` foreground;
  - `FONT_BUTTON` size;
  - `BUTTON_BORDER` 1px border;
  - `CONTROL_RADIUS` corners;
  - tooltip padding tokens for 6px vertical and 10px horizontal padding.
- **Rationale**: Keeps every tooltip value in the single visual authority while satisfying the exact requested geometry. Existing generic spacing tokens do not include the required 10px horizontal value.
- **Alternatives rejected**: QSS literals in widgets or stylesheets, which would violate central-theme and no-visual-literals rules; reusing an unrelated 16px spacing token, which would change the requested padding.

### R-02: Keep application-level styling for separate tooltip windows

- **Decision**: Continue applying `build_stylesheet()` with `app.setStyleSheet()` at `QApplication` level and avoid widget-level tooltip styling.
- **Rationale**: Tooltip popups are separate top-level windows; application-level styling is what reaches them without duplicating rules.
- **Alternatives rejected**: Per-widget tooltip stylesheets, which would fragment the theme and risk missing popups.

### R-03: Implement the delay with a narrow QProxyStyle hint

- **Decision**: Add a small `QProxyStyle` subclass that returns `500` only for `SH_ToolTip_WakeUpDelay` and delegates every other style hint unchanged; install it once during application startup.
- **Rationale**: This is the Qt-supported mechanism for tooltip timing and avoids custom hover timers or tooltip-window code.
- **Alternatives rejected**: Manual hover timers, which would duplicate native behavior and complicate dismissal/placement; changing unrelated style behavior.

### R-04: Preserve native tooltip placement and all existing text

- **Decision**: Make no tooltip-text or tooltip-positioning changes; rely on compact themed padding and native Qt placement.
- **Rationale**: The requested “only as much as necessary” behavior is a placement outcome, not a new positioning feature, and text preservation is explicitly required.
- **Alternatives rejected**: Custom tooltip windows or manual placement logic, both outside the approved scope.

### R-05: Test generated QSS, delay, contrast, and text preservation

- **Decision**:
  - Assert the generated stylesheet contains the `QToolTip` rule and token colors.
  - Add an explicit tooltip foreground/background WCAG AA test alongside the existing generic contrast gate.
  - Assert the proxy style returns 500ms for tooltip wake-up delay.
  - Reuse the existing transcript-tooltip test for full-text preservation.
- **Rationale**: These tests directly encode the technical direction without timing-flaky hover tests or new user-facing behavior.
- **Alternatives rejected**: Timing-based hover appearance tests; screenshot-only verification without token assertions.

## Performance notes

- Stylesheet generation remains a startup-only string operation.
- The proxy style changes one style hint and delegates everything else.
- No additional paint, layout, timer, or state work is introduced.
