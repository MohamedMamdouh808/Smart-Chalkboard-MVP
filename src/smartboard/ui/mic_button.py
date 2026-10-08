"""Circular stateful microphone button with listening pulse."""

from __future__ import annotations

from typing import Any

from . import theme
from .icons import load_icon

VOICE_STATES: tuple[str, ...] = ("idle", "listening", "processing", "validating", "executing")

try:
    from PyQt6.QtCore import (  # type: ignore[attr-defined]
        QPropertyAnimation,
        Qt,
        pyqtProperty,
        pyqtSignal,
    )
    from PyQt6.QtGui import QColor, QPainter, QPen
    from PyQt6.QtWidgets import QPushButton

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False


class MicButton(QPushButton if _QT else object):  # type: ignore[misc]
    """112px circular primary control. Appearance follows `voiceState`."""

    if _QT:
        recordingStarted = pyqtSignal()
        recordingStopped = pyqtSignal()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not _QT:  # pragma: no cover
            raise RuntimeError("PyQt6 is required for the mic button.")
        super().__init__(*args, **kwargs)
        self.setFixedSize(theme.MIC_DIAMETER, theme.MIC_DIAMETER)
        self.setText("")
        self.setToolTip("Hold to talk (F11 toggles fullscreen)")
        self._voice_state = "idle"
        self._pulse = 0.0
        self.pulse_anim = QPropertyAnimation(self, b"pulse")
        self.pulse_anim.setDuration(1000)  # ~1 Hz pulse
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.setStartValue(0.0)
        self.pulse_anim.setEndValue(1.0)
        self._icon = load_icon("mic", theme.TEXT)

    if _QT:

        @pyqtProperty(str)
        def voiceState(self) -> str:
            return self._voice_state

        @voiceState.setter  # type: ignore[no-redef]
        def voiceState(self, value: str) -> None:
            self.set_voice_state(value)

        @pyqtProperty(float)
        def pulse(self) -> float:
            return self._pulse

        @pulse.setter  # type: ignore[no-redef]
        def pulse(self, value: float) -> None:
            self._pulse = float(value)
            self.update()

    def set_voice_state(self, state: str) -> None:
        if state not in VOICE_STATES:
            raise ValueError(f"unknown voice state: {state}")
        self._voice_state = state
        if state == "listening":
            if self.pulse_anim.state() != self.pulse_anim.State.Running:
                self.pulse_anim.start()
        else:
            self.pulse_anim.stop()
            self._pulse = 0.0
        self.update()

    def set_loading(self, loading: bool) -> None:
        """Show model readiness without changing the voice-state ring."""
        self.setText("Loading voice model..." if loading else "")
        self.setEnabled(not loading)
        self.update()

    def mousePressEvent(self, event: Any) -> None:
        self.recordingStarted.emit()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: Any) -> None:
        self.recordingStopped.emit()
        super().mouseReleaseEvent(event)

    def ring_color(self) -> str:
        return theme.STATE_COLORS[self._voice_state]

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        side = min(self.width(), self.height())
        radius = side / 2 - 6
        center = (self.width() / 2, self.height() / 2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(theme.BUTTON_BG))
        from PyQt6.QtCore import QPointF

        painter.drawEllipse(QPointF(*center), radius, radius)
        ring = QPen(QColor(self.ring_color()))
        width = 4 + (10 * self._pulse if self._voice_state == "listening" else 0)
        ring.setWidth(int(width))
        painter.setPen(ring)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(*center), radius - width / 2, radius - width / 2)
        icon_side = int(side * 0.44)
        self._icon.paint(
            painter,
            int(center[0] - icon_side / 2),
            int(center[1] - icon_side / 2),
            icon_side,
            icon_side,
        )
        painter.end()
