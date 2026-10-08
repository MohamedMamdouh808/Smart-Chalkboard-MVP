"""T019: renderer contract — state in, layout out, read-only, render budget."""

from __future__ import annotations

import time

import pytest

from smartboard.ui.board_view import aspect_scale, layout_for_state

STATE = {
    "canvas": {"width": 1920, "height": 1080},
    "elements": [
        {"id": "heading_001", "type": "heading", "x": 160, "y": 80, "width": 800, "height": 96},
        {"id": "text_001", "type": "text", "x": 160, "y": 200, "width": 320, "height": 80},
    ],
    "selected_element_id": "text_001",
}


def test_aspect_scale_preserves_ratio() -> None:
    assert aspect_scale(1920, 1080, 1920, 1080) == pytest.approx(1.0)
    assert aspect_scale(1920, 1080, 960, 540) == pytest.approx(0.5)
    assert aspect_scale(1920, 1080, 1920, 500) == pytest.approx(500 / 1080)


def test_layout_marks_selection_and_never_mutates() -> None:
    before = [dict(el) for el in STATE["elements"]]
    items = layout_for_state(STATE, 1920, 1080)
    assert [i["id"] for i in items] == ["heading_001", "text_001"]
    assert [i["selected"] for i in items] == [False, True]
    assert STATE["elements"] == before


def test_layout_within_render_budget() -> None:
    big = dict(STATE, elements=STATE["elements"] * 100)  # 200 elements
    start = time.perf_counter()
    layout_for_state(big, 1920, 1080)
    assert (time.perf_counter() - start) < 0.1


def test_qt_board_view_smoke() -> None:
    QtWidgets = pytest.importorskip("PyQt6.QtWidgets")
    from smartboard.ui.board_view import BoardView

    assert QtWidgets is not None and BoardView is not None
