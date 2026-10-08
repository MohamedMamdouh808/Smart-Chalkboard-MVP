"""T040/T042: lessons — CRUD, confirmations, autosave, reopen identity (50x)."""

from __future__ import annotations

import sqlite3

import pytest

from smartboard.app.lesson_service import LessonService, Session
from smartboard.core.board import Element
from smartboard.core.engine import CommandEngine
from smartboard.persistence.history_repo import HistoryRepo
from smartboard.persistence.lesson_repo import LessonRepo
from smartboard.persistence.migrations import migrate
from smartboard.persistence.sqlite import connect

TS = "2026-10-03T18:15:00Z"


@pytest.fixture()
def repos() -> tuple[LessonRepo, HistoryRepo, LessonService]:
    conn = connect(":memory:")
    migrate(conn)
    lessons = LessonRepo(conn)
    return lessons, HistoryRepo(conn), LessonService(lessons)


def test_new_open_rename_delete(repos: tuple[LessonRepo, HistoryRepo, LessonService]) -> None:
    lessons, _, service = repos
    assert service.new_lesson("lesson_001", "Physics", dirty=True, confirmed=False)["status"] == (
        "confirmation_required")
    assert service.new_lesson("lesson_001", "Physics", dirty=True, confirmed=True)["status"] == "created"
    lessons.rename("lesson_001", "Physics 101")
    assert lessons.get("lesson_001")["title"] == "Physics 101"
    assert service.delete_lesson("lesson_001", confirmed=False)["status"] == "confirmation_required"
    assert service.delete_lesson("lesson_001", confirmed=True)["status"] == "deleted"


def test_manual_save_and_reopen_restores_exactly(
    repos: tuple[LessonRepo, HistoryRepo, LessonService],
) -> None:
    lessons, _, _ = repos
    lessons.create("lesson_001", "Physics")
    eng = CommandEngine()
    eng.execute({"command": "create_heading", "target_id": None,
                 "parameters": {"text": "Newton's Second Law"}, "timestamp": TS})
    session = Session(lesson_id="lesson_001", lessons=lessons)
    session.mark_dirty()
    session.save(eng.board.to_dict(), "manual")
    assert session.dirty is False
    restored = lessons.latest_snapshot("lesson_001")
    assert restored == eng.board.to_dict()


def test_autosave_cadence_without_blocking(repos: tuple[LessonRepo, HistoryRepo, LessonService]) -> None:
    lessons, _, _ = repos
    session = Session(lesson_id="lesson_001", lessons=lessons)
    assert session.autosave_due(now=session.last_autosave + 1) is False  # clean: never due
    session.mark_dirty()
    assert session.autosave_due(now=session.last_autosave + 1) is False  # too early
    assert session.autosave_due(now=session.last_autosave + 31) is True


def test_history_persists_so_undo_survives_reopen(
    repos: tuple[LessonRepo, HistoryRepo, LessonService],
) -> None:
    lessons, history, _ = repos
    lessons.create("lesson_001", "Physics")
    eng = CommandEngine(hook=lambda rec: history.append("lesson_001", rec))
    eng.execute({"command": "create_text", "target_id": None, "parameters": {"text": "hi"}, "timestamp": TS})
    loaded = history.load("lesson_001")
    assert len(loaded) == 1 and loaded[0]["status"] == "applied"


def test_fifty_save_reopen_round_trips_identical(
    repos: tuple[LessonRepo, HistoryRepo, LessonService],
) -> None:
    lessons, _, _ = repos
    lessons.create("lesson_001", "Physics")
    eng = CommandEngine()
    eng.execute({"command": "create_heading", "target_id": None,
                 "parameters": {"text": "Newton's Second Law"}, "timestamp": TS})
    eng.execute({"command": "create_text", "target_id": None,
                 "parameters": {"text": "F = ma", "equation_style": True}, "timestamp": TS})
    expected = eng.board.to_dict()
    for _ in range(50):
        lessons.save_snapshot("lesson_001", eng.board.to_dict(), "auto")
        assert lessons.latest_snapshot("lesson_001") == expected


def test_element_deserialization_round_trip() -> None:
    el = Element(id="shape_001", type="shape", x=1, y=2, width=30, height=40,
                 extra={"shape_type": "arrow"})
    assert Element.from_dict(el.to_dict()).to_dict() == el.to_dict()
