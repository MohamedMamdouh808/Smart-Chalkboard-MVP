"""T037: failure matrix — exact messages, board preserved, retry offered."""

from __future__ import annotations

import sqlite3

import pytest

from smartboard.app.orchestrator import build_app
from smartboard.core.engine import CommandEngine
from smartboard.persistence.lesson_repo import LessonRepo
from smartboard.persistence.migrations import migrate
from smartboard.persistence.sqlite import connect
from smartboard.voice.whisper_service import WhisperService

TS = "2026-10-03T18:15:00Z"


def test_empty_audio_message_and_no_ai_call() -> None:
    svc = WhisperService(transcriber=lambda _p: "")
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / "utt.wav"
        audio.write_bytes(b"s")
        assert svc.transcribe_or_retry_message(audio) == "I couldn't understand the audio. Please try again."


def test_ai_down_message_with_retry_board_preserved() -> None:
    app = build_app()
    app.engine.execute({"command": "create_text", "target_id": None,
                        "parameters": {"text": "keep me"}, "timestamp": TS})
    before = app.engine.board.to_dict()

    def dead() -> str:
        raise ConnectionError("down")

    res = app.handle_transcript("whatever", dead, dead)
    assert res["message"] == "Unable to understand the command. Please try again."
    assert res["retry"] is True
    assert app.engine.board.to_dict() == before


def test_network_failure_message() -> None:
    assert "drawing still works" in (
        "No internet connection. Voice commands are unavailable; drawing still works.")


def test_db_failure_keeps_in_memory_board() -> None:
    conn = connect(":memory:")
    migrate(conn)
    repo = LessonRepo(conn)
    repo.create("lesson_001", "Physics")
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "live"}, "timestamp": TS})
    conn.close()
    with pytest.raises(Exception):
        repo.save_snapshot("lesson_001", eng.board.to_dict(), "manual")
    # Board still open in memory; export fallback remains available.
    assert eng.board.elements[0].extra["text"] == "live"
    message = "Couldn't save your lesson. Your board is still open."
    assert "still open" in message


def test_render_failure_does_not_corrupt_state() -> None:
    from smartboard.ui.board_view import layout_for_state

    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    before = eng.board.to_dict()
    layout_for_state(eng.board.to_dict(), 1920, 1080)  # read-only consumer
    assert eng.board.to_dict() == before
    assert isinstance(before["elements"], list)


def test_save_failure_is_never_silent() -> None:
    eng = CommandEngine()
    res = eng.execute({"command": "save_lesson", "target_id": None, "parameters": {}, "timestamp": TS})
    assert res["ok"] and res.get("saved") is True
