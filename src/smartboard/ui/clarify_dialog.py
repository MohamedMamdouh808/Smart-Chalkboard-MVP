"""Clarification dialog (themed) + headless question helper."""

from __future__ import annotations

from typing import Any

try:  # pragma: no cover
    from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

    _QT = True
except ImportError:  # pragma: no cover
    QDialog = object  # type: ignore[assignment,misc]
    _QT = False


def clarification_question(action: str) -> str:
    verb = action.replace("_item", "").replace("_", " ")
    return f"Which object would you like me to {verb}?"


if _QT:

    class ClarifyDialog(QDialog):
        """Themed clarification: question + Cancel/Select (≥48px)."""

        def __init__(self, question: str, parent: Any = None) -> None:
            super().__init__(parent)
            from PyQt6.QtCore import Qt as _Qt
            from .theme import DIALOG_BUTTON_H, FONT_STATUS, TEXT, dialog_stylesheet

            self.setAttribute(_Qt.WidgetAttribute.WA_StyledBackground, True)

            self.setWindowTitle("Which object?")
            self.setModal(True)
            self.question = question
            layout = QVBoxLayout(self)
            message = QLabel(question)
            message.setStyleSheet(
                f"font-size: {FONT_STATUS}px; padding: 24px; color: {TEXT};"
                " background: transparent;")
            layout.addWidget(message)
            row = QHBoxLayout()
            cancel = QPushButton("Cancel")
            select = QPushButton("Select")
            for btn in (cancel, select):
                btn.setMinimumSize(220, DIALOG_BUTTON_H)
            cancel.clicked.connect(self.reject)
            select.clicked.connect(self.accept)
            row.addWidget(cancel)
            row.addWidget(select)
            layout.addLayout(row)
            self.setStyleSheet(dialog_stylesheet())

else:  # pragma: no cover - headless CI

    class ClarifyDialog:  # type: ignore[no-redef]
        def __init__(self, question: str, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("PyQt6 is required for dialogs.")
