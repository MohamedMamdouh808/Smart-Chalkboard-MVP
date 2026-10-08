"""Single visual authority: tokens, QSS generation, contrast pairs.

Every color/size/font in the app originates here. Widgets MUST NOT contain
visual literals (enforced by tests/ui/test_theme_tokens.py).
"""

from __future__ import annotations

# -- palette ---------------------------------------------------------------
WINDOW_BG = "#14141f"
BOARD_SURFACE = "#262640"
BOARD_BORDER = "#6a6a96"
BOARD_SHADOW = "#0a0a12"
STRIP_BG = "#1e1e2e"
BUTTON_BG = "#2a2a44"
BUTTON_BG_ALT = "#22223a"
BUTTON_HOVER_BG = "#34345e"
BUTTON_PRESSED_BG = "#1a1a28"
BUTTON_DISABLED_BG = "#1e1e2c"
BUTTON_BORDER = "#4a4a6a"
FOCUS_RING = "#7aa2ff"

TEXT = "#F5F5F5"
TEXT_MUTED = "#B0B0C8"
TEXT_DISABLED = "#8a8a9e"
TEXT_ON_DARK = "#F5F5F5"
TEXT_ON_ACCENT = "#14141f"
INPUT_BG = BUTTON_BG_ALT

STATE_COLORS: dict[str, str] = {
    "idle": "#9E9E9E",
    "listening": "#E53935",
    "processing": "#1E88E5",
    "validating": "#FDD835",
    "executing": "#43A047",
}

OUTCOME_COLORS: dict[str, str] = {
    "done": "#69F0AE",
    "needs_confirmation": "#FDD835",
    "needs_clarification": "#1E88E5",
    "error": "#E53935",
}

SELECTION = "#FFEB3B"
HIGHLIGHT = "#69F0AE"
EQUATION = "#FFE082"

STATE_ICONS: dict[str, str] = {
    "idle": "dot-idle",
    "listening": "mic",
    "processing": "dot-processing",
    "validating": "dot-validating",
    "executing": "dot-executing",
}

OUTCOME_ICONS: dict[str, str] = {
    "done": "check",
    "needs_confirmation": "alert",
    "needs_clarification": "question",
    "error": "error",
}

# -- typography (single sans-serif stack) -------------------------------------
FONT_FAMILY = "Segoe UI, Arial, sans-serif"
FONT_TRANSCRIPT = 24
FONT_STATUS = 22
FONT_BUTTON = 20
FONT_BOARD_HEADING = 64
FONT_BOARD_BODY = 36
FONT_HEARD_LABEL = 16

# -- sizes / spacing / radii --------------------------------------------------
MIC_DIAMETER = 64
COMPACT_CONTROL_H = 44
PILL_H = 36
STRIP_H = 44
FONT_STRIP = 18
CHIP_H = 34
BOARD_MARGIN = 8
BAR_PAD_V = 6
DIALOG_BUTTON_H = 64
BOARD_RADIUS = 24
CONTROL_RADIUS = 8
HANDLE_SIZE = 14
SPACING = 16

# -- contrast pairs (fg, bg, kind) --------------------------------------------
# kind "normal" → ≥4.5:1, kind "large" → ≥3:1 (WCAG AA).
CONTRAST_PAIRS: tuple[tuple[str, str, str], ...] = (
    (TEXT, BUTTON_BG, "normal"),
    (TEXT, BUTTON_BG_ALT, "normal"),
    (TEXT, STRIP_BG, "normal"),
    (TEXT_MUTED, STRIP_BG, "normal"),
    (TEXT, BOARD_SURFACE, "normal"),
    (EQUATION, BOARD_SURFACE, "normal"),
    (TEXT_DISABLED, BUTTON_DISABLED_BG, "normal"),
    (TEXT, BUTTON_HOVER_BG, "normal"),
    (TEXT, BUTTON_PRESSED_BG, "normal"),
    (TEXT, INPUT_BG, "normal"),
    *( (color, BUTTON_BG, "large") for color in STATE_COLORS.values() ),
    *( (color, BUTTON_BG, "large") for color in OUTCOME_COLORS.values() ),
    (SELECTION, BOARD_SURFACE, "large"),
    (HIGHLIGHT, BOARD_SURFACE, "large"),
    (TEXT_ON_ACCENT, SELECTION, "normal"),
    (BOARD_BORDER, WINDOW_BG, "large"),
    (FOCUS_RING, BUTTON_BG, "large"),
)

