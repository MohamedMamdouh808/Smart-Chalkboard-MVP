"""T011: persistence contract tests (migrations, CRUD, snapshots, WAL, rollback)."""

from __future__ import annotations

import sqlite3

import pytest

from smartboard.persistence.history_repo import HistoryRepo
from smartboard.persistence.lesson_repo import LessonRepo
from smartboard.persistence.metrics import Metrics
from smartboard.persistence.migrations import CURRENT_VERSION, migrate
from smartboard.persistence.sqlite import connect


@pytest.fixture()
def conn() -> sqlite3.Connection:
    c = connect(":memory:")
    migrate(c)
    yield c
    c.close()


def test_migrate_is_idempotent_and_versioned(conn: sqlite3.Connection) -> None:
    assert migrate(conn) == CURRENT_VERSION
    assert migrate(conn) == CURRENT_VERSION


def test_wal_mode_enabled(tmp_path) -> None:
    c = connect(tmp_path / "wal_check.db")
    cur = c.execute("PRAGMA journal_mode")
    assert cur.fetchone()[0].lower() == "wal"
    c.close()


def test_lesson_crud_and_soft_delete(conn: sqlite3.Connection) -> None:
    repo = LessonRepo(conn)
    repo.create("lesson_001", "Physics")
    assert repo.get("lesson_001") is not None
    repo.rename("lesson_001", "Physics 101")
    assert repo.get("lesson_001")["title"] == "Physics 101"
    repo.soft_delete("lesson_001")
    assert repo.get("lesson_001")["deleted_at"] is not None


def test_snapshot_round_trip_and_retention_cap(conn: sqlite3.Connection) -> None:
    repo = LessonRepo(conn)
    repo.create("lesson_001", "Physics")
    state = {"lesson_id": "lesson_001", "elements": [], "version": 1}
    for i in range(25):
        state = {"lesson_id": "lesson_001", "elements": [], "version": i}
        repo.save_snapshot("lesson_001", state, "auto")
    cur = conn.execute("SELECT COUNT(*) FROM board_states WHERE lesson_id = 'lesson_001'")
    assert cur.fetchone()[0] == 20
    latest = repo.latest_snapshot("lesson_001")
    assert latest is not None and latest["version"] == 24


def test_history_append_load_and_undo_status(conn: sqlite3.Connection) -> None:
    repo = HistoryRepo(conn)
    LessonRepo(conn).create("lesson_001", "Physics")
    record = {"seq": 1, "command_json": {"command": "undo"}, "inverse_json": {"op": "noop"},
              "source": "voice", "executed_at": "2026-10-03T18:15:00Z"}
    repo.append("lesson_001", record)
    repo.mark_undone("lesson_001", 1)
    loaded = repo.load("lesson_001")
    assert len(loaded) == 1 and loaded[0]["status"] == "undone"


def test_transactional_rollback_on_db_failure(conn: sqlite3.Connection) -> None:
    repo = LessonRepo(conn)
    repo.create("lesson_001", "Physics")
    with pytest.raises(sqlite3.IntegrityError), conn:
        conn.execute("INSERT INTO lessons (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                     ("lesson_001", "dup", "t", "t"))
    assert repo.get("lesson_001")["title"] == "Physics"


def test_metrics_record_without_content(conn: sqlite3.Connection) -> None:
    Metrics(conn).record("command_attempt", value_ms=120, lesson_id="lesson_001",
                         detail={"provider": "gemini"})
    cur = conn.execute("SELECT event_type, value_ms FROM metrics_events")
    row = cur.fetchone()
    assert (row["event_type"], row["value_ms"]) == ("command_attempt", 120)
