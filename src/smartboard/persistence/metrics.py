"""Local metrics events (counts/latencies only; never content)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any


class Metrics:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def record(
        self, event_type: str, value_ms: int | None = None,
        lesson_id: str | None = None, detail: dict[str, Any] | None = None,
    ) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO metrics_events (lesson_id, event_type, value_ms, detail_json, created_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (
                    lesson_id,
                    event_type,
                    value_ms,
                    json.dumps(detail or {}),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
