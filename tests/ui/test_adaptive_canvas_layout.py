"""Edgeless board layout — camera viewport, resize stability, window chrome."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.board_view import BoardView


def test_camera_round_trip_through_widget(qapp: object) -> None:
    from smartboard.app.camera import normalize_camera

    view = BoardView()
    view.resize(960, 540)
    view.set_camera(normalize_camera(100.0, 50.0, 2.0))
    for wx, wy in ((0.0, 0.0), (160.0, 80.0), (-3000.0, 4200.0)):
        sx, sy = view.transform().to_screen(wx, wy)
        rx, ry = view.transform().to_world(sx, sy)
        assert abs(rx - wx) < 1e-6 and abs(ry - wy) < 1e-6


def test_resize_emits_view_size_without_moving_elements(qapp: object) -> None:
    view = BoardView()
    view.resize(960, 540)
    view.show()
    try:
        state = {
            "elements": [
                {
                    "id": "text_001",
                    "type": "text",
                    "x": 80,
                    "y": 80,
                    "width": 400,
                    "height": 96,
                    "z": 1,
                }
            ],
            "selected_element_id": None,
        }
        view.render_state(state)
        emitted: list[tuple[int, int]] = []
        view.ViewSizeChanged.connect(lambda w, h: emitted.append((w, h)))
        view.resize(1280, 720)
        qapp.processEvents()
        assert emitted and emitted[-1] == (1280, 720)
        assert view._state["elements"][0]["x"] == 80
    finally:
        view.close()


def test_main_window_board_fills_minus_margins(qapp: object) -> None:
    from smartboard.ui.main_window import MIN_WINDOW_H, MIN_WINDOW_W, MainWindow
    from smartboard.ui.theme import BOARD_MARGIN

    assert (MIN_WINDOW_W, MIN_WINDOW_H) == (960, 540)
    window = MainWindow()
    try:
        window.resize(975, 600)
        window.show()
        qapp.processEvents()
        assert window.board_view.width() == 975 - 2 * BOARD_MARGIN
    finally:
        window.close()


def test_main_window_has_zoom_controls(qapp: object) -> None:
    from smartboard.ui.main_window import MainWindow

    window = MainWindow()
    try:
        window.set_zoom_label(2.5)
        assert window.zoom_label.text() == "250%"
        for name in ("zoom_in_button", "zoom_out_button", "zoom_reset_button", "zoom_fit_button"):
            assert hasattr(window, name)
    finally:
        window.close()


def test_repeated_resizes_keep_elements_stable(qapp: object) -> None:
    view = BoardView()
    view.resize(960, 540)
    view.show()
    try:
        state = {
            "elements": [
                {
                    "id": "shape_001",
                    "type": "shape",
                    "x": 160,
                    "y": 80,
                    "width": 200,
                    "height": 200,
                    "z": 1,
                    "shape_type": "rectangle",
                }
            ],
            "selected_element_id": None,
        }
        view.render_state(state)
        for size in ((1280, 720), (800, 1000), (1920, 1080), (960, 540)):
            view.resize(*size)
            qapp.processEvents()
        element = view._state["elements"][0]
        assert (element["x"], element["y"], element["width"], element["height"]) == (
            160,
            80,
            200,
            200,
        )
    finally:
        view.close()
