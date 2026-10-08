"""AIProvider abstraction — returns data only, never mutates anything."""

from __future__ import annotations

from typing import Any, Protocol


class BoardContext(dict):  # transcript + element summaries + selection + schemas
    pass


class AIProvider(Protocol):
    def interpret(self, transcript: str, context: dict[str, Any]) -> dict[str, str]: ...
