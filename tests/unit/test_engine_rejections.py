"""T009: engine rejection tests — every E_* code leaves state+history identical."""

from __future__ import annotations

import pytest

from smartboard.core import errors
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def seeded() -> CommandEngine:
    eng = CommandEngine()
    eng.execute({"command": "create_heading", "target_id": None,
                 "parameters": {"text": "Newton's Second Law"}, "timestamp": TS})
    return eng


def unchanged(eng: CommandEngine, before_state: dict, before_hist: int) -> None:
    assert eng.board.to_dict() == before_state
    assert len(eng.history.entries) == before_hist


def test_e_schema_malformed_json() -> None:
    eng = seeded()
    before, hist = eng.board.to_dict(), len(eng.history.entries)
    res = eng.execute("{not json", source="voice")
    assert res["error_code"] == errors.E_SCHEMA
    unchanged(eng, before, hist)


def test_e_unsupported_command() -> None:
    eng = seeded()
    before, hist = eng.board.to_dict(), len(eng.history.entries)
    res = eng.execute({"command": "teleport", "target_id": None, "parameters": {}, "timestamp": TS})
    assert res["error_code"] == errors.E_UNSUPPORTED_COMMAND
    unchanged(eng, before, hist)


def test_e_param_invalid_and_empty_board_clear() -> None:
    eng = CommandEngine()
    res = eng.execute({"command": "clear_board", "target_id": None, "parameters": {}, "timestamp": TS},
                      confirmed=True)
    assert res["error_code"] == errors.E_PARAM_INVALID
    assert "already empty" in res["message"]
    assert len(eng.history.entries) == 0


def test_e_nothing_to_undo_redo() -> None:
    eng = CommandEngine()
    assert eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})[
        "error_code"] == errors.E_NOTHING_TO_UNDO
    assert eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})[
        "error_code"] == errors.E_NOTHING_TO_REDO


def test_e_confirmation_required_then_confirm() -> None:
    eng = seeded()
    sel = eng.board.selected_element_id
    before_hist = len(eng.history.entries)
    res = eng.execute({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS})
    assert res["error_code"] == errors.E_CONFIRMATION_REQUIRED
    assert res.get("needs_confirmation") is True
    assert len(eng.history.entries) == before_hist  # cancel-equivalent: no change yet
    ok = eng.execute({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS},
                     confirmed=True)
    assert ok["ok"]
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find(sel) is not None  # type: ignore[arg-type]


def test_new_lesson_dirty_requires_confirmation() -> None:
    eng = seeded()
    res = eng.execute({"command": "new_lesson", "target_id": None, "parameters": {}, "timestamp": TS}, dirty=True)
    assert res["error_code"] == errors.E_CONFIRMATION_REQUIRED
    ok = eng.execute({"command": "new_lesson", "target_id": None, "parameters": {}, "timestamp": TS},
                     dirty=True, confirmed=True)
    assert ok["ok"]


def test_all_rejection_codes_covered() -> None:
    assert set(errors.MESSAGES) == {
        errors.E_SCHEMA, errors.E_UNSUPPORTED_COMMAND, errors.E_PARAM_INVALID,
        errors.E_TARGET_MISSING, errors.E_TARGET_NOT_FOUND, errors.E_OUT_OF_BOUNDS,
        errors.E_NOTHING_TO_UNDO, errors.E_NOTHING_TO_REDO,
        errors.E_CONFIRMATION_REQUIRED, errors.E_AMBIGUOUS,
    }


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        ({"command": "undo", "target_id": None, "parameters": {"x": 1}, "timestamp": TS},
         errors.E_PARAM_INVALID),
        ({"command": "undo", "target_id": None, "timestamp": TS}, errors.E_SCHEMA),
        ({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS, "zzz": 1},
         errors.E_SCHEMA),
    ],
)
def test_shape_violations_rejected(payload: dict, code: str) -> None:
    eng = seeded()
    before, hist = eng.board.to_dict(), len(eng.history.entries)
    res = eng.execute(payload)
    assert res["error_code"] == code
    unchanged(eng, before, hist)
