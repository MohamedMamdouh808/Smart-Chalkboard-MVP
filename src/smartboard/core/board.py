"""Board state model. UI-independent; mutated only via the engine."""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Any

MIN_SIZE = 24

#: Finite sanity limits for the unbounded world model. "Infinite" means no
#: page edge, not unbounded floats or unbounded allocations.
MAX_WORLD_COORD = 1_000_000.0
MAX_WORLD_SIZE = 1_000_000.0

ELEMENT_TYPES = ("heading", "text", "shape", "drawing")

DRAWING_WIDTHS: tuple[int, ...] = (2, 4, 8)
DEFAULT_DRAWING_WIDTH = 4

#: Samples closer than this to the last kept point are dropped at commit.
POINT_REDUCTION_DISTANCE = 2.0


def reduce_points(
    points: list[dict[str, Any]],
    min_distance: float = POINT_REDUCTION_DISTANCE,
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
            gap = math.hypot(
                float(point["x"]) - float(last["x"]), float(point["y"]) - float(last["y"])
            )
        except (KeyError, TypeError, ValueError):
            continue
        if gap >= min_distance:
            kept.append(point)
    kept.append(points[-1])
    return kept


def drawing_bbox(
    strokes: list[list[dict[str, Any]]], stroke_width: float
) -> tuple[int, int, int, int]:
    """Bounding box derived from stroke points plus half the stroke width.

    The result is expanded to MIN_SIZE but never clamped to a canvas. Returns
    (x, y, width, height) as ints in unbounded world coordinates.
    """
    half_width = float(stroke_width) / 2.0
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
    x0, x1 = min(xs) - half_width, max(xs) + half_width
    y0, y1 = min(ys) - half_width, max(ys) + half_width
    width = max(x1 - x0, float(MIN_SIZE))
    height = max(y1 - y0, float(MIN_SIZE))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # Preserve integer-valued geometry despite binary floating-point noise.
    width = math.ceil(width - 1e-9)
    height = math.ceil(height - 1e-9)
    x = math.floor(cx - width / 2 + 1e-9)
    y = math.floor(cy - height / 2 + 1e-9)
    return (x, y, width, height)


def _stroke_container(data: Any) -> dict[str, Any]:
    """Mapping containing a drawing’s strokes and nominal width, if present."""
    container = data.extra if isinstance(data, Element) else data
    while isinstance(container, dict):
        strokes = container.get("strokes")
        if isinstance(strokes, list):
            return container
        nested = container.get("extra")
        if nested is container or not isinstance(nested, dict):
            break
        container = nested
    return {}


def _drawing_point_lists(data: Any) -> list[list[dict[str, Any]]]:
    """Live point lists from an Element or board-state mapping."""
    strokes = _stroke_container(data).get("strokes", [])
    if not isinstance(strokes, list):
        return []
    point_lists: list[list[dict[str, Any]]] = []
    for stroke in strokes:
        if isinstance(stroke, dict) and isinstance(stroke.get("points"), list):
            point_lists.append(stroke["points"])
        elif isinstance(stroke, list):
            point_lists.append(stroke)
    return point_lists


def drawing_stroke_width(data: Any) -> float:
    """Nominal width shared by a drawing’s strokes."""
    container = _stroke_container(data)
    nominal = container.get("width")
    if isinstance(nominal, (int, float)) and not isinstance(nominal, bool):
        return float(nominal)
    strokes = container.get("strokes", [])
    stroke_widths: list[float] = []
    for stroke in strokes if isinstance(strokes, list) else []:
        if isinstance(stroke, dict):
            width = stroke.get("width")
            if isinstance(width, (int, float)) and not isinstance(width, bool):
                stroke_widths.append(float(width))
    if stroke_widths:
        return max(stroke_widths)
    return float(DEFAULT_DRAWING_WIDTH)


def drawing_bounds_for_element(data: Any) -> tuple[int, int, int, int]:
    """Canonical bounds for an Element or board-state drawing mapping."""
    return drawing_bbox(_drawing_point_lists(data), drawing_stroke_width(data))


def drawing_fixed_anchor(
    point_lists: list[list[dict[str, Any]]],
    fixed_corner: str,
    fallback: tuple[float, float] = (0.0, 0.0),
) -> tuple[float, float]:
    """Raw point extremum corresponding to an expanded-bounds fixed corner.

    Scaling about this raw extremum preserves the expanded fixed corner in
    exact arithmetic because the nominal half-width envelope is constant.
    """
    xs: list[float] = []
    ys: list[float] = []
    for stroke in point_lists:
        for point in stroke:
            try:
                xs.append(float(point["x"]))
                ys.append(float(point["y"]))
            except (KeyError, TypeError, ValueError):
                continue
    if not xs:
        return fallback
    if fixed_corner == "nw":
        return (min(xs), min(ys))
    if fixed_corner == "ne":
        return (max(xs), min(ys))
    if fixed_corner == "sw":
        return (min(xs), max(ys))
    if fixed_corner == "se":
        return (max(xs), max(ys))
    raise ValueError(f"unknown fixed corner: {fixed_corner}")


def translate_points(strokes: list[list[dict[str, Any]]], dx: float, dy: float) -> None:
    """Translate stroke points in place (mutation is engine-internal)."""
    for stroke in strokes:
        for point in stroke:
            point["x"] = float(point["x"]) + dx
            point["y"] = float(point["y"]) + dy


def scale_points(
    strokes: list[list[dict[str, Any]]], ox: float, oy: float, fx: float, fy: float
) -> None:
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

    def within_world_limits(self) -> bool:
        return (
            math.isfinite(float(self.x))
            and math.isfinite(float(self.y))
            and math.isfinite(float(self.width))
            and math.isfinite(float(self.height))
            and abs(float(self.x)) <= MAX_WORLD_COORD
            and abs(float(self.y)) <= MAX_WORLD_COORD
            and MIN_SIZE <= float(self.width) <= MAX_WORLD_SIZE
            and MIN_SIZE <= float(self.height) <= MAX_WORLD_SIZE
        )

    def to_dict(self) -> dict[str, Any]:
        data = {
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
        if self.type == "drawing":
            # The flattened nominal stroke width keeps the established
            # persistence shape; preserve canonical bounds separately.
            data["bbox_width"] = self.width
            data["bbox_height"] = self.height
        return data

    def refresh_drawing_bounds(self) -> Element:
        """Recalculate a drawing's bounds from its current points and width."""
        if self.type != "drawing":
            return self
        self.x, self.y, self.width, self.height = drawing_bounds_for_element(self)
        return self

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Element:
        known = {"id", "type", "x", "y", "width", "height", "color", "z"}
        preserved = {"bbox_width", "bbox_height"}
        extra = {k: v for k, v in data.items() if k not in known and k not in preserved}
        element = Element(
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
        if element.type == "drawing":
            nominal_width = data.get("width")
            if isinstance(nominal_width, (int, float)) and not isinstance(nominal_width, bool):
                element.extra["width"] = nominal_width
            element.refresh_drawing_bounds()
        return element


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

    def snapshot(self) -> Board:
        return copy.deepcopy(self)

    def restore(self, other: Board) -> None:
        self.lesson_id = other.lesson_id
        self.elements = copy.deepcopy(other.elements)
        self.selected_element_id = other.selected_element_id
        self.version = other.version

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "elements": [el.to_dict() for el in self.elements],
            "selected_element_id": self.selected_element_id,
            "version": self.version,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Board:
        """Rebuild a board; legacy canvas fields are ignored (coordinates preserved)."""
        elements = [Element.from_dict(item) for item in data.get("elements", [])]
        selected = data.get("selected_element_id")
        return Board(
            lesson_id=str(data.get("lesson_id", "lesson_001")),
            elements=elements,
            selected_element_id=str(selected) if selected is not None else None,
            version=int(data.get("version", 1)),
        )
