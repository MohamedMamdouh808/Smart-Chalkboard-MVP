"""T006: per-command parameter validator tests."""

from __future__ import annotations

from smartboard.core import errors
from smartboard.core.engine import CommandEngine
from smartboard.core.validators import validate_color, validate_params

TS = "2026-10-03T18:15:00Z"


def run(command: str, params: dict, target=None) -> dict:
    eng = CommandEngine()
    return eng.execute({"command": command, "target_id": target, "parameters": params, "timestamp": TS})


def test_heading_text_bounds() -> None:
    assert run("create_heading", {"text": "Hi"})["ok"]
    assert run("create_heading", {"text": ""})["error_code"] == errors.E_PARAM_INVALID
    assert run("create_heading", {"text": "x" * 201})["error_code"] == errors.E_PARAM_INVALID


def test_text_length_bounds() -> None:
    assert run("create_text", {"text": "F = ma", "equation_style": True})["ok"]
    assert run("create_text", {"text": ""})["error_code"] == errors.E_PARAM_INVALID
    assert run("create_text", {"text": "x" * 2001})["error_code"] == errors.E_PARAM_INVALID
    assert run("create_text", {"text": "ok", "equation_style": "yes"})["error_code"] == errors.E_PARAM_INVALID


def test_unknown_param_keys_rejected() -> None:
    ok, code, _ = validate_params("undo", {"surprise": 1})
    assert not ok and code == errors.E_PARAM_INVALID


def test_shape_enum_locked_to_five() -> None:
    for shape in ("rectangle", "circle", "line", "arrow", "triangle"):
        assert run("create_shape", {"shape_type": shape})["ok"], shape
    bad = run("create_shape", {"shape_type": "hexagon"})
    assert bad["error_code"] == errors.E_PARAM_INVALID
    assert run("create_shape", {})["error_code"] == errors.E_PARAM_INVALID


def test_color_model_names_plus_hex() -> None:
    assert validate_color("red") and validate_color("#FF0000") and validate_color("#ff0000")
    assert not validate_color("chartreuse") and not validate_color("#FFF") and not validate_color(123)


def test_scale_factor_bounds() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    for bad in (0.1, 5.0, "huge"):
        res = eng.execute(
            {"command": "resize_item", "target_id": sel, "parameters": {"scale_factor": bad}, "timestamp": TS}
        )
        assert res["error_code"] == errors.E_PARAM_INVALID
    assert eng.execute(
        {"command": "resize_item", "target_id": sel, "parameters": {"scale_factor": 1.25}, "timestamp": TS}
    )["ok"]


def test_move_requires_exactly_one_mode() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    both = {"position": {"x": 1, "y": 1}, "relative": {"direction": "down", "distance": "medium"}}
    res = eng.execute({"command": "move_item", "target_id": sel, "parameters": both, "timestamp": TS})
    assert res["error_code"] == errors.E_PARAM_INVALID
    res = eng.execute({"command": "move_item", "target_id": sel, "parameters": {}, "timestamp": TS})
    assert res["error_code"] == errors.E_PARAM_INVALID
    bad_dir = {"relative": {"direction": "sideways", "distance": "medium"}}
    res = eng.execute({"command": "move_item", "target_id": sel, "parameters": bad_dir, "timestamp": TS})
    assert res["error_code"] == errors.E_PARAM_INVALID


def test_off_canvas_move_rejected_not_clamped() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    before = (eng.board.find(sel).x, eng.board.find(sel).y) if sel else (0, 0)
    res = eng.execute(
        {"command": "move_item", "target_id": sel, "parameters": {"position": {"x": 5000, "y": 5000}},
         "timestamp": TS}
    )
    assert res["error_code"] == errors.E_OUT_OF_BOUNDS
    assert (eng.board.find(sel).x, eng.board.find(sel).y) == before  # type: ignore[union-attr]


def test_resize_min_size_and_bounds() -> None:
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    sel = eng.board.selected_element_id
    res = eng.execute(
        {"command": "resize_item", "target_id": sel, "parameters": {"size": {"w": 4, "h": 4}}, "timestamp": TS}
    )
    assert res["error_code"] == errors.E_PARAM_INVALID
    res = eng.execute(
        {"command": "resize_item", "target_id": sel, "parameters": {"size": {"w": 5000, "h": 5000}},
         "timestamp": TS}
    )
    assert res["error_code"] == errors.E_OUT_OF_BOUNDS
