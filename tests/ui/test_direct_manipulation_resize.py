"""US3 synthetic resize tests for handles, corners, bounds, and commits."""

from __future__ import annotations

import copy

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.orchestrator import build_app
from smartboard.ui.board_view import BoardView

TS = "2026-10-03T18:15:00Z"
DRAWING_STROKES = [[{"x": 1000.0, "y": 200.0}, {"x": 1200.0, "y": 300.0}]]
MOVES = {"nw": (-100.0, -60.0), "ne": (100.0, -60.0), "sw": (-100.0, 60.0), "se": (100.0, 60.0)}


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


def _corner_point(origin: tuple[int, int, int, int], corner: str) -> tuple[float, float]:
    x, y, w, h = origin
    return {
        "nw": (float(x), float(y)),
        "ne": (float(x + w), float(y)),
        "sw": (float(x), float(y + h)),
        "se": (float(x + w), float(y + h)),
    }[corner]


def _fixed_point(origin: tuple[int, int, int, int], corner: str) -> tuple[float, float]:
    opposite = {"nw": "se", "ne": "sw", "sw": "ne", "se": "nw"}[corner]
    return _corner_point(origin, opposite)


@pytest.mark.parametrize("kind", ["heading", "text", "equation", "shape", "drawing"])
@pytest.mark.parametrize("corner", ["nw", "ne", "sw", "se"])
def test_resize_each_corner_keeps_opposite_fixed(qapp: object, kind: str, corner: str) -> None:
    from PyQt6.QtCore import Qt

    app, element = _make_app(kind)
    assert element is not None
    origin = (element.x, element.y, element.width, element.height)
    history_before = len(app.engine.history.entries)
    view = BoardView()
    view.resize(960, 540)
    try:
        view.set_mode("select")
        assert app.engine.select(element.id)["ok"]
        view.render_state(app.engine.board.to_dict())
        received: list[dict] = []
        view.GestureFinished.connect(
            lambda payload: received.append(app.queue.submit_and_run(payload, source="ui"))
        )
        start = _corner_point(origin, corner)
        end = (start[0] + MOVES[corner][0], start[1] + MOVES[corner][1])
        sx, sy = _screen(view, *start)
        ex, ey = _screen(view, *end)
        assert view._press(("mouse",), sx, sy, None) is True
        view._sample(("mouse",), ex, ey, None)
        assert view.gesture_state == "resizing"
        assert view.gesture_preview is not None
        assert view._state["elements"] == app.engine.board.to_dict()["elements"]
        expected_fixed = _fixed_point(origin, corner)
        preview_fixed = {
            "nw": (
                view.gesture_preview["x"] + view.gesture_preview["width"],
                view.gesture_preview["y"] + view.gesture_preview["height"],
            ),
            "ne": (
                view.gesture_preview["x"],
                view.gesture_preview["y"] + view.gesture_preview["height"],
            ),
            "sw": (
                view.gesture_preview["x"] + view.gesture_preview["width"],
                view.gesture_preview["y"],
            ),
            "se": (view.gesture_preview["x"], view.gesture_preview["y"]),
        }[corner]
        assert preview_fixed == expected_fixed
        if kind in ("drawing", "shape", "equation"):
            original_ratio = origin[2] / origin[3]
            preview_ratio = view.gesture_preview["width"] / view.gesture_preview["height"]
            assert preview_ratio == pytest.approx(original_ratio, rel=0.05)
        view._release(("mouse",), ex, ey)
        assert view.gesture_state == "idle"
        assert len(received) == 1 and received[0]["ok"]
        assert len(app.engine.history.entries) == history_before + 1
        resized = app.engine.board.find(element.id)
        assert resized is not None
        assert resized.width >= 24 and resized.height >= 24
        assert resized.within_world_limits()
        actual_fixed = {
            "nw": (resized.x + resized.width, resized.y + resized.height),
            "ne": (resized.x, resized.y + resized.height),
            "sw": (resized.x + resized.width, resized.y),
            "se": (resized.x, resized.y),
        }[corner]
        if kind == "drawing":
            # Integer quantization of the half-width envelope can move the
            # recalculated drawing corner by one canvas unit.
            assert abs(actual_fixed[0] - expected_fixed[0]) <= 1
            assert abs(actual_fixed[1] - expected_fixed[1]) <= 1
        else:
            assert actual_fixed == expected_fixed
        assert app.engine.board.selected_element_id == element.id
        assert view.cursor().shape() in (
            Qt.CursorShape.ArrowCursor,
            Qt.CursorShape.SizeFDiagCursor,
            Qt.CursorShape.SizeBDiagCursor,
        )
    finally:
        view.close()


@pytest.mark.parametrize(
    "corner,expected",
    [
        ("nw", "SizeFDiagCursor"),
        ("se", "SizeFDiagCursor"),
        ("ne", "SizeBDiagCursor"),
        ("sw", "SizeBDiagCursor"),
    ],
)
def test_handle_hover_shows_directional_cursor(qapp: object, corner: str, expected: str) -> None:
    from PyQt6.QtCore import QEvent, QPointF, Qt
    from PyQt6.QtGui import QMouseEvent

    app, element = _make_app("shape")
    assert element is not None
    view = BoardView()
    view.resize(960, 540)
    try:
        view.set_mode("select")
        view.render_state(app.engine.board.to_dict())
        view.show()
        qapp.processEvents()
        corner_canvas = _corner_point((element.x, element.y, element.width, element.height), corner)
        sx, sy = _screen(view, *corner_canvas)
        event = QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(sx, sy),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        view.mouseMoveEvent(event)
        assert view.cursor().shape() == getattr(Qt.CursorShape, expected)
    finally:
        view.close()
