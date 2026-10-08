"""Edgeless board surface — background grid, no page edge, token fonts, handles."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.text_fit import font_for
from smartboard.ui import theme
from smartboard.ui.board_view import BoardView

STATE = {
    "elements": [
        {
            "id": "heading_001",
            "type": "heading",
            "x": 160,
            "y": 80,
            "width": 800,
            "height": 96,
            "text": "Hi",
            "z": 1,
        },
    ],
    "selected_element_id": "heading_001",
}


def _grab(view: BoardView):  # → QImage
    view.show()
    view.repaint()
    return view.grab().toImage()


def _pixel_hex(image, sx: float, sy: float) -> str:
    return image.pixelColor(int(sx), int(sy)).name().upper()


def test_background_grid_without_page_edge(qapp: object) -> None:
    view = BoardView()
    view.resize(800, 1000)
    view.render_state({"elements": [], "selected_element_id": None})
    image = _grab(view)
    # Dot lattice at zoom 1.0 uses 64-unit spacing: on-dot differs from bg.
    assert _pixel_hex(image, 64, 64) == theme.GRID_DOT.upper()
    assert _pixel_hex(image, 32, 32) == theme.WINDOW_BG.upper()
    # No page edge anywhere: sample a sweep for the old border color.
    for sx in range(0, 800, 40):
        for sy in range(0, 1000, 40):
            assert _pixel_hex(image, sx, sy) != theme.BOARD_BORDER.upper()


def test_token_fonts_meet_minima() -> None:
    assert font_for("heading").pointSize() >= 64
    assert font_for("text").pointSize() >= 36


def test_selection_handles_on_selected_only(qapp: object) -> None:
    view = BoardView()
    view.resize(1920, 1080)  # zoom 1.0 → filled handle squares sample exactly
    view.render_state(STATE)
    image = _grab(view)
    el = STATE["elements"][0]
    # Points strictly inside each 14-unit handle square, off the outline.
    corners = [
        (el["x"] - 4, el["y"] - 4),
        (el["x"] + el["width"] + 4, el["y"] - 4),
        (el["x"] - 4, el["y"] + el["height"] + 4),
        (el["x"] + el["width"] + 4, el["y"] + el["height"] + 4),
    ]
    for cx, cy in corners:
        assert _pixel_hex(image, cx, cy) == theme.SELECTION, (cx, cy)
    # Deselect → no selection pixels near the element corner.
    view.render_state({**STATE, "selected_element_id": None})
    image = _grab(view)
    assert _pixel_hex(image, el["x"] - 4, el["y"] - 4) != theme.SELECTION
