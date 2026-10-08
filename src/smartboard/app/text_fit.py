"""Creation-time text-fit gate (app layer; `core/` untouched).

Text wraps inside the fixed element box. Text that cannot fit the default
box is rejected BEFORE queueing with TOO_LONG_MESSAGE.
"""

from __future__ import annotations

from typing import Any

TOO_LONG_MESSAGE = "Text is too long for this element. Resize it or shorten the text."

# Default boxes mirror the engine's creation defaults (read-only copy).
DEFAULT_BOXES: dict[str, dict[str, int]] = {
    "heading": {"width": 800, "height": 96},
    "text": {"width": 600, "height": 120},
    "equation": {"width": 320, "height": 80},
}


def font_for(kind: str, equation_style: bool = False) -> Any:
    """The exact fonts the board painter uses (single source)."""
    from PyQt6.QtGui import QFont

    if kind == "heading":
        return QFont("Arial", 64, QFont.Weight.Bold)
    return QFont("Arial", 36)


def fits_in_box(text: str, box_w: int, box_h: int, font: Any) -> bool:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFontMetrics

    flags = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) | int(
        Qt.TextFlag.TextWordWrap)
    rect = QFontMetrics(font).boundingRect(0, 0, box_w, box_h, flags, text)
    return rect.width() <= box_w and rect.height() <= box_h


def check_create(kind: str, text: str, equation_style: bool = False) -> tuple[bool, str]:
    """Return (True, '') or (False, TOO_LONG_MESSAGE). Pure check, no mutation."""
    key = "equation" if (kind == "text" and equation_style) else kind
    box = DEFAULT_BOXES.get(key, DEFAULT_BOXES["text"])
    if fits_in_box(text, box["width"], box["height"], font_for(kind, equation_style)):
        return True, ""
    return False, TOO_LONG_MESSAGE
