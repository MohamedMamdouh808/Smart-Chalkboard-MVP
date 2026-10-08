"""US3A unbounded world-gesture tests (fail-first)."""

from __future__ import annotations

from smartboard.core import gesture


def test_drag_is_unclamped_in_world_space() -> None:
    geometry = gesture.drag_candidate(
        {"x": 1800, "y": 950, "width": 100, "height": 100}, (1800.0, 950.0), (5000.0, -4000.0)
    )
    assert (geometry["x"], geometry["y"]) == (5000, -4000)
    assert geometry["moved"] is True


def test_small_press_does_not_move() -> None:
    geometry = gesture.drag_candidate(
        {"x": 0, "y": 0, "width": 100, "height": 100}, (0.0, 0.0), (1.0, 1.0)
    )
    assert geometry["moved"] is False


def test_resize_is_unclamped_with_fixed_corner() -> None:
    geometry = gesture.resize_candidate(
        {"x": 100, "y": 100, "width": 200, "height": 100},
        "se",
        (300.0, 200.0),
        (5000.0, 4000.0),
        False,
    )
    assert geometry["valid"] is True
    assert (geometry["width"], geometry["height"]) == (4900, 3900)
    assert (geometry["x"], geometry["y"]) == (100, 100)


def test_resize_rejects_out_of_range_geometry() -> None:
    geometry = gesture.resize_candidate(
        {"x": 0, "y": 0, "width": 100, "height": 100},
        "se",
        (100.0, 100.0),
        (5_000_000.0, 100.0),
        False,
    )
    assert geometry["valid"] is False
