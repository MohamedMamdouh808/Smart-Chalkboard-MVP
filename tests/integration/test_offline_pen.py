"""T026: offline pen drill — network disabled, board + pen fully usable."""

from __future__ import annotations

from smartboard.app.orchestrator import build_app

TS = "2026-10-03T18:15:00Z"


def test_board_and_pen_work_with_no_network() -> None:
    app = build_app()
    res = app.handle_transcript("create heading", primary=_dead, fallback=_dead)
    assert res["ok"] is False and res.get("retry") is True
    assert app.engine.board.elements == []  # existing board preserved (empty here)
    pen = app.commit_pen([[ {"x": 1, "y": 1} ]])
    assert pen["ok"]


def _dead() -> str:
    raise ConnectionError("No internet connection.")
