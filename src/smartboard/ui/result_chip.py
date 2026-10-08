"""Result chip: transcript outcome as (color, icon, text) — never color alone."""

from __future__ import annotations

from typing import Any

from . import theme
from .icons import load_icon

OUTCOMES: tuple[str, ...] = ("done", "needs_confirmation", "needs_clarification", "error")
LABELS: dict[str, str] = {
    "done": "Done",
    "needs_confirmation": "Needs confirmation",
    "needs_clarification": "Needs clarification",
    "error": "Error",
}
PLACEHOLDER = "Hold the mic and speak a command"


def outcome_for_result(result: dict[str, Any]) -> str:
    if result.get("ok"):
        return "done"
    if result.get("needs_confirmation"):
        return "needs_confirmation"
    if result.get("needs_clarification"):
        return "needs_clarification"
    return "error"


try:
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False


class ResultChip(QWidget if _QT else object):  # type: ignore[misc]
    """Top-bar right chip rendering the outcome triple."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not _QT:  # pragma: no cover
            raise RuntimeError("PyQt6 is required for the result chip.")
        super().__init__(*args, **kwargs)
        from PyQt6.QtCore import Qt as _Qt

        self.setAttribute(_Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 2, 16, 2)
        self._icon = QLabel()
        self._label = QLabel("—")
        self._label.setStyleSheet(
            f"font-size: {theme.FONT_STATUS}px; color: {theme.TEXT}; background: transparent;"
        )
        layout.addWidget(self._icon)
        layout.addWidget(self._label)
        self.setStyleSheet(
            f"ResultChip {{ background-color: {theme.BUTTON_BG_ALT}; border-radius: 16px; }}"
        )
        self._outcome = "done"
        self.set_outcome("done")

    def set_outcome(self, outcome: str) -> None:
        if outcome not in OUTCOMES:
            raise ValueError(f"unknown outcome: {outcome}")
        self._outcome = outcome
        self._label.setText(LABELS[outcome])
        icon = load_icon(theme.OUTCOME_ICONS[outcome], theme.OUTCOME_COLORS[outcome])
        self._icon.setPixmap(icon.pixmap(20, 20))

    def text(self) -> str:
        return self._label.text()

    def color(self) -> str:
        return theme.OUTCOME_COLORS[self._outcome]

    def icon_name(self) -> str:
        return theme.OUTCOME_ICONS[self._outcome]
