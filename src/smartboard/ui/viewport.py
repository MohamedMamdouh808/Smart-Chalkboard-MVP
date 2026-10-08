"""Single-source viewport: uniform scale + centered offset, exact inverse.

Canvas is fixed (1920x1080). This module is the ONLY place the
screen<->canvas formula lives — paint, pen, mouse, and hit-test all use it.
Qt-agnostic and headless-testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CANVAS_W = 1920
CANVAS_H = 1080


@dataclass(frozen=True)
class Viewport:
    """Reversible mapping between canvas coordinates and view pixels."""

    view_w: int
    view_h: int
    scale: float
    ox: float
    oy: float

    @staticmethod
    def from_sizes(view_w: int, view_h: int) -> "Viewport":
        if view_w <= 0 or view_h <= 0:
            return Viewport(view_w, view_h, 1.0, 0.0, 0.0)
        scale = min(view_w / CANVAS_W, view_h / CANVAS_H)
        return Viewport(
            view_w,
            view_h,
            scale,
            (view_w - CANVAS_W * scale) / 2,
            (view_h - CANVAS_H * scale) / 2,
        )

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        return (x * self.scale + self.ox, y * self.scale + self.oy)

    def to_canvas(self, sx: float, sy: float) -> tuple[float, float]:
        return ((sx - self.ox) / self.scale, (sy - self.oy) / self.scale)


def hit_test(state: dict[str, Any], cx: float, cy: float) -> str | None:
    """Topmost element id containing canvas point (cx, cy), else None."""
    hit: str | None = None
    top_z = -1
    for el in state.get("elements", []):
        if el["x"] <= cx <= el["x"] + el["width"] and el["y"] <= cy <= el["y"] + el["height"]:
            z = int(el.get("z", 0))
            if z >= top_z:
                top_z = z
                hit = str(el["id"])
    return hit
