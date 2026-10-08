"""Gap-closing coverage for the 95% gate on validation/history (constitution V)."""

from __future__ import annotations

from smartboard.core import errors
from smartboard.core.command_schema import validate_shape
from smartboard.core.element_ids import IdGenerator
from smartboard.core.engine import _Reject, CommandEngine
from smartboard.core.history import History
from smartboard.core.validators import fits_canvas, resolve_move, validate_params

TS = "2026-10-03T18:15:00Z"


def test_timestamp_must_be_string() -> None:
    ok, code, _ = validate_shape(
        {"command": "undo", "target_id": None, "parameters": {}, "timestamp": 12345})
    assert not ok and code == errors.E_SCHEMA


def test_id_generator_seed_and_count() -> None:
    gen = IdGenerator()
    gen.seed_from_ids(["heading_001", "heading_003", "noid", "text_NaN", "shape_007"])
    assert gen.count("heading") == 3 and gen.count("shape") == 7 and gen.count("text") == 0
    assert gen.next("heading") == "heading_004"
    assert gen.next("drawing") == "drawing_001"


def test_history_empty_undo_redo_and_applied() -> None:
    hist = History()
    assert hist.undo_entry() is None and hist.redo_entry() is None
    hist.record({"command": "x"}, {"op": "noop"}, "voice")
    assert len(hist.applied()) == 1


def test_validator_leftover_branches() -> None:
    assert validate_params("create_shape", {"shape_type": "circle", "color": "nope"})[0] is False
    assert validate_params("change_color", {})[0] is False
    assert validate_params("move_item", {"position": [1, 2]})[0] is False
    assert validate_params("move_item", {"position": {"x": 1}})[0] is False
    assert validate_params("move_item", {"relative": True})[0] is False  # type: ignore[dict-item]
    assert validate_params(
        "move_item", {"relative": {"direction": "up", "distance": "huge"}})[0] is False
    assert validate_params(
        "move_item", {"relative": {"direction": "up", "distance": None}})[0] is False
    assert validate_params(
        "resize_item", {"scale_factor": 2.0, "size": {"w": 30, "h": 30}})[0] is False
    assert validate_params("resize_item", {"size": [30, 30]})[0] is False  # type: ignore[dict-item]
    assert validate_params("resize_item", {"size": {"w": 30}})[0] is False
    assert validate_params("resize_item", {})[0] is False
    assert validate_params("new_lesson", {"title": ""})[0] is False


def test_resolve_move_all_directions() -> None:
    assert resolve_move({"position": {"x": 5, "y": 6}}, 0, 0) == (5, 6)
    assert resolve_move({"relative": {"direction": "up", "distance": "small"}}, 100, 100) == (100, 60)
    assert resolve_move({"relative": {"direction": "left", "distance": 10}}, 100, 100) == (90, 100)
    assert resolve_move({"relative": {"direction": "right", "distance": "large"}}, 0, 0) == (200, 0)
    assert resolve_move({"relative": {"direction": "down", "distance": 7}}, 0, 0) == (0, 7)
    assert fits_canvas(0, 0, 24, 24) and not fits_canvas(-1, 0, 24, 24)


def test_heading_no_room_message_and_drawing_no_room() -> None:
    eng = CommandEngine()
    last = None
    for i in range(12):
        last = eng.execute({"command": "create_heading", "target_id": None,
                            "parameters": {"text": f"H{i}"}, "timestamp": TS})
    assert last is not None and last["error_code"] == errors.E_OUT_OF_BOUNDS
    assert "no room" in last["message"]
    # Drawing boxes derive from points now: small strokes always fit, while
    # empty/invalid input is rejected.
    res = eng.add_drawing([[ {"x": 1, "y": 1} ]])
    assert res["ok"]
    res = eng.add_drawing([])
    assert res["error_code"] == errors.E_OUT_OF_BOUNDS
    res = eng.add_drawing([[ {"nonsense": True} ]])
    assert res["error_code"] == errors.E_OUT_OF_BOUNDS


