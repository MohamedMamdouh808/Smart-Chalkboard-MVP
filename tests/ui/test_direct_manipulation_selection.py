"""US1 selection presentation: outlines, handles, and empty-space deselection."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.core.engine import CommandEngine
from smartboard.ui import theme
from smartboard.ui.board_view import BoardView

TS = "2026-10-03T18:15:00Z"
SCRIBBLE = [
    {"x": 100.0, "y": 140.0},
    {"x": 160.0, "y": 110.0},
    {"x": 230.0, "y": 150.0},
    {"x": 190.0, "y": 180.0},
    {"x": 260.0, "y": 120.0},
]
STRAIGHT_LINE = [
    {"x": 500.0, "y": 220.0},
    {"x": 820.0, "y": 220.0},
]


def _engine() -> CommandEngine:
    eng = CommandEngine()
    assert eng.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Heading", "position": {"x": 100, "y": 100}},
            "timestamp": TS,
        }
    )["ok"]
    assert eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "Body", "position": {"x": 100, "y": 300}},
            "timestamp": TS,
        }
    )["ok"]
    assert eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {
                "text": "E=mc^2",
                "equation_style": True,
                "position": {"x": 100, "y": 500},
            },
            "timestamp": TS,
        }
    )["ok"]
    assert eng.execute(
        {
            "command": "create_shape",
            "target_id": None,
            "parameters": {"shape_type": "rectangle", "position": {"x": 100, "y": 700}},
            "timestamp": TS,
        }
    )["ok"]
    assert eng.add_drawing([SCRIBBLE, STRAIGHT_LINE], width=8)["ok"]
    return eng


def _grab(view: BoardView):
    view.show()
    view.repaint()
    return view.grab().toImage()


def _pixel_hex(image, sx: float, sy: float) -> str:
    return image.pixelColor(int(sx), int(sy)).name().upper()


def test_outlines_enclose_every_element_type(qapp: object) -> None:
    eng = _engine()
    view = BoardView()
    view.resize(1920, 1080)
    try:
        for element in eng.board.elements:
            assert eng.select(element.id)["ok"]
            view.render_state(eng.board.to_dict())
            image = _grab(view)
            midpoint = element.x + element.width // 2
            assert _pixel_hex(image, midpoint, element.y) == theme.SELECTION.upper()
            assert element.width >= 24 and element.height >= 24
        drawing = eng.board.find("drawing_001")
        assert drawing is not None
        assert (drawing.x, drawing.y, drawing.width, drawing.height) == (96, 106, 728, 118)
    finally:
        view.close()


def test_only_selected_element_has_four_handles(qapp: object) -> None:
    eng = _engine()
    view = BoardView()
    view.resize(1920, 1080)
    try:
        assert eng.select("text_001")["ok"]
        view.render_state(eng.board.to_dict())
        image = _grab(view)
        selected = eng.board.find("text_001")
        assert selected is not None
        corners = [
            (selected.x - 4, selected.y - 4),
            (selected.x + selected.width + 4, selected.y - 4),
            (selected.x - 4, selected.y + selected.height + 4),
            (selected.x + selected.width + 4, selected.y + selected.height + 4),
        ]
        for corner_x, corner_y in corners:
            assert _pixel_hex(image, corner_x, corner_y) == theme.SELECTION.upper()
        unselected = eng.board.find("heading_001")
        assert unselected is not None
        assert _pixel_hex(image, unselected.x - 4, unselected.y - 4) != theme.SELECTION.upper()
    finally:
        view.close()


def test_empty_press_clears_selection_immediately(qapp: object) -> None:
    eng = _engine()
    view = BoardView()
    view.resize(960, 540)
    try:
        assert eng.select("heading_001")["ok"]
        view.render_state(eng.board.to_dict())
        picked: list = []
        view.SelectionChanged.connect(picked.append)
        viewport = view.transform()
        sx, sy = viewport.to_screen(5000.0, 5000.0)
        assert view._press(("mouse",), float(sx), float(sy), None) is True
        view._release(("mouse",), float(sx), float(sy))
        assert picked == [None]
        assert view._state["selected_element_id"] is None
    finally:
        view.close()
