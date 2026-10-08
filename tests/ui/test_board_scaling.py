"""Camera-driven paint — edgeless board, shared transform, repaint budget."""

from __future__ import annotations

import time

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.board_view import BoardView
from smartboard.ui.camera_transform import CameraTransform

STATE = {
    "elements": [
        {
            "id": "heading_001",
            "type": "heading",
            "x": 160,
            "y": 80,
            "width": 800,
            "height": 96,
            "text": "Newton's Second Law",
            "z": 1,
        },
    ],
    "selected_element_id": None,
}


def test_paint_uses_camera_transform(qapp: object) -> None:
    view = BoardView()
    view.resize(960, 540)
    view.render_state(STATE)
    transform = view.transform()
    assert isinstance(transform, CameraTransform)
    assert transform.to_world(*transform.to_screen(160, 80)) == (160, 80)


def test_no_page_edge_signals_remain(qapp: object) -> None:
    view = BoardView()
    assert not hasattr(view, "CanvasResized")
    assert hasattr(view, "CameraChanged")
    assert hasattr(view, "ViewSizeChanged")


def test_repaint_within_frame_for_200_elements(qapp: object) -> None:
    big = dict(
        STATE,
        elements=[
            {
                "id": f"text_{i:03d}",
                "type": "text",
                "x": 10,
                "y": 10,
                "width": 100,
                "height": 30,
                "text": f"t{i}",
                "z": i,
            }
            for i in range(200)
        ],
    )
    view = BoardView()
    view.resize(1280, 720)
    view.render_state(big)
    start = time.perf_counter()
    view.repaint()
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 100
