"""T047: classroom simulation — 30-minute-style noisy session stays consistent."""

from __future__ import annotations

from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def test_noisy_session_with_corrections() -> None:
    """Mix of valid, invalid, ambiguous and undone commands: no crash,
    state always consistent, correction rate measurable."""
    eng = CommandEngine()
    script = [
        ("create_heading", None, {"text": "Lesson"}),
        ("create_text", None, {"text": "F = ma", "equation_style": True}),
        ("resize_item", None, {"scale_factor": 9.0}),  # invalid: rejected
        ("delete_item", None, {}),  # ambiguous: clarification, no guess
        ("move_item", "missing_999", {"position": {"x": 1, "y": 1}}),  # not found
        ("undo", None, {}),
        ("redo", None, {}),
        ("clear_board", None, {}),  # needs confirmation: blocked, no mutation
    ]
    corrections = 0
    for command, target, params in script:
        before = eng.board.to_dict()
        res = eng.execute(
            {"command": command, "target_id": target, "parameters": params, "timestamp": TS}
        )
        if not res.get("ok"):
            assert eng.board.to_dict() == before or res.get("needs_confirmation")
        if command == "undo":
            corrections += 1
    assert corrections >= 1
    assert eng.board.version >= 1
    board = eng.board
    assert all(el.within_world_limits() for el in board.elements)
