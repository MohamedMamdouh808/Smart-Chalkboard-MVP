"""T011: drawing engine — undo/redo, voice ops, persistence, offline."""

from __future__ import annotations

from smartboard.app.orchestrator import build_app
from smartboard.core import errors
from smartboard.core.engine import CommandEngine
from smartboard.persistence.history_repo import HistoryRepo
from smartboard.persistence.lesson_repo import LessonRepo
from smartboard.persistence.migrations import migrate
from smartboard.persistence.sqlite import connect

TS = "2026-10-03T18:15:00Z"
STROKES = [[{"x": 100.0, "y": 100.0}, {"x": 300.0, "y": 200.0, "pressure": 0.7}]]


def test_undo_redo_round_trip_identical_points() -> None:
    eng = CommandEngine()
    eng.add_drawing(STROKES, color="red", width=8)
    before = eng.board.find("drawing_001").to_dict()  # type: ignore[union-attr]
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001") is None
    eng.execute({"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS})
    assert eng.board.find("drawing_001").to_dict() == before  # type: ignore[union-attr]


def test_voice_move_translates_points() -> None:
    eng = CommandEngine()
    eng.add_drawing(STROKES)
    eng.execute(
        {
            "command": "move_item",
            "target_id": "drawing_001",
            "parameters": {"position": {"x": 500, "y": 500}},
            "timestamp": TS,
        }
    )
    el = eng.board.find("drawing_001")
    assert el is not None
    points = el.extra["strokes"][0]["points"]
    assert (points[0]["x"], points[0]["y"]) == (502.0, 502.0)
    assert (points[1]["x"], points[1]["y"]) == (702.0, 602.0)
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    points = eng.board.find("drawing_001").extra["strokes"][0]["points"]  # type: ignore[union-attr]
    assert (points[0]["x"], points[0]["y"]) == (100.0, 100.0)


def test_voice_resize_scales_points_proportionally() -> None:
    eng = CommandEngine()
    eng.add_drawing(STROKES)
    el = eng.board.find("drawing_001")
    assert el is not None
    old_w, old_h = el.width, el.height
    eng.execute(
        {
            "command": "resize_item",
            "target_id": "drawing_001",
            "parameters": {"scale_factor": 2.0},
            "timestamp": TS,
        }
    )
    el = eng.board.find("drawing_001")
    assert el is not None
    assert (el.width, el.height) == (old_w * 2 - 4, old_h * 2 - 4)
    points = el.extra["strokes"][0]["points"]
    assert (points[1]["x"], points[1]["y"]) == (502.0, 302.0)
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    points = eng.board.find("drawing_001").extra["strokes"][0]["points"]  # type: ignore[union-attr]
    assert (points[1]["x"], points[1]["y"]) == (300.0, 200.0)


def test_voice_recolor_and_confirmed_delete() -> None:
    eng = CommandEngine()
    eng.add_drawing(STROKES)
    res = eng.execute(
        {
            "command": "change_color",
            "target_id": "drawing_001",
            "parameters": {"color": "red"},
            "timestamp": TS,
        }
    )
    assert res["ok"] and eng.board.find("drawing_001").color == "red"  # type: ignore[union-attr]
    res = eng.execute(
        {"command": "delete_item", "target_id": "drawing_001", "parameters": {}, "timestamp": TS}
    )
    assert res["error_code"] == errors.E_CONFIRMATION_REQUIRED
    res = eng.execute(
        {"command": "delete_item", "target_id": "drawing_001", "parameters": {}, "timestamp": TS},
        confirmed=True,
    )
    assert res["ok"] and eng.board.find("drawing_001") is None
    eng.execute({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    restored = eng.board.find("drawing_001")
    assert restored is not None
    assert restored.extra["strokes"][0]["points"][1] == {"x": 300.0, "y": 200.0, "pressure": 0.7}


def test_grouping_two_quick_strokes_one_element() -> None:
    from smartboard.ui.pen_input import StrokeGrouper

    app = build_app()
    grouper = StrokeGrouper()
    grouper.pen_up([{"x": 10.0, "y": 10.0}], now=100.0)
    grouper.pen_up([{"x": 20.0, "y": 20.0}], now=100.8)  # within 1.5 s
    group = grouper.flush()
    assert group is not None and len(group) == 2
    committed = app.engine.add_drawing(group, source="pen")
    assert committed["ok"] and committed["affected_id"] == "drawing_001"
    assert len(app.engine.board.elements) == 1


def test_save_reopen_round_trip_identical() -> None:
    conn = connect(":memory:")
    migrate(conn)
    lessons, history = LessonRepo(conn), HistoryRepo(conn)
    lessons.create("lesson_001", "Sketch")
    eng = CommandEngine(hook=lambda rec: history.append("lesson_001", rec))
    eng.add_drawing(STROKES, color="blue", width=2)
    lessons.save_snapshot("lesson_001", eng.board.to_dict(), "manual")
    restored = lessons.latest_snapshot("lesson_001")
    assert restored is not None
    assert restored["elements"][0]["strokes"] == eng.board.elements[0].extra["strokes"]
    assert restored["elements"][0]["color"] == "blue"
    assert len(history.load("lesson_001")) == 1
    conn.close()


def test_offline_draw_commits_without_providers() -> None:
    app = build_app()
    res = app.engine.add_drawing(STROKES, source="pen")
    assert res["ok"]
    assert len(app.engine.history.entries) == 1


def test_pen_commit_goes_through_queue_in_order() -> None:
    """A pen commit waits its turn behind queued voice work, never beside it."""
    app = build_app()
    app.queue.submit(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Plan"},
            "timestamp": TS,
        }
    )
    assert app.queue.depth() == 1
    result = app.commit_pen_drawing(STROKES, color="#00FF00", width=2)
    assert result["ok"] and result["affected_id"] == "drawing_001"
    assert app.queue.depth() == 0  # both items drained, FIFO
    kinds = [el.type for el in app.engine.board.elements]
    assert kinds == ["heading", "drawing"]
    assert app.engine.board.find("drawing_001").color == "#00FF00"  # type: ignore[union-attr]


def test_pen_commit_never_executes_while_voice_head_is_blocked() -> None:
    app = build_app()
    app.engine.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Doomed"},
            "timestamp": TS,
        }
    )
    app.queue.submit(
        {"command": "delete_item", "target_id": "heading_001", "parameters": {}, "timestamp": TS}
    )
    assert app.queue.pump().get("needs_confirmation") is True
    assert app.queue.blocked is True
    blocked = app.commit_pen_drawing(STROKES)
    assert blocked["error_code"] == "E_BLOCKED"
    assert app.engine.board.find("drawing_001") is None  # nothing was written
    app.queue.resolve_block(confirmed=True)  # teacher answers, queue drains
    result = app.commit_pen_drawing(STROKES)
    assert result["ok"] and app.engine.board.find("drawing_001") is not None


def test_pen_commit_reports_queue_full_without_writing() -> None:
    app = build_app()
    for i in range(app.queue.max_waiting):
        app.queue.submit(
            {
                "command": "create_heading",
                "target_id": None,
                "parameters": {"text": f"H{i}"},
                "timestamp": TS,
            }
        )
    result = app.commit_pen_drawing(STROKES)
    assert result["error_code"] == "E_QUEUE_FULL"
    assert all(el.type != "drawing" for el in app.engine.board.elements)


def test_pen_commit_and_voice_command_do_not_interleave() -> None:
    """Concurrent producers: the engine sees whole commands, never half of one.

    A full queue may reject work, so the invariant is that every element that
    did land is intact and uniquely identified — not that every call succeeded.
    """
    import threading

    app = build_app()
    accepted: list[dict] = []

    def voice() -> None:
        for i in range(5):
            accepted.append(
                app.handle_live_transcript(
                    f"shape {i}",
                    _StubProvider(
                        f'{{"command": "create_shape", '
                        f'"target_id": null, "parameters": '
                        f'{{"shape_type": "rectangle", '
                        f'"position": {{"x": {200 + i * 150}, "y": 80}}, '
                        f'"size": {{"w": 24, "h": 24}}}}, '
                        f'"timestamp": "{TS}"}}'
                    ),
                )
            )

    def pen() -> None:
        for i in range(5):
            accepted.append(
                app.commit_pen_drawing(
                    [[{"x": 100.0 + i, "y": 500.0}, {"x": 200.0 + i, "y": 600.0}]]
                )
            )

    threads = [threading.Thread(target=voice), threading.Thread(target=pen)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    elements = app.engine.board.elements
    ids = [el.id for el in elements]
    assert len(ids) == len(set(ids))  # no torn or interleaved writes
    assert all(el.type != "drawing" or el.extra["strokes"] for el in elements)
    # Every element that landed is accounted for by exactly one version bump:
    # rejected submissions (full/blocked queue) wrote nothing.
    succeeded = [r for r in accepted if r.get("ok")]
    assert len(succeeded) == len(elements)
    assert app.engine.board.version == 1 + len(succeeded)


def test_drawing_commit_notifies_autosave_like_any_command() -> None:
    """Contract: autosave fires on drawing commit exactly like other commands."""
    records: list[dict] = []

    eng = CommandEngine(hook=records.append)
    eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "typed"},
            "timestamp": TS,
        }
    )
    eng.add_drawing(STROKES, color="red", width=8)
    assert len(records) == 2

    command_record, drawing_record = records
    assert set(command_record) == set(drawing_record)  # identical record shape
    assert command_record["seq"] == 1 and drawing_record["seq"] == 2
    for record in records:
        assert record["command_json"]["command"]
        assert record["inverse_json"]["op"]  # invertible, so undo/save both work
        assert record["executed_at"]
    assert drawing_record["source"] == "pen"
    assert drawing_record["command_json"]["command"] == "add_drawing"


class _StubProvider:
    def __init__(self, raw_text: str) -> None:
        self.raw_text = raw_text

    def interpret(self, transcript: str, context: object) -> dict[str, str]:
        return {"raw_text": self.raw_text}
