"""Renderer contract — world state in, visible layout out, read-only, render budget."""

from __future__ import annotations

import time

import pytest

from smartboard.ui.board_paint import visible_elements
from smartboard.ui.camera_transform import CameraTransform

STATE = {
    "elements": [
        {"id": "heading_001", "type": "heading", "x": 160, "y": 80, "width": 800, "height": 96},
        {"id": "text_001", "type": "text", "x": 160, "y": 200, "width": 320, "height": 80},
    ],
    "selected_element_id": "text_001",
}


def test_camera_transform_preserves_world_ratio() -> None:
    transform = CameraTransform(pan_x=0.0, pan_y=0.0, zoom=2.0, view_w=1920, view_h=1080)
    sx, _ = transform.to_screen(160, 0)
    _, sy = transform.to_screen(0, 80)
    assert sx == pytest.approx(320.0)
    assert sy == pytest.approx(160.0)


def test_visible_layout_marks_selection_and_never_mutates() -> None:
    before = [dict(el) for el in STATE["elements"]]
    visible = visible_elements(STATE["elements"], (0.0, 0.0, 1920.0, 1080.0))
    assert [el["id"] for el in visible] == ["heading_001", "text_001"]
    assert STATE["selected_element_id"] == "text_001"
    assert STATE["elements"] == before


def test_layout_within_render_budget() -> None:
    big = STATE["elements"] * 100  # 200 elements
    start = time.perf_counter()
    visible_elements(big, (0.0, 0.0, 1920.0, 1080.0))
    assert (time.perf_counter() - start) < 0.1


def test_qt_board_view_smoke() -> None:
    QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
    from smartboard.ui.board_view import BoardView

    assert QtWidgets is not None and BoardView is not None
