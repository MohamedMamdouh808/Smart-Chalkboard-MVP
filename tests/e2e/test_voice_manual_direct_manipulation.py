"""Mixed voice/manual scenario: voice resize followed by manual drag."""

from __future__ import annotations

import copy

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.orchestrator import build_app
from smartboard.core.board import drawing_bounds_for_element
from smartboard.ui.board_view import BoardView

TS = "2026-10-03T18:15:00Z"
STROKES = [[{"x": 100.0, "y": 100.0}, {"x": 300.0, "y": 200.0}]]
SIZES = [(960, 540), (1280, 720), (1920, 1080), (800, 1000)]


def _screen(view: BoardView, wx: float, wy: float) -> tuple[float, float]:
    sx, sy = view.transform().to_screen(wx, wy)
    return float(sx), float(sy)


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_voice_resize_then_manual_drag(qapp: object, view_w: int, view_h: int) -> None:
    app = build_app()
    assert app.engine.add_drawing(copy.deepcopy(STROKES), width=4)["ok"]
    voice = app.engine.execute(
        {
            "command": "resize_item",
            "target_id": "drawing_001",
            "parameters": {"scale_factor": 2.0},
            "timestamp": TS,
        },
        source="voice",
    )
    assert voice["ok"]
    resized = app.engine.board.find("drawing_001")
    assert resized is not None
    assert (
        resized.extra["strokes"][0]["points"][1]["x"],
        resized.extra["strokes"][0]["points"][1]["y"],
    ) == (502.0, 302.0)
    assert app.engine.board.selected_element_id == "drawing_001"

    view = BoardView()
    view.resize(view_w, view_h)
    try:
        view.set_mode("select")
        view.render_state(app.engine.board.to_dict())
        received: list[dict] = []
        view.GestureFinished.connect(
            lambda payload: received.append(app.queue.submit_and_run_if_idle(payload, source="ui"))
        )
        history_before = len(app.engine.history.entries)
        version_before = app.engine.board.version
        start = (resized.x + resized.width / 2.0, resized.y + resized.height / 2.0)
        end = (start[0] + 100.0, start[1] + 60.0)
        sx, sy = _screen(view, *start)
        ex, ey = _screen(view, *end)
        assert view._press(("mouse",), sx, sy, None) is True
        view._sample(("mouse",), ex, ey, None)
        assert view.gesture_state == "dragging"
        assert len(app.engine.history.entries) == history_before
        assert app.engine.board.version == version_before
        view._release(("mouse",), ex, ey)
        assert len(received) == 1 and received[0]["ok"]
        assert len(app.engine.history.entries) == history_before + 1
        assert [entry.command["command"] for entry in app.engine.history.entries[-2:]] == [
            "resize_item",
            "move_item",
        ]
        moved = app.engine.board.find("drawing_001")
        assert moved is not None
        assert (
            moved.extra["strokes"][0]["points"][1]["x"],
            moved.extra["strokes"][0]["points"][1]["y"],
        ) == (602.0, 362.0)
        assert drawing_bounds_for_element(moved) == (moved.x, moved.y, moved.width, moved.height)
        assert app.engine.board.selected_element_id == "drawing_001"

        strokes: list[list[dict]] = []
        view.StrokeFinished.connect(strokes.append)
        gestures: list[dict] = []
        view.GestureFinished.connect(gestures.append)
        view.set_mode("pen")
        assert view._press(("mouse",), sx, sy, None) is True
        view._sample(("mouse",), ex, ey, None)
        view._release(("mouse",), ex, ey)
        assert len(strokes) == 1
        assert gestures == []
        assert view.gesture_state == "idle"
    finally:
        view.close()
