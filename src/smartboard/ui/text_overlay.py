"""Inline text overlay: provisional in-place editing anchored to world geometry."""

from __future__ import annotations

from typing import Any

try:
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtWidgets import QLineEdit, QPlainTextEdit, QWidget

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False


class TextOverlay(QWidget if _QT else object):  # type: ignore[misc]
    """Temporary editor for new or existing text. Emits intents; never writes state."""

    if _QT:
        Committed = pyqtSignal(dict)
        Discarded = pyqtSignal(dict)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not _QT:  # pragma: no cover
            raise RuntimeError("PyQt6 is required for the text overlay.")
        super().__init__(*args, **kwargs)
        self._editor: Any | None = None
        self._session: dict[str, Any] | None = None
        self.hide()

    @property
    def session(self) -> dict[str, Any] | None:
        return dict(self._session) if self._session is not None else None

    @property
    def is_open(self) -> bool:
        return self._session is not None

    @property
    def editor_widget(self) -> Any | None:
        return self._editor

    def begin_new(self, world_x: float, world_y: float, screen_rect: Any, font: Any) -> None:
        """Open a provisional editor for double-click-created text."""
        self._open(
            {
                "mode": "new",
                "target_id": None,
                "kind": "text",
                "world_x": float(world_x),
                "world_y": float(world_y),
                "original_text": "",
            },
            "",
            screen_rect,
            font,
            multiline=True,
        )

    def begin_existing(
        self, target_id: str, kind: str, text: str, screen_rect: Any, font: Any
    ) -> None:
        """Open an editor with stored content for heading/text/equation."""
        multiline = kind != "heading"
        self._open(
            {"mode": "existing", "target_id": target_id, "kind": kind, "original_text": text},
            text,
            screen_rect,
            font,
            multiline=multiline,
        )

    def _open(
        self, session: dict[str, Any], text: str, screen_rect: Any, font: Any, multiline: bool
    ) -> None:
        self.close_editor()
        self._session = session
        editor: Any
        if multiline:
            editor = QPlainTextEdit(self.parentWidget())
            editor.setPlainText(text)
            editor.installEventFilter(self)
        else:
            editor = QLineEdit(self.parentWidget())
            editor.setText(text)
            editor.returnPressed.connect(self._commit)
        editor.setFont(font)
        editor.setGeometry(screen_rect)
        editor.show()
        editor.raise_()
        editor.setFocus()
        self._editor = editor

    def follow_camera(self, screen_rect: Any) -> None:
        """Keep the open editor anchored while the camera moves."""
        if self._editor is not None:
            self._editor.setGeometry(screen_rect)

    def eventFilter(self, watched: Any, event: Any) -> bool:
        from PyQt6.QtCore import QEvent as _QEvent

        if watched is self._editor and event.type() == _QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (
                modifiers & Qt.KeyboardModifier.ShiftModifier
            ):
                self._commit()
                return True
            if key == Qt.Key.Key_Escape:
                self._cancel()
                return True
        return bool(super().eventFilter(watched, event))

    def focus_out_commit(self) -> None:
        """Commit on outside click (called by the application focus watcher)."""
        if self._session is not None:
            self._commit()

    def _current_text(self) -> str:
        if isinstance(self._editor, QLineEdit):
            return self._editor.text()
        if isinstance(self._editor, QPlainTextEdit):
            return self._editor.toPlainText()
        return ""

    def _commit(self) -> None:
        session = self._session
        if session is None:
            return
        text = self._current_text()
        if not text.strip():
            self._cancel()
            return
        payload = dict(session)
        payload["text"] = text
        self.close_editor()
        self.Committed.emit(payload)

    def _cancel(self) -> None:
        session = self._session
        if session is None:
            return
        payload = dict(session)
        self.close_editor()
        self.Discarded.emit(payload)

    def close_editor(self) -> None:
        if self._editor is not None:
            self._editor.deleteLater()
            self._editor = None
        self._session = None
        self.hide()
