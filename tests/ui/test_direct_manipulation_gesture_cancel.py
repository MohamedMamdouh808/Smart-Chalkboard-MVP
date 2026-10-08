"""Cancellation and rejected-gesture tests: no state, version, or history changes."""

from __future__ import annotations

import copy

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.orchestrator import build_app
from smartboard.ui.board_view import BoardView

TS = "2026-10-03T18:15:00Z"


def _app_with_shape():
    app = build_app()
    assert app.engine.execute(
        {
            "command": "create_shape",
            "target_id": None,
            "parameters": {"shape_type": "rectangle"},
            "timestamp": TS,
        }
    )["ok"]
    return app


def _screen(view: BoardView, wx: float, wy: float) -> tuple[float, float]:
    sx, sy = view.transform().to_screen(wx, wy)
    return float(sx), float(sy)


def _snapshot(app) -> tuple[dict, int, int]:
    return (
        copy.deepcopy(app.engine.board.to_dict()),
        app.engine.board.version,
        len(app.engine.history.entries),
    )


def _assert_unchanged(app, before: tuple[dict, int, int]) -> None:
    state, version, history = before
    assert app.engine.board.to_dict() == state
    assert app.engine.board.version == version
    assert len(app.engine.history.entries) == history


def test_escape_cancels_active_drag(qapp: object) -> None:
    from PyQt6.QtCore import Qt
    from PyQt6.QtTest import QTest

    app = _app_with_shape()
    view = BoardView()
    view.resize(960, 540)
    try:
        view.set_mode("select")
        view.render_state(app.engine.board.to_dict())
        element = app.engine.board.find("shape_001")
        assert element is not None
        before = _snapshot(app)
        sx, sy = _screen(view, element.x + 100.0, element.y + 100.0)
        ex, ey = _screen(view, element.x + 200.0, element.y + 160.0)
        assert view._press(("mouse",), sx, sy, None) is True
        view._sample(("mouse",), ex, ey, None)
        assert view.gesture_state == "dragging"
        QTest.keyClick(view, Qt.Key.Key_Escape)
        assert view.gesture_state == "idle"
        assert view.gesture_preview is None
        _assert_unchanged(app, before)
    finally:
        view.close()


def test_mode_change_cancels_active_drag(qapp: object) -> None:
    app = _app_with_shape()
    view = BoardView()
    view.resize(960, 540)
    try:
        view.set_mode("select")
        view.render_state(app.engine.board.to_dict())
        element = app.engine.board.find("shape_001")
        assert element is not None
        before = _snapshot(app)
        sx, sy = _screen(view, element.x + 100.0, element.y + 100.0)
        ex, ey = _screen(view, element.x + 200.0, element.y + 160.0)
        assert view._press(("mouse",), sx, sy, None) is True
        view._sample(("mouse",), ex, ey, None)
        assert view.gesture_state == "dragging"
        view.set_mode("select")
        assert view.gesture_state == "idle"
        assert view.gesture_preview is None
        _assert_unchanged(app, before)
    finally:
        view.close()


def test_release_without_movement_writes_nothing(qapp: object) -> None:
    app = _app_with_shape()
    view = BoardView()
    view.resize(960, 540)
    try:
        view.set_mode("select")
        view.render_state(app.engine.board.to_dict())
        element = app.engine.board.find("shape_001")
        assert element is not None
        before = _snapshot(app)
        finished: list[dict] = []
        view.GestureFinished.connect(finished.append)
        sx, sy = _screen(view, element.x + 100.0, element.y + 100.0)
        assert view._press(("mouse",), sx, sy, None) is True
        view._release(("mouse",), sx, sy)
        assert finished == []
        assert view.gesture_state == "idle"
        _assert_unchanged(app, before)
    finally:
        view.close()


def test_rejected_out_of_range_writes_nothing(qapp: object) -> None:
    app = _app_with_shape()
    before = _snapshot(app)
    payload = {
        "command": "move_item",
        "target_id": "shape_001",
        "parameters": {"position": {"x": 3_000_000, "y": 0}},
        "timestamp": TS,
    }
    rejected = app.queue.submit_and_run(payload, source="ui")
    assert rejected["error_code"] == "E_OUT_OF_BOUNDS"
    _assert_unchanged(app, before)


def test_blocked_and_full_queues_do_not_write(qapp: object) -> None:
    app = _app_with_shape()
    delete = {"command": "delete_item", "target_id": "shape_001", "parameters": {}, "timestamp": TS}
    assert app.queue.submit_and_run(delete, source="voice").get("needs_confirmation") is True
    before = _snapshot(app)
    manual = {
        "command": "move_item",
        "target_id": "shape_001",
        "parameters": {"position": {"x": 500, "y": 500}},
        "timestamp": TS,
    }
    assert app.queue.submit_and_run(manual, source="ui")["error_code"] == "E_BLOCKED"
    _assert_unchanged(app, before)
    assert app.queue.resolve_block(confirmed=False)["error_code"] == "E_CANCELLED"
