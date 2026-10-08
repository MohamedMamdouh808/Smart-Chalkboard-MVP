"""Infinite board canvas: renders world snapshots through an app-owned camera."""

from __future__ import annotations

import copy
import math
from datetime import UTC, datetime
from typing import Any

from smartboard.app.camera import (
    CameraState,
    default_camera,
    normalize_camera,
    pan_by_screen,
    zoom_about_cursor,
)
from smartboard.core.board import drawing_bounds_for_element

from . import theme
from .board_paint import element_world_rect, paint_elements, resolve_color, visible_elements
from .camera_transform import CameraTransform

# 002-era aliases (values now live in theme.py; kept for import compatibility).
NAMED_QCOLORS = theme.ELEMENT_COLORS
BACKGROUND = theme.WINDOW_BG
EQUATION_COLOR = theme.EQUATION
SELECTION_COLOR = theme.SELECTION
HIGHLIGHT_COLOR = theme.HIGHLIGHT

GRID_BASE_WORLD = 32.0
GRID_MIN_SCREEN = 48.0
GRID_MAX_SCREEN = 96.0
GRID_DOT_RADIUS = 1.5
HIT_TOLERANCE_SCREEN = 6.0
WHEEL_ZOOM_BASE = 1.2


def grid_spacing_for_zoom(zoom: float) -> float:
    """Power-of-two world spacing keeping on-screen dot pitch in a fixed band."""
    safe_zoom = zoom if isinstance(zoom, (int, float)) and zoom > 0 else 1.0
    target = (GRID_MIN_SCREEN + GRID_MAX_SCREEN) / 2.0
    steps = round(math.log2(target / (GRID_BASE_WORLD * safe_zoom)))
    return GRID_BASE_WORLD * (2.0**steps)


try:
    from PyQt6.QtCore import QPointF, Qt, pyqtSignal
    from PyQt6.QtGui import QColor, QPainter, QPen
    from PyQt6.QtWidgets import QWidget

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False


