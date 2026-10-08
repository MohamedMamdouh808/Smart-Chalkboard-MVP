"""US3A world-manipulation widget tests (fail-first)."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.camera import normalize_camera
from smartboard.core.engine import CommandEngine
from smartboard.ui.board_view import BoardView

TS = "2026-10-03T18:15:00Z"


def _view(qapp: object, engine: CommandEngine) -> BoardView:
    view = BoardView()
    view.resize(960, 540)
    view.show()
    view.render_state(engine.board.to_dict())
    return view


def _screen(view: BoardView, wx: float, wy: float) -> tuple[float, float]:
    return view.transform().to_screen(wx, wy)


def test_pen_stroke_stores_world_coordinates_at_zoom(qapp: object) -> None:
    eng = CommandEngine()
    view = _view(qapp, eng)
    view.set_mode("pen")
    view.set_camera(normalize_camera(-400.0, -200.0, 2.0))
    received: list = []
    view.StrokeFinished.connect(received.append)
    targets = [(0.0, 0.0), (100.0, 50.0)]
    view._press(("mouse",), *_screen(view, *targets[0]), None)
    view._sample(("mouse",), *_screen(view, *targets[1]), None)
    view._release(("mouse",), *_screen(view, *targets[1]))
    assert len(received) == 1
    assert received[0][0]["x"] == pytest.approx(0.0)
    assert received[0][1]["x"] == pytest.approx(100.0)
    view.close()


def test_drag_commits_world_position_at_zoom(qapp: object) -> None:
    eng = CommandEngine()
    created = eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "drag me", "position": {"x": 100, "y": 100}},
            "timestamp": TS,
        }
    )
    assert created["ok"]
    view = _view(qapp, eng)
    view.set_mode("select")
    view.set_camera(normalize_camera(0.0, 0.0, 2.0))
    received: list = []
    view.GestureFinished.connect(received.append)
    view._press(("mouse",), *_screen(view, 150.0, 150.0), None)
    view._sample(("mouse",), *_screen(view, 350.0, 150.0), None)
    view._release(("mouse",), *_screen(view, 350.0, 150.0))
    assert len(received) == 1
    assert received[0]["command"] == "move_item"
    assert received[0]["parameters"]["position"] == {"x": 300, "y": 100}
    view.close()


def test_resize_handle_usable_at_low_zoom(qapp: object) -> None:
    from smartboard.core.hit_test import handle_at

    assert (
        handle_at({"x": 0, "y": 0, "width": 1000, "height": 1000}, 1000.0, 1000.0, 0.10, 14.0)
        == "se"
    )
