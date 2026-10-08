"""US1 infinite-rendering widget tests (fail-first)."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.board_paint import visible_elements
from smartboard.ui.board_view import BoardView, grid_spacing_for_zoom


def _view(qapp: object) -> BoardView:
    view = BoardView()
    view.resize(960, 540)
    view.show()
    return view


def test_visible_elements_culls_offscreen_content() -> None:
    elements = [
        {"id": "a", "type": "text", "x": 0, "y": 0, "width": 100, "height": 50, "z": 1},
        {"id": "b", "type": "text", "x": 5000, "y": 5000, "width": 100, "height": 50, "z": 2},
    ]
    visible = visible_elements(elements, (0.0, 0.0, 960.0, 540.0))
    assert [el["id"] for el in visible] == ["a"]


def test_grid_spacing_stays_in_screen_band() -> None:
    for zoom in (0.10, 0.25, 0.5, 1.0, 2.0, 4.0):
        screen = grid_spacing_for_zoom(zoom) * zoom
        assert 48.0 <= screen <= 96.0


def test_screen_rect_scales_geometry_with_zoom(qapp: object) -> None:
    view = _view(qapp)
    element = {"id": "text_001", "type": "text", "x": 100, "y": 100, "width": 200, "height": 100}
    view.render_state({"elements": [element], "selected_element_id": "text_001"})
    view.zoom_about(0.0, 0.0, 2.0)
    _x, _y, w, h = view._screen_rect(element)
    assert (w, h) == (400.0, 200.0)
    view.close()


def test_hit_tolerance_scales_with_zoom(qapp: object) -> None:
    view = _view(qapp)
    assert view._hit_tolerance_world() == pytest.approx(6.0)
    view.zoom_about(0.0, 0.0, 4.0)
    assert view._hit_tolerance_world() == pytest.approx(1.5)
    view.close()


def test_handles_use_constant_screen_size(qapp: object) -> None:
    from smartboard.ui import theme

    view = _view(qapp)
    assert theme.HANDLE_SIZE == 14
    view.close()
