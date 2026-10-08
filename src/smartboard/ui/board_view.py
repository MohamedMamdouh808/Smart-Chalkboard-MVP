"""Read-only board renderer: pure layout math + Qt paint view."""

from __future__ import annotations

from typing import Any

from . import theme
from .viewport import Viewport

# 002-era aliases (values now live in theme.py; kept for import compatibility).
NAMED_QCOLORS = theme.ELEMENT_COLORS
BACKGROUND = theme.WINDOW_BG
EQUATION_COLOR = theme.EQUATION
SELECTION_COLOR = theme.SELECTION
HIGHLIGHT_COLOR = theme.HIGHLIGHT


def aspect_scale(canvas_w: int, canvas_h: int, view_w: int, view_h: int) -> float:
    """Aspect-preserving scale factor (canvas -> view). Pure function."""
    if canvas_w <= 0 or canvas_h <= 0:
        return 1.0
    del canvas_w, canvas_h  # canvas is fixed; single source is Viewport
    return Viewport.from_sizes(view_w, view_h).scale


def layout_for_state(state: dict[str, Any], view_w: int, view_h: int) -> list[dict[str, Any]]:
    """Map board state to view rectangles. Read-only; never mutates input."""
    vp = Viewport.from_sizes(view_w, view_h)
    items = []
    for el in state.get("elements", []):
        sx, sy = vp.to_screen(el["x"], el["y"])
        items.append(
            {
                "id": el["id"],
                "type": el["type"],
                "rect": (sx, sy, el["width"] * vp.scale, el["height"] * vp.scale),
                "selected": el["id"] == state.get("selected_element_id"),
            }
        )
    return items


def resolve_color(value: str) -> str:
    """Map palette name or hex to a hex string Qt understands."""
    if not isinstance(value, str):
        return theme.DEFAULT_ELEMENT_COLOR
    if value.startswith("#"):
        return value
    return NAMED_QCOLORS.get(value, theme.DEFAULT_ELEMENT_COLOR)


try:
    from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
    from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
    from PyQt6.QtWidgets import QWidget

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False


