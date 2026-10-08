# Style and Delay Contract

## Application styling

- The generated stylesheet is applied with `app.setStyleSheet()` at `QApplication` level.
- Tooltip popups, as separate top-level windows, receive the central rule.
- No additional application stylesheet path for tooltips is introduced.

## Delay behavior

- A narrow `QProxyStyle` subclass returns `TOOLTIP_WAKEUP_DELAY_MS` for `SH_ToolTip_WakeUpDelay`.
- The required delay is 500 milliseconds.
- All other style hints delegate unchanged to the base style.
- The proxy style is installed once during application startup.
- No custom hover timers or tooltip-window implementations are introduced.
