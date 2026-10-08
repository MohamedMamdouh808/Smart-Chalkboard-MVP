"""Command-history repository (persisted undo across reopen)."""

from __future__ import annotations

import json
import sqlite3
from typing import Any


class HistoryRepo:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def append(self, lesson_id: str, record: dict[str, Any]) -> None:
        with self.conn:
            self.conn.execute(
                """INSERT INTO command_history
                   (lesson_id, seq, command_json, inverse_json, source, status, executed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    lesson_id,
                    int(record["seq"]),
                    json.dumps(record["command_json"]),
                    json.dumps(record.get("inverse_json")),
                    str(record["source"]),
                    "applied",
                    str(record["executed_at"]),
                ),
            )

    def mark_undone(self, lesson_id: str, seq: int) -> None:
        with self.conn:
            self.conn.execute(
                "UPDATE command_history SET status = 'undone' WHERE lesson_id = ? AND seq = ?",
                (lesson_id, seq),
            )

    def load(self, lesson_id: str) -> list[dict[str, Any]]:
        cur = self.conn.execute(
            "SELECT seq, command_json, inverse_json, source, status, executed_at"
            " FROM command_history WHERE lesson_id = ? ORDER BY seq",
            (lesson_id,),
        )
        return [
            {
                "seq": row["seq"],
                "command_json": json.loads(row["command_json"]),
                "inverse_json": json.loads(row["inverse_json"]) if row["inverse_json"] else {},
                "source": row["source"],
                "status": row["status"],
                "executed_at": row["executed_at"],
            }
            for row in cur.fetchall()
        ]
