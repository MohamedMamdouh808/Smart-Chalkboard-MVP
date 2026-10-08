"""Foundation unbounded-world engine tests (fail-first)."""

from __future__ import annotations

import pytest

from smartboard.core import errors
from smartboard.core.board import Board
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def test_create_move_resize_anywhere_in_world() -> None:
    eng = CommandEngine()
    created = eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "far", "position": {"x": -5000, "y": -3000}},
            "timestamp": TS,
        }
    )
    assert created["ok"]
    target = created["affected_id"]
    moved = eng.execute(
        {
            "command": "move_item",
            "target_id": target,
            "parameters": {"position": {"x": 100000, "y": 200000}},
            "timestamp": TS,
        }
    )
    assert moved["ok"]
    resized = eng.execute(
        {
            "command": "resize_item",
            "target_id": target,
            "parameters": {"size": {"w": 90000, "h": 80000}},
            "timestamp": TS,
        }
    )
    assert resized["ok"]
    element = eng.board.find(target)
    assert element is not None
    assert (element.x, element.y, element.width, element.height) == (100000, 200000, 90000, 80000)


def test_drawing_points_are_not_clipped_to_a_canvas() -> None:
    eng = CommandEngine()
    strokes = [[{"x": -2500.0, "y": -1200.0}, {"x": 2500.0, "y": 1800.0}]]
    result = eng.add_drawing(strokes, color="#FFFFFF", width=4, source="pen")
    assert result["ok"]
    element = eng.board.find(result["affected_id"])
    assert element is not None
    xs = [point["x"] for stroke in element.extra["strokes"] for point in stroke["points"]]
    assert min(xs) < 0.0 and max(xs) > 0.0


def test_new_board_has_no_canvas_and_legacy_canvas_is_ignored() -> None:
    eng = CommandEngine()
    assert "canvas" not in eng.board.to_dict()
    legacy = {
        "lesson_id": "lesson_001",
        "canvas": {"width": 1920, "height": 1080, "unit": "px"},
        "elements": [
            {
                "id": "text_001",
                "type": "text",
                "x": 160,
                "y": 200,
                "width": 600,
                "height": 120,
                "color": "#FFFFFF",
                "z": 1,
            }
        ],
        "selected_element_id": None,
        "version": 2,
    }
    board = Board.from_dict(legacy)
    element = board.find("text_001")
    assert element is not None
    assert (element.x, element.y, element.width, element.height) == (160, 200, 600, 120)
    assert "canvas" not in board.to_dict()


@pytest.mark.parametrize("bad", [float("inf"), float("-inf"), float("nan"), 2_000_000, -2_000_000])
def test_non_finite_or_out_of_range_geometry_rejected(bad: float) -> None:
    eng = CommandEngine()
    before = eng.board.to_dict()
    history_before = len(eng.history.entries)
    result = eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "bad", "position": {"x": bad, "y": 0}},
            "timestamp": TS,
        }
    )
    assert result["error_code"] == errors.E_OUT_OF_BOUNDS
    assert eng.board.to_dict() == before
    assert len(eng.history.entries) == history_before


def test_minimum_size_still_rejected() -> None:
    eng = CommandEngine()
    created = eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "tiny", "position": {"x": 0, "y": 0}},
            "timestamp": TS,
        }
    )
    assert created["ok"]
    result = eng.execute(
        {
            "command": "resize_item",
            "target_id": created["affected_id"],
            "parameters": {"size": {"w": 10, "h": 10}},
            "timestamp": TS,
        }
    )
    assert result["error_code"] == errors.E_PARAM_INVALID