# -- element palette (voice-addressable named colors + default) ------------------
ELEMENT_COLORS: dict[str, str] = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#E53935",
    "green": "#43A047",
    "blue": "#1E88E5",
    "yellow": "#FDD835",
    "orange": "#FB8C00",
    "purple": "#8E24AA",
    "brown": "#6D4C41",
    "gray": "#9E9E9E",
}
DEFAULT_ELEMENT_COLOR = "#FFFFFF"

# -- backwards-compatible aliases (002-era names) ------------------------------
BUTTON_TEXT = TEXT
BUTTON_BACKGROUNDS = (BUTTON_BG, BUTTON_BG_ALT)
BOARD_BACKGROUND = WINDOW_BG
STRIP_BACKGROUND = STRIP_BG
STATUS_DIM = TEXT_MUTED


def build_stylesheet() -> str:
    """Generate the entire application QSS from tokens."""
    return f"""
QMainWindow, QWidget#root {{ background-color: {WINDOW_BG}; }}
QLabel {{ color: {TEXT}; font-family: "{FONT_FAMILY}"; }}
QToolTip {{ color: {TEXT}; background-color: {BUTTON_BG}; font-size: {FONT_BUTTON}px; }}
QPushButton {{
  font-family: "{FONT_FAMILY}"; font-size: {FONT_BUTTON}px; color: {TEXT};
  background-color: {BUTTON_BG}; border: 1px solid {BUTTON_BORDER};
  border-radius: {CONTROL_RADIUS}px; padding: 8px;
}}
QPushButton:hover {{ background-color: {BUTTON_HOVER_BG}; color: {TEXT}; }}
QPushButton:pressed {{ background-color: {BUTTON_PRESSED_BG}; color: {TEXT}; }}
QPushButton:disabled {{ background-color: {BUTTON_DISABLED_BG}; color: {TEXT_DISABLED}; }}
QPushButton:focus {{ border: 2px solid {FOCUS_RING}; outline: none; }}
QDialog {{
  background-color: {WINDOW_BG}; color: {TEXT};
  font-family: "{FONT_FAMILY}";
}}
QDialog QPushButton {{ min-height: {DIALOG_BUTTON_H}px; font-size: {FONT_BUTTON + 4}px; }}
QLineEdit {{
  background-color: {INPUT_BG}; color: {TEXT};
  border: 1px solid {BUTTON_BORDER}; border-radius: {CONTROL_RADIUS}px;
  padding: 6px 10px; font-size: {FONT_BUTTON}px;
}}
QLineEdit:focus {{ border: 2px solid {FOCUS_RING}; }}
QLineEdit:disabled {{ background-color: {BUTTON_DISABLED_BG}; color: {TEXT_DISABLED}; }}
""".strip()


BUTTON_STYLESHEET = build_stylesheet()


def dialog_stylesheet() -> str:
    """Shared dialog chrome (same theme, large buttons)."""
    return (
        f"QDialog {{ background-color: {WINDOW_BG}; color: {TEXT}; "
        f"font-family: \"{FONT_FAMILY}\"; }}"
        f"QDialog QLabel {{ color: {TEXT}; font-size: {FONT_STATUS}px; }}"
        f"QDialog QPushButton {{ min-width: 220px; min-height: {DIALOG_BUTTON_H}px; "
        f"font-size: {FONT_BUTTON + 4}px; color: {TEXT}; background-color: {BUTTON_BG}; "
        f"border: 1px solid {BUTTON_BORDER}; border-radius: {CONTROL_RADIUS}px; }}"
        f"QDialog QPushButton:hover {{ background-color: {BUTTON_HOVER_BG}; }}"
        f"QDialog QPushButton:pressed {{ background-color: {BUTTON_PRESSED_BG}; }}"
        f"QDialog QPushButton:focus {{ border: 2px solid {FOCUS_RING}; }}"
    )
