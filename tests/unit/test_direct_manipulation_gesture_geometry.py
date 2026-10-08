"""Qt-independent drag/resize geometry — unbounded world coordinates."""

from __future__ import annotations

from smartboard.core.gesture import (
    PRESS_DRAG_THRESHOLD,
    drag_candidate,
    resize_candidate,
    resize_preview_points,
)

ORIGINAL = {"x": 100, "y": 100, "width": 200, "height": 100}


def test_drag_candidate_preserves_grab_offset() -> None:
    candidate = drag_candidate(ORIGINAL, (120.0, 130.0), (180.0, 170.0))
    assert (candidate["x"], candidate["y"]) == (160, 140)
    assert (candidate["width"], candidate["height"]) == (200, 100)
    assert candidate["moved"] is True
    assert ORIGINAL == {"x": 100, "y": 100, "width": 200, "height": 100}


def test_drag_candidate_is_unclamped() -> None:
    original = {"x": 1800, "y": 950, "width": 100, "height": 100}
    candidate = drag_candidate(original, (1800.0, 950.0), (2000.0, 1200.0))
    assert (candidate["x"], candidate["y"]) == (2000, 1200)
    assert candidate["moved"] is True


def test_drag_candidate_quantizes_and_detects_clicks() -> None:
    clicked = drag_candidate(ORIGINAL, (100.2, 100.0), (102.8, 100.0))
    assert (clicked["x"], clicked["y"]) == (103, 100)
    assert clicked["moved"] is False
    assert PRESS_DRAG_THRESHOLD == 4.0
    moved = drag_candidate(ORIGINAL, (100.0, 100.0), (104.0, 100.0))
    assert moved["moved"] is True


def test_resize_preserves_aspect_from_each_corner() -> None:
    northwest = resize_candidate(ORIGINAL, "nw", (100.0, 100.0), (50.0, 75.0), True)
    assert (northwest["x"], northwest["y"], northwest["width"], northwest["height"]) == (
        50,
        75,
        250,
        125,
    )
    assert (northwest["fixed_corner"], northwest["fixed_x"], northwest["fixed_y"]) == (
        "se",
        300,
        200,
    )
    northeast = resize_candidate(ORIGINAL, "ne", (300.0, 100.0), (350.0, 75.0), True)
    assert (northeast["x"], northeast["y"], northeast["width"], northeast["height"]) == (
        100,
        75,
        250,
        125,
    )
    southwest = resize_candidate(ORIGINAL, "sw", (100.0, 200.0), (50.0, 250.0), True)
    assert (southwest["x"], southwest["y"], southwest["width"], southwest["height"]) == (
        0,
        100,
        300,
        150,
    )
    southeast = resize_candidate(ORIGINAL, "se", (300.0, 200.0), (400.0, 250.0), True)
    assert (southeast["x"], southeast["y"], southeast["width"], southeast["height"]) == (
        100,
        100,
        300,
        150,
    )
    assert ORIGINAL == {"x": 100, "y": 100, "width": 200, "height": 100}


def test_resize_enforces_minimum_without_canvas_clamp() -> None:
    tiny = resize_candidate(ORIGINAL, "se", (300.0, 200.0), (110.0, 105.0), True)
    assert (tiny["width"], tiny["height"]) == (48, 24)
    assert (tiny["x"], tiny["y"]) == (100, 100)
    far = resize_candidate(ORIGINAL, "se", (300.0, 200.0), (2000.0, 1200.0), True)
    assert (far["width"], far["height"]) == (2200, 1100)
    crossed = resize_candidate(ORIGINAL, "nw", (100.0, 100.0), (350.0, 250.0), True)
    assert (crossed["x"], crossed["y"], crossed["width"], crossed["height"]) == (252, 176, 48, 24)
    free = resize_candidate(ORIGINAL, "se", (300.0, 200.0), (110.0, 102.0), False)
    assert (free["width"], free["height"]) == (24, 24)
    assert free["moved"] is True
    click = resize_candidate(ORIGINAL, "se", (300.0, 200.0), (301.0, 200.0), True)
    assert click["moved"] is False


def test_resize_rejects_invalid_geometry() -> None:
    import pytest

    with pytest.raises(ValueError, match="unknown resize corner"):
        resize_candidate(ORIGINAL, "middle", (100.0, 100.0), (200.0, 200.0), True)
    assert resize_candidate(
        {"x": 0, "y": 0, "width": 0, "height": 100}, "se", (0.0, 0.0), (10.0, 10.0), True
    ) == {"valid": False, "moved": False}
    assert resize_candidate(
        {"x": 0, "y": 0, "width": 200, "height": 100}, "se", (200.0, 100.0), (200.0, 100.0), False
    ) == {
        "x": 0,
        "y": 0,
        "width": 200,
        "height": 100,
        "fixed_corner": "nw",
        "fixed_x": 0,
        "fixed_y": 0,
        "valid": True,
        "moved": False,
    }
    degenerate = resize_preview_points(
        [], {"width": 0, "height": 0}, {"width": 24, "height": 24}, "se"
    )
    assert degenerate == []
    outside = {"x": 900000, "y": 0, "width": 100, "height": 100}
    assert resize_candidate(outside, "se", (900100.0, 100.0), (5_000_000.0, 100.0), True) == {
        "valid": False,
        "moved": False,
    }
    assert resize_candidate(outside, "se", (900100.0, 100.0), (5_000_000.0, 100.0), False) == {
        "valid": False,
        "moved": False,
    }
