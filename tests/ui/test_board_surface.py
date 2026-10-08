"""T007: board surface — distinct surface, border, token fonts, handles."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.text_fit import font_for  # noqa: E402
from smartboard.ui import theme  # noqa: E402
from smartboard.ui.board_view import BoardView  # noqa: E402
from smartboard.ui.viewport import Viewport  # noqa: E402

STATE = {
    "canvas": {"width": 1920, "height": 1080},
    "elements": [
        {"id": "heading_001", "type": "heading", "x": 160, "y": 80, "width": 800, "height": 96,
         "text": "Hi", "z": 1},
    ],
    "selected_element_id": "heading_001",
}


def _grab(view: BoardView):  # → QImage
    view.show()
    view.repaint()
    return view.grab().toImage()


def _pixel_hex(image, sx: float, sy: float) -> str:
    return image.pixelColor(int(sx), int(sy)).name().upper()


def test_surface_centered_and_distinct(qapp: object) -> None:
    view = BoardView()
    view.resize(800, 1000)
    view.render_state({"canvas": STATE["canvas"], "elements": [], "selected_element_id": None})
    image = _grab(view)
    vp = Viewport.from_sizes(view.width(), view.height())
    # Margin outside the canvas shows the darker window background.
    assert _pixel_hex(image, 400, 10) == theme.WINDOW_BG.upper()
    # Canvas interior shows the lighter surface.
    sx, sy = vp.to_screen(960, 540)
    assert _pixel_hex(image, sx, sy) == theme.BOARD_SURFACE.upper()


def test_border_drawn_around_surface(qapp: object) -> None:
    view = BoardView()
    view.resize(1920, 1080)
    view.render_state({"canvas": STATE["canvas"], "elements": [], "selected_element_id": None})
    rect = view.surface_rect()
    assert rect.width() == pytest.approx(1920) and rect.height() == pytest.approx(1080)
    image = _grab(view)
    # Top-edge midpoint at scale 1.0 lands exactly on the border stroke.
    assert _pixel_hex(image, 960, 0) == theme.BOARD_BORDER.upper()


def test_token_fonts_meet_minima() -> None:
    assert font_for("heading").pointSize() >= 64
    assert font_for("text").pointSize() >= 36


def test_selection_handles_on_selected_only(qapp: object) -> None:
    view = BoardView()
    view.resize(1920, 1080)  # scale 1.0 → filled handle squares sample exactly
    view.render_state(STATE)
    image = _grab(view)
    el = STATE["elements"][0]
    # Points strictly inside each 14-unit handle square, off the outline.
    corners = [(el["x"] - 4, el["y"] - 4),
               (el["x"] + el["width"] + 4, el["y"] - 4),
               (el["x"] - 4, el["y"] + el["height"] + 4),
               (el["x"] + el["width"] + 4, el["y"] + el["height"] + 4)]
    for cx, cy in corners:
        assert _pixel_hex(image, cx, cy) == theme.SELECTION, (cx, cy)
    # Deselect → no selection pixels anywhere near the element.
    view.render_state({**STATE, "selected_element_id": None})
    image = _grab(view)
    assert _pixel_hex(image, el["x"] + 7, el["y"] + 7) != theme.SELECTION