class BoardView(QWidget if _QT else object):  # type: ignore[valid-type,misc]
    """Canvas widget. Renders `Board.to_dict()` snapshots only — never mutates."""

    if _QT:
        StrokeFinished = pyqtSignal(list)
        SelectionChanged = pyqtSignal(object)

    MODES = ("pen", "select")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not _QT:  # pragma: no cover
            raise RuntimeError("PyQt6 is required for the board view.")
        super().__init__(*args, **kwargs)
        self._state: dict[str, Any] = {
            "canvas": {"width": 1920, "height": 1080},
            "elements": [],
            "selected_element_id": None,
        }
        self._highlight_id: str | None = None
        self._mode = "select"
        self._active: tuple | None = None
        self._live: list[dict[str, Any]] = []
        self._press_at: tuple[float, float] | None = None
        self.live_width = 4
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)

    # -- input mode ---------------------------------------------------------
    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        if mode not in self.MODES:
            raise ValueError(f"unknown board mode: {mode}")
        self._mode = mode
        self._active = None
        self._live = []

    def render_state(self, state: dict[str, Any], highlight_id: str | None = None) -> None:
        self._state = state
        self._highlight_id = highlight_id
        self.update()

    def viewport(self) -> Any:
        """The live viewport for the current widget size (single source)."""
        return Viewport.from_sizes(max(self.width(), 1), max(self.height(), 1))

    def surface_rect(self) -> Any:
        """Canvas rect in screen pixels (for tests and hit-adjacent math)."""
        vp = self.viewport()
        sx, sy = vp.to_screen(0, 0)
        return QRectF(sx, sy, 1920 * vp.scale, 1080 * vp.scale)

    def letterbox_color(self) -> str:
        return theme.WINDOW_BG

    def paintEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(theme.WINDOW_BG))
        vp = self.viewport()
        rect = self.surface_rect()
        # Soft shadow: expanding translucent rounded rects (device space).
        painter.setPen(Qt.PenStyle.NoPen)
        for expand, alpha in ((16, 36), (10, 60), (5, 100)):
            shadow = QColor(theme.BOARD_SHADOW)
            shadow.setAlpha(alpha)
            painter.setBrush(shadow)
            painter.drawRoundedRect(
                rect.adjusted(-expand, -expand, expand, expand),
                theme.BOARD_RADIUS + expand, theme.BOARD_RADIUS + expand)
        # Canvas space: surface fill, clipped elements, border, adornments.
        painter.save()
        painter.translate(vp.ox, vp.oy)
        painter.scale(vp.scale, vp.scale)
        path = QPainterPath()
        path.addRoundedRect(
            QRectF(0, 0, 1920, 1080), theme.BOARD_RADIUS, theme.BOARD_RADIUS)
        painter.fillPath(path, QColor(theme.BOARD_SURFACE))
        painter.setClipPath(path)
        for el in self._state.get("elements", []):
            self._paint_element(painter, el, vp.scale)
        border = QPen(QColor(theme.BOARD_BORDER))
        border.setWidth(2)
        painter.setPen(border)
        # NOTE: the border is stroked as filled rects, not drawPath: path
        # stroking after translucent shadow fills corrupts interior pixels
        # on some rasterizers (see tests/ui/test_board_surface.py).
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(theme.BOARD_BORDER))
        painter.drawRect(QRectF(-1, -1, 1922, 2))
        painter.drawRect(QRectF(-1, 1079, 1922, 2))
        painter.drawRect(QRectF(-1, 1, 2, 1078))
        painter.drawRect(QRectF(1919, 1, 2, 1078))
        self._paint_adornments(painter, vp.scale)
        self._paint_live(painter)
        painter.restore()
        painter.end()

    # -- unified pointer input (pen / mouse / touch, one active pointer) -----
    def _canvas_pos(self, sx: float, sy: float) -> tuple[float, float] | None:
        vp = self.viewport()
        cx, cy = vp.to_canvas(sx, sy)
        if 0 <= cx <= 1920 and 0 <= cy <= 1080:
            return (cx, cy)
        return None

    @staticmethod
    def _pressure_of(event: Any) -> float | None:
        try:
            pressure = float(event.pressure())
        except (AttributeError, TypeError, ValueError):
            return None
        return pressure if pressure >= 0 else None

    def _press(self, key: tuple, sx: float, sy: float, pressure: float | None) -> bool:
        """Begin a press. Returns True when this press owns the pointer."""
        if self._active is not None:
            return False  # one active pointer: ignore further contacts
        pos = self._canvas_pos(sx, sy)
        if pos is None:
            return False  # strokes starting outside the board are ignored
        self._active = key
        self._press_at = (sx, sy)
        if self._mode == "pen":
            point: dict[str, Any] = {"x": pos[0], "y": pos[1]}
            if pressure is not None:
                point["pressure"] = pressure
            self._live = [point]
            self.update()
        return True

    def _sample(self, key: tuple, sx: float, sy: float, pressure: float | None) -> None:
        if self._active != key or self._mode != "pen":
            return
        vp = self.viewport()
        cx, cy = vp.to_canvas(sx, sy)
        cx = min(max(cx, 0.0), 1920.0)  # clip stray points to the canvas edge
        cy = min(max(cy, 0.0), 1080.0)
        point: dict[str, Any] = {"x": cx, "y": cy}
        if pressure is not None:
            point["pressure"] = pressure
        self._live.append(point)
        self.update()

    def _release(self, key: tuple, sx: float, sy: float) -> None:
        if self._active != key:
            return
        self._active = None
        if self._mode == "pen":
            finished, self._live = self._live, []
            self.update()
            if finished:
                self.StrokeFinished.emit(finished)
        else:
            start = self._press_at
            self._press_at = None
            if start is not None and abs(sx - start[0]) < 8 and abs(sy - start[1]) < 8:
                self._click_select(sx, sy)

    def _click_select(self, sx: float, sy: float) -> None:
        from smartboard.core.hit_test import select_at

        vp = self.viewport()
        cx, cy = vp.to_canvas(sx, sy)
        element_id = select_at(self._state.get("elements", []), cx, cy)
        self._state["selected_element_id"] = element_id
        self.SelectionChanged.emit(element_id)
        self.update()

    def tabletEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        kind = event.type()
        pos = event.position()
        pressure = self._pressure_of(event)
        type_name = kind.name if hasattr(kind, "name") else str(kind)
        if "Press" in type_name:
            self._press(("tablet",), float(pos.x()), float(pos.y()), pressure)
        elif "Move" in type_name:
            self._sample(("tablet",), float(pos.x()), float(pos.y()), pressure)
        elif "Release" in type_name:
            self._release(("tablet",), float(pos.x()), float(pos.y()))

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        from PyQt6.QtCore import Qt as _Qt

        if event.button() == _Qt.MouseButton.LeftButton:
            pos = event.position()
            self._press(("mouse",), float(pos.x()), float(pos.y()), None)

    def mouseMoveEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        pos = event.position()
        self._sample(("mouse",), float(pos.x()), float(pos.y()), None)

    def mouseReleaseEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        from PyQt6.QtCore import Qt as _Qt

        if event.button() == _Qt.MouseButton.LeftButton:
            pos = event.position()
            self._release(("mouse",), float(pos.x()), float(pos.y()))

    def touchEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        for point in event.points():
            pos = point.position()
            key = ("touch", point.id())
            state = point.state().name if hasattr(point.state(), "name") else str(point.state())
            if "Pressed" in state:
                self._press(key, float(pos.x()), float(pos.y()), None)
            elif "Updated" in state:
                self._sample(key, float(pos.x()), float(pos.y()), None)
            elif "Released" in state:
                self._release(key, float(pos.x()), float(pos.y()))

    def event(self, event: Any) -> bool:
        from PyQt6.QtCore import QEvent as _QEvent

        if event.type() in (_QEvent.Type.TouchBegin, _QEvent.Type.TouchUpdate,
                            _QEvent.Type.TouchEnd):
            self.touchEvent(event)
            return True
        if event.type() in (_QEvent.Type.TabletPress, _QEvent.Type.TabletMove,
                            _QEvent.Type.TabletRelease):
            self.tabletEvent(event)
            return True
        return super().event(event)

    def _paint_adornments(self, painter: Any, scale: float) -> None:
        selected = self._state.get("selected_element_id")
        for el in self._state.get("elements", []):
            if el["id"] == selected:
                pen = QPen(QColor(theme.SELECTION))
                pen.setWidth(max(2, int(3 / max(scale, 0.01))))
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(el["x"], el["y"], el["width"], el["height"])
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(theme.SELECTION))
                half = theme.HANDLE_SIZE / 2
                for hx, hy in ((el["x"], el["y"]),
                               (el["x"] + el["width"], el["y"]),
                               (el["x"], el["y"] + el["height"]),
                               (el["x"] + el["width"], el["y"] + el["height"])):
                    painter.drawRect(
                        QRectF(hx - half, hy - half, theme.HANDLE_SIZE, theme.HANDLE_SIZE))
            if el["id"] == self._highlight_id:
                pen = QPen(QColor(theme.HIGHLIGHT))
                pen.setWidth(max(3, int(6 / max(scale, 0.01))))
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(el["x"] - 8, el["y"] - 8, el["width"] + 16, el["height"] + 16)

    def _paint_element(self, painter: Any, el: dict[str, Any], scale: float) -> None:
        kind = el.get("type", "text")
        color = QColor(resolve_color(el.get("color", theme.DEFAULT_ELEMENT_COLOR)))
        if kind in ("heading", "text"):
            from smartboard.app.text_fit import font_for as _font_for

            equation = bool(el.get("equation_style"))
            font = _font_for(kind, equation)
            if equation:
                font.setItalic(True)
                painter.setPen(QPen(QColor(EQUATION_COLOR)))
            else:
                painter.setPen(QPen(color))
            painter.setFont(font)
            # Wrap inside the fixed element box (box/coordinates never change).
            flags = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) | int(
                Qt.TextFlag.TextWordWrap)
            painter.drawText(el["x"], el["y"], el["width"], el["height"], flags,
                             str(el.get("text", "")))
        elif kind == "shape":
            pen = QPen(color)
            pen.setWidth(max(2, int(4 / max(scale, 0.01))))
            painter.setPen(pen)
            self._paint_shape(painter, el)
        elif kind == "drawing":
            self._paint_drawing(painter, el, scale)
        # Selection outline, corner handles, and highlight ring are painted
        # centrally in _paint_adornments (after all elements).

    def _paint_drawing(self, painter: Any, el: dict[str, Any], scale: float) -> None:
        """Committed drawing in z-order: QPainterPath, round caps, pressure widths."""
        base = QColor(resolve_color(el.get("color", theme.DEFAULT_ELEMENT_COLOR)))
        for stroke in el.get("strokes", []):
            if isinstance(stroke, dict):
                points = stroke.get("points", [])
                width = float(stroke.get("width", el.get("width", 4)))
                tint = stroke.get("color")
                color = QColor(resolve_color(tint)) if tint else base
            else:  # legacy point-list shape
                points = stroke
                width = float(el.get("width", 4))
                color = base
            pts = [(float(p.get("x", 0)), float(p.get("y", 0)),
                    p.get("pressure")) for p in points if "x" in p and "y" in p]
            if not pts:
                continue
            if all(pressure is None for _, _, pressure in pts):
                path = QPainterPath()
                path.moveTo(pts[0][0], pts[0][1])
                for x, y, _ in pts[1:]:
                    path.lineTo(x, y)
                pen = QPen(color)
                pen.setWidthF(max(1.0, width))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawPath(path)
            else:
                # Pressure-based width per segment; round caps throughout.
                for (ax, ay, ap), (bx, by, bp) in zip(pts, pts[1:]):
                    pressure = ((ap or 0.5) + (bp or 0.5)) / 2
                    pen = QPen(color)
                    pen.setWidthF(max(1.0, width * (0.4 + pressure)))
                    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                    painter.setPen(pen)
                    painter.drawLine(QPointF(ax, ay), QPointF(bx, by))
                dot = QPen(color)
                dot.setWidthF(max(1.0, width * (0.4 + (pts[0][2] or 0.5))))
                dot.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(dot)
                painter.drawPoint(QPointF(pts[0][0], pts[0][1]))

    def _paint_live(self, painter: Any) -> None:
        """Temporary overlay for the in-progress stroke (never stored)."""
        if not self._live:
            return
        color = QColor(resolve_color(self._live_color()))
        pts = [QPointF(float(p["x"]), float(p["y"])) for p in self._live]
        path = QPainterPath()
        path.moveTo(pts[0])
        for point in pts[1:]:
            path.lineTo(point)
        pen = QPen(color)
        pen.setWidthF(max(1.0, float(self.live_width)))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def _live_color(self) -> str:
        return theme.DEFAULT_ELEMENT_COLOR

    def _paint_shape(self, painter: Any, el: dict[str, Any]) -> None:
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
            painter.drawPolygon(QPolygonF([QPointF(x + w / 2, y), QPointF(x + w, y + h), QPointF(x, y + h)]))
        else:
            painter.drawRect(x, y, w, h)
