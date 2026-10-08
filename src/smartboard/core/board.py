"""Board state model. UI-independent; mutated only via the engine."""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any

CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080
MIN_SIZE = 24

ELEMENT_TYPES = ("heading", "text", "shape", "drawing")

DRAWING_WIDTHS: tuple[int, ...] = (2, 4, 8)
DEFAULT_DRAWING_WIDTH = 4

#: Samples closer than this to the last kept point are dropped at commit.
POINT_REDUCTION_DISTANCE = 2.0


def reduce_points(
    points: list[dict[str, Any]], min_distance: float = POINT_REDUCTION_DISTANCE,
) -> list[dict[str, Any]]:
    """Drop samples nearer than ``min_distance`` to the last kept sample.

    The first and last samples are always kept so every stroke still renders
    with its true endpoints.
    """
    if len(points) < 3:
        return list(points)
    kept = [points[0]]
    for point in points[1:-1]:
        last = kept[-1]
        try:
            gap = math.hypot(float(point["x"]) - float(last["x"]),
                             float(point["y"]) - float(last["y"]))
        except (KeyError, TypeError, ValueError):
            continue
        if gap >= min_distance:
            kept.append(point)
    kept.append(points[-1])
    return kept


def clip_point(x: float, y: float) -> tuple[float, float]:
    """Clip a canvas point to the canvas edge."""
    return (min(max(x, 0.0), float(CANVAS_WIDTH)), min(max(y, 0.0), float(CANVAS_HEIGHT)))


def drawing_bbox(strokes: list[list[dict[str, Any]]]) -> tuple[int, int, int, int]:
    """Bounding box derived from stroke points, expanded to MIN_SIZE and
    clamped into the canvas. Returns (x, y, width, height) as ints."""
    xs: list[float] = []
    ys: list[float] = []
    for stroke in strokes:
        for point in stroke:
            try:
                xs.append(float(point["x"]))
                ys.append(float(point["y"]))
            except (KeyError, TypeError, ValueError):
                continue
    if not xs:
        return (0, 0, MIN_SIZE, MIN_SIZE)
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    width = max(x1 - x0, float(MIN_SIZE))
    height = max(y1 - y0, float(MIN_SIZE))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x = min(max(cx - width / 2, 0.0), float(CANVAS_WIDTH - width))
    y = min(max(cy - height / 2, 0.0), float(CANVAS_HEIGHT - height))
    return (int(x), int(y), int(width), int(height))


def translate_points(strokes: list[list[dict[str, Any]]], dx: float, dy: float) -> None:
    """Translate stroke points in place (mutation is engine-internal)."""
    for stroke in strokes:
        for point in stroke:
            point["x"] = float(point["x"]) + dx
            point["y"] = float(point["y"]) + dy


def scale_points(strokes: list[list[dict[str, Any]]], ox: float, oy: float,
                 fx: float, fy: float) -> None:
    """Scale stroke points about the bbox origin (ox, oy), in place."""
    for stroke in strokes:
        for point in stroke:
            point["x"] = ox + (float(point["x"]) - ox) * fx
            point["y"] = oy + (float(point["y"]) - oy) * fy


@dataclass
class Element:
    id: str
    type: str
    x: int
    y: int
    width: int
    height: int
    color: str = "#FFFFFF"
    z: int = 1
    extra: dict[str, Any] = field(default_factory=dict)

    def bbox_inside_canvas(self) -> bool:
        return (
            self.x >= 0
            and self.y >= 0
            and self.width >= MIN_SIZE
            and self.height >= MIN_SIZE
            and self.x + self.width <= CANVAS_WIDTH
            and self.y + self.height <= CANVAS_HEIGHT
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": self.color,
            "z": self.z,
            **self.extra,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Element":
        known = {"id", "type", "x", "y", "width", "height", "color", "z"}
        extra = {k: v for k, v in data.items() if k not in known}
        return Element(
            id=str(data["id"]),
            type=str(data["type"]),
            x=int(data["x"]),
            y=int(data["y"]),
            width=int(data["width"]),
            height=int(data["height"]),
            color=str(data.get("color", "#FFFFFF")),
            z=int(data.get("z", 1)),
            extra=extra,
        )


@dataclass
class Board:
    lesson_id: str = "lesson_001"
    elements: list[Element] = field(default_factory=list)
    selected_element_id: str | None = None
    version: int = 1

    def find(self, element_id: str) -> Element | None:
        for el in self.elements:
            if el.id == element_id:
                return el
        return None

    def top_z(self) -> int:
        return max((el.z for el in self.elements), default=0)

    def lowest_bottom(self) -> int:
        return max((el.y + el.height for el in self.elements), default=0)

    def snapshot(self) -> "Board":
        return copy.deepcopy(self)

    def restore(self, other: "Board") -> None:
        self.lesson_id = other.lesson_id
        self.elements = copy.deepcopy(other.elements)
        self.selected_element_id = other.selected_element_id
        self.version = other.version

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "canvas": {"width": CANVAS_WIDTH, "height": CANVAS_HEIGHT, "unit": "px"},
            "elements": [el.to_dict() for el in self.elements],
            "selected_element_id": self.selected_element_id,
            "version": self.version,
        }
