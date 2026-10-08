"""T008: history tests (record, inverses, undo/redo pointer, depth, exclusions)."""

from __future__ import annotations

from smartboard.core import errors
from smartboard.core.engine import CommandEngine
from smartboard.core.history import MAX_DEPTH

TS = "2026-10-03T18:15:00Z"


def test_record_and_inverse_on_create() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    assert len(eng.history.entries) == 1
    assert eng.history.entries[0].inverse["op"] == "remove"


def test_undo_redo_pointer_and_redo_clear() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "a"}, "timestamp": TS})
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "b"}, "timestamp": TS})
    assert len(eng.board.elements) == 2
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert len(eng.board.elements) == 1
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "c"}, "timestamp": TS})
    assert not eng.history.can_redo()  # new command clears redo
    assert len(eng.board.elements) == 2


def test_undo_redo_round_trip_restores_identity() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    eng.execute({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS}, confirmed=True)
    assert eng.board.find(sel) is None  # type: ignore[arg-type]
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find(sel) is not None  # type: ignore[arg-type]
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find(sel) is None  # type: ignore[arg-type]


def test_undo_redo_themselves_are_not_recorded() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "a"}, "timestamp": TS})
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert len(eng.history.entries) == 1


def test_save_and_new_are_not_undoable() -> None:
    eng = CommandEngine()
    eng.execute({"command": "save_lesson", "target_id": None, "parameters": {}, "timestamp": TS})
    eng.execute({"command": "new_lesson", "target_id": None, "parameters": {}, "timestamp": TS})
    assert len(eng.history.entries) == 0
    res = eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert res["error_code"] == errors.E_NOTHING_TO_UNDO


def test_cancelled_command_not_recorded() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "a"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    eng.execute({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS}, confirmed=False)
    assert len(eng.history.entries) == 1


def test_depth_bounded_at_100() -> None:
    from smartboard.core.history import History

    hist = History()
    for i in range(MAX_DEPTH + 10):
        hist.record({"command": "create_text"}, {"op": "remove", "id": f"text_{i:03d}"}, "voice")
    assert len(hist.entries) == MAX_DEPTH
    assert hist.pointer == MAX_DEPTH
