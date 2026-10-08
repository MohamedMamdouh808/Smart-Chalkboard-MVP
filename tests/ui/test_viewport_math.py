"""T004: viewport math — uniform scale, centered offsets, exact round-trip."""

from __future__ import annotations

import pytest

from smartboard.ui.viewport import CANVAS_H, CANVAS_W, Viewport

SIZES = [(960, 540), (1280, 720), (1920, 1080), (800, 1000), (1920, 500), (500, 900)]


def test_canvas_constants() -> None:
    assert (CANVAS_W, CANVAS_H) == (1920, 1080)


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_uniform_scale_and_centering(view_w: int, view_h: int) -> None:
    vp = Viewport.from_sizes(view_w, view_h)
    assert vp.scale == pytest.approx(min(view_w / 1920, view_h / 1080))
    assert vp.ox == pytest.approx((view_w - 1920 * vp.scale) / 2, abs=1e-6)
    assert vp.oy == pytest.approx((view_h - 1080 * vp.scale) / 2, abs=1e-6)
    assert vp.ox >= -1e-6 and vp.oy >= -1e-6  # letterbox margins, never negative


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_round_trip_exact(view_w: int, view_h: int) -> None:
    vp = Viewport.from_sizes(view_w, view_h)
    for cx, cy in ((0, 0), (160, 80), (1920, 1080), (960, 540), (1919.5, 1079.5)):
        sx, sy = vp.to_screen(cx, cy)
        rx, ry = vp.to_canvas(sx, sy)
        assert abs(rx - cx) < 0.5 and abs(ry - cy) < 0.5


def test_whole_canvas_visible_and_undistorted(view_size: tuple[int, int]) -> None:
    view_w, view_h = view_size
    vp = Viewport.from_sizes(view_w, view_h)
    corners = [vp.to_screen(x, y) for x, y in ((0, 0), (1920, 0), (0, 1080), (1920, 1080))]
    for sx, sy in corners:
        assert 0 <= sx <= view_w and 0 <= sy <= view_h
    # Uniform: x and y scale identically (aspect preserved).
    sx1, _ = vp.to_screen(1920, 0)
    _, sy1 = vp.to_screen(0, 1080)
    assert (sx1 - vp.ox) / 1920 == pytest.approx((sy1 - vp.oy) / 1080)


def test_zero_view_size_safe() -> None:
    vp = Viewport.from_sizes(0, 0)
    assert vp.scale == 1.0
