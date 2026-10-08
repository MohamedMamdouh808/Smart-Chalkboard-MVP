"""Hit-testing for drawings: point-to-segment distance with 6-unit tolerance."""

from __future__ import annotations

import math
from typing import Any, Iterable

TOLERANCE = 6.0


def point_segment_distance(px: float, py: float, ax: float, ay: float,
                           bx: float, by: float) -> float:
    """Shortest distance from point P to segment AB (canvas units)."""
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _stroke_points(stroke: Any) -> list[dict[str, Any]]:
    if isinstance(stroke, dict) and isinstance(stroke.get("points"), list):
        return stroke["points"]
    if isinstance(stroke, list):
        return stroke
    return []


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
        for (ax, ay), (bx, by) in zip(coords, coords[1:]):
            if point_segment_distance(cx, cy, ax, ay, bx, by) <= tolerance:
                return True
    return False


def _bbox_contains(element: Any, cx: float, cy: float) -> bool:
    get = (lambda k: getattr(element, k)) if hasattr(element, "x") else element.__getitem__
    try:
        x, y, w, h = float(get("x")), float(get("y")), float(get("width")), float(get("height"))
    except (KeyError, TypeError, ValueError, AttributeError):
        return False
    return x <= cx <= x + w and y <= cy <= y + h


def select_at(elements: Iterable[Any], cx: float, cy: float) -> str | None:
    """Topmost element id at canvas point: drawings by segment distance,
    other types by bounding box. Returns None on empty space."""
    hit: str | None = None
    top_z = -1
    for element in elements:
        kind = element.type if hasattr(element, "type") else element.get("type")
        if kind == "drawing":
            matched = drawing_hit(element, cx, cy)
        else:
            matched = _bbox_contains(element, cx, cy)
        if not matched:
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
