"""Qt-agnostic camera transform adapter for the board widget."""

from __future__ import annotations

from dataclasses import dataclass

from smartboard.app.camera import (
    CameraState,
    default_camera,
    fit_camera_for_bounds,
    normalize_camera,
    pan_by_screen,
    reset_zoom,
    screen_to_world,
    visible_world_rect,
    world_to_screen,
    zoom_about_cursor,
)

__all__ = [
    "CameraState",
    "CameraTransform",
    "default_camera",
    "fit_camera_for_bounds",
    "normalize_camera",
    "pan_by_screen",
    "reset_zoom",
    "screen_to_world",
    "visible_world_rect",
    "world_to_screen",
    "zoom_about_cursor",
]


@dataclass(frozen=True)
class CameraTransform:
    """Widget-facing transform pairing a camera with current view dimensions."""

    pan_x: float = 0.0
    pan_y: float = 0.0
    zoom: float = 1.0
    view_w: float = 0.0
    view_h: float = 0.0

    def __post_init__(self) -> None:
        valid = normalize_camera(self.pan_x, self.pan_y, self.zoom)
        object.__setattr__(self, "pan_x", valid.pan_x)
        object.__setattr__(self, "pan_y", valid.pan_y)
        object.__setattr__(self, "zoom", valid.zoom)

    @staticmethod
    def from_camera(camera: CameraState, view_w: float, view_h: float) -> CameraTransform:
        valid = normalize_camera(camera.pan_x, camera.pan_y, camera.zoom)
        return CameraTransform(
            pan_x=valid.pan_x, pan_y=valid.pan_y, zoom=valid.zoom, view_w=view_w, view_h=view_h
        )

    def to_camera(self) -> CameraState:
        return normalize_camera(self.pan_x, self.pan_y, self.zoom)

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        return world_to_screen(self.to_camera(), x, y)

    def to_world(self, sx: float, sy: float) -> tuple[float, float]:
        return screen_to_world(self.to_camera(), sx, sy)

    def visible_rect(self) -> tuple[float, float, float, float]:
        return visible_world_rect(self.to_camera(), self.view_w, self.view_h)
