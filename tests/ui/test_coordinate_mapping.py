"""World-space tap mapping — taps select exactly the intended element at any zoom."""

from __future__ import annotations

import pytest

from smartboard.core.hit_test import select_at
from smartboard.ui.camera_transform import CameraTransform

STATE = {
    "elements": [
        {
            "id": "heading_001",
            "type": "heading",
            "x": 160,
            "y": 80,
            "width": 800,
            "height": 96,
            "z": 1,
        },
        {"id": "text_001", "type": "text", "x": 160, "y": 200, "width": 320, "height": 80, "z": 2},
    ]
}

CAMERAS = [
    CameraTransform(pan_x=0.0, pan_y=0.0, zoom=1.0, view_w=960, view_h=540),
    CameraTransform(pan_x=500.0, pan_y=300.0, zoom=2.0, view_w=1280, view_h=720),
    CameraTransform(pan_x=-2000.0, pan_y=-1000.0, zoom=0.10, view_w=1920, view_h=1080),
]


@pytest.mark.parametrize("transform", CAMERAS)
def test_tap_hits_intended_element(transform: CameraTransform) -> None:
    sx, sy = transform.to_screen(200, 100)  # inside heading_001
    wx, wy = transform.to_world(sx, sy)
    assert select_at(STATE["elements"], wx, wy) == "heading_001"
    sx, sy = transform.to_screen(200, 240)  # inside text_001
    wx, wy = transform.to_world(sx, sy)
    assert select_at(STATE["elements"], wx, wy) == "text_001"


@pytest.mark.parametrize("transform", CAMERAS)
def test_tap_on_empty_space_selects_nothing(transform: CameraTransform) -> None:
    sx, sy = transform.to_screen(5000, 5000)  # empty world area
    wx, wy = transform.to_world(sx, sy)
    assert select_at(STATE["elements"], wx, wy) is None


def test_topmost_wins_on_overlap() -> None:
    state = {
        "elements": [
            {"id": "a", "type": "text", "x": 0, "y": 0, "width": 500, "height": 500, "z": 1},
            {"id": "b", "type": "text", "x": 100, "y": 100, "width": 200, "height": 200, "z": 2},
        ]
    }
    assert select_at(state["elements"], 150, 150) == "b"
    assert select_at(state["elements"], 10, 10) == "a"


def test_hundred_taps_all_correct() -> None:
    """100 taps across cameras, 100% accuracy."""
    taps = 0
    for transform in CAMERAS:
        for i in range(34):
            wx, wy = 160 + (i * 37) % 800, 80 + (i * 13) % 96  # inside heading
            sx, sy = transform.to_screen(wx, wy)
            assert select_at(STATE["elements"], *transform.to_world(sx, sy)) == "heading_001"
            taps += 1
    assert taps >= 100


def test_mid_stroke_camera_move_keeps_shape() -> None:
    """Samples taken under different cameras still describe the same stroke."""
    first = CameraTransform(pan_x=0.0, pan_y=0.0, zoom=1.0, view_w=960, view_h=540)
    second = CameraTransform(pan_x=400.0, pan_y=200.0, zoom=2.0, view_w=960, view_h=540)
    world_points = [(x, 500.0) for x in (100, 300, 500, 700, 900)]
    screen_first = [first.to_screen(x, y) for x, y in world_points[:2]]
    screen_rest = [second.to_screen(x, y) for x, y in world_points[2:]]
    back = [first.to_world(*p) for p in screen_first] + [second.to_world(*p) for p in screen_rest]
    for (bx, by), (cx, cy) in zip(back, world_points):
        assert abs(bx - cx) < 1e-6 and abs(by - cy) < 1e-6
