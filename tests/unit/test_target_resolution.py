"""T007: target / selection resolution tests (never guess)."""

from __future__ import annotations

from smartboard.core import errors
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def make_engine_with_text() -> CommandEngine:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    return eng


def test_explicit_id_resolves() -> None:
    eng = make_engine_with_text()
    sel = eng.board.selected_element_id
    assert sel is not None
    res = eng.execute(
        {"command": "move_item", "target_id": sel,
         "parameters": {"relative": {"direction": "down", "distance": "small"}}, "timestamp": TS}
    )
    assert res["ok"]


def test_use_selection_resolves() -> None:
    eng = make_engine_with_text()
    res = eng.execute(
        {"command": "resize_item", "target_id": None, "parameters": {"scale_factor": 1.25, "use_selection": True},
         "timestamp": TS}
    )
    assert res["ok"]


def test_missing_selection_asks_to_select() -> None:
    eng = CommandEngine()
    before = eng.board.to_dict()
    res = eng.execute(
        {"command": "resize_item", "target_id": None, "parameters": {"scale_factor": 1.25, "use_selection": True},
         "timestamp": TS}
    )
    assert res["error_code"] == errors.E_TARGET_MISSING
    assert eng.board.to_dict() == before


def test_unknown_id_reports_not_found() -> None:
    eng = make_engine_with_text()
    before = eng.board.to_dict()
    res = eng.execute(
        {"command": "delete_item", "target_id": "text_999", "parameters": {}, "timestamp": TS}, confirmed=True
    )
    assert res["error_code"] == errors.E_TARGET_NOT_FOUND
    assert eng.board.to_dict() == before


def test_ambiguous_never_guesses() -> None:
    eng = make_engine_with_text()
    eng.board.selected_element_id = None  # no contextual selection
    before = eng.board.to_dict()
    res = eng.execute({"command": "delete_item", "target_id": None, "parameters": {}, "timestamp": TS})
    assert res["error_code"] == errors.E_AMBIGUOUS
    assert res.get("needs_clarification") is True
    assert eng.board.to_dict() == before
    assert len(eng.history.entries) == 1  # only the creation


def test_deleted_selection_clears_selection() -> None:
    eng = make_engine_with_text()
    sel = eng.board.selected_element_id
    eng.execute({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS}, confirmed=True)
    assert eng.board.selected_element_id is None
