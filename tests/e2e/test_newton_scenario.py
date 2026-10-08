"""T043: Newton's Second Law E2E with scripted fixtures (constitution gate)."""

from __future__ import annotations

import json

from smartboard.app.orchestrator import build_app

TS = "2026-10-03T18:15:00Z"

SCRIPT = [
    (
        "Create a heading called Newton's Second Law.",
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Newton's Second Law"},
            "timestamp": TS,
        },
    ),
    (
        "Add the equation F = ma below it.",
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "F = ma", "equation_style": True},
            "timestamp": TS,
        },
    ),
]


def test_newton_scenario_end_to_end() -> None:
    app = build_app()
    # 1. heading created; transcription visible.
    res = app.handle_transcript(
        SCRIPT[0][0], lambda: json.dumps(SCRIPT[0][1]), lambda: json.dumps(SCRIPT[0][1])
    )
    assert res["ok"] and app.transcription.startswith("Create a heading")
    heading = app.engine.board.elements[0]
    assert heading.extra["text"] == "Newton's Second Law"
    # 2. equation below the heading.
    res = app.handle_transcript(
        SCRIPT[1][0], lambda: json.dumps(SCRIPT[1][1]), lambda: json.dumps(SCRIPT[1][1])
    )
    assert res["ok"]
    equation = next(el for el in app.engine.board.elements if el.extra.get("equation_style"))
    assert equation.extra["text"] == "F = ma"
    assert equation.y > heading.y
    # 3. make the equation bigger via selection.
    app.engine.board.selected_element_id = equation.id
    before_w = equation.width
    res = app.engine.execute(
        {
            "command": "resize_item",
            "target_id": None,
            "parameters": {"scale_factor": 1.25, "use_selection": True},
            "timestamp": TS,
        },
        source="voice",
    )
    assert res["ok"] and equation.width == int(before_w * 1.25)
    # 4. pen drawing with unique ID.
    pen = app.commit_pen([[{"x": 10, "y": 10}, {"x": 60, "y": 40}]])
    assert pen["ok"] and pen["affected_id"] == "drawing_001"
    # 5. delete with confirmation.
    need = app.engine.execute(
        {"command": "delete_item", "target_id": equation.id, "parameters": {}, "timestamp": TS},
        source="voice",
    )
    assert need.get("needs_confirmation") is True
    done = app.engine.execute(
        {"command": "delete_item", "target_id": equation.id, "parameters": {}, "timestamp": TS},
        source="voice",
        confirmed=True,
    )
    assert done["ok"] and app.engine.board.find(equation.id) is None
    # 6. Undo restores the equation with its original identity; Redo removes it.
    app.engine.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    restored = app.engine.board.find(equation.id)
    assert restored is not None and restored.extra["text"] == "F = ma"
    app.engine.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert app.engine.board.find(equation.id) is None
