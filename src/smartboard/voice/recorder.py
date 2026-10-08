"""Push-to-talk recorder (backend-agnostic; 15 s cap; no continuous listen)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Recording:
    audio: bytes
    duration_s: float


class PushToTalk:
    """Press-and-hold control. Release submits. Backend injected for tests."""

    def __init__(self, backend: Callable[[], Recording] | None = None, max_s: float = 15.0) -> None:
        self._backend = backend
        self._holding = False

    def press(self) -> None:
        self._holding = True

    def release(self) -> Recording | None:
        if not self._holding:
            return None
        self._holding = False
        if self._backend is None:
            raise RuntimeError("No audio backend configured.")
        rec = self._backend()
        if not rec.audio or rec.duration_s <= 0:
            return None
        return rec