class BoardView(QWidget if _QT else object):  # type: ignore[misc]
    """Edgeless canvas widget. Renders snapshots; never mutates board state."""

    if _QT:
        StrokeFinished = pyqtSignal(list)
        SelectionChanged = pyqtSignal(object)
        GestureFinished = pyqtSignal(dict)
        CameraChanged = pyqtSignal(object)
        ViewSizeChanged = pyqtSignal(int, int)
        InlineEditRequested = pyqtSignal(dict)

    MODES = ("pen", "select")
    GESTURE_STATES = ("idle", "dragging", "resizing")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not _QT:  # pragma: no cover
            raise RuntimeError("PyQt6 is required for the board view.")
        super().__init__(*args, **kwargs)
        self._state: dict[str, Any] = {
            "elements": [],
            "selected_element_id": None,
        }
        self._highlight_id: str | None = None
        self._mode = "select"
        self._camera: CameraState = default_camera()
        self._active: tuple[Any, ...] | None = None
        self._live: list[dict[str, Any]] = []
        self._press_at: tuple[float, float] | None = None
        self._gesture_state: str = "idle"
        self._press_candidate: dict[str, Any] | None = None
        self._gesture_preview: dict[str, Any] | None = None
        self._space_held = False
        self._pan_pointer: tuple[Any, ...] | None = None
        self._pan_camera: CameraState | None = None
        self._pinch_last_total: float | None = None
        self.live_width = 4
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        try:
            self.grabGesture(Qt.GestureType.PinchGesture)
        except (AttributeError, RuntimeError):  # pragma: no cover - platform variance
            pass

    # -- camera ---------------------------------------------------------------
    def camera_state(self) -> CameraState:
        return normalize_camera(self._camera.pan_x, self._camera.pan_y, self._camera.zoom)

    def set_camera(self, camera: CameraState) -> None:
        """Apply the authoritative application camera (render/input copy)."""
        self._camera = normalize_camera(camera.pan_x, camera.pan_y, camera.zoom)
        self.update()

    def transform(self) -> CameraTransform:
        return CameraTransform.from_camera(
            self._camera, max(self.width(), 1), max(self.height(), 1)
        )

    def visible_world_rect(self) -> tuple[float, float, float, float]:
        return self.transform().visible_rect()

    def _apply_camera(self, camera: CameraState) -> None:
        self._camera = normalize_camera(camera.pan_x, camera.pan_y, camera.zoom)
        self.CameraChanged.emit(self.camera_state())
        self.update()

    def pan_by_screen(self, dx: float, dy: float) -> CameraState:
        camera = pan_by_screen(self._camera, dx, dy)
        self._apply_camera(camera)
        return self.camera_state()

    def zoom_about(self, sx: float, sy: float, factor: float) -> CameraState:
        camera = zoom_about_cursor(self._camera, sx, sy, factor)
        self._apply_camera(camera)
        return self.camera_state()

    def handle_pinch(self, center_x: float, center_y: float, scale_factor: float) -> CameraState:
        """Normalized pinch-zoom entry point (gesture and native events funnel here)."""
        return self.zoom_about(center_x, center_y, scale_factor)

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
        self.cancel_gesture()

    @property
    def gesture_state(self) -> str:
        return self._gesture_state

    @property
    def gesture_preview(self) -> dict[str, Any] | None:
        if self._gesture_preview is None:
            return None
        preview: dict[str, Any] | None = copy.deepcopy(self._gesture_preview)
        return preview

    def cancel_gesture(self) -> None:
        """Clear gesture state and previews without emitting board operations."""
        self._gesture_state = "idle"
        self._press_candidate = None
        self._gesture_preview = None
        self._press_at = None
        self._pan_pointer = None
        self._pan_camera = None
        self.update()

    def keyPressEvent(self, event: Any) -> None:
        from PyQt6.QtCore import Qt as _Qt

        if event.key() == _Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_held = True
            event.accept()
            return
        if event.key() == _Qt.Key.Key_Escape and (
            self._press_candidate is not None or self._gesture_state != "idle"
        ):
            self._active = None
            self.cancel_gesture()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: Any) -> None:
        from PyQt6.QtCore import Qt as _Qt

        if event.key() == _Qt.Key.Key_Space and not event.isAutoRepeat():
            self._space_held = False
            event.accept()
            return
        super().keyReleaseEvent(event)

    def render_state(
        self,
        state: dict[str, Any],
        highlight_id: str | None = None,
        camera: CameraState | None = None,
    ) -> None:
        self._state = state
        self._highlight_id = highlight_id
        if camera is not None:
            self._camera = normalize_camera(camera.pan_x, camera.pan_y, camera.zoom)
        self.update()

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        self.ViewSizeChanged.emit(max(self.width(), 1), max(self.height(), 1))

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        self.ViewSizeChanged.emit(max(self.width(), 1), max(self.height(), 1))

    def letterbox_color(self) -> str:
        return theme.WINDOW_BG

    def paintEvent(self, event: Any) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(theme.WINDOW_BG))
        camera = self.camera_state()
        visible = self.visible_world_rect()
        self._paint_grid(painter, camera, visible)
        painter.save()
        painter.translate(-camera.pan_x * camera.zoom, -camera.pan_y * camera.zoom)
        painter.scale(camera.zoom, camera.zoom)
        elements = self._state.get("elements", [])
        for el in visible_elements(elements, visible):
            if self._gesture_preview is not None and el.get("id") == self._gesture_preview.get(
                "id"
            ):
                continue
            paint_elements(painter, [el], camera.zoom)
        if isinstance(self._gesture_preview, dict):
            paint_elements(painter, [self._gesture_preview], camera.zoom)
        self._paint_live(painter)
        painter.restore()
        self._paint_adornments(painter, camera)
        painter.end()

    def _paint_grid(
        self, painter: Any, camera: CameraState, visible: tuple[float, float, float, float]
    ) -> None:
        spacing = grid_spacing_for_zoom(camera.zoom)
        vx, vy, vw, vh = visible
        if vw <= 0 or vh <= 0:
            return
        first_x = math.floor(vx / spacing) * spacing
        first_y = math.floor(vy / spacing) * spacing
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(theme.GRID_DOT))
        x = first_x
        while x <= vx + vw:
            sx = (x - camera.pan_x) * camera.zoom
            y = first_y
            while y <= vy + vh:
                sy = (y - camera.pan_y) * camera.zoom
                painter.drawEllipse(QPointF(sx, sy), GRID_DOT_RADIUS, GRID_DOT_RADIUS)
                y += spacing
            x += spacing

    # -- unified pointer input (pen / mouse / touch, one active pointer) -----
    def _world_pos(self, sx: float, sy: float) -> tuple[float, float]:
        return self.transform().to_world(sx, sy)

    @staticmethod
    def _pressure_of(event: Any) -> float | None:
        try:
            pressure = float(event.pressure())
        except (AttributeError, TypeError, ValueError):
            return None
        return pressure if pressure >= 0 else None

    def _hit_tolerance_world(self) -> float:
        return HIT_TOLERANCE_SCREEN / max(self._camera.zoom, 0.01)

    def _find_element(self, element_id: str | None) -> dict[str, Any] | None:
        if element_id is None:
            return None
        elements: list[dict[str, Any]] = self._state.get("elements", [])
        for element in elements:
            if element.get("id") == element_id:
                return element
        return None

    def _select_pressed(self, element_id: str | None) -> None:
        """Record press-time selection locally and notify the application."""
        self._state["selected_element_id"] = element_id
        self.SelectionChanged.emit(element_id)
        self.update()

    def _canonical_press_bounds(self, element: dict[str, Any]) -> dict[str, Any]:
        bounds = dict(element)
        if element.get("type") == "drawing":
            x, y, w, h = drawing_bounds_for_element(element)
            bounds.update({"x": x, "y": y, "width": w, "height": h})
        return bounds

    def _original_geometry(self, element: dict[str, Any]) -> dict[str, int]:
        """Canonical integer rectangle used for gesture previews and commits."""
        if element.get("type") == "drawing":
            x, y, w, h = drawing_bounds_for_element(element)
            return {"x": x, "y": y, "width": w, "height": h}
        return {
            "x": int(element.get("x", 0)),
            "y": int(element.get("y", 0)),
            "width": int(element.get("width", 0)),
            "height": int(element.get("height", 0)),
        }

    @staticmethod
    def _resize_preserves_aspect(element: dict[str, Any]) -> bool:
        """Aspect policy for headings, text, equations, shapes, and drawings."""
        kind = element.get("type")
        if kind in ("drawing", "shape"):
            return True
        if kind == "text":
            extra = element.get("extra")
            if isinstance(extra, dict) and "equation_style" in extra:
                return bool(extra.get("equation_style"))
            return bool(element.get("equation_style", False))
        return False

    @staticmethod
    def _cursor_for_corner(corner: str | None) -> Any:
        from PyQt6.QtCore import Qt as _Qt
        from PyQt6.QtGui import QCursor as _QCursor

        if corner in ("nw", "se"):
            return _QCursor(_Qt.CursorShape.SizeFDiagCursor)
        if corner in ("ne", "sw"):
            return _QCursor(_Qt.CursorShape.SizeBDiagCursor)
        return None

    def _update_hover_cursor(self, sx: float, sy: float) -> None:
        if self._mode != "select" or self._active is not None:
            return
        pos = self._world_pos(sx, sy)
        from smartboard.core.hit_test import handle_at

        selected = self._find_element(self._state.get("selected_element_id"))
        corner = None
        if selected is not None:
            corner = handle_at(
                self._canonical_press_bounds(selected),
                pos[0],
                pos[1],
                self._camera.zoom,
                theme.HANDLE_SIZE,
            )
        cursor = self._cursor_for_corner(corner)
        if cursor is None:
            self.unsetCursor()
        else:
            self.setCursor(cursor)

    def _begin_pan(self, key: tuple[Any, ...], sx: float, sy: float) -> None:
        self._pan_pointer = key
        self._pan_camera = self.camera_state()
        self._press_at = (sx, sy)

    def _update_pan(self, sx: float, sy: float) -> None:
        if self._pan_camera is None or self._press_at is None:
            return
        dx = self._press_at[0] - sx
        dy = self._press_at[1] - sy
        self._apply_camera(pan_by_screen(self._pan_camera, dx, dy))

    def _end_pan(self) -> None:
        self._pan_pointer = None
        self._pan_camera = None
        self._press_at = None

    def _press(self, key: tuple[Any, ...], sx: float, sy: float, pressure: float | None) -> bool:
        """Begin a press. Returns True when this press owns the pointer."""
        if self._active is not None:
            return False  # one active pointer: ignore further contacts
        if self._space_held or key[0] == "middle":
            self._active = key
            self._begin_pan(key, sx, sy)
            return True
        pos = self._world_pos(sx, sy)
        self._active = key
        self._press_at = (sx, sy)
        if self._mode == "pen":
            point: dict[str, Any] = {"x": pos[0], "y": pos[1]}
            if pressure is not None:
                point["pressure"] = pressure
            self._live = [point]
            self.update()
            return True
        self.setFocus()
        from smartboard.core.hit_test import handle_at, select_at

        selected = self._find_element(self._state.get("selected_element_id"))
        if selected is not None:
            corner = handle_at(
                self._canonical_press_bounds(selected),
                pos[0],
                pos[1],
                self._camera.zoom,
                theme.HANDLE_SIZE,
            )
            if corner is not None:
                self._press_candidate = {
                    "kind": "resize",
                    "target_id": selected.get("id"),
                    "corner": corner,
                    "start": pos,
                    "origin": self._original_geometry(selected),
                }
                return True
        target_id = select_at(
            self._state.get("elements", []), pos[0], pos[1], tolerance=self._hit_tolerance_world()
        )
        self._select_pressed(target_id)
        target = self._find_element(target_id)
        if target is None:
            # Select-mode empty-space press: potential pan (click clears selection).
            self._press_candidate = {"kind": "maybe-pan", "start": pos}
        else:
            self._press_candidate = {
                "kind": "drag",
                "target_id": target.get("id"),
                "start": pos,
                "origin": self._original_geometry(target),
            }
        return True

    def _translated_preview_points(
        self, element: dict[str, Any], dx: float, dy: float
    ) -> list[Any]:
        preview_strokes: list[Any] = []
        for stroke in element.get("strokes", []):
            if isinstance(stroke, dict) and isinstance(stroke.get("points"), list):
                points = []
                for point in stroke["points"]:
                    if "x" not in point or "y" not in point:
                        continue
                    moved = dict(point)
                    moved["x"] = float(point["x"]) + dx
                    moved["y"] = float(point["y"]) + dy
                    points.append(moved)
                moved_stroke = dict(stroke)
                moved_stroke["points"] = points
                preview_strokes.append(moved_stroke)
            else:
                preview_strokes.append(copy.deepcopy(stroke))
        return preview_strokes

    def _sample(self, key: tuple[Any, ...], sx: float, sy: float, pressure: float | None) -> None:
        if self._active != key:
            return
        if self._pan_pointer == key:
            self._update_pan(sx, sy)
            return
        pos = self._world_pos(sx, sy)
        if self._mode == "pen":
            point: dict[str, Any] = {"x": pos[0], "y": pos[1]}
            if pressure is not None:
                point["pressure"] = pressure
            self._live.append(point)
            self.update()
            return
        candidate = self._press_candidate
        if candidate is None:
            return
        if candidate.get("kind") == "maybe-pan":
            if self._press_at is None:
                return
            moved_px = math.hypot(sx - self._press_at[0], sy - self._press_at[1])
            if moved_px >= 4.0:
                candidate["kind"] = "pan"
                self._pan_pointer = key
                self._pan_camera = self.camera_state()
                self._update_pan(sx, sy)
            return
        if candidate.get("kind") == "pan":
            self._update_pan(sx, sy)
            return
        if candidate.get("kind") not in ("drag", "resize"):
            return
        original = self._find_element(candidate.get("target_id"))
        if original is None:
            self.cancel_gesture()
            return
        if candidate.get("kind") == "drag":
            from smartboard.core.gesture import drag_candidate

            geometry = drag_candidate(candidate["origin"], candidate["start"], pos)
            if not geometry["moved"]:
                self._gesture_state = "idle"
                self._gesture_preview = None
                self.update()
                return
            preview = dict(original)
            preview.update(
                {
                    "x": geometry["x"],
                    "y": geometry["y"],
                    "width": geometry["width"],
                    "height": geometry["height"],
                }
            )
            if preview.get("type") == "drawing":
                preview["strokes"] = self._translated_preview_points(
                    original, float(geometry["dx"]), float(geometry["dy"])
                )
            self._gesture_state = "dragging"
            self._gesture_preview = preview
            self.update()
            return
        from smartboard.core.gesture import resize_candidate, resize_preview_points

        geometry = resize_candidate(
            candidate["origin"],
            str(candidate.get("corner")),
            candidate["start"],
            pos,
            self._resize_preserves_aspect(original),
        )
        if not geometry.get("valid", False) or not geometry.get("moved", False):
            self._gesture_state = "idle"
            self._gesture_preview = None
            self.update()
            return
        preview = dict(original)
        preview.update(
            {
                "x": geometry["x"],
                "y": geometry["y"],
                "width": geometry["width"],
                "height": geometry["height"],
            }
        )
        if preview.get("type") == "drawing":
            from smartboard.core.board import _drawing_point_lists
            from smartboard.core.gesture import FIXED_CORNERS

            fixed_corner = FIXED_CORNERS[str(candidate.get("corner"))]
            transformed = resize_preview_points(
                _drawing_point_lists(original), candidate["origin"], geometry, fixed_corner
            )
            resized_strokes: list[Any] = []
            for stroke, points in zip(original.get("strokes", []), transformed):
                if isinstance(stroke, dict):
                    resized = dict(stroke)
                    resized["points"] = points
                    resized_strokes.append(resized)
                else:
                    resized_strokes.append(points)
            preview["strokes"] = resized_strokes
        candidate["geometry"] = geometry
        self._gesture_state = "resizing"
        self._gesture_preview = preview
        self.update()

    def _release(self, key: tuple[Any, ...], sx: float, sy: float) -> None:
        if self._active != key:
            return
        self._active = None
        if self._pan_pointer == key:
            self._end_pan()
            self.update()
            return
        if self._mode == "pen":
            finished, self._live = self._live, []
            self.update()
            if finished:
                self.StrokeFinished.emit(finished)
            return
        candidate = self._press_candidate
        preview = self._gesture_preview
        self._press_candidate = None
        self._gesture_preview = None
        self._gesture_state = "idle"
        self._press_at = None
        self.update()
        if isinstance(candidate, dict) and candidate.get("kind") in ("maybe-pan", "pan"):
            return  # empty-space click clears selection; drag pans; neither commits
        if candidate is not None and candidate.get("kind") == "drag" and isinstance(preview, dict):
            self.GestureFinished.emit(
                {
                    "command": "move_item",
                    "target_id": candidate.get("target_id"),
                    "parameters": {"position": {"x": preview["x"], "y": preview["y"]}},
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
        if (
            candidate is not None
            and candidate.get("kind") == "resize"
            and isinstance(preview, dict)
            and isinstance(candidate.get("geometry"), dict)
        ):
            geometry = candidate["geometry"]
            self.GestureFinished.emit(
                {
                    "command": "__manual_resize__",
                    "target_id": candidate.get("target_id"),
                    "parameters": {"size": {"w": preview["width"], "h": preview["height"]}},
                    "anchor": {
                        "corner": candidate.get("corner"),
                        "fixed_corner": geometry.get("fixed_corner"),
                        "x": geometry.get("fixed_x"),
                        "y": geometry.get("fixed_y"),
                    },
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

    def mouseDoubleClickEvent(self, event: Any) -> None:
        from PyQt6.QtCore import Qt as _Qt

        if self._mode != "select" or event.button() != _Qt.MouseButton.LeftButton:
            return
        # Cancel any press candidate the second click started.
        self._press_candidate = None
        self._gesture_preview = None
        self._gesture_state = "idle"
        self._active = None
        pos = event.position()
        world = self._world_pos(float(pos.x()), float(pos.y()))
        from smartboard.core.hit_test import select_at

        target_id = select_at(
            self._state.get("elements", []),
            world[0],
            world[1],
            tolerance=self._hit_tolerance_world(),
        )
        payload: dict[str, Any] = {"world_x": world[0], "world_y": world[1], "target_id": target_id}
        if target_id is not None:
            target = self._find_element(target_id)
            if target is None or target.get("type") not in ("heading", "text"):
                text = ""
                if isinstance(target, dict):
                    text = str(target.get("text", ""))
                    if not text and isinstance(target.get("extra"), dict):
                        text = str(target["extra"].get("text", ""))
                if (
                    target is not None
                    and not text
                    and target.get("type") not in ("heading", "text")
                ):
                    return
            self._select_pressed(target_id)
        self.InlineEditRequested.emit(payload)
        event.accept()

    def wheelEvent(self, event: Any) -> None:
        from PyQt6.QtCore import Qt as _Qt

        pos = event.position()
        sx, sy = float(pos.x()), float(pos.y())
        modifiers = event.modifiers()
        delta = event.angleDelta()
        dx, dy = float(delta.x()), float(delta.y())
        if modifiers & _Qt.KeyboardModifier.ControlModifier:
            steps = dy / 120.0
            if steps == 0:
                event.accept()
                return
            self.zoom_about(sx, sy, WHEEL_ZOOM_BASE**steps)
            event.accept()
            return
        if modifiers & _Qt.KeyboardModifier.ShiftModifier:
            self.pan_by_screen((dx + dy) / 8.0, 0.0)
        else:
            self.pan_by_screen(dx / 8.0, dy / 8.0)
        event.accept()

    def leaveEvent(self, event: Any) -> None:
        if self._active is None:
            self.unsetCursor()
        super().leaveEvent(event)

    def tabletEvent(self, event: Any) -> None:
        kind = event.type()
        pos = event.position()
        pressure = self._pressure_of(event)
        type_name = kind.name if hasattr(kind, "name") else str(kind)
        if "Press" in type_name:
            self._press(("tablet",), float(pos.x()), float(pos.y()), pressure)
        elif "Move" in type_name:
            if self._active == ("tablet",):
                self._sample(("tablet",), float(pos.x()), float(pos.y()), pressure)
            else:
                self._update_hover_cursor(float(pos.x()), float(pos.y()))
        elif "Release" in type_name:
            self._release(("tablet",), float(pos.x()), float(pos.y()))

    def mousePressEvent(self, event: Any) -> None:
        from PyQt6.QtCore import Qt as _Qt

        pos = event.position()
        if event.button() == _Qt.MouseButton.MiddleButton:
            self._press(("middle",), float(pos.x()), float(pos.y()), None)
        elif event.button() == _Qt.MouseButton.LeftButton:
            self._press(("mouse",), float(pos.x()), float(pos.y()), None)

    def mouseMoveEvent(self, event: Any) -> None:
        pos = event.position()
        if self._active == ("mouse",) or self._active == ("middle",):
            self._sample(self._active, float(pos.x()), float(pos.y()), None)
        else:
            self._update_hover_cursor(float(pos.x()), float(pos.y()))

    def mouseReleaseEvent(self, event: Any) -> None:
        from PyQt6.QtCore import Qt as _Qt

        pos = event.position()
        if event.button() == _Qt.MouseButton.MiddleButton:
            self._release(("middle",), float(pos.x()), float(pos.y()))
        elif event.button() == _Qt.MouseButton.LeftButton:
            self._release(("mouse",), float(pos.x()), float(pos.y()))

    def touchEvent(self, event: Any) -> None:
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

        if event.type() in (
            _QEvent.Type.TouchBegin,
            _QEvent.Type.TouchUpdate,
            _QEvent.Type.TouchEnd,
        ):
            self.touchEvent(event)
            return True
        if event.type() in (
            _QEvent.Type.TabletPress,
            _QEvent.Type.TabletMove,
            _QEvent.Type.TabletRelease,
        ):
            self.tabletEvent(event)
            return True
        if event.type() == _QEvent.Type.Gesture:
            return self._handle_gesture_event(event)
        if event.type() == _QEvent.Type.NativeGesture:
            return self._handle_native_gesture(event)
        return bool(super().event(event))

    def _handle_gesture_event(self, event: Any) -> bool:
        from PyQt6.QtCore import Qt as _Qt

        try:
            from PyQt6.QtWidgets import QPinchGesture
        except ImportError:  # pragma: no cover - platform variance
            return False
        gesture = event.gesture(_Qt.GestureType.PinchGesture)
        if not isinstance(gesture, QPinchGesture):
            return False
        state = gesture.state()
        state_name = state.name if hasattr(state, "name") else str(state)
        total = float(gesture.totalScaleFactor() or 1.0)
        center = gesture.centerPoint()
        if "Started" in state_name:
            self._pinch_last_total = total
            return True
        if "Finished" in state_name or "Canceled" in state_name:
            self._pinch_last_total = None
            return True
        last = self._pinch_last_total if self._pinch_last_total else total
        if last <= 0 or total <= 0:
            return True
        self.handle_pinch(float(center.x()), float(center.y()), total / last)
        self._pinch_last_total = total
        return True

    def _handle_native_gesture(self, event: Any) -> bool:
        from PyQt6.QtCore import Qt as _Qt

        try:
            gesture_type = event.gestureType()
        except AttributeError:  # pragma: no cover - platform variance
            return False
        if gesture_type != _Qt.NativeGestureType.ZoomNativeGesture:
            return False
        try:
            value = float(event.value())
        except (AttributeError, TypeError, ValueError):
            return False
        factor = min(max(1.0 + value, 0.5), 2.0)
        pos = event.position()
        self.handle_pinch(float(pos.x()), float(pos.y()), factor)
        return True

    def element_screen_rect(self, element_id: str | None) -> Any:
        """Screen rectangle for an element id (used to anchor the text overlay)."""
        from PyQt6.QtCore import QRect as _QRect

        if element_id is not None:
            element = self._find_element(element_id)
            if element is not None:
                x, y, w, h = self._screen_rect(element)
                return _QRect(int(x), int(y), max(int(w), 1), max(int(h), 1))
        return _QRect(0, 0, 1, 1)

    def _screen_rect(self, el: dict[str, Any]) -> tuple[float, float, float, float]:
        camera = self.camera_state()
        x, y, w, h = element_world_rect(el)
        tx, ty = ((x - camera.pan_x) * camera.zoom, (y - camera.pan_y) * camera.zoom)
        return (tx, ty, w * camera.zoom, h * camera.zoom)

    def _paint_selection_bounds(self, painter: Any, el: dict[str, Any]) -> None:
        """Paint the selection outline and handles in constant screen space."""
        from PyQt6.QtCore import QRectF as _QRectF

        x, y, w, h = self._screen_rect(el)
        pen = QPen(QColor(theme.SELECTION))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(_QRectF(x, y, w, h))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(theme.SELECTION))
        half = theme.HANDLE_SIZE / 2
        for hx, hy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
            painter.drawRect(_QRectF(hx - half, hy - half, theme.HANDLE_SIZE, theme.HANDLE_SIZE))

    def _paint_adornments(self, painter: Any, camera: CameraState) -> None:
        from PyQt6.QtCore import QRectF as _QRectF

        selected = self._state.get("selected_element_id")
        preview = self._gesture_preview
        for el in self._state.get("elements", []):
            if el["id"] == selected and not (
                isinstance(preview, dict) and preview.get("id") == el.get("id")
            ):
                self._paint_selection_bounds(painter, el)
            if el["id"] == self._highlight_id:
                x, y, w, h = self._screen_rect(el)
                pen = QPen(QColor(theme.HIGHLIGHT))
                pen.setWidth(3)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(_QRectF(x - 8, y - 8, w + 16, h + 16))
        if isinstance(preview, dict):
            self._paint_selection_bounds(painter, preview)

    def _paint_live(self, painter: Any) -> None:
        """Temporary overlay for the in-progress stroke (never stored)."""
        if not self._live:
            return
        from PyQt6.QtCore import QPointF as _QPointF
        from PyQt6.QtGui import QPainterPath as _QPainterPath

        color = QColor(resolve_color(self._live_color()))
        pts = [_QPointF(float(p["x"]), float(p["y"])) for p in self._live]
        path = _QPainterPath()
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
