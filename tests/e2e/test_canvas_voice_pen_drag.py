"""Mixed voice/pen/drag scenario on the infinite world board."""

from __future__ import annotations

from smartboard.app.orchestrator import build_app

TS = "2026-10-03T18:15:00Z"


class _StubProvider:
    def __init__(self, raw_text: str) -> None:
        self.raw_text = raw_text

    def interpret(self, transcript: str, context: object) -> dict[str, str]:
        assert "viewport" in context
        assert "canvas" not in context
        return {"raw_text": self.raw_text}


def test_voice_pen_drag_share_infinite_board() -> None:
    app = build_app()
    voice = app.handle_live_transcript(
        "make a heading",
        _StubProvider(
            '{"command": "create_heading", "target_id": null, '
            '"parameters": {"text": "Plan"}, "timestamp": "' + TS + '"}'
        ),
    )
    assert voice["ok"]
    heading = app.engine.board.find(voice["affected_id"])
    assert heading is not None
    vx, vy, vw, vh = app.visible_rect()
    assert vx <= heading.x <= vx + vw and vy <= heading.y <= vy + vh
    pen = app.engine.add_drawing(
        [[{"x": -500.0, "y": -500.0}, {"x": 300.0, "y": 200.0}]], source="pen"
    )
    assert pen["ok"]
    history_before = len(app.engine.history.entries)
    drag = app.queue.submit_and_run(
        {
            "command": "move_item",
            "target_id": "drawing_001",
            "parameters": {"position": {"x": -8000, "y": 9000}},
            "timestamp": TS,
        },
        source="ui",
    )
    assert drag["ok"]
    drawing = app.engine.board.find("drawing_001")
    assert drawing is not None
    assert (drawing.x, drawing.y) == (-8000, 9000)
    assert len(app.engine.history.entries) == history_before + 1
    assert app.engine.board.selected_element_id == "drawing_001"
