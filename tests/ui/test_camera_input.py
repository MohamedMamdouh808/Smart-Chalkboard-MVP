"""US1 camera-input widget tests (fail-first)."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.board_view import BoardView


def _view(qapp: object) -> BoardView:
    view = BoardView()
    view.resize(960, 540)
    view.show()
    return view


def _wheel(view: BoardView, dx: int, dy: int, modifiers: object) -> None:
    from PyQt6.QtCore import QPoint, QPointF, Qt
    from PyQt6.QtGui import QWheelEvent

    event = QWheelEvent(
        QPointF(480.0, 270.0),
        QPointF(480.0, 270.0),
        QPoint(0, 0),
        QPoint(dx, dy),
        Qt.MouseButton.NoButton,
        modifiers,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    view.wheelEvent(event)


def test_wheel_pans_camera_without_history(qapp: object) -> None:
    view = _view(qapp)
    emitted: list = []
    view.CameraChanged.connect(emitted.append)
    before = view.camera_state()
    _wheel(view, 0, 120, __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.KeyboardModifier.NoModifier)
    after = view.camera_state()
    assert after.pan_y > before.pan_y
    assert after.zoom == before.zoom
    assert len(emitted) == 1
    view.close()


def test_shift_wheel_pans_horizontally(qapp: object) -> None:
    from PyQt6.QtCore import Qt

    view = _view(qapp)
    before = view.camera_state()
    _wheel(view, 0, 120, Qt.KeyboardModifier.ShiftModifier)
    after = view.camera_state()
    assert after.pan_x > before.pan_x
    assert after.pan_y == before.pan_y
    view.close()


def test_ctrl_wheel_zooms_about_cursor(qapp: object) -> None:
    from PyQt6.QtCore import Qt

    view = _view(qapp)
    before = view.camera_state()
    anchor = view.transform().to_world(480.0, 270.0)
    _wheel(view, 0, 120, Qt.KeyboardModifier.ControlModifier)
    after = view.camera_state()
    assert after.zoom > before.zoom
    assert view.transform().to_world(480.0, 270.0) == anchor
    view.close()


def test_space_drag_pans_in_select_and_pen_modes(qapp: object) -> None:
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest

    for mode in ("select", "pen"):
        view = _view(qapp)
        view.set_mode(mode)
        before = view.camera_state()
        QTest.keyPress(view, Qt.Key.Key_Space)
        QTest.mousePress(
            view,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(480, 270),
        )
        QTest.mouseMove(view, __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(380, 270))
        QTest.mouseRelease(
            view,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            __import__("PyQt6.QtCore", fromlist=["QPoint"]).QPoint(380, 270),
        )
        QTest.keyRelease(view, Qt.Key.Key_Space)
        after = view.camera_state()
        assert after.pan_x > before.pan_x
        assert view.mode == mode  # navigation never changes the active mode
        view.close()


def test_middle_button_drag_pans(qapp: object) -> None:
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    view = _view(qapp)
    before = view.camera_state()
    QTest.mousePress(
        view, Qt.MouseButton.MiddleButton, Qt.KeyboardModifier.NoModifier, QPoint(480, 270)
    )
    QTest.mouseMove(view, QPoint(480, 170))
    QTest.mouseRelease(
        view, Qt.MouseButton.MiddleButton, Qt.KeyboardModifier.NoModifier, QPoint(480, 170)
    )
    after = view.camera_state()
    assert after.pan_y > before.pan_y
    view.close()


def test_select_empty_drag_pans_but_click_only_deselects(qapp: object) -> None:
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    view = _view(qapp)
    view.set_mode("select")
    before = view.camera_state()
    QTest.mouseClick(
        view, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(100, 100)
    )
    assert view.camera_state().pan_x == before.pan_x
    QTest.mousePress(
        view, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(100, 100)
    )
    QTest.mouseMove(view, QPoint(200, 100))
    QTest.mouseRelease(
        view, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(200, 100)
    )
    assert view.camera_state().pan_x < before.pan_x
    view.close()


def test_pinch_normalization_zooms_about_center(qapp: object) -> None:
    view = _view(qapp)
    anchor = view.transform().to_world(300.0, 200.0)
    view.handle_pinch(300.0, 200.0, 2.0)
    assert view.camera_state().zoom == 2.0
    assert view.transform().to_world(300.0, 200.0) == anchor
    view.close()
