# Theme Contract

`ui/theme.py` is the ONLY module that may contain color/size/font values.

## Tokens (normative minima; exact hexes live in code + contrast test)

| Token group | Contents |
|---|---|
| `window_bg`, `board_surface`, `board_border`, `board_shadow` | Dark slate window; lighter surface; thin border; soft shadow |
| `text`, `text_muted`, `text_on_accent` | Primary, secondary, on-colored-fill |
| `state_{idle,listening,processing,validating,executing}` | One color per pipeline state |
| `outcome_{done,needs_confirmation,needs_clarification,error}` | One color per result outcome |
| `font_family` | Single sans-serif stack |
| `font_{transcript,status}(≥20)`, `font_button(≥18)`, `font_board_{heading≥64,body≥36}` | Type scale (px at full canvas scale for board) |
| `mic_diameter=112`, `secondary_min=48`, `dialog_button_h≥48`, `board_radius=24`, `control_radius=8` | Sizes/radii |

## Rules

- `build_stylesheet()` generates ALL application QSS from tokens; widgets
  MUST NOT embed QSS literals or palette hexes.
- Every `(text, background)` token pair used in chrome MUST be listed in
  `CONTRAST_PAIRS` and satisfy WCAG AA (≥4.5:1 normal, ≥3:1 large text
  and controls) under the relative-luminance formula — enforced by test.
- Adding a token pair without a contrast entry fails the suite.
