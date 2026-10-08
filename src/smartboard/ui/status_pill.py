"""Status pill: pipeline state as (color, icon, text) — never color alone."""

from __future__ import annotations

from typing import Any

from . import theme
from .icons import load_icon

STATES: tuple[str, ...] = ("Idle", "Listening", "Processing", "Validating", "Executing")
_KEYS = ("idle", "listening", "processing", "validating", "executing")

try:
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False


class StatusPill(QWidget if _QT else object):  # type: ignore[misc]
    """Small pill rendering the current pipeline state triple."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not _QT:  # pragma: no cover
            raise RuntimeError("PyQt6 is required for the status pill.")
        super().__init__(*args, **kwargs)
        from PyQt6.QtCore import Qt as _Qt

        self.setAttribute(_Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(theme.PILL_H)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 2, 16, 2)
        self._dot = QLabel()
        self._label = QLabel("Idle")
        self._label.setStyleSheet(
            f"font-size: {theme.FONT_STATUS}px; color: {theme.TEXT}; background: transparent;"
        )
        layout.addWidget(self._dot)
        layout.addWidget(self._label)
        self.setStyleSheet(
            f"StatusPill {{ background-color: {theme.BUTTON_BG_ALT}; border-radius: 16px; }}"
        )
        self._key = "idle"
        self.set_state("Idle")

    def set_state(self, state: str) -> None:
        if state not in STATES:
            raise ValueError(f"unknown pipeline state: {state}")
        self._key = _KEYS[STATES.index(state)]
        self._label.setText(state)
        icon = load_icon(theme.STATE_ICONS[self._key], theme.STATE_COLORS[self._key])
        pixmap: QPixmap = icon.pixmap(20, 20)
        self._dot.setPixmap(pixmap)

    def text(self) -> str:
        return self._label.text()

    def color(self) -> str:
        return theme.STATE_COLORS[self._key]

    def icon_name(self) -> str:
        return theme.STATE_ICONS[self._key]
