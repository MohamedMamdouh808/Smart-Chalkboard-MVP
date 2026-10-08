"""Foundation camera/transform tests (fail-first for infinite board)."""

from __future__ import annotations

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


def test_world_screen_round_trip_across_zoom_and_pan() -> None:
    for zoom in (0.10, 1.00, 4.00):
        camera = normalize_camera(123.25, -987.5, zoom)
        for world in ((0.0, 0.0), (160.0, 200.0), (-5000.0, 7500.0)):
            screen = world_to_screen(camera, world[0], world[1])
            restored = screen_to_world(camera, screen[0], screen[1])
            assert restored == world


def test_zoom_about_cursor_preserves_world_anchor() -> None:
    camera = normalize_camera(100.0, 50.0, 1.0)
    cursor = (320.0, 200.0)
    before = screen_to_world(camera, cursor[0], cursor[1])
    zoomed = zoom_about_cursor(camera, cursor[0], cursor[1], 2.0)
    assert zoomed.zoom == 2.0
    assert screen_to_world(zoomed, cursor[0], cursor[1]) == before


def test_zoom_limits_and_reset() -> None:
    camera = normalize_camera(0.0, 0.0, 1.0)
    assert zoom_about_cursor(camera, 10.0, 10.0, 100.0).zoom == 4.00
    assert zoom_about_cursor(camera, 10.0, 10.0, 0.001).zoom == 0.10
    assert reset_zoom(normalize_camera(25.0, -75.0, 2.5)).zoom == 1.0


def test_pan_by_screen_scales_with_zoom() -> None:
    camera = normalize_camera(0.0, 0.0, 2.0)
    moved = pan_by_screen(camera, 100.0, -50.0)
    assert (moved.pan_x, moved.pan_y) == (50.0, -25.0)


def test_visible_rect_and_fit_all() -> None:
    camera = normalize_camera(10.0, 20.0, 2.0)
    assert visible_world_rect(camera, 960, 540) == (10.0, 20.0, 480.0, 270.0)
    fitted = fit_camera_for_bounds((0.0, 0.0, 600.0, 120.0), 960, 540)
    x, y, width, height = visible_world_rect(fitted, 960, 540)
    assert x <= 0.0 and y <= 0.0
    assert x + width >= 600.0 and y + height >= 120.0


def test_invalid_camera_normalizes() -> None:
    assert default_camera() == CameraState(pan_x=0.0, pan_y=0.0, zoom=1.0)
    normalized = normalize_camera("bad", None, "bad")
    assert normalized == default_camera()
