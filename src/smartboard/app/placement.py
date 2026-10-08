"""Deterministic visible-viewport default placement (application layer)."""

from __future__ import annotations

from typing import Any

DEFAULT_SIZES: dict[str, tuple[int, int]] = {
    "heading": (800, 96),
    "text": (600, 120),
    "equation": (320, 80),
    "shape": (200, 200),
}

PLACEMENT_MARGIN = 48.0
PLACEMENT_GAP = 24.0


def default_size_for(kind: str, params: dict[str, Any]) -> tuple[int, int]:
    """Default world size for a creation kind (mirrors engine creation defaults)."""
    if kind == "text" and params.get("equation_style"):
        return DEFAULT_SIZES["equation"]
    if kind in DEFAULT_SIZES:
        return DEFAULT_SIZES[kind]
    size = params.get("size", {})
    try:
        return (int(size.get("w", 200)), int(size.get("h", 200)))
    except (TypeError, ValueError):
        return DEFAULT_SIZES["shape"]


def _intersects(candidate: tuple[float, float, int, int], element: dict[str, Any]) -> bool:
    cx, cy, cw, ch = candidate
    try:
        ex, ey = float(element["x"]), float(element["y"])
        ew, eh = float(element["width"]), float(element["height"])
    except (KeyError, TypeError, ValueError):
        return False
    return cx < ex + ew and ex < cx + cw and cy < ey + eh and ey < cy + ch


def find_placement(
    kind: str,
    params: dict[str, Any],
    viewport: tuple[float, float, float, float],
    elements: list[dict[str, Any]],
) -> tuple[int, int]:
    """Deterministic visible-area position: top-left margin, then below content.

    Scans visible elements in (y, x) order and moves the candidate below the
    first intersecting element. Falls below the lowest visible element when
    the viewport is full.
    """
    vx, vy, _, _ = viewport
    width, height = default_size_for(kind, params)
    candidate: tuple[float, float, int, int] = (
        vx + PLACEMENT_MARGIN,
        vy + PLACEMENT_MARGIN,
        width,
        height,
    )
    ordered = sorted(elements, key=lambda el: (float(el.get("y", 0.0)), float(el.get("x", 0.0))))
    for element in ordered:
        if _intersects(candidate, element):
            try:
                bottom = float(element["y"]) + float(element["height"])
            except (KeyError, TypeError, ValueError):
                continue
            candidate = (candidate[0], bottom + PLACEMENT_GAP, width, height)
    return (round(candidate[0]), round(candidate[1]))
