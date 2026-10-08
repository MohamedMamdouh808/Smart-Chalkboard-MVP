"""Camera-transform math — origin-anchored pan, cursor zoom, exact round-trip."""

from __future__ import annotations

import pytest

from smartboard.ui.camera_transform import CameraTransform

SIZES = [(960, 540), (1280, 720), (1920, 1080), (800, 1000), (1920, 500), (500, 900)]


def test_world_constants_replaced_canvas_constants() -> None:
    from smartboard.core.board import MAX_WORLD_COORD, MAX_WORLD_SIZE, MIN_SIZE

    assert (MAX_WORLD_COORD, MAX_WORLD_SIZE, MIN_SIZE) == (1_000_000.0, 1_000_000.0, 24)


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_round_trip_exact(view_w: int, view_h: int) -> None:
    transform = CameraTransform(pan_x=123.25, pan_y=-456.5, zoom=1.5, view_w=view_w, view_h=view_h)
    for wx, wy in ((0, 0), (160, 80), (-5000, 7500), (960, 540)):
        sx, sy = transform.to_screen(wx, wy)
        rx, ry = transform.to_world(sx, sy)
        assert abs(rx - wx) < 1e-6 and abs(ry - wy) < 1e-6


def test_visible_rect_matches_camera_and_size(view_size: tuple[int, int]) -> None:
    view_w, view_h = view_size
    transform = CameraTransform(pan_x=10.0, pan_y=20.0, zoom=2.0, view_w=view_w, view_h=view_h)
    assert transform.visible_rect() == (10.0, 20.0, view_w / 2.0, view_h / 2.0)


def test_zero_view_size_safe() -> None:
    transform = CameraTransform(pan_x=0.0, pan_y=0.0, zoom=1.0, view_w=0, view_h=0)
    assert transform.visible_rect() == (0.0, 0.0, 0.0, 0.0)


def test_zoom_range_clamped() -> None:
    assert CameraTransform(pan_x=0.0, pan_y=0.0, zoom=99.0, view_w=960, view_h=540).zoom == 4.0
    assert CameraTransform(pan_x=0.0, pan_y=0.0, zoom=0.001, view_w=960, view_h=540).zoom == 0.10
