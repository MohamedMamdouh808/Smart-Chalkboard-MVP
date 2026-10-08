"""Qt-independent direct-manipulation geometry for drag and resize gestures."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .board import MIN_SIZE
from .validators import within_world_limits

PRESS_DRAG_THRESHOLD = 4.0
CORNERS: tuple[str, ...] = ("nw", "ne", "sw", "se")
FIXED_CORNERS: dict[str, str] = {"nw": "se", "ne": "sw", "sw": "ne", "se": "nw"}
ASPECT_LOCKED_TYPES: tuple[str, ...] = ("drawing", "shape", "equation")
_X_SIGN: dict[str, int] = {"nw": -1, "ne": 1, "sw": -1, "se": 1}
_Y_SIGN: dict[str, int] = {"nw": -1, "ne": -1, "sw": 1, "se": 1}


def _quantize(value: float) -> int:
    """Round a world coordinate to the nearest integer world unit."""
    return round(float(value))


def drag_candidate(
    original: Mapping[str, Any], start: tuple[float, float], current: tuple[float, float]
) -> dict[str, Any]:
    """Unclamped integer translation preserving the press grab offset.

    The input mapping is never mutated. Callers use the returned rectangle
    for a non-mutating preview and, on release, for one move operation.
    Numeric sanity limits are enforced by engine validation, not previews.
    """
    origin_x = float(original["x"])
    origin_y = float(original["y"])
    width = int(original["width"])
    height = int(original["height"])
    dx = float(current[0]) - float(start[0])
    dy = float(current[1]) - float(start[1])
    x = _quantize(origin_x + dx)
    y = _quantize(origin_y + dy)
    return {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "dx": dx,
        "dy": dy,
        "moved": (dx * dx + dy * dy) >= PRESS_DRAG_THRESHOLD * PRESS_DRAG_THRESHOLD,
    }


def resize_candidate(
    original: Mapping[str, Any],
    active_corner: str,
    start: tuple[float, float],
    current: tuple[float, float],
    preserve_aspect: bool,
) -> dict[str, Any]:
    """Unclamped integer resize anchored at the opposite fixed corner.

    The input mapping is never mutated. Callers use the returned rectangle
    for a non-mutating preview and, on release, for one resize operation.
    Candidates outside finite numeric sanity limits are invalid.
    """
    if active_corner not in CORNERS:
        raise ValueError(f"unknown resize corner: {active_corner}")
    origin_x = float(original["x"])
    origin_y = float(original["y"])
    original_width = float(original["width"])
    original_height = float(original["height"])
    if original_width <= 0 or original_height <= 0:
        return {"valid": False, "moved": False}
    fixed_x = origin_x if _X_SIGN[active_corner] > 0 else origin_x + original_width
    fixed_y = origin_y if _Y_SIGN[active_corner] > 0 else origin_y + original_height
    pointer_x, pointer_y = float(current[0]), float(current[1])
    if _X_SIGN[active_corner] > 0:
        raw_width = max(pointer_x - fixed_x, 0.0)
    else:
        raw_width = max(fixed_x - pointer_x, 0.0)
    if _Y_SIGN[active_corner] > 0:
        raw_height = max(pointer_y - fixed_y, 0.0)
    else:
        raw_height = max(fixed_y - pointer_y, 0.0)
    if preserve_aspect:
        raw_scale = max(raw_width / original_width, raw_height / original_height)
        min_scale = max(MIN_SIZE / original_width, MIN_SIZE / original_height)
        scale = max(raw_scale, min_scale)
        width = max(_quantize(original_width * scale), MIN_SIZE)
        height = max(_quantize(original_height * scale), MIN_SIZE)
    else:
        width = max(_quantize(raw_width), MIN_SIZE)
        height = max(_quantize(raw_height), MIN_SIZE)
    x = int(fixed_x - width) if _X_SIGN[active_corner] < 0 else int(fixed_x)
    y = int(fixed_y - height) if _Y_SIGN[active_corner] < 0 else int(fixed_y)
    if not within_world_limits(x, y, width, height):
        return {"valid": False, "moved": False}
    dx = float(start[0]) - float(current[0])
    dy = float(start[1]) - float(current[1])
    return {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "fixed_corner": FIXED_CORNERS[active_corner],
        "fixed_x": int(fixed_x),
        "fixed_y": int(fixed_y),
        "valid": True,
        "moved": (dx * dx + dy * dy) >= PRESS_DRAG_THRESHOLD * PRESS_DRAG_THRESHOLD,
    }


def resize_preview_points(
    points: list[list[dict[str, Any]]],
    original: Mapping[str, Any],
    candidate: Mapping[str, Any],
    fixed_corner: str,
) -> list[list[dict[str, Any]]]:
    """Return a transformed copy of drawing points for a resize preview.

    Stored stroke widths are intentionally untouched; only coordinates move.
    Points scale about the raw point extremum for the fixed corner so the
    expanded-bounds fixed corner is preserved in exact arithmetic.
    """
    from .board import drawing_fixed_anchor

    original_width = float(original["width"])
    original_height = float(original["height"])
    if original_width <= 0 or original_height <= 0:
        return deepcopy(points)
    anchor = drawing_fixed_anchor(points, fixed_corner)
    x_scale = float(candidate["width"]) / original_width
    y_scale = float(candidate["height"]) / original_height
    moved: list[list[dict[str, Any]]] = []
    for stroke in points:
        moved_stroke: list[dict[str, Any]] = []
        for point in stroke:
            transformed = dict(point)
            transformed["x"] = anchor[0] + (float(point["x"]) - anchor[0]) * x_scale
            transformed["y"] = anchor[1] + (float(point["y"]) - anchor[1]) * y_scale
            moved_stroke.append(transformed)
        moved.append(moved_stroke)
    return moved
