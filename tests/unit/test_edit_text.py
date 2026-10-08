"""US2 internal edit_text engine tests (fail-first)."""

from __future__ import annotations

from smartboard.core import errors
from smartboard.core.command_schema import COMMANDS
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def _engine_with_text() -> tuple[CommandEngine, str]:
    eng = CommandEngine()
    created = eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "original", "position": {"x": 10, "y": 20}},
            "timestamp": TS,
        }
    )
    assert created["ok"]
    return eng, created["affected_id"]


def test_edit_text_updates_content_with_one_history_entry() -> None:
    eng, target = _engine_with_text()
    history_before = len(eng.history.entries)
    result = eng.edit_text(target, "revised", source="ui")
    assert result["ok"]
    assert eng.board.find(target).extra["text"] == "revised"
    assert len(eng.history.entries) == history_before + 1


def test_edit_text_undo_redo_round_trip() -> None:
    eng, target = _engine_with_text()
    assert eng.edit_text(target, "revised", source="ui")["ok"]
    assert eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})[
        "ok"
    ]
    assert eng.board.find(target).extra["text"] == "original"
    assert eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})[
        "ok"
    ]
    assert eng.board.find(target).extra["text"] == "revised"


def test_edit_text_rejects_missing_target_and_bad_text() -> None:
    eng, target = _engine_with_text()
    before = eng.board.to_dict()
    assert eng.edit_text("missing_999", "x", source="ui")["error_code"] == errors.E_TARGET_NOT_FOUND
    assert eng.edit_text(target, "   ", source="ui")["error_code"] == errors.E_PARAM_INVALID
    assert eng.board.to_dict() == before


def test_edit_text_rejects_non_text_targets() -> None:
    eng = CommandEngine()
    created = eng.execute(
        {
            "command": "create_shape",
            "target_id": None,
            "parameters": {"shape_type": "rectangle", "position": {"x": 0, "y": 0}},
            "timestamp": TS,
        }
    )
    assert created["ok"]
    result = eng.edit_text(created["affected_id"], "nope", source="ui")
    assert result["error_code"] == errors.E_PARAM_INVALID


def test_edit_text_is_not_an_ai_command() -> None:
    assert "edit_text" not in COMMANDS
    eng, target = _engine_with_text()
    raw = {
        "command": "edit_text",
        "target_id": target,
        "parameters": {"text": "sneaky"},
        "timestamp": TS,
    }
    result = eng.execute(raw, source="voice")
    assert result["error_code"] == errors.E_UNSUPPORTED_COMMAND


def test_edit_text_history_replays_without_camera() -> None:
    eng, target = _engine_with_text()
    assert eng.edit_text(target, "revised", source="ui")["ok"]
    entry = eng.history.entries[-1]
    assert entry.command["command"] == "edit_text"
