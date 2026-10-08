"""UI-independent hit-testing for board elements and resize handles."""

from __future__ import annotations

import itertools
import math
from collections.abc import Iterable
from typing import Any

TOLERANCE = 6.0
HANDLE_VISUAL_SIZE = 14.0
HANDLE_MIN_SCREEN_SIZE = 24.0
CORNERS: tuple[str, ...] = ("nw", "ne", "sw", "se")


def point_segment_distance(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> float:
    """Shortest distance from point P to segment AB (canvas units)."""
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _stroke_points(stroke: Any) -> list[dict[str, Any]]:
    from typing import cast

    if isinstance(stroke, dict) and isinstance(stroke.get("points"), list):
        return cast("list[dict[str, Any]]", stroke["points"])
    if isinstance(stroke, list):
        return cast("list[dict[str, Any]]", stroke)
    return []


def _rect(element: Any) -> tuple[float, float, float, float] | None:
    """Authoritative rectangle as floats, or None when malformed."""
    try:
        if hasattr(element, "x"):
            x = float(element.x)
            y = float(element.y)
            w = float(element.width)
            h = float(element.height)
        else:
            x = float(element["x"])
            y = float(element["y"])
            w = float(element["width"])
            h = float(element["height"])
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
    return (x, y, w, h)


def _kind(element: Any) -> str | None:
    try:
        if hasattr(element, "type"):
            return str(element.type)
        return str(element.get("type"))
    except (AttributeError, TypeError, ValueError):
        return None


def _rect_contains(element: Any, cx: float, cy: float) -> bool:
    bounds = _rect(element)
    if bounds is None:
        return False
    x, y, w, h = bounds
    return x <= cx <= x + w and y <= cy <= y + h


def heading_hit(element: Any, cx: float, cy: float) -> bool:
    """True for a pointer in a heading’s authoritative rectangle."""
    return _rect_contains(element, cx, cy)


def text_hit(element: Any, cx: float, cy: float) -> bool:
    """True for a pointer in a text object’s authoritative rectangle."""
    return _rect_contains(element, cx, cy)


def equation_hit(element: Any, cx: float, cy: float) -> bool:
    """True for a pointer in an equation’s authoritative rectangle."""
    return _rect_contains(element, cx, cy)


def _shape_type(element: Any) -> str:
    try:
        if hasattr(element, "extra"):
            extra = element.extra
            shape = extra.get("shape_type") if isinstance(extra, dict) else None
        else:
            extra = element.get("extra")
            shape = extra.get("shape_type") if isinstance(extra, dict) else None
            if shape is None:
                shape = element.get("shape_type")
    except (AttributeError, TypeError, ValueError):
        return "rectangle"
    return str(shape) if shape is not None else "rectangle"


def _point_in_polygon(px: float, py: float, polygon: list[tuple[float, float]]) -> bool:
    """Ray-casting containment, treating polygon edges as hits."""
    inside = False
    total = len(polygon)
    for index in range(total):
        ax, ay = polygon[index]
        bx, by = polygon[(index + 1) % total]
        if point_segment_distance(px, py, ax, ay, bx, by) <= 0.0:
            return True
        if (ay > py) != (by > py):
            intersection = ax + (py - ay) * (bx - ax) / (by - ay)
            if intersection >= px:
                inside = not inside
    return inside


def shape_hit(element: Any, cx: float, cy: float, tolerance: float = TOLERANCE) -> bool:
    """True for a pointer on the rendered geometry of a shape subtype."""
    bounds = _rect(element)
    if bounds is None:
        return False
    x, y, w, h = bounds
    shape = _shape_type(element)
    if shape == "circle":
        if w <= 0 or h <= 0:
            return False
        dx = (cx - (x + w / 2)) / (w / 2)
        dy = (cy - (y + h / 2)) / (h / 2)
        return dx * dx + dy * dy <= 1.0
    if shape in ("line", "arrow"):
        if point_segment_distance(cx, cy, x, y, x + w, y + h) <= tolerance:
            return True
        if shape == "arrow":
            tip = (x + w, y + h)
            return (
                point_segment_distance(cx, cy, tip[0], tip[1], tip[0] - 24.0, tip[1]) <= tolerance
                or point_segment_distance(cx, cy, tip[0], tip[1], tip[0], tip[1] - 24.0)
                <= tolerance
            )
        return False
    if shape == "triangle":
        return _point_in_polygon(cx, cy, [(x + w / 2, y), (x + w, y + h), (x, y + h)])
    return _rect_contains(element, cx, cy)


def drawing_hit(element: Any, cx: float, cy: float, tolerance: float = TOLERANCE) -> bool:
    """True when (cx, cy) is within tolerance of any stroke segment."""
    if hasattr(element, "extra"):
        strokes = element.extra.get("strokes", [])
    else:
        strokes = element.get("strokes", []) or element.get("extra", {}).get("strokes", [])
    for stroke in strokes:
        points = _stroke_points(stroke)
        coords = [(float(p["x"]), float(p["y"])) for p in points if "x" in p and "y" in p]
        if not coords:
            continue
        if len(coords) == 1:
            if math.hypot(cx - coords[0][0], cy - coords[0][1]) <= tolerance:
                return True
            continue
        for (ax, ay), (bx, by) in itertools.pairwise(coords):
            if point_segment_distance(cx, cy, ax, ay, bx, by) <= tolerance:
                return True
    return False


def element_hit(element: Any, cx: float, cy: float, tolerance: float = TOLERANCE) -> bool:
    """Type-specific hit result for headings, text, shapes, and drawings."""
    kind = _kind(element)
    if kind == "heading":
        return heading_hit(element, cx, cy)
    if kind == "text":
        equation = False
        try:
            if hasattr(element, "extra"):
                extra = element.extra
                equation = bool(extra.get("equation_style")) if isinstance(extra, dict) else False
            else:
                extra = element.get("extra")
                equation = bool(extra.get("equation_style")) if isinstance(extra, dict) else False
        except (AttributeError, TypeError, ValueError):
            equation = False
        if equation:
            return equation_hit(element, cx, cy)
        return text_hit(element, cx, cy)
    if kind == "shape":
        return shape_hit(element, cx, cy, tolerance)
    if kind == "drawing":
        return drawing_hit(element, cx, cy, tolerance) or _rect_contains(element, cx, cy)
    return False


def handle_at(
    element: Any, cx: float, cy: float, scale: float = 1.0, visual_size: float = HANDLE_VISUAL_SIZE
) -> str | None:
    """Selected-element corner under a canvas pointer, if any.

    The visual handle remains small, but interaction uses at least the
    screen-pixel equivalent of HANDLE_MIN_SCREEN_SIZE.
    """
    bounds = _rect(element)
    if bounds is None:
        return None
    effective_scale = scale if isinstance(scale, (int, float)) and scale > 0 else 1.0
    half_target = max(float(visual_size) / 2.0, HANDLE_MIN_SCREEN_SIZE / (2.0 * effective_scale))
    x, y, w, h = bounds
    for corner, corner_x, corner_y in (
        ("nw", x, y),
        ("ne", x + w, y),
        ("sw", x, y + h),
        ("se", x + w, y + h),
    ):
        if abs(cx - corner_x) <= half_target and abs(cy - corner_y) <= half_target:
            return corner
    return None


def select_at(
    elements: Iterable[Any], cx: float, cy: float, tolerance: float = TOLERANCE
) -> str | None:
    """Topmost element id at a canvas point. Returns None on empty space."""
    hit: str | None = None
    top_z = -1
    for element in elements:
        if not element_hit(element, cx, cy, tolerance):
            continue
        try:
            z = int(element.z if hasattr(element, "z") else element.get("z", 0))
            eid = str(element.id if hasattr(element, "id") else element["id"])
        except (AttributeError, KeyError, TypeError, ValueError):
            continue
        if z >= top_z:
            top_z = z
            hit = eid
    return hit
