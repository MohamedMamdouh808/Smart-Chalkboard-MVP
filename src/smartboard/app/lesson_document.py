"""Lesson-document envelope: board content plus camera (application layer)."""

from __future__ import annotations

from typing import Any

from smartboard.app.camera import CameraState, default_camera, normalize_camera

EXPORT_MARGIN = 48.0


def build_snapshot(board_dict: dict[str, Any], camera: CameraState) -> dict[str, Any]:
    """Compose a new lesson snapshot from board content and camera."""
    valid = normalize_camera(camera.pan_x, camera.pan_y, camera.zoom)
    return {
        "lesson_id": str(board_dict.get("lesson_id", "lesson_001")),
        "version": int(board_dict.get("version", 1)),
        "elements": list(board_dict.get("elements", [])),
        "selected_element_id": board_dict.get("selected_element_id"),
        "camera": valid.to_dict(),
    }


def _legacy_canvas(data: dict[str, Any]) -> tuple[float, float] | None:
    canvas = data.get("canvas")
    if not isinstance(canvas, dict):
        return None
    try:
        width, height = float(canvas.get("width", 0)), float(canvas.get("height", 0))
    except (TypeError, ValueError):
        return None
    if width <= 0 or height <= 0:
        return None
    return (width, height)


def restore_snapshot(
    data: dict[str, Any], view_w: float, view_h: float
) -> tuple[dict[str, Any], CameraState]:
    """Split a stored snapshot into board content and viewing camera.

    Coordinates are never altered; only the viewing model is derived. Legacy
    snapshots with canvas dimensions reopen centered at 100% zoom.
    """
    board_dict = {
        "lesson_id": str(data.get("lesson_id", "lesson_001")),
        "version": int(data.get("version", 1)),
        "elements": list(data.get("elements", [])),
        "selected_element_id": data.get("selected_element_id"),
    }
    camera_data = data.get("camera")
    if isinstance(camera_data, dict):
        return board_dict, CameraState.from_dict(camera_data)
    legacy = _legacy_canvas(data)
    if legacy is None:
        return board_dict, default_camera()
    canvas_w, canvas_h = legacy
    try:
        vw, vh = float(view_w), float(view_h)
    except (TypeError, ValueError):
        vw, vh = 0.0, 0.0
    return board_dict, normalize_camera((canvas_w - vw) / 2.0, (canvas_h - vh) / 2.0, 1.0)
