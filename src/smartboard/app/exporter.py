"""Lesson export — content-bounds PNG at 100% (Qt required, read-only)."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from smartboard.ui.board_paint import element_world_rect, paint_elements
from smartboard.ui.theme import WINDOW_BG

EMPTY_EXPORT_SIZE = (960, 540)
EXPORT_MARGIN = 48


def content_bounds(state: dict[str, Any]) -> tuple[float, float, float, float] | None:
    """Union of canonical world bounds for all elements, or None when empty."""
    boxes = [element_world_rect(el) for el in state.get("elements", [])]
    if not boxes:
        return None
    x0 = min(box[0] for box in boxes)
    y0 = min(box[1] for box in boxes)
    x1 = max(box[0] + box[2] for box in boxes)
    y1 = max(box[1] + box[3] for box in boxes)
    return (x0, y0, x1 - x0, y1 - y0)


def export_png(
    state: dict[str, Any], path: str | Path, width: int | None = None, height: int | None = None
) -> Path:
    """Export all content bounds plus a fixed margin, rendered at 100%.

    Read-only: never mutates board state or history. Empty lessons produce a
    valid fixed-size image.
    """
    try:
        from PyQt6.QtGui import QColor, QImage, QPainter
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyQt6 is required for PNG export.") from exc
    bounds = content_bounds(state)
    if bounds is None:
        width, height = EMPTY_EXPORT_SIZE
        ox, oy = 0.0, 0.0
    else:
        x0, y0, bw, bh = bounds
        width = math.ceil(bw) + 2 * EXPORT_MARGIN
        height = math.ceil(bh) + 2 * EXPORT_MARGIN
        ox, oy = -x0 + EXPORT_MARGIN, -y0 + EXPORT_MARGIN
    if width <= 0 or height <= 0:
        raise RuntimeError("Could not determine export dimensions.")
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(WINDOW_BG))
    painter = QPainter(image)
    try:
        painter.translate(ox, oy)
        paint_elements(painter, state.get("elements", []), 1.0)
    finally:
        painter.end()
    out = Path(path)
    if image.isNull() or not image.save(str(out), "PNG"):
        raise RuntimeError(f"Could not write export to {out}")
    return out
