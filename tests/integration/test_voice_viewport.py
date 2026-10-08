"""US3B voice-viewport integration tests (fail-first)."""

from __future__ import annotations

from smartboard.app.orchestrator import Orchestrator
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def _orchestrator() -> Orchestrator:
    orch = Orchestrator(CommandEngine())
    orch.set_view_size(960, 540)
    return orch


def test_missing_position_is_placed_in_visible_area() -> None:
    orch = _orchestrator()
    orch.pan_by_screen(5000.0, 3000.0)
    payload = {
        "command": "create_text",
        "target_id": None,
        "parameters": {"text": "visible"},
        "timestamp": TS,
    }
    normalized = orch.normalize_command(payload)
    x, y = normalized["parameters"]["position"]["x"], normalized["parameters"]["position"]["y"]
    vx, vy, vw, vh = orch.visible_rect()
    assert vx <= x <= vx + vw and vy <= y <= vy + vh
    result = orch.queue.submit_and_run(normalized, source="voice")
    assert result["ok"]
    element = orch.engine.board.find(result["affected_id"])
    assert element is not None
    assert (element.x, element.y) == (x, y)


def test_explicit_position_is_preserved() -> None:
    orch = _orchestrator()
    payload = {
        "command": "create_text",
        "target_id": None,
        "parameters": {"text": "far", "position": {"x": -9000, "y": 42000}},
        "timestamp": TS,
    }
    normalized = orch.normalize_command(payload)
    assert normalized["parameters"]["position"] == {"x": -9000, "y": 42000}


def test_relative_moves_scale_with_zoom() -> None:
    orch = _orchestrator()
    created = orch.engine.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "mover", "position": {"x": 0, "y": 0}},
            "timestamp": TS,
        }
    )
    assert created["ok"]
    target = created["affected_id"]
    orch.zoom_about(480.0, 270.0, 2.0)
    payload = {
        "command": "move_item",
        "target_id": target,
        "parameters": {"relative": {"direction": "right", "distance": "small"}},
        "timestamp": TS,
    }
    normalized = orch.normalize_command(payload)
    assert normalized["parameters"]["relative"]["distance"] == 20
    result = orch.queue.submit_and_run(normalized, source="voice")
    assert result["ok"]
    assert orch.engine.board.find(target).x == 20


def test_normalized_history_replays_without_camera() -> None:
    orch = _orchestrator()
    payload = {
        "command": "create_text",
        "target_id": None,
        "parameters": {"text": "replay"},
        "timestamp": TS,
    }
    normalized = orch.normalize_command(payload)
    first = Orchestrator(CommandEngine())
    second = Orchestrator(CommandEngine())
    first.queue.submit_and_run(dict(normalized), source="voice")
    second.queue.submit_and_run(dict(normalized), source="voice")
    assert first.engine.board.to_dict() == second.engine.board.to_dict()
