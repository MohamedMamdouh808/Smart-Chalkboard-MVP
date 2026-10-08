"""US1 regression tests for canonical drawing bounds and mandatory refresh."""

from __future__ import annotations

import copy

from smartboard.core.board import (
    Element,
    _drawing_point_lists,
    _stroke_container,
    drawing_bbox,
    drawing_fixed_anchor,
    drawing_stroke_width,
)

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
STROKES = [SCRIBBLE, STRAIGHT_LINE]
WIDTH = 8
EXPECTED_BOUNDS = (96, 106, 728, 118)
TS = "2026-10-03T18:15:00Z"


def test_scribble_plus_line_bounds_include_half_stroke_width() -> None:
    assert drawing_bbox(STROKES, WIDTH) == EXPECTED_BOUNDS


def test_thin_marks_expand_to_minimum_after_half_width() -> None:
    vertical = [[{"x": 500.0, "y": 200.0}, {"x": 500.0, "y": 600.0}]]
    assert drawing_bbox(vertical, WIDTH) == (488, 196, 24, 408)
    assert drawing_bbox([], WIDTH) == (0, 0, 24, 24)


def test_creation_move_resize_undo_redo_refresh_bounds() -> None:
    from smartboard.core.engine import CommandEngine

    eng = CommandEngine()
    assert eng.add_drawing(copy.deepcopy(STROKES), width=WIDTH)["ok"]
    created = eng.board.find("drawing_001")
    assert created is not None
    assert (created.x, created.y, created.width, created.height) == EXPECTED_BOUNDS

    moved = eng.execute(
        {
            "command": "move_item",
            "target_id": "drawing_001",
            "parameters": {"position": {"x": 500, "y": 500}},
            "timestamp": TS,
        }
    )
    assert moved["ok"]
    target = eng.board.find("drawing_001")
    assert target is not None
    assert (target.x, target.y, target.width, target.height) == (500, 500, 728, 118)
    assert (
        target.extra["strokes"][0]["points"][0]["x"],
        target.extra["strokes"][0]["points"][0]["y"],
    ) == (504.0, 534.0)

    resized = eng.execute(
        {
            "command": "resize_item",
            "target_id": "drawing_001",
            "parameters": {"scale_factor": 0.5},
            "timestamp": TS,
        }
    )
    assert resized["ok"]
    target = eng.board.find("drawing_001")
    assert target is not None
    assert (target.x, target.y, target.width, target.height) == (498, 498, 368, 63)
    assert (
        target.extra["strokes"][1]["points"][1]["x"],
        target.extra["strokes"][1]["points"][1]["y"],
    ) == (862.0, 557.0)

    assert eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})[
        "ok"
    ]
    target = eng.board.find("drawing_001")
    assert target is not None
    assert (target.x, target.y, target.width, target.height) == (500, 500, 728, 118)

    assert eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})[
        "ok"
    ]
    target = eng.board.find("drawing_001")
    assert target is not None
    assert (target.x, target.y, target.width, target.height) == (498, 498, 368, 63)


def test_restored_legacy_snapshot_refreshes_bounds() -> None:
    legacy = {
        "id": "drawing_001",
        "type": "drawing",
        "x": 100,
        "y": 110,
        "width": 720,
        "height": 110,
        "color": "#FFFFFF",
        "z": 1,
        "extra": {
            "strokes": [
                {"points": copy.deepcopy(SCRIBBLE), "width": WIDTH, "color": "#FFFFFF"},
                {"points": copy.deepcopy(STRAIGHT_LINE), "width": WIDTH, "color": "#FFFFFF"},
            ]
        },
    }
    restored = Element.from_dict(legacy)
    assert (restored.x, restored.y, restored.width, restored.height) == EXPECTED_BOUNDS


def test_container_width_and_anchor_fallbacks() -> None:
    import pytest

    assert _stroke_container("not-a-drawing") == {}
    self_referential: dict = {}
    self_referential["extra"] = self_referential
    assert _stroke_container(self_referential) == {}
    assert _stroke_container({"extra": {"strokes": "not-a-list"}}) == {}
    assert _drawing_point_lists({"strokes": "not-a-list"}) == []
    assert drawing_stroke_width("not-a-drawing") == 4.0
    assert drawing_stroke_width({"strokes": [{"points": [], "width": True}]}) == 4.0
    assert drawing_stroke_width({"strokes": [{"points": [], "width": 2}]}) == 2.0
    assert drawing_fixed_anchor([], "se") == (0.0, 0.0)
    assert drawing_fixed_anchor([], "se", (7.0, 9.0)) == (7.0, 9.0)
    with pytest.raises(ValueError, match="unknown fixed corner"):
        drawing_fixed_anchor(STROKES, "middle")
