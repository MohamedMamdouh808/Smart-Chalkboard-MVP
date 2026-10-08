"""Unit tests for drawing model helpers and segment hit-testing."""

from __future__ import annotations

import math

from smartboard.core.board import (
    POINT_REDUCTION_DISTANCE,
    clip_point,
    drawing_bbox,
    reduce_points,
    scale_points,
    translate_points,
)
from smartboard.core.hit_test import (
    TOLERANCE,
    drawing_hit,
    point_segment_distance,
    select_at,
)


def test_clip_point_to_edge() -> None:
    assert clip_point(-5, 2000) == (0.0, 1080.0)
    assert clip_point(100, 100) == (100.0, 100.0)


def test_drawing_bbox_derived_and_minimum() -> None:
    assert drawing_bbox([[{"x": 100.0, "y": 100.0}, {"x": 300.0, "y": 200.0}]]) == (
        100, 100, 200, 100)
    x, y, w, h = drawing_bbox([[{"x": 5.0, "y": 5.0}]])
    assert (w, h) == (24, 24) and x >= 0 and y >= 0
    assert drawing_bbox([]) == (0, 0, 24, 24)
    assert drawing_bbox([[{"nonsense": 1}]]) == (0, 0, 24, 24)


def test_translate_and_scale_points() -> None:
    strokes = [[{"x": 10.0, "y": 20.0}]]
    translate_points(strokes, 5.0, -5.0)
    assert strokes[0][0] == {"x": 15.0, "y": 15.0}
    scale_points(strokes, 15.0, 15.0, 2.0, 3.0)
    assert strokes[0][0] == {"x": 15.0, "y": 15.0}
    strokes = [[{"x": 25.0, "y": 35.0}]]
    scale_points(strokes, 15.0, 15.0, 2.0, 3.0)
    assert strokes[0][0] == {"x": 35.0, "y": 75.0}


def test_point_segment_distance() -> None:
    assert point_segment_distance(5, 5, 0, 0, 10, 0) == 5.0
    assert point_segment_distance(0, 0, 0, 0, 0, 0) == 0.0
    assert point_segment_distance(20, 0, 0, 0, 10, 0) == 10.0
    assert TOLERANCE == 6.0


def test_drawing_hit_dict_and_object_forms() -> None:
    from smartboard.core.board import Element

    element = Element(id="drawing_001", type="drawing", x=0, y=0, width=400, height=300,
                      extra={"strokes": [{"points": [{"x": 0.0, "y": 0.0}, {"x": 100.0, "y": 0.0}],
                                         "width": 4, "color": "#FFFFFF"}]})
    assert drawing_hit(element, 50.0, 3.0) is True
    assert drawing_hit(element, 50.0, 50.0) is False
    as_dict = {"extra": {"strokes": [[{"x": 0.0, "y": 0.0}]]}}
    assert drawing_hit(as_dict, 0.0, 0.0) is True
    assert drawing_hit(as_dict, 100.0, 100.0) is False
    assert drawing_hit({"extra": {"strokes": []}}, 0.0, 0.0) is False
    assert drawing_hit({"extra": {"strokes": [[{"y": 1.0}]]}}, 0.0, 0.0) is False
    assert drawing_hit({"extra": {}}, 0.0, 0.0) is False


def test_select_at_topmost_and_empty() -> None:
    elements = [
        {"id": "a", "type": "text", "x": 0, "y": 0, "width": 500, "height": 500, "z": 1},
        {"id": "b", "type": "drawing", "x": 0, "y": 0, "width": 500, "height": 500,
         "z": 2, "strokes": [{"points": [{"x": 10.0, "y": 10.0}, {"x": 20.0, "y": 10.0}],
                              "width": 4, "color": "#FFFFFF"}]},
    ]
    assert select_at(elements, 15.0, 10.0) == "b"
    assert select_at(elements, 400.0, 400.0) == "a"
    assert select_at(elements, 1900.0, 1000.0) is None
    assert select_at([], 0.0, 0.0) is None
    assert select_at([{"id": 1}], 0.0, 0.0) is None
    assert math.isfinite(TOLERANCE)


TS = "2026-10-03T18:15:00Z"
ENGINE_STROKES = [[{"x": 100.0, "y": 100.0}, {"x": 300.0, "y": 200.0}]]


def _engine():
    from smartboard.core.engine import CommandEngine

    return CommandEngine()


def test_execute_hook_and_invalid_width_and_pressure() -> None:
    eng = _engine()
    calls: list = []
    eng.hook = calls.append
    res = eng.execute({"command": "create_text", "target_id": None,
                       "parameters": {"text": "hi"}, "timestamp": TS})
    assert res["ok"] and len(calls) == 1
    res = eng.add_drawing(ENGINE_STROKES, width=99)  # unknown width → default
    assert res["ok"]
    assert eng.board.find("drawing_001").extra["width"] == 4  # type: ignore[union-attr]


