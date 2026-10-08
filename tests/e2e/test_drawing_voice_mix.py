"""T012: mixed scenario — typed heading + pen drawing + voice move/resize + undo."""

from __future__ import annotations

from smartboard.app.orchestrator import build_app

TS = "2026-10-03T18:15:00Z"


def test_heading_drawing_voice_mix() -> None:
    app = build_app()
    eng = app.engine
    # 1. Typed heading through the engine (voice path equivalent).
    res = eng.execute({"command": "create_heading", "target_id": None,
                       "parameters": {"text": "Sketch"}, "timestamp": TS}, source="voice")
    assert res["ok"]
    # 2. Pen drawing committed as an internal operation (not AI-addressable).
    strokes = [[{"x": 200.0, "y": 400.0}, {"x": 400.0, "y": 500.0, "pressure": 0.6}]]
    pen = eng.add_drawing(strokes, color="red", source="pen")
    assert pen["ok"] and pen["affected_id"] == "drawing_001"
    original_points = [dict(p) for p in eng.board.find("drawing_001").extra["strokes"][0]["points"]]  # type: ignore[union-attr]
    # 3. Voice move of the drawing via selection.
    eng.board.selected_element_id = "drawing_001"
    res = eng.execute({"command": "move_item", "target_id": None,
                       "parameters": {"relative": {"direction": "right", "distance": 100},
                                      "use_selection": True}, "timestamp": TS}, source="voice")
    assert res["ok"]
    moved = [dict(p) for p in
             eng.board.find("drawing_001").extra["strokes"][0]["points"]]  # type: ignore[union-attr]
    assert moved[0]["x"] == original_points[0]["x"] + 100
    # 4. Voice resize of the drawing.
    res = eng.execute({"command": "resize_item", "target_id": None,
                       "parameters": {"scale_factor": 1.25, "use_selection": True},
                       "timestamp": TS}, source="voice")
    assert res["ok"]
    # 5. Undo chain restores resize, then move, then the drawing itself.
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001").extra["strokes"][0]["points"] == moved  # type: ignore[union-attr]
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001").extra["strokes"][0]["points"] == original_points  # type: ignore[union-attr]
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001") is None
    # Heading survives; add_drawing is internal-only (never AI-addressable).
    assert eng.board.find("heading_001") is not None
    from smartboard.core import errors as _errors

    res = eng.execute({"command": "add_drawing", "target_id": None,
                       "parameters": {}, "timestamp": TS}, source="voice")
    assert res["error_code"] == _errors.E_UNSUPPORTED_COMMAND
