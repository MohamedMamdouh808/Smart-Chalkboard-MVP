"""T010: determinism — 100x same sequence on same state gives identical state."""

from __future__ import annotations

from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"

SEQUENCE = [
    {"command": "create_heading", "target_id": None, "parameters": {"text": "Newton's Second Law"},
     "timestamp": TS},
    {"command": "create_text", "target_id": None,
     "parameters": {"text": "F = ma", "equation_style": True}, "timestamp": TS},
    {"command": "create_shape", "target_id": None, "parameters": {"shape_type": "arrow"},
     "timestamp": TS},
]


def run_once() -> dict:
    eng = CommandEngine()
    for raw in SEQUENCE:
        res = eng.execute(dict(raw))
        assert res["ok"], res
    # selection-driven ops on the equation (second element)
    eq = [el for el in eng.board.elements if el.extra.get("equation_style")]
    assert len(eq) == 1
    eng.board.selected_element_id = eq[0].id
    res = eng.execute({"command": "resize_item", "target_id": None,
                       "parameters": {"scale_factor": 1.25, "use_selection": True}, "timestamp": TS})
    assert res["ok"], res
    res = eng.execute({"command": "change_color", "target_id": None,
                       "parameters": {"color": "red", "use_selection": True}, "timestamp": TS})
    assert res["ok"], res
    return eng.board.to_dict()


def test_hundred_runs_identical() -> None:
    first = run_once()
    for _ in range(99):
        assert run_once() == first


def test_ids_deterministic_across_runs() -> None:
    a = [el["id"] for el in run_once()["elements"]]
    b = [el["id"] for el in run_once()["elements"]]
    assert a == b == ["heading_001", "text_001", "shape_001"]
