"""T010: drawing input matrix — synthetic events, mapping, grouping, safety."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.board_view import BoardView  # noqa: E402
from smartboard.ui.viewport import Viewport  # noqa: E402


class FakePoint:
    def __init__(self, x: float, y: float) -> None:
        self._x, self._y = x, y

    def x(self) -> float:
        return self._x

    def y(self) -> float:
        return self._y


class FakeTabletEvent:
    """Minimal QTabletEvent stand-in (type/position/pressure only)."""

    def __init__(self, kind: str, x: float, y: float, pressure: float = 0.5) -> None:
        self._kind, self._x, self._y, self._pressure = kind, x, y, pressure

    def type(self) -> str:
        return self._kind

    def position(self) -> FakePoint:
        return FakePoint(self._x, self._y)

    def pressure(self) -> float:
        return self._pressure


def _view(qapp: object, view_w: int = 960, view_h: int = 540) -> BoardView:
    view = BoardView()
    view.resize(view_w, view_h)
    view.show()
    view.set_mode("pen")
    return view


def _screen(view: BoardView, cx: float, cy: float) -> tuple[int, int]:
    vp = Viewport.from_sizes(view.width(), view.height())
    sx, sy = vp.to_screen(cx, cy)
    origin = view.mapTo(view, view.rect().topLeft())
    return int(origin.x() + sx), int(origin.y() + sy)


def test_synthetic_mouse_draw_emits_canvas_points(qapp: object) -> None:
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    from smartboard.ui.viewport import Viewport

    view = _view(qapp)
    received: list = []
    view.StrokeFinished.connect(received.append)
    vp = Viewport.from_sizes(view.width(), view.height())
    targets = [(200.0, 200.0), (300.0, 250.0), (400.0, 300.0)]
    pts = [QPoint(int(vp.to_screen(cx, cy)[0]), int(vp.to_screen(cx, cy)[1])) for cx, cy in targets]
    QTest.mousePress(view, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pts[0])
    for pt in pts[1:]:
        QTest.mouseMove(view, pt)
    QTest.mouseRelease(view, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, pts[-1])
    assert len(received) == 1
    for got, (cx, cy) in zip(received[0], targets):
        assert abs(got["x"] - cx) < 2.0 and abs(got["y"] - cy) < 2.0
    view.close()


def test_pen_drag_maps_to_canvas(qapp: object) -> None:
    view = _view(qapp)
    received: list = []
    view.StrokeFinished.connect(received.append)
    targets = [(200.0, 200.0), (300.0, 250.0), (400.0, 300.0)]
    view._press(("mouse",), *_screen(view, *targets[0]), None)
    for target in targets[1:]:
        view._sample(("mouse",), *_screen(view, *target), None)
    view._release(("mouse",), *_screen(view, *targets[-1]))
    assert len(received) == 1
    for got, (cx, cy) in zip(received[0], targets):
        assert abs(got["x"] - cx) < 1.0 and abs(got["y"] - cy) < 1.0
    view.close()


def test_synthetic_tablet_keeps_pressure(qapp: object) -> None:
    view = _view(qapp)
    received: list = []
    view.StrokeFinished.connect(received.append)
    view.tabletEvent(FakeTabletEvent("TabletPress", 100, 100, 0.8))
    view.tabletEvent(FakeTabletEvent("TabletMove", 150, 150, 0.4))
    view.tabletEvent(FakeTabletEvent("TabletRelease", 150, 150, 0.0))
    assert len(received) == 1
    assert received[0][0]["pressure"] == 0.8
    assert received[0][1]["pressure"] == 0.4
    view.close()


@pytest.mark.parametrize(("view_w", "view_h"), [(960, 540), (1366, 768), (1920, 1080)])
def test_same_gesture_identical_canvas_points(qapp: object, view_w: int, view_h: int) -> None:
    view = _view(qapp, view_w, view_h)
    received: list = []
    view.StrokeFinished.connect(received.append)
    targets = [(100.0, 100.0), (500.0, 500.0), (900.0, 300.0)]
    view._press(("mouse",), *_screen(view, *targets[0]), None)
    for target in targets[1:]:
        view._sample(("mouse",), *_screen(view, *target), None)
    view._release(("mouse",), *_screen(view, *targets[-1]))
    for got, (cx, cy) in zip(received[0], targets):
        # Integer screen pixels quantize: allow < 2 canvas units.
        assert abs(got["x"] - cx) < 2.0 and abs(got["y"] - cy) < 2.0
    view.close()


def test_press_outside_canvas_ignored(qapp: object) -> None:
    view = _view(qapp)
    received: list = []
    view.StrokeFinished.connect(received.append)
    assert view._press(("mouse",), -50.0, -50.0, None) is False
    assert received == []
    view.close()


def test_single_pointer_rule(qapp: object) -> None:
    view = _view(qapp)
    received: list = []
    view.StrokeFinished.connect(received.append)
    assert view._press(("mouse",), 100.0, 100.0, None) is True
    assert view._press(("touch", 7), 200.0, 200.0, None) is False  # ignored
    view._sample(("touch", 7), 300.0, 300.0, None)  # ignored too
    view._release(("mouse",), 120.0, 120.0)
    assert len(received) == 1 and len(received[0]) == 1
    view.close()


def test_resize_mid_stroke_keeps_shape(qapp: object) -> None:
    view = _view(qapp)
    received: list = []
    view.StrokeFinished.connect(received.append)
    canvas = [(100.0, 500.0), (300.0, 500.0), (500.0, 500.0), (700.0, 500.0)]
    view._press(("mouse",), *_screen(view, *canvas[0]), None)
    for target in canvas[1:3]:
        view._sample(("mouse",), *_screen(view, *target), None)
    view.resize(1366, 768)  # resize mid-stroke
    for target in canvas[3:]:
        view._sample(("mouse",), *_screen(view, *target), None)
    view._release(("mouse",), *_screen(view, *canvas[-1]))
    for got, (cx, cy) in zip(received[0], canvas):
        assert abs(got["x"] - cx) < 1.0 and abs(got["y"] - cy) < 1.0
    view.close()


def test_select_mode_click_selects_drawing(qapp: object) -> None:
    from smartboard.core.hit_test import select_at  # noqa: F401 (contract import)

    view = _view(qapp)
    view.set_mode("select")
    view.render_state({
        "canvas": {"width": 1920, "height": 1080},
        "elements": [{"id": "drawing_001", "type": "drawing", "x": 0, "y": 0,
                      "width": 400, "height": 300, "color": "#FFFFFF", "z": 1,
                      "strokes": [{"points": [{"x": 100, "y": 100}, {"x": 300, "y": 200}],
                                    "width": 4, "color": "#FFFFFF"}]}],
        "selected_element_id": None,
    })
    picked: list = []
    view.SelectionChanged.connect(picked.append)
    sx, sy = _screen(view, 200, 150)  # near the stroke
    assert view._press(("mouse",), float(sx), float(sy), None) is True
    view._release(("mouse",), float(sx), float(sy))
    assert picked == ["drawing_001"]
    assert view._state["selected_element_id"] == "drawing_001"
    view.close()


def test_select_mode_click_empty_clears(qapp: object) -> None:
    view = _view(qapp)
    view.set_mode("select")
    view.render_state({
        "canvas": {"width": 1920, "height": 1080},
        "elements": [{"id": "drawing_001", "type": "drawing", "x": 0, "y": 0,
                      "width": 400, "height": 300, "color": "#FFFFFF", "z": 1,
                      "strokes": [{"points": [{"x": 100, "y": 100}, {"x": 300, "y": 200}],
                                    "width": 4, "color": "#FFFFFF"}]}],
        "selected_element_id": "drawing_001",
    })
    picked: list = []
    view.SelectionChanged.connect(picked.append)
    sx, sy = _screen(view, 1500, 900)  # empty canvas
    view._press(("mouse",), float(sx), float(sy), None)
    view._release(("mouse",), float(sx), float(sy))
    assert picked == [None]
    assert view._state["selected_element_id"] is None
    view.close()
