"""Application-owned infinite-board camera (view state only, never board content)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from smartboard.core.board import MAX_WORLD_COORD

MIN_ZOOM = 0.10
MAX_ZOOM = 4.00
FIT_MARGIN = 48.0


def _finite_number(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    if not math.isfinite(number):
        return fallback
    return number


def clamp_zoom(zoom: Any) -> float:
    """Clamp zoom to the supported 10%..400% range (invalid becomes 100%)."""
    finite = _finite_number(zoom, 1.0)
    return min(max(finite, MIN_ZOOM), MAX_ZOOM)


def clamp_pan(value: Any) -> float:
    """Clamp pan to finite world coordinates (invalid becomes origin)."""
    finite = _finite_number(value, 0.0)
    return min(max(finite, -MAX_WORLD_COORD), MAX_WORLD_COORD)


def normalize_camera(pan_x: Any, pan_y: Any, zoom: Any) -> CameraState:
    """Return a valid camera for arbitrary persisted or computed input."""
    return CameraState(pan_x=clamp_pan(pan_x), pan_y=clamp_pan(pan_y), zoom=clamp_zoom(zoom))


def default_camera() -> CameraState:
    return CameraState(pan_x=0.0, pan_y=0.0, zoom=1.0)


@dataclass
class CameraState:
    """Transient view state: world coordinates visible at screen origin plus zoom."""

    pan_x: float = 0.0
    pan_y: float = 0.0
    zoom: float = 1.0

    def __post_init__(self) -> None:
        self.pan_x = clamp_pan(self.pan_x)
        self.pan_y = clamp_pan(self.pan_y)
        self.zoom = clamp_zoom(self.zoom)

    def to_dict(self) -> dict[str, float]:
        return {"pan_x": float(self.pan_x), "pan_y": float(self.pan_y), "zoom": float(self.zoom)}

    @staticmethod
    def from_dict(data: Any) -> CameraState:
        if not isinstance(data, dict):
            return default_camera()
        return normalize_camera(data.get("pan_x"), data.get("pan_y"), data.get("zoom"))


def world_to_screen(camera: CameraState, x: float, y: float) -> tuple[float, float]:
    return ((float(x) - camera.pan_x) * camera.zoom, (float(y) - camera.pan_y) * camera.zoom)


def screen_to_world(camera: CameraState, sx: float, sy: float) -> tuple[float, float]:
    return (float(sx) / camera.zoom + camera.pan_x, float(sy) / camera.zoom + camera.pan_y)


def pan_by_screen(camera: CameraState, dx: float, dy: float) -> CameraState:
    """Pan by screen pixels (positive dx moves the view right/down in world space)."""
    return normalize_camera(
        camera.pan_x + float(dx) / camera.zoom, camera.pan_y + float(dy) / camera.zoom, camera.zoom
    )


def zoom_about_cursor(camera: CameraState, sx: float, sy: float, factor: float) -> CameraState:
    """Zoom about a screen point while keeping its world anchor fixed."""
    try:
        scale = float(factor)
    except (TypeError, ValueError):
        return normalize_camera(camera.pan_x, camera.pan_y, camera.zoom)
    if not math.isfinite(scale) or scale <= 0.0:
        return normalize_camera(camera.pan_x, camera.pan_y, camera.zoom)
    anchor_x, anchor_y = screen_to_world(camera, float(sx), float(sy))
    new_zoom = clamp_zoom(camera.zoom * scale)
    return normalize_camera(
        anchor_x - float(sx) / new_zoom, anchor_y - float(sy) / new_zoom, new_zoom
    )


def reset_zoom(camera: CameraState) -> CameraState:
    return normalize_camera(camera.pan_x, camera.pan_y, 1.0)


def visible_world_rect(
    camera: CameraState, view_w: float, view_h: float
) -> tuple[float, float, float, float]:
    """Visible world rectangle for the current camera and widget size."""
    try:
        width = float(view_w)
        height = float(view_h)
    except (TypeError, ValueError):
        width, height = 0.0, 0.0
    if not math.isfinite(width) or width < 0.0:
        width = 0.0
    if not math.isfinite(height) or height < 0.0:
        height = 0.0
    return (camera.pan_x, camera.pan_y, width / camera.zoom, height / camera.zoom)


def fit_camera_for_bounds(
    bounds: tuple[float, float, float, float] | None, view_w: float, view_h: float
) -> CameraState:
    """Frame world bounds at a clamped zoom (empty bounds return default view)."""
    try:
        width = float(view_w)
        height = float(view_h)
    except (TypeError, ValueError):
        return default_camera()
    if (
        not math.isfinite(width)
        or not math.isfinite(height)
        or width <= 0.0
        or height <= 0.0
        or bounds is None
    ):
        return default_camera()
    try:
        x, y, w, h = (float(bounds[0]), float(bounds[1]), float(bounds[2]), float(bounds[3]))
    except (TypeError, ValueError, IndexError):
        return default_camera()
    if not all(math.isfinite(value) for value in (x, y, w, h)) or w < 0.0 or h < 0.0:
        return default_camera()
    full_w = max(w + 2.0 * FIT_MARGIN, 1.0)
    full_h = max(h + 2.0 * FIT_MARGIN, 1.0)
    zoom = clamp_zoom(min(width / full_w, height / full_h))
    return normalize_camera(x - FIT_MARGIN, y - FIT_MARGIN, zoom)
