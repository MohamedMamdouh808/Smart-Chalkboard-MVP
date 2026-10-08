"""Lesson / snapshot repository (transactional)."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any


def _now() -> str:
    return datetime.now(UTC).isoformat()


class LessonRepo:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, lesson_id: str, title: str) -> None:
        now = _now()
        with self.conn:
            self.conn.execute(
                "INSERT INTO lessons (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (lesson_id, title, now, now),
            )

    def rename(self, lesson_id: str, title: str) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE lessons SET title = ?, updated_at = ? WHERE id = ? AND deleted_at IS NULL",
                (title, _now(), lesson_id),
            )

    def soft_delete(self, lesson_id: str) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE lessons SET deleted_at = ?, updated_at = ? WHERE id = ?",
                (_now(), _now(), lesson_id),
            )

    def get(self, lesson_id: str) -> dict[str, Any] | None:
        cur = self.conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
        row = cur.fetchone()
        return dict(row) if row is not None else None

    def save_snapshot(self, lesson_id: str, state: dict[str, Any], save_type: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO board_states (lesson_id, state_json, save_type, saved_at)"
                " VALUES (?, ?, ?, ?)",
                (lesson_id, json.dumps(state), save_type, _now()),
            )
            self.conn.execute(
                "UPDATE lessons SET last_saved_at = ?, updated_at = ? WHERE id = ?",
                (_now(), _now(), lesson_id),
            )
            self.conn.execute(
                """DELETE FROM board_states WHERE id NOT IN (
                     SELECT id FROM board_states WHERE lesson_id = ?
                     ORDER BY saved_at DESC LIMIT 20) AND lesson_id = ?""",
                (lesson_id, lesson_id),
            )

    def latest_snapshot(self, lesson_id: str) -> dict[str, Any] | None:
        cur = self.conn.execute(
            "SELECT state_json FROM board_states WHERE lesson_id = ? ORDER BY saved_at DESC LIMIT 1",
            (lesson_id,),
        )
        row = cur.fetchone()
        return json.loads(row["state_json"]) if row is not None else None
