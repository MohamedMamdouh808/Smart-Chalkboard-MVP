"""T036: confirmation / clarification flows (confirm, cancel, timeout, ambiguity)."""

from __future__ import annotations

from smartboard.core import errors
from smartboard.core.engine import CommandEngine
from smartboard.ui.clarify_dialog import clarification_question
from smartboard.ui.confirm_dialog import CONFIRM_TIMEOUT_S, confirmation_prompt, resolve_timeout

TS = "2026-10-03T18:15:00Z"


def test_confirm_and_cancel_paths() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "a"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    need = eng.execute({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS})
    assert need["needs_confirmation"] is True
    assert eng.board.find(sel) is not None  # type: ignore[arg-type]
    eng.execute({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS}, confirmed=True)
    assert eng.board.find(sel) is None  # type: ignore[arg-type]


def test_timeout_counts_as_cancel() -> None:
    assert CONFIRM_TIMEOUT_S == 30
    assert resolve_timeout(False) is False
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "a"}, "timestamp": TS})
    before = eng.board.to_dict()
    eng.execute({"command": "clear_board", "target_id": None, "parameters": {}, "timestamp": TS},
                confirmed=resolve_timeout(False))
    assert eng.board.to_dict() == before


def test_ambiguous_prompts_for_selection() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "a"}, "timestamp": TS})
    eng.board.selected_element_id = None
    res = eng.execute({"command": "delete_item", "target_id": None, "parameters": {}, "timestamp": TS})
    assert res["error_code"] == errors.E_AMBIGUOUS
    assert res["clarification_question"].startswith("Which object")
    assert clarification_question("delete_item").startswith("Which object")


def test_confirmation_prompt_texts() -> None:
    assert "Cancel" in confirmation_prompt("delete_item") and "Confirm" in confirmation_prompt("delete_item")
    assert "entire board" in confirmation_prompt("clear_board")
    assert "unsaved changes" in confirmation_prompt("new_lesson")
