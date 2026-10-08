# Tokens & Styles Contract

- Additive tokens only: `STRIP_H=44`, `FONT_STRIP=18`,
  `CHIP_H=34` (32–36 band), `BOARD_MARGIN=8`, `BAR_PAD_V=6`. No
  existing token value changes.
- Generated QSS gains a `QLineEdit` block: background, color,
  `placeholder-text-color` (muted token), border, `:focus` border
  (focus token), padding, font-size — all token-sourced. After this,
  the dev input carries no inline visuals except its placeholder string.
- Input text/background pair joins `CONTRAST_PAIRS` (≥4.5:1).
