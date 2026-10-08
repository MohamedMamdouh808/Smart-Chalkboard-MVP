"""Pen input: HID/stylus stroke capture with 1.5 s grouping (Qt-optional core)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

GROUP_WINDOW_S = 1.5


def map_stroke_to_canvas(
    screen_points: list[dict[str, Any]],
    viewport: Any,
) -> list[dict[str, Any]]:
    """Map sampled screen points (``sx``/``sy``) to world coordinates through
    the viewport current at sample time. Committed strokes store world
    coordinates, so a mid-stroke camera move cannot skew the element."""
    mapped = []
    for p in screen_points:
        cx, cy = viewport.to_world(float(p.get("sx", 0)), float(p.get("sy", 0)))
        point: dict[str, Any] = {"x": cx, "y": cy}
        if "pressure" in p:
            point["pressure"] = p["pressure"]
        mapped.append(point)
    return mapped


@dataclass
class StrokeGrouper:
    """Groups raw strokes into one drawing element per the 1.5 s rule."""

    groups: list[list[list[dict[str, Any]]]] = field(default_factory=list)
    _current: list[list[dict[str, Any]]] = field(default_factory=list)
    _last_up: float | None = None
    _interrupted: bool = False

    def mark_interaction(self) -> None:
        """Call on selection/command between strokes to break grouping."""
        self._interrupted = True

    def pen_up(
        self, stroke: list[dict[str, Any]], now: float | None = None
    ) -> list[list[dict[str, Any]]] | None:
        """Feed one finished stroke. Returns a committed group when the group closes."""
        now = time.monotonic() if now is None else now
        if (
            self._interrupted
            or (self._last_up is not None and now - self._last_up > GROUP_WINDOW_S)
            and self._current
        ):
            self.groups.append(self._current)
            self._current = []
        self._interrupted = False
        self._current.append(stroke)
        self._last_up = now
        return None

    def flush(self) -> list[list[dict[str, Any]]] | None:
        if self._current:
            group = self._current
            self.groups.append(group)
            self._current = []
            return group
        return None
