"""T006: mode switching — F11/button toggles keep content and selection identical."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.orchestrator import build_app
from smartboard.ui.main_window import MainWindow

TS = "2026-10-03T18:15:00Z"


@pytest.fixture()
def window(qapp: object) -> MainWindow:
    app = build_app()
    app.engine.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Newton's Second Law"},
            "timestamp": TS,
        }
    )
    win = MainWindow()
    win.render_board(app.engine.board.to_dict())
    win.resize(1280, 720)
    win.show()
    return win


def test_four_toggles_leave_state_identical(window: MainWindow, qapp: object) -> None:
    before = window.board_view._state
    assert before["elements"], "needs content on the board"
    for _ in range(4):
        window.toggle_mode()
    after = window.board_view._state
    assert after == before


def test_f11_shortcut_toggles(window: MainWindow, qapp: object) -> None:
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest

    was_fullscreen = window.isFullScreen()
    QTest.keyClick(window, Qt.Key.Key_F11)
    assert window.isFullScreen() != was_fullscreen
    QTest.keyClick(window, Qt.Key.Key_F11)
    assert window.isFullScreen() == was_fullscreen


def test_toggle_button_exists_and_is_visible(window: MainWindow, qapp: object) -> None:
    assert window.mode_button is not None
    assert window.mode_button.isVisible()
    assert 32 <= window.mode_button.height() <= 36  # 007 compact toggle
    assert window.mode_button.toolTip() == "Window"
    assert window.mode_button.accessibleName() == "Window"
