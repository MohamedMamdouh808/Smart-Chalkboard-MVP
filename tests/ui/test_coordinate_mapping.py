"""T005: pen/mouse mapping — taps select exactly the intended element at any size."""

from __future__ import annotations

import pytest

from smartboard.ui.viewport import Viewport, hit_test

STATE = {
    "elements": [
        {"id": "heading_001", "type": "heading", "x": 160, "y": 80, "width": 800, "height": 96,
         "z": 1},
        {"id": "text_001", "type": "text", "x": 160, "y": 200, "width": 320, "height": 80,
         "z": 2},
    ]
}

SIZES = [(960, 540), (1280, 720), (1920, 1080), (800, 1000)]


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_tap_hits_intended_element(view_w: int, view_h: int) -> None:
    vp = Viewport.from_sizes(view_w, view_h)
    sx, sy = vp.to_screen(200, 100)  # inside heading_001
    assert hit_test(STATE, *vp.to_canvas(sx, sy)) == "heading_001"
    sx, sy = vp.to_screen(200, 240)  # inside text_001
    assert hit_test(STATE, *vp.to_canvas(sx, sy)) == "text_001"


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_tap_on_empty_space_selects_nothing(view_w: int, view_h: int) -> None:
    vp = Viewport.from_sizes(view_w, view_h)
    sx, sy = vp.to_screen(1500, 900)  # empty canvas area
    assert hit_test(STATE, *vp.to_canvas(sx, sy)) is None


def test_topmost_wins_on_overlap() -> None:
    state = {"elements": [
        {"id": "a", "x": 0, "y": 0, "width": 500, "height": 500, "z": 1},
        {"id": "b", "x": 100, "y": 100, "width": 200, "height": 200, "z": 2},
    ]}
    assert hit_test(state, 150, 150) == "b"
    assert hit_test(state, 10, 10) == "a"


def test_hundred_taps_all_correct() -> None:
    """SC-003 style: 100 taps across three sizes, 100% accuracy."""
    taps = 0
    for view_w, view_h in ((960, 540), (1280, 720), (1920, 1080)):
        vp = Viewport.from_sizes(view_w, view_h)
        for i in range(34):
            cx, cy = 160 + (i * 37) % 800, 80 + (i * 13) % 96  # inside heading
            sx, sy = vp.to_screen(cx, cy)
            assert hit_test(STATE, *vp.to_canvas(sx, sy)) == "heading_001"
            taps += 1
    assert taps >= 100


def test_mid_stroke_viewport_swap_keeps_shape() -> None:
    """Samples taken under different viewports still describe the same stroke."""
    small = Viewport.from_sizes(960, 540)
    big = Viewport.from_sizes(1920, 1080)
    # Teacher draws a horizontal line across canvas y=500; resize happens mid-stroke.
    canvas_points = [(x, 500.0) for x in (100, 300, 500, 700, 900)]
    screen_first = [small.to_screen(x, y) for x, y in canvas_points[:2]]
    screen_rest = [big.to_screen(x, y) for x, y in canvas_points[2:]]
    back = [small.to_canvas(*p) for p in screen_first] + [big.to_canvas(*p) for p in screen_rest]
    for (bx, by), (cx, cy) in zip(back, canvas_points):
        assert abs(bx - cx) < 0.5 and abs(by - cy) < 0.5
