"""Undo/redo history with inverse operations. Bounded at 100 steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MAX_DEPTH = 100


@dataclass
class HistoryEntry:
    seq: int
    command: dict[str, Any]
    inverse: dict[str, Any]
    source: str
    status: str = "applied"


@dataclass
class History:
    entries: list[HistoryEntry] = field(default_factory=list)
    pointer: int = 0  # number of applied entries from the start
    _next_seq: int = 1

    def record(self, command: dict[str, Any], inverse: dict[str, Any], source: str) -> HistoryEntry:
        del self.entries[self.pointer :]
        entry = HistoryEntry(seq=self._next_seq, command=command, inverse=inverse, source=source)
        self._next_seq += 1
        self.entries.append(entry)
        self.pointer += 1
        while len(self.entries) > MAX_DEPTH:
            self.entries.pop(0)
            self.pointer -= 1
        return entry

    def can_undo(self) -> bool:
        return self.pointer > 0

    def can_redo(self) -> bool:
        return self.pointer < len(self.entries)

    def undo_entry(self) -> HistoryEntry | None:
        if not self.can_undo():
            return None
        self.pointer -= 1
        entry = self.entries[self.pointer]
        entry.status = "undone"
        return entry

    def redo_entry(self) -> HistoryEntry | None:
        if not self.can_redo():
            return None
        entry = self.entries[self.pointer]
        entry.status = "applied"
        self.pointer += 1
        return entry

    def applied(self) -> list[HistoryEntry]:
        return self.entries[: self.pointer]
