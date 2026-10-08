"""US2 synthetic drag tests with preview-only motion and one queued commit."""

from __future__ import annotations

import copy

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.orchestrator import build_app
from smartboard.ui.board_view import BoardView

TS = "2026-10-03T18:15:00Z"
DRAWING_STROKES = [[{"x": 1000.0, "y": 200.0}, {"x": 1200.0, "y": 300.0}]]


class FakePoint:
    def __init__(self, x: float, y: float) -> None:
        self._x, self._y = x, y

    def x(self) -> float:
        return self._x

    def y(self) -> float:
        return self._y


class FakeTabletEvent:
    def __init__(self, kind: str, x: float, y: float) -> None:
        self._kind, self._x, self._y = kind, x, y

    def type(self) -> str:
        return self._kind

    def position(self) -> FakePoint:
        return FakePoint(self._x, self._y)

    def pressure(self) -> float:
        return 0.5


def _screen(view: BoardView, wx: float, wy: float) -> tuple[float, float]:
    sx, sy = view.transform().to_screen(wx, wy)
    return float(sx), float(sy)


def _make_app(kind: str):
    app = build_app()
    if kind == "heading":
        assert app.engine.execute(
            {
                "command": "create_heading",
                "target_id": None,
                "parameters": {"text": "Heading"},
                "timestamp": TS,
            }
        )["ok"]
        return app, app.engine.board.find("heading_001")
    if kind == "text":
        assert app.engine.execute(
            {
                "command": "create_text",
                "target_id": None,
                "parameters": {"text": "Body"},
                "timestamp": TS,
            }
        )["ok"]
        return app, app.engine.board.find("text_001")
    if kind == "equation":
        assert app.engine.execute(
            {
                "command": "create_text",
                "target_id": None,
                "parameters": {"text": "E=mc^2", "equation_style": True},
                "timestamp": TS,
            }
        )["ok"]
        return app, app.engine.board.find("text_001")
    if kind == "shape":
        assert app.engine.execute(
            {
                "command": "create_shape",
                "target_id": None,
                "parameters": {"shape_type": "rectangle"},
                "timestamp": TS,
            }
        )["ok"]
        return app, app.engine.board.find("shape_001")
    assert app.engine.add_drawing(copy.deepcopy(DRAWING_STROKES), width=4)["ok"]
    return app, app.engine.board.find("drawing_001")


def _drag_with_pointer(app, view: BoardView, element, pointer: str) -> tuple[list[dict], int]:
    received: list[dict] = []
    view.GestureFinished.connect(
        lambda payload: received.append(app.queue.submit_and_run(payload, source="ui"))
    )
    start = (element.x + element.width / 2.0, element.y + element.height / 2.0)
    end = (start[0] + 100.0, start[1] + 60.0)
    before_state = copy.deepcopy(view._state)
    before_version = app.engine.board.version
    before_history = len(app.engine.history.entries)
    if pointer == "mouse":
        sx, sy = _screen(view, *start)
        ex, ey = _screen(view, *end)
        assert view._press(("mouse",), sx, sy, None) is True
        view._sample(("mouse",), ex, ey, None)
    elif pointer == "tablet":
        sx, sy = _screen(view, *start)
        ex, ey = _screen(view, *end)
        view.tabletEvent(FakeTabletEvent("TabletPress", sx, sy))
        view.tabletEvent(FakeTabletEvent("TabletMove", ex, ey))
    else:
        sx, sy = _screen(view, *start)
        ex, ey = _screen(view, *end)
        assert view._press(("touch", 7), sx, sy, None) is True
        view._sample(("touch", 7), ex, ey, None)
    assert view.gesture_state == "dragging"
    assert view.gesture_preview is not None
    assert (view.gesture_preview["x"], view.gesture_preview["y"]) == (
        element.x + 100,
        element.y + 60,
    )
    assert view._state["elements"] == before_state["elements"]
    assert view._state["selected_element_id"] == element.id
    assert app.engine.board.version == before_version
    assert len(app.engine.history.entries) == before_history
    if pointer == "mouse":
        view._release(("mouse",), ex, ey)
    elif pointer == "tablet":
        view.tabletEvent(FakeTabletEvent("TabletRelease", ex, ey))
    else:
        view._release(("touch", 7), ex, ey)
    assert view.gesture_state == "idle"
    assert view.gesture_preview is None
    return received, before_history


@pytest.mark.parametrize("kind", ["heading", "text", "equation", "shape", "drawing"])
@pytest.mark.parametrize("pointer", ["mouse", "tablet", "touch"])
def test_drag_moves_each_element_once(qapp: object, kind: str, pointer: str) -> None:
    app, element = _make_app(kind)
    assert element is not None
    origin = (element.x, element.y, element.width, element.height)
    view = BoardView()
    view.resize(960, 540)
    try:
        view.set_mode("select")
        view.render_state(app.engine.board.to_dict())
        received, history_before = _drag_with_pointer(app, view, element, pointer)
        assert len(received) == 1
        assert received[0]["ok"]
        assert received[0]["affected_id"] == element.id
        moved = app.engine.board.find(element.id)
        assert moved is not None
        assert (moved.x, moved.y) == (origin[0] + 100, origin[1] + 60)
        assert (moved.width, moved.height) == (origin[2], origin[3])
        assert len(app.engine.history.entries) == history_before + 1
        assert app.engine.board.selected_element_id == element.id
        if kind == "drawing":
            assert (
                moved.extra["strokes"][0]["points"][0]["x"],
                moved.extra["strokes"][0]["points"][0]["y"],
            ) == (1100.0, 260.0)
    finally:
        view.close()


def test_drag_has_no_canvas_edge(qapp: object) -> None:
    app, element = _make_app("heading")
    assert element is not None
    view = BoardView()
    view.resize(960, 540)
    try:
        view.set_mode("select")
        view.render_state(app.engine.board.to_dict())
        received: list[dict] = []
        view.GestureFinished.connect(
            lambda payload: received.append(app.queue.submit_and_run(payload, source="ui"))
        )
        start = (element.x + element.width / 2.0, element.y + element.height / 2.0)
        end = (start[0] + 5000.0, start[1] + 4000.0)
        origin = (element.x, element.y)
        sx, sy = _screen(view, *start)
        ex, ey = _screen(view, *end)
        assert view._press(("mouse",), sx, sy, None) is True
        view._sample(("mouse",), ex, ey, None)
        assert (view.gesture_preview["x"], view.gesture_preview["y"]) == (
            origin[0] + 5000,
            origin[1] + 4000,
        )
        view._release(("mouse",), ex, ey)
        assert received[0]["ok"]
        moved = app.engine.board.find(element.id)
        assert moved is not None
        assert (moved.x, moved.y) == (origin[0] + 5000, origin[1] + 4000)
    finally:
        view.close()
