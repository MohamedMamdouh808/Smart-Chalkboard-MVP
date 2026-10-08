# Stylesheet Contract

## Central rule

- `theme.build_stylesheet()` contains exactly one authoritative `QToolTip` rule for application tooltips.
- The rule uses:
  - `BUTTON_BG` background;
  - `TEXT` foreground;
  - `FONT_BUTTON` size;
  - 1px `BUTTON_BORDER` border;
  - `CONTROL_RADIUS` corners;
  - `TOOLTIP_PAD_V` vertical padding;
  - `TOOLTIP_PAD_H` horizontal padding.
- Required values are `6px` vertical padding and `10px` horizontal padding.
- No widget-level stylesheet may define tooltip colors, sizes, borders, radii, padding, or delay.
- No tooltip text may change as part of styling.
