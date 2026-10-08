"""Infinite world model — no canvas state, unbounded coordinates, numeric guards."""

from __future__ import annotations

from smartboard.core.board import (
    MAX_WORLD_COORD,
    MAX_WORLD_SIZE,
    MIN_SIZE,
    Board,
    Element,
)
from smartboard.core.engine import CommandEngine
from smartboard.core.validators import within_world_limits

TS = "2026-10-03T18:15:00Z"


def test_new_board_has_no_canvas_state() -> None:
    board = Board()
    assert not hasattr(board, "canvas_width")
    assert not hasattr(board, "canvas_height")
    assert (MAX_WORLD_COORD, MAX_WORLD_SIZE, MIN_SIZE) == (1_000_000.0, 1_000_000.0, 24)
    assert "canvas" not in board.to_dict()


def test_legacy_canvas_ignored_without_moving_elements() -> None:
    element = {
        "id": "text_001",
        "type": "text",
        "x": 160,
        "y": 200,
        "width": 600,
        "height": 120,
        "color": "#FFFFFF",
        "z": 1,
    }
    board = Board.from_dict(
        {
            "lesson_id": "lesson_001",
            "elements": [element],
            "canvas": {"width": 1920, "height": 1080, "unit": "px"},
            "selected_element_id": None,
            "version": 1,
        }
    )
    restored = board.find("text_001")
    assert restored is not None
    assert (restored.x, restored.y, restored.width, restored.height) == (160, 200, 600, 120)


def test_world_geometry_has_no_page_edge() -> None:
    assert within_world_limits(-5000, -3000, 100, 100) is True
    assert within_world_limits(100000, 200000, 90000, 80000) is True
    assert within_world_limits(2_000_000, 0, 100, 100) is False
    element = Element(id="text_001", type="text", x=-5000, y=-3000, width=100, height=100)
    assert element.within_world_limits() is True


def test_direct_engine_fallback_uses_world_origin() -> None:
    eng = CommandEngine()
    heading = eng.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Hi"},
            "timestamp": TS,
        }
    )
    assert heading["ok"]
    element = eng.board.find(heading["affected_id"])
    assert element is not None
    assert (element.x, element.y) == (0, 0)
    assert (element.width, element.height) == (800, 96)
    assert element.within_world_limits() is True
