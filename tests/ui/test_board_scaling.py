"""T009: viewport-driven paint — letterbox, aspect, repaint budget."""

from __future__ import annotations

import time

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.board_view import BoardView  # noqa: E402
from smartboard.ui.viewport import Viewport  # noqa: E402

STATE = {
    "canvas": {"width": 1920, "height": 1080},
    "elements": [
        {"id": "heading_001", "type": "heading", "x": 160, "y": 80, "width": 800, "height": 96,
         "text": "Newton's Second Law", "z": 1},
    ],
    "selected_element_id": None,
}


def test_paint_uses_shared_viewport(qapp: object) -> None:
    view = BoardView()
    view.resize(960, 540)
    view.render_state(STATE)
    vp = Viewport.from_sizes(view.width(), view.height())
    assert view.viewport().scale == pytest.approx(vp.scale)
    assert view.viewport().ox == pytest.approx(vp.ox, abs=1e-6)


def test_letterbox_margins_share_background(qapp: object) -> None:
    view = BoardView()
    view.resize(800, 1000)  # portrait: side margins expected
    view.render_state(STATE)
    vp = view.viewport()
    assert vp.oy > 0  # top/bottom letterbox on a portrait view of a 16:9 canvas
    from smartboard.ui import theme as _theme

    assert view.letterbox_color().lower() == _theme.WINDOW_BG


def test_repaint_within_frame_for_200_elements(qapp: object) -> None:
    big = dict(STATE, elements=[
        {"id": f"text_{i:03d}", "type": "text", "x": 10, "y": 10, "width": 100, "height": 30,
         "text": f"t{i}", "z": i} for i in range(200)])
    view = BoardView()
    view.resize(1280, 720)
    view.render_state(big)
    start = time.perf_counter()
    view.repaint()
    elapsed = (time.perf_counter() - start) * 1000
    assert elapsed < 100
