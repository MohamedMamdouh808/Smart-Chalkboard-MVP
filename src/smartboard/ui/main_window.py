"""Main window shell: fullscreen board + mic + status + transcription.

Emits intents through injected callbacks; never mutates board state itself.
"""

from __future__ import annotations

from typing import Any, Callable

from .board_view import BACKGROUND
from .status import STATUS_STATES
from .theme import FONT_HEARD_LABEL, FONT_TRANSCRIPT, TEXT_MUTED

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QKeySequence, QShortcut
    from PyQt6.QtWidgets import (
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False

MIN_WINDOW_W = 960
MIN_WINDOW_H = 540
MIN_TARGET_PX = 48


class MainWindow(QMainWindow if _QT else object):  # type: ignore[valid-type,misc]
    """Fullscreen shell: board view + mic button + status + transcription."""

    MIC_MIN_SIZE = 96

    def __init__(
        self,
        on_mic: Callable[[], None] | None = None,
        on_undo: Callable[[], None] | None = None,
        on_redo: Callable[[], None] | None = None,
        on_close: Callable[[], None] | None = None,
        on_dev_text: Callable[[str], None] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if not _QT:  # pragma: no cover
            raise RuntimeError("PyQt6 is required for the main window.")
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Smart Chalkboard")
        self.setMinimumSize(MIN_WINDOW_W, MIN_WINDOW_H)
        self._status = "Idle"
        self._transcription = ""
        self._open_dialogs: list[Any] = []
        self._on_close = on_close

        self._f11 = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        self._f11.activated.connect(self.toggle_mode)

        from .board_view import BoardView
        from .icons import load_icon
        from .mic_button import MicButton
        from .result_chip import PLACEHOLDER, ResultChip
        from .status_pill import StatusPill
        from .theme import (
            BUTTON_STYLESHEET,
            BAR_PAD_V,
            BOARD_MARGIN,
            CHIP_H,
            COMPACT_CONTROL_H,
            FOCUS_RING,
            FONT_BUTTON,
            FONT_FAMILY,
            FONT_STRIP,
            STRIP_BG,
            STRIP_H,
            TEXT,
        )
        from PyQt6.QtGui import QFont as _QFont

        root = QWidget()
        root.setObjectName("root")
        root.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(BOARD_MARGIN, BOARD_MARGIN, BOARD_MARGIN, BOARD_MARGIN)
        layout.setSpacing(BOARD_MARGIN)

        self.strip = QWidget()
        strip_layout = QHBoxLayout(self.strip)
        strip_layout.setContentsMargins(BOARD_MARGIN, BAR_PAD_V, BOARD_MARGIN, BAR_PAD_V)
        self.heard_label = QLabel("Heard:")
        self.heard_label.setFont(_QFont("Segoe UI", FONT_STRIP))
        self.heard_label.setStyleSheet(
            f"color: {TEXT_MUTED};")
        self.transcription_label = QLabel(PLACEHOLDER)
        self.transcription_label.setFont(_QFont("Segoe UI", FONT_STRIP))
        self.transcription_label.setStyleSheet(f"padding: 4px 8px; color: {TEXT};")
        self.result_chip = ResultChip()
        self.result_chip.setFixedHeight(CHIP_H)
        self.mode_button = QPushButton()
        self.mode_button.setIcon(load_icon("window"))
        self.mode_button.setText("")
        self.mode_button.setToolTip("Window")
        self.mode_button.setAccessibleName("Window")
        self.mode_button.setFixedSize(COMPACT_CONTROL_H, CHIP_H)
        self.mode_button.setStyleSheet(BUTTON_STYLESHEET)
        self.mode_button.clicked.connect(self.toggle_mode)
        strip_layout.addWidget(self.heard_label)
        strip_layout.addWidget(self.transcription_label, stretch=1)
        strip_layout.addWidget(self.result_chip)
        strip_layout.addWidget(self.mode_button)
        self.strip.setObjectName("strip")
        self.strip.setMinimumHeight(STRIP_H)
        self.strip.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.strip.setStyleSheet(f"QWidget#strip {{ background: {STRIP_BG}; }}")
        layout.addWidget(self.strip)

        self.board_view = BoardView()
        layout.addWidget(self.board_view, stretch=1)

        self.control_bar = QWidget()
        bar = QHBoxLayout(self.control_bar)
        bar.setContentsMargins(0, 0, 0, 0)
        self.control_bar.setMinimumHeight(MIN_TARGET_PX)
        self.mic_button = MicButton()
        self.mic_button.setToolTip("Speak a command (scripted demo) — click for the next utterance")
        if on_mic is not None:
            self.mic_button.clicked.connect(on_mic)
        bar.addWidget(self.mic_button)

        self.undo_button = QPushButton("Undo")
        self.undo_button.setIcon(load_icon("undo"))
        self.redo_button = QPushButton("Redo")
        self.redo_button.setIcon(load_icon("redo"))
        for btn in (self.undo_button, self.redo_button):
            btn.setMinimumHeight(COMPACT_CONTROL_H)
            btn.setStyleSheet(BUTTON_STYLESHEET)
        if on_undo is not None:
            self.undo_button.clicked.connect(on_undo)
        if on_redo is not None:
            self.redo_button.clicked.connect(on_redo)
        bar.addWidget(self.undo_button)
        bar.addWidget(self.redo_button)

        self.pen_button = QPushButton("Select")
        self.pen_button.setCheckable(True)
        self.pen_button.setChecked(False)
        self.pen_button.setToolTip("Toggle Pen / Select mode (P / S)")
        self.pen_button.setMinimumHeight(COMPACT_CONTROL_H)
        self.pen_button.setStyleSheet(BUTTON_STYLESHEET)
        self.pen_button.clicked.connect(self._flip_pen_mode)
        self.pen_mode_changed: Callable[[str], None] | None = None
        self._shortcut_p = QShortcut(QKeySequence(Qt.Key.Key_P), self)
        self._shortcut_p.activated.connect(lambda: self.set_pen_mode("pen"))
        self._shortcut_s = QShortcut(QKeySequence(Qt.Key.Key_S), self)
        self._shortcut_s.activated.connect(lambda: self.set_pen_mode("select"))
        bar.addWidget(self.pen_button)

        import os as _os

        from PyQt6.QtWidgets import QLineEdit as _QLineEdit

        self.dev_input = _QLineEdit()
        self.dev_input.setPlaceholderText("Dev transcript — type a command and press Enter")
        dev_shown = _os.environ.get("SMARTBOARD_DEV_INPUT") == "1"
        self.dev_input.setVisible(dev_shown)
        self.dev_input.setFixedHeight(COMPACT_CONTROL_H)
        self.dev_input.setFont(_QFont("Segoe UI", FONT_BUTTON))
        from PyQt6.QtGui import QColor as _QColor
        from PyQt6.QtGui import QPalette as _QPalette

        palette = self.dev_input.palette()
        palette.setColor(_QPalette.ColorRole.PlaceholderText, _QColor(TEXT_MUTED))
        self.dev_input.setPalette(palette)
        if on_dev_text is not None:
            self.dev_input.returnPressed.connect(
                lambda: (on_dev_text(self.dev_input.text()), self.dev_input.clear()))
        bar.addWidget(self.dev_input, stretch=1)
        if not dev_shown:
            # Flag off: the hidden input takes no space, so a spacer keeps
            # the pill right-anchored and the bar identical to before.
            bar.addStretch(1)

        self.status_pill = StatusPill()
        bar.addWidget(self.status_pill)
        layout.addWidget(self.control_bar)
        root.setStyleSheet(f"QWidget#root {{ background: {BACKGROUND}; }}")

    @property
    def pen_mode(self) -> str:
        return self.board_view.mode

    def set_pen_mode(self, mode: str) -> None:
        """Switch Pen/Select mode (Select default); notifies the app layer."""
        self.board_view.set_mode(mode)
        self.pen_button.setChecked(mode == "pen")
        self.pen_button.setText("Pen" if mode == "pen" else "Select")
        if self.pen_mode_changed is not None:
            self.pen_mode_changed(mode)

    def _flip_pen_mode(self) -> None:
        self.set_pen_mode("select" if self.pen_mode == "pen" else "pen")

    @property
    def status(self) -> str:
        return self._status

    def set_status(self, status: str) -> None:
        assert status in STATUS_STATES, f"unknown status {status}"
        self._status = status
        self.status_pill.set_state(status)
        self.mic_button.set_voice_state(status.lower())

    @property
    def transcription(self) -> str:
        return self._transcription

    def show_transcription(self, text: str) -> None:
        from .result_chip import PLACEHOLDER as _PLACEHOLDER

        self._transcription = text
        self._apply_elision()

    def _apply_elision(self) -> None:
        from .result_chip import PLACEHOLDER as _PLACEHOLDER

        from PyQt6.QtGui import QFontMetrics as _QFontMetrics

        full = self._transcription if self._transcription else _PLACEHOLDER
        self.transcription_label.setToolTip(self._transcription)
        available = self.transcription_label.contentsRect().width()
        if available <= 0:
            self.transcription_label.setText(full)
            return
        metrics = _QFontMetrics(self.transcription_label.font())
        if metrics.horizontalAdvance(full) <= available:
            self.transcription_label.setText(full)
            return
        words = full.split(" ")
        shown = ""
        for word in words:
            candidate = (shown + " " + word).strip()
            if metrics.horizontalAdvance(candidate + "...") > available:
                break
            shown = candidate
        self.transcription_label.setText((shown if shown else full[:1]) + "...")

    def show_result(self, result: dict[str, Any]) -> None:
        from .result_chip import outcome_for_result as _outcome_for

        self.result_chip.set_outcome(_outcome_for(result))

    def render_board(self, state: dict[str, Any], highlight_id: str | None = None) -> None:
        self.board_view.render_state(state, highlight_id)

    # -- window mode ------------------------------------------------------
    def toggle_mode(self) -> None:
        """Fullscreen ↔ normal window at any time; content untouched."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_restored(self, mode: str) -> None:
        """Show per persisted preference (before first paint)."""
        if mode == "fullscreen":
            self.showFullScreen()
        elif mode == "maximized":
            self.showMaximized()
        else:
            self.showNormal()

    # -- dialogs ------------------------------------------------------------
    def register_dialog(self, dialog: Any) -> None:
        self._open_dialogs.append(dialog)

    def unregister_dialog(self, dialog: Any) -> None:
        if dialog in self._open_dialogs:
            self._open_dialogs.remove(dialog)

    def recenter_dialog(self, dialog: Any) -> None:
        center = self.geometry().center()
        geo = dialog.geometry()
        geo.moveCenter(center)
        dialog.setGeometry(geo)

    def moveEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        super().moveEvent(event)
        for dialog in list(self._open_dialogs):
            self.recenter_dialog(dialog)

    def resizeEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        super().resizeEvent(event)
        self._apply_elision()
        for dialog in list(self._open_dialogs):
            self.recenter_dialog(dialog)

    def showEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        super().showEvent(event)
        self._apply_elision()

    def closeEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        if self._on_close is not None:
            self._on_close()
        super().closeEvent(event)

    def keyPressEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)
