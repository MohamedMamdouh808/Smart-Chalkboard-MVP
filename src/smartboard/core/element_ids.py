"""Deterministic per-type element ID generation. IDs are never reused."""

from __future__ import annotations


class IdGenerator:
    """Monotonic per-type counters producing `<type>_<NNN>` IDs."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}

    def seed_from_ids(self, ids: list[str]) -> None:
        for raw in ids:
            if "_" not in raw:
                continue
            kind, _, num = raw.rpartition("_")
            if num.isdigit():
                self._counters[kind] = max(self._counters.get(kind, 0), int(num))

    def next(self, kind: str) -> str:
        self._counters[kind] = self._counters.get(kind, 0) + 1
        return f"{kind}_{self._counters[kind]:03d}"

    def count(self, kind: str) -> int:
        return self._counters.get(kind, 0)
