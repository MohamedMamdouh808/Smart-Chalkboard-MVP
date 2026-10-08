"""T017: themed dialogs — shared theme, ≥48px buttons, centered, once-only."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui import theme  # noqa: E402
from smartboard.ui.clarify_dialog import ClarifyDialog  # noqa: E402
from smartboard.ui.confirm_dialog import ConfirmDialog  # noqa: E402
from smartboard.ui.main_window import MainWindow  # noqa: E402


def _buttons(dialog) -> list:
    return dialog.findChildren(QtWidgets.QPushButton)


def test_dialogs_share_theme_stylesheet(qapp: object) -> None:
    for dialog in (ConfirmDialog("Delete this text? [Cancel] [Confirm]"),
                   ClarifyDialog("Which object?")):
        assert theme.WINDOW_BG in dialog.styleSheet()
        assert theme.TEXT in dialog.styleSheet()


def test_dialog_buttons_large(qapp: object) -> None:
    for dialog in (ConfirmDialog("Delete this text? [Cancel] [Confirm]"),
                   ClarifyDialog("Which object?")):
        buttons = _buttons(dialog)
        assert len(buttons) >= 2
        for btn in buttons:
            assert btn.minimumHeight() >= 48
    assert theme.DIALOG_BUTTON_H >= 48


def test_clarify_dialog_has_select_action(qapp: object) -> None:
    dialog = ClarifyDialog("Which object would you like me to delete?")
    assert dialog.question.startswith("Which object")
    assert any(b.text() == "Select" for b in _buttons(dialog))


def test_dialog_centered_over_parent(qapp: object) -> None:
    window = MainWindow()
    window.resize(1280, 720)
    window.show()
    dialog = ConfirmDialog("Delete this text? [Cancel] [Confirm]", window)
    dialog.show()
    window.recenter_dialog(dialog)
    center = window.geometry().center()
    assert abs(dialog.geometry().center().x() - center.x()) < 4
    assert abs(dialog.geometry().center().y() - center.y()) < 4


def test_window_title_exact(qapp: object) -> None:
    window = MainWindow()
    assert window.windowTitle() == "Smart Chalkboard"