def test_drawing_move_resize_undo_redo_unit() -> None:
    eng = _engine()
    eng.add_drawing(ENGINE_STROKES)
    eng.execute({"command": "move_item", "target_id": "drawing_001",
                 "parameters": {"position": {"x": 0, "y": 0}}, "timestamp": TS})
    assert eng.board.find("drawing_001").extra["strokes"][0]["points"][0] == {  # type: ignore[union-attr]
        "x": 0.0, "y": 0.0}
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001").extra["strokes"][0]["points"][0] == {  # type: ignore[union-attr]
        "x": 100.0, "y": 100.0}
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001").extra["strokes"][0]["points"][0] == {  # type: ignore[union-attr]
        "x": 0.0, "y": 0.0}
    eng.execute({"command": "resize_item", "target_id": "drawing_001",
                 "parameters": {"size": {"w": 100, "h": 100}}, "timestamp": TS})
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001").width == 100  # type: ignore[union-attr]


def test_legacy_list_strokes_and_delete_selection() -> None:
    eng = _engine()
    eng.add_drawing(ENGINE_STROKES)
    target = eng.board.find("drawing_001")
    assert target is not None
    target.extra["strokes"] = [[{"x": 10.0, "y": 10.0}]]  # legacy point-list shape
    assert len(eng._drawing_point_lists(target)) == 1
    eng.execute({"command": "create_text", "target_id": None,
                 "parameters": {"text": "other"}, "timestamp": TS})
    other = eng.board.selected_element_id
    eng.execute({"command": "delete_item", "target_id": other,
                 "parameters": {}, "timestamp": TS}, confirmed=True)
    assert eng.board.selected_element_id is None  # deleting selection clears it
    assert eng._confirm_prompt("new_lesson", None) == "Confirm this action? [Cancel] [Confirm]"


def test_apply_forward_legacy_drawing_redo() -> None:
    eng = _engine()
    eng._apply_forward({"command": "add_drawing", "parameters": {}},
                       {"op": "remove", "id": "drawing_009"})
    assert eng.board.find("drawing_009") is not None
    eng._apply_forward({"command": "x", "parameters": {}},
                       {"op": "move", "id": "ghost", "x": 1, "y": 2})
    assert eng.board.find("ghost") is None


def test_reduce_points_drops_near_duplicates_keeps_endpoints() -> None:
    assert POINT_REDUCTION_DISTANCE == 2.0
    dense = [
        {"x": 0.0, "y": 0.0},
        {"x": 0.5, "y": 0.0},   # too close to previous → dropped
        {"x": 1.0, "y": 0.0},   # too close → dropped
        {"x": 10.0, "y": 0.0},  # far enough → kept
        {"x": 10.5, "y": 0.0},  # last sample → always kept
    ]
    reduced = reduce_points(dense)
    assert reduced == [{"x": 0.0, "y": 0.0}, {"x": 10.0, "y": 0.0}, {"x": 10.5, "y": 0.0}]
    assert reduce_points([]) == []
    assert reduce_points([{"x": 1.0, "y": 1.0}]) == [{"x": 1.0, "y": 1.0}]
    two = [{"x": 0.0, "y": 0.0}, {"x": 0.1, "y": 0.0}]
    assert reduce_points(two) == two
    bad = [{"x": 0.0, "y": 0.0}, {"nope": 1}, {"x": 9.0, "y": 9.0}]
    assert reduce_points(bad) == [{"x": 0.0, "y": 0.0}, {"x": 9.0, "y": 9.0}]


def test_add_drawing_reduces_dense_samples_at_commit() -> None:
    eng = _engine()
    dense = [[{"x": 10.0, "y": 10.0}, {"x": 10.4, "y": 10.0},
              {"x": 10.8, "y": 10.0}, {"x": 200.0, "y": 100.0}]]
    assert eng.add_drawing(dense)["ok"]
    kept = eng.board.find("drawing_001").extra["strokes"][0]["points"]  # type: ignore[union-attr]
    assert len(kept) == 2
    assert kept[0] == {"x": 10.0, "y": 10.0} and kept[-1] == {"x": 200.0, "y": 100.0}


def test_change_color_repaints_every_stroke() -> None:
    eng = _engine()
    eng.add_drawing([[{"x": 10.0, "y": 10.0}, {"x": 90.0, "y": 90.0}],
                     [{"x": 20.0, "y": 20.0}, {"x": 95.0, "y": 95.0}]],
                    color="#FFFFFF")
    eng.select("drawing_001")
    res = eng.execute({"command": "change_color", "target_id": None,
                       "parameters": {"color": "red", "use_selection": True}, "timestamp": TS})
    assert res["ok"]
    element = eng.board.find("drawing_001")
    assert element.color == "red"  # type: ignore[union-attr]
    assert all(s["color"] == "red" for s in element.extra["strokes"])  # type: ignore[union-attr]
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    element = eng.board.find("drawing_001")
    assert element.color == "#FFFFFF"  # type: ignore[union-attr]
    assert all(s["color"] == "#FFFFFF" for s in element.extra["strokes"])  # type: ignore[union-attr]
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    element = eng.board.find("drawing_001")
    assert all(s["color"] == "red" for s in element.extra["strokes"])  # type: ignore[union-attr]


def test_select_is_engine_only_and_records_no_history() -> None:
    eng = _engine()
    eng.add_drawing(ENGINE_STROKES)
    version = eng.board.version
    entries = len(eng.history.entries)
    assert eng.select("drawing_001")["ok"]
    assert eng.board.selected_element_id == "drawing_001"
    assert eng.select(None)["ok"] and eng.board.selected_element_id is None
    assert eng.select("drawing_999")["affected_id"] is None  # unknown id → no selection
    assert eng.board.version == version  # selection is not a content change
    assert len(eng.history.entries) == entries
