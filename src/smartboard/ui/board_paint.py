"""Read-only world-space element painting shared by the board view and export."""

from __future__ import annotations

import itertools
from typing import Any

from smartboard.core.board import drawing_bounds_for_element
from smartboard.ui import theme


def element_world_rect(el: dict[str, Any]) -> tuple[float, float, float, float]:
    """Canonical world rectangle for any element mapping."""
    if el.get("type") == "drawing":
        x, y, w, h = drawing_bounds_for_element(el)
        return (float(x), float(y), float(w), float(h))
    return (
        float(el.get("x", 0)),
        float(el.get("y", 0)),
        float(el.get("width", 0)),
        float(el.get("height", 0)),
    )


def intersects(
    rect: tuple[float, float, float, float], other: tuple[float, float, float, float]
) -> bool:
    """True when two world rectangles overlap (edges count as intersecting)."""
    ax, ay, aw, ah = rect
    bx, by, bw, bh = other
    return ax <= bx + bw and bx <= ax + aw and ay <= by + bh and by <= ay + ah


def visible_elements(
    elements: list[dict[str, Any]], visible: tuple[float, float, float, float]
) -> list[dict[str, Any]]:
    """Elements whose world bounds intersect the visible rectangle, in order."""
    return [el for el in elements if intersects(element_world_rect(el), visible)]


def resolve_color(value: Any) -> str:
    """Map palette name or hex to a hex string Qt understands."""
    if not isinstance(value, str):
        return theme.DEFAULT_ELEMENT_COLOR
    if value.startswith("#"):
        return value
    return theme.ELEMENT_COLORS.get(value, theme.DEFAULT_ELEMENT_COLOR)


def paint_elements(painter: Any, elements: list[dict[str, Any]], zoom: float) -> None:
    """Paint content elements in world coordinates (caller sets the transform).

    Read-only: never mutates elements. Shape stroke widths are scaled by the
    inverse zoom so they remain constant on screen.
    """
    from PyQt6.QtCore import QPointF, Qt
    from PyQt6.QtGui import QColor, QPainterPath, QPen, QPolygonF

    safe_zoom = zoom if isinstance(zoom, (int, float)) and zoom > 0 else 1.0
    for el in elements:
        kind = el.get("type", "text")
        color = QColor(resolve_color(el.get("color", theme.DEFAULT_ELEMENT_COLOR)))
        if kind in ("heading", "text"):
            from smartboard.app.text_fit import font_for as _font_for

            equation = bool(el.get("equation_style"))
            font = _font_for(kind, equation)
            if equation:
                font.setItalic(True)
                painter.setPen(QPen(QColor(theme.EQUATION)))
            else:
                painter.setPen(QPen(color))
            painter.setFont(font)
            flags = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) | int(
                Qt.TextFlag.TextWordWrap
            )
            painter.drawText(
                el["x"], el["y"], el["width"], el["height"], flags, str(el.get("text", ""))
            )
        elif kind == "shape":
            pen = QPen(color)
            pen.setWidthF(max(1.0, 4.0 / safe_zoom))
            painter.setPen(pen)
            x, y, w, h = el["x"], el["y"], el["width"], el["height"]
            shape = el.get("shape_type", "rectangle")
            if shape == "circle":
                painter.drawEllipse(x, y, w, h)
            elif shape == "line":
                painter.drawLine(x, y, x + w, y + h)
            elif shape == "arrow":
                painter.drawLine(x, y, x + w, y + h)
                painter.drawLine(x + w, y + h, x + w - 24, y + h)
                painter.drawLine(x + w, y + h, x + w, y + h - 24)
            elif shape == "triangle":
                painter.drawPolygon(
                    QPolygonF([QPointF(x + w / 2, y), QPointF(x + w, y + h), QPointF(x, y + h)])
                )
            else:
                painter.drawRect(x, y, w, h)
        elif kind == "drawing":
            base = color
            for stroke in el.get("strokes", []):
                if isinstance(stroke, dict):
                    points = stroke.get("points", [])
                    width = float(stroke.get("width", el.get("width", 4)))
                    tint = stroke.get("color")
                    stroke_color = QColor(resolve_color(tint)) if tint else base
                else:  # legacy point-list shape
                    points = stroke
                    width = float(el.get("width", 4))
                    stroke_color = base
                pts = [
                    (float(p.get("x", 0)), float(p.get("y", 0)), p.get("pressure"))
                    for p in points
                    if "x" in p and "y" in p
                ]
                if not pts:
                    continue
                if all(pressure is None for _, _, pressure in pts):
                    path = QPainterPath()
                    path.moveTo(pts[0][0], pts[0][1])
                    for x, y, _ in pts[1:]:
                        path.lineTo(x, y)
                    pen = QPen(stroke_color)
                    pen.setWidthF(max(1.0, width))
                    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                    painter.setPen(pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawPath(path)
                else:
                    for (ax, ay, ap), (bx, by, bp) in itertools.pairwise(pts):
                        pressure = ((ap or 0.5) + (bp or 0.5)) / 2
                        pen = QPen(stroke_color)
                        pen.setWidthF(max(1.0, width * (0.4 + pressure)))
                        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                        painter.setPen(pen)
                        painter.drawLine(QPointF(ax, ay), QPointF(bx, by))
                    dot = QPen(stroke_color)
                    dot.setWidthF(max(1.0, width * (0.4 + (pts[0][2] or 0.5))))
                    dot.setCapStyle(Qt.PenCapStyle.RoundCap)
                    painter.setPen(dot)
                    painter.drawPoint(QPointF(pts[0][0], pts[0][1]))
