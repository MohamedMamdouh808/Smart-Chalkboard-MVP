"""US3B deterministic voice-placement tests (fail-first)."""

from __future__ import annotations

from smartboard.app.placement import DEFAULT_SIZES, find_placement


def test_empty_viewport_places_at_top_left_margin() -> None:
    x, y = find_placement("text", {}, (100.0, 200.0, 960.0, 540.0), [])
    assert (x, y) == (148.0, 248.0)


def test_placement_avoids_visible_content() -> None:
    elements = [{"id": "a", "type": "text", "x": 148, "y": 248, "width": 600, "height": 120}]
    x, y = find_placement("text", {}, (100.0, 200.0, 960.0, 540.0), elements)
    assert (x, y) == (148.0, 248.0 + 120.0 + 24.0)


def test_full_viewport_falls_below_lowest_element() -> None:
    elements = [{"id": "a", "type": "text", "x": 100, "y": 200, "width": 960, "height": 540}]
    _x, y = find_placement("text", {}, (100.0, 200.0, 960.0, 540.0), elements)
    assert y == 200.0 + 540.0 + 24.0


def test_default_sizes_match_engine() -> None:
    assert DEFAULT_SIZES["heading"] == (800, 96)
    assert DEFAULT_SIZES["text"] == (600, 120)
    assert DEFAULT_SIZES["equation"] == (320, 80)
    assert DEFAULT_SIZES["shape"] == (200, 200)
