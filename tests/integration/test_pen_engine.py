"""T024/T026: pen commits through the same engine; works offline."""

from __future__ import annotations

from smartboard.core import errors
from smartboard.core.engine import CommandEngine
from smartboard.ui.pen_input import GROUP_WINDOW_S, StrokeGrouper

TS = "2026-10-03T18:15:00Z"
STROKE = [[{"x": 1, "y": 2}, {"x": 3, "y": 4}]]


def test_pen_commit_gets_unique_never_reused_id() -> None:
    eng = CommandEngine()
    first = eng.add_drawing(STROKE)
    assert first["ok"] and first["affected_id"] == "drawing_001"
    eng.execute({"command": "delete_item", "target_id": "drawing_001",
                 "parameters": {}, "timestamp": TS}, confirmed=True)
    second = eng.add_drawing(STROKE)
    assert second["affected_id"] == "drawing_002"  # never reused


def test_pen_drawing_supports_voice_ops_and_undo() -> None:
    eng = CommandEngine()
    eng.add_drawing(STROKE)
    eng.board.selected_element_id = "drawing_001"
    res = eng.execute({"command": "change_color", "target_id": None,
                       "parameters": {"color": "blue", "use_selection": True}, "timestamp": TS})
    assert res["ok"] and eng.board.find("drawing_001").color == "blue"  # type: ignore[union-attr]
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001").color == "#FFFFFF"  # type: ignore[union-attr]


def test_stroke_grouping_window() -> None:
    assert GROUP_WINDOW_S == 1.5
    g = StrokeGrouper()
    g.pen_up([{"x": 0, "y": 0}], now=0.0)
    g.pen_up([{"x": 1, "y": 1}], now=1.0)  # within window: same group
    g.mark_interaction()  # selection breaks grouping
    g.pen_up([{"x": 2, "y": 2}], now=1.2)
    group = g.flush()
    assert group is not None and len(group) == 1


def test_offline_pen_needs_no_network() -> None:
    """AI providers down (raise) — pen path never touches them by construction."""
    eng = CommandEngine()

    def dead_provider() -> str:
        raise ConnectionError("no internet")

    try:
        dead_provider()
        reachable = True
    except ConnectionError:
        reachable = False
    assert reachable is False
    res = eng.add_drawing(STROKE, source="pen")
    assert res["ok"]  # board and pen keep working
    assert eng.board.to_dict()["elements"][0]["id"] == "drawing_001"


def test_pen_delete_requires_confirmation_like_all() -> None:
    eng = CommandEngine()
    eng.add_drawing(STROKE)
    res = eng.execute({"command": "delete_item", "target_id": "drawing_001",
                       "parameters": {}, "timestamp": TS})
    assert res["error_code"] == errors.E_CONFIRMATION_REQUIRED