def test_add_drawing_invokes_hook() -> None:
    calls: list[dict] = []
    eng = CommandEngine(hook=calls.append)
    res = eng.add_drawing([[ {"x": 1, "y": 1} ]], source="pen")
    assert res["ok"] and len(calls) == 1 and calls[0]["source"] == "pen"


def test_undo_redo_move_resize_recolor_and_clear() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "a"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    assert sel is not None
    el = eng.board.find(sel)
    assert el is not None
    x0, y0, w0, h0, c0 = el.x, el.y, el.width, el.height, el.color
    eng.execute({"command": "move_item", "target_id": sel,
                 "parameters": {"position": {"x": 300, "y": 300}}, "timestamp": TS})
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert (eng.board.find(sel).x, eng.board.find(sel).y) == (x0, y0)  # type: ignore[union-attr]
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert (eng.board.find(sel).x, eng.board.find(sel).y) == (300, 300)  # type: ignore[union-attr]
    eng.execute({"command": "resize_item", "target_id": sel,
                 "parameters": {"size": {"w": 200, "h": 100}}, "timestamp": TS})
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert (eng.board.find(sel).width, eng.board.find(sel).height) == (w0, h0)  # type: ignore[union-attr]
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert (eng.board.find(sel).width, eng.board.find(sel).height) == (200, 100)  # type: ignore[union-attr]
    eng.execute({"command": "change_color", "target_id": sel,
                 "parameters": {"color": "#00FF00"}, "timestamp": TS})
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find(sel).color == c0  # type: ignore[union-attr]
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find(sel).color == "#00FF00"  # type: ignore[union-attr]
    eng.execute({"command": "resize_item", "target_id": sel,
                 "parameters": {"scale_factor": 2.0}, "timestamp": TS})
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    scaled = eng.board.find(sel)
    assert scaled is not None and scaled.width == 400  # type: ignore[union-attr]
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "b"}, "timestamp": TS})
    eng.execute({"command": "clear_board", "target_id": None, "parameters": {}, "timestamp": TS},
                confirmed=True)
    assert eng.board.elements == []
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert len(eng.board.elements) == 2
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.elements == []


def test_redo_create_restores_same_id() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "a"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find(sel) is None  # type: ignore[arg-type]
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find(sel) is not None  # type: ignore[arg-type]


def test_inverse_and_forward_missing_targets_are_safe() -> None:
    eng = CommandEngine()
    for inverse in (
        {"op": "move", "id": "ghost_001", "x": 1, "y": 2},
        {"op": "resize", "id": "ghost_001", "w": 10, "h": 10},
        {"op": "recolor", "id": "ghost_001", "color": "red"},
    ):
        eng._apply_inverse(inverse)  # must not raise
        eng._apply_forward({"command": "move_item", "parameters": {}}, inverse)
    eng.board.selected_element_id = "other_001"
    eng._apply_inverse({"op": "remove", "id": "gone_001"})  # selection differs: no clear
    assert eng.board.selected_element_id == "other_001"
    eng._apply_forward({"command": "add_drawing", "parameters": {}},
                       {"op": "remove", "id": "drawing_009"})  # legacy redo path
    assert eng.board.find("drawing_009") is not None
    eng2 = CommandEngine()
    eng2._apply_forward({"command": "change_color", "parameters": {"color": "red"}},
                        {"op": "recolor", "id": "ghost_001", "color": "blue"})
    assert eng2.board.elements == []


def test_clear_board_prompt_and_new_lesson_clean_and_fail_default() -> None:
    eng = CommandEngine()
    res = eng.execute({"command": "clear_board", "target_id": None, "parameters": {}, "timestamp": TS})
    assert "entire board" in res["message"]
    res = eng.execute({"command": "new_lesson", "target_id": None, "parameters": {}, "timestamp": TS})
    assert res["ok"] and res.get("new_lesson") is True
    res = eng._fail(errors.E_SCHEMA, "")
    assert res["message"] == errors.message_for(errors.E_SCHEMA)
    exc = _Reject(errors.E_PARAM_INVALID, "boom")
    assert exc.code == errors.E_PARAM_INVALID and str(exc) == "boom"
