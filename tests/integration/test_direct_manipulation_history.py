"""History accounting for UI-sourced manual gestures."""

from __future__ import annotations

import threading

from smartboard.app.orchestrator import build_app

TS = "2026-10-03T18:15:00Z"


def _create_heading(app, text: str = "Heading") -> str:
    result = app.engine.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": text},
            "timestamp": TS,
        },
        source="voice",
    )
    assert result["ok"]
    assert result["affected_id"] is not None
    return result["affected_id"]


def test_ui_drag_records_one_reversible_move() -> None:
    app = build_app()
    target = _create_heading(app)
    version_before = app.engine.board.version
    history_before = len(app.engine.history.entries)
    payload = {
        "command": "move_item",
        "target_id": target,
        "parameters": {"position": {"x": 500, "y": 500}},
        "timestamp": TS,
    }
    result = app.queue.submit_and_run(payload, source="ui")
    assert result["ok"] and result["affected_id"] == target
    assert len(app.engine.history.entries) == history_before + 1
    assert app.engine.history.entries[-1].source == "ui"
    assert app.engine.history.entries[-1].command["command"] == "move_item"
    assert app.engine.board.version == version_before + 1
    assert app.engine.board.selected_element_id == target
    assert app.engine.execute(
        {"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS}
    )["ok"]
    assert app.engine.board.find(target).x == 0  # type: ignore[union-attr]
    assert app.engine.execute(
        {"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS}
    )["ok"]
    assert app.engine.board.find(target).x == 500  # type: ignore[union-attr]


def test_ui_resize_records_standard_command_with_fixed_corner() -> None:
    app = build_app()
    target = _create_heading(app)
    history_before = len(app.engine.history.entries)
    payload = {
        "command": "__manual_resize__",
        "target_id": target,
        "parameters": {"size": {"w": 400, "h": 200}},
        "anchor": {"corner": "se", "fixed_corner": "nw", "x": 0, "y": 0},
        "timestamp": TS,
    }
    result = app.queue.submit_and_run(payload, source="ui")
    assert result["ok"] and result["affected_id"] == target
    entry = app.engine.history.entries[-1]
    assert entry.command["command"] == "resize_item"
    assert entry.source == "ui"
    assert "anchor" not in entry.command
    resized = app.engine.board.find(target)
    assert resized is not None
    assert (resized.x, resized.y, resized.width, resized.height) == (0, 0, 400, 200)
    assert len(app.engine.history.entries) == history_before + 1
    assert app.engine.execute(
        {"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS}
    )["ok"]
    restored = app.engine.board.find(target)
    assert restored is not None
    assert (restored.width, restored.height) == (800, 96)
    assert app.engine.execute(
        {"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS}
    )["ok"]
    assert app.engine.board.find(target).width == 400  # type: ignore[union-attr]


def test_manual_gesture_waits_behind_voice_work() -> None:
    app = build_app()
    target = _create_heading(app, "First")
    voice = {
        "command": "create_heading",
        "target_id": None,
        "parameters": {"text": "Second"},
        "timestamp": TS,
    }
    assert app.queue.submit(voice, source="voice")["ok"]
    manual = {
        "command": "move_item",
        "target_id": target,
        "parameters": {"position": {"x": 700, "y": 700}},
        "timestamp": TS,
    }
    result = app.queue.submit_and_run(manual, source="ui")
    assert result["ok"] and result["affected_id"] == target
    assert [element.id for element in app.engine.board.elements] == [target, "heading_002"]
    assert app.engine.board.find(target).x == 700  # type: ignore[union-attr]


def test_blocked_manual_gesture_applies_once_after_confirmation() -> None:
    app = build_app()
    target = _create_heading(app)
    delete = {"command": "delete_item", "target_id": target, "parameters": {}, "timestamp": TS}
    assert app.queue.submit_and_run(delete, source="voice").get("needs_confirmation") is True
    history_before = len(app.engine.history.entries)
    version_before = app.engine.board.version
    manual = {
        "command": "move_item",
        "target_id": target,
        "parameters": {"position": {"x": 700, "y": 700}},
        "timestamp": TS,
    }
    blocked = app.queue.submit_and_run(manual, source="ui")
    assert blocked["error_code"] == "E_BLOCKED"
    assert len(app.engine.history.entries) == history_before
    assert app.engine.board.version == version_before
    assert app.queue.resolve_block(confirmed=False)["error_code"] == "E_CANCELLED"
    assert app.queue.pump()["ok"]
    assert app.engine.board.find(target).x == 700  # type: ignore[union-attr]
    assert len(app.engine.history.entries) == history_before + 1


def test_full_queue_rejects_manual_gesture_without_writing() -> None:
    app = build_app()
    target = _create_heading(app)
    for index in range(app.queue.max_waiting):
        assert app.queue.submit(
            {
                "command": "create_heading",
                "target_id": None,
                "parameters": {"text": f"Holding {index}"},
                "timestamp": TS,
            },
            source="voice",
        )["ok"]
    history_before = len(app.engine.history.entries)
    manual = {
        "command": "move_item",
        "target_id": target,
        "parameters": {"position": {"x": 700, "y": 700}},
        "timestamp": TS,
    }
    rejected = app.queue.submit_and_run(manual, source="ui")
    assert rejected["error_code"] == "E_QUEUE_FULL"
    assert app.engine.board.find(target).x == 0  # type: ignore[union-attr]
    assert len(app.engine.history.entries) == history_before


def test_busy_queue_leaves_manual_gesture_unsigned_for_retry() -> None:
    app = build_app()
    target = _create_heading(app)
    holding = {
        "command": "create_heading",
        "target_id": None,
        "parameters": {"text": "Holding"},
        "timestamp": TS,
    }
    assert app.queue.submit(holding, source="voice")["ok"]
    history_before = len(app.engine.history.entries)
    manual = {
        "command": "move_item",
        "target_id": target,
        "parameters": {"position": {"x": 700, "y": 700}},
        "timestamp": TS,
    }
    busy = app.commit_manual_gesture(manual)
    assert busy["error_code"] == "E_BUSY"
    assert app.queue.depth() == 1
    assert len(app.engine.history.entries) == history_before
    assert app.queue.pump()["ok"]
    history_after_holding = len(app.engine.history.entries)
    retried = app.commit_manual_gesture(manual)
    assert retried["ok"] and retried["affected_id"] == target
    assert len(app.engine.history.entries) == history_after_holding + 1


def test_manual_resize_rejects_invalid_requests_without_writing() -> None:
    from smartboard.core import errors
    from smartboard.core.engine import CommandEngine

    eng = CommandEngine()
    eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "Body"},
            "timestamp": TS,
        }
    )
    target = eng.board.find("text_001")
    assert target is not None
    history_before = len(eng.history.entries)
    version_before = eng.board.version
    anchor = {"corner": "se", "fixed_corner": "nw", "x": 0, "y": 120}
    assert (
        eng.manual_resize(target.id, {"size": {"w": 300, "h": 200}}, anchor, "not-a-timestamp")[
            "error_code"
        ]
        == errors.E_SCHEMA
    )
    assert (
        eng.manual_resize(target.id, {"size": {"w": 10, "h": 200}}, anchor, TS)["error_code"]
        == errors.E_PARAM_INVALID
    )
    assert (
        eng.manual_resize("missing", {"size": {"w": 300, "h": 200}}, anchor, TS)["error_code"]
        == errors.E_TARGET_NOT_FOUND
    )
    assert (
        eng.manual_resize(target.id, {"size": {"w": 300, "h": 200}}, None, TS)["error_code"]
        == errors.E_PARAM_INVALID
    )
    assert (
        eng.manual_resize(target.id, {"size": {"w": 300, "h": 200}}, {"fixed_corner": "nw"}, TS)[
            "error_code"
        ]
        == errors.E_PARAM_INVALID
    )
    assert (
        eng.manual_resize(
            target.id,
            {"size": {"w": 300, "h": 200}},
            {"fixed_corner": "middle", "x": 0, "y": 120},
            TS,
        )["error_code"]
        == errors.E_PARAM_INVALID
    )
    assert (
        eng.manual_resize(target.id, {"size": {"w": 3_000_000, "h": 2000}}, anchor, TS)[
            "error_code"
        ]
        == errors.E_OUT_OF_BOUNDS
    )
    target.width = 0
    assert (
        eng.manual_resize(target.id, {"size": {"w": 300, "h": 200}}, anchor, TS)["error_code"]
        == errors.E_PARAM_INVALID
    )
    assert len(eng.history.entries) == history_before
    assert eng.board.version == version_before


def test_drawing_commit_out_of_range_writes_nothing() -> None:
    from smartboard.core import errors
    from smartboard.core.engine import CommandEngine

    eng = CommandEngine()
    history_before = len(eng.history.entries)
    result = eng.add_drawing(
        [[{"x": -1_000_000.0, "y": 0.0}, {"x": 1_000_000.0, "y": 0.0}]], width=8
    )
    assert result["error_code"] == errors.E_OUT_OF_BOUNDS
    assert eng.board.elements == []
    assert len(eng.history.entries) == history_before


def test_concurrent_voice_and_manual_producers_stay_serialized() -> None:
    app = build_app()
    barrier = threading.Barrier(3)
    outcomes: list[dict] = []
    outcomes_lock = threading.Lock()

    def producer(start: int) -> None:
        barrier.wait()
        made = 0
        attempts = 0
        while made < 5 and attempts < 500:
            attempts += 1
            payload = {
                "command": "create_shape",
                "target_id": None,
                "parameters": {
                    "shape_type": "rectangle",
                    "position": {"x": 160 + start * 300 + made * 50, "y": 80},
                    "size": {"w": 24, "h": 24},
                },
                "timestamp": TS,
            }
            result = app.queue.submit_and_run(payload, source="ui")
            if result.get("ok"):
                with outcomes_lock:
                    outcomes.append(result)
                made += 1

    workers = [threading.Thread(target=producer, args=(worker,)) for worker in range(2)]
    for worker in workers:
        worker.start()
    barrier.wait()
    for worker in workers:
        worker.join()
    assert len(outcomes) == 10
    assert len(app.engine.board.elements) == 10
    assert len({element.id for element in app.engine.board.elements}) == 10
    assert app.engine.board.version == 1 + 10  # ten accepted creations
