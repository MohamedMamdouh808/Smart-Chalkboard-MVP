"""Modal confirmation dialog: large Cancel/Confirm, 30 s timeout = cancel."""

from __future__ import annotations

from typing import Any

CONFIRM_TIMEOUT_S = 30

try:
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False


def confirmation_prompt(action: str, label: str = "this item") -> str:
    prompts = {
        "delete_item": f"Delete {label}? [Cancel] [Confirm]",
        "clear_board": "Clear the entire board? [Cancel] [Confirm]",
        "new_lesson": "You have unsaved changes. Save first? [Cancel] [Confirm]",
    }
    return prompts.get(action, f"Confirm this action on {label}? [Cancel] [Confirm]")


def resolve_timeout(confirmed_yet: bool) -> bool:
    """A 30 s timeout without an answer counts as cancel."""
    return confirmed_yet


if _QT:

    class ConfirmDialog(QDialog):
        """Pen-usable modal: big buttons, auto-cancel after 30 s."""

        TIMEOUT_S = CONFIRM_TIMEOUT_S

        def __init__(self, prompt: str, parent: Any = None) -> None:
            super().__init__(parent)
            from PyQt6.QtCore import Qt as _Qt

            from .theme import DIALOG_BUTTON_H, FONT_STATUS, TEXT, dialog_stylesheet

            self.setAttribute(_Qt.WidgetAttribute.WA_StyledBackground, True)

            self.setWindowTitle("Please confirm")
            self.setModal(True)
            layout = QVBoxLayout(self)
            message = QLabel(prompt)
            message.setStyleSheet(
                f"font-size: {FONT_STATUS}px; padding: 24px; color: {TEXT};"
                " background: transparent;"
            )
            layout.addWidget(message)
            row = QHBoxLayout()
            cancel = QPushButton("Cancel")
            confirm = QPushButton("Confirm")
            for btn in (cancel, confirm):
                btn.setMinimumSize(220, DIALOG_BUTTON_H)
            cancel.clicked.connect(self.reject)
            confirm.clicked.connect(self.accept)
            row.addWidget(cancel)
            row.addWidget(confirm)
            layout.addLayout(row)
            self.setStyleSheet(dialog_stylesheet())
            QTimer.singleShot(self.TIMEOUT_S * 1000, self._on_timeout)

        def _on_timeout(self) -> None:
            if self.isVisible():
                self.reject()

else:  # pragma: no cover - headless CI

    class ConfirmDialog:  # type: ignore[no-redef]
        TIMEOUT_S = CONFIRM_TIMEOUT_S

        def __init__(self, prompt: str, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("PyQt6 is required for dialogs.")
