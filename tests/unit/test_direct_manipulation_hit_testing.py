"""US1 per-type hit-testing and handle-detection tests."""

from __future__ import annotations

from smartboard.core.hit_test import (
    TOLERANCE,
    drawing_hit,
    element_hit,
    equation_hit,
    handle_at,
    heading_hit,
    select_at,
    shape_hit,
    text_hit,
)

RECTANGLE = {"id": "rectangle_001", "type": "shape", "x": 100, "y": 100,
             "width": 200, "height": 100, "z": 1, "shape_type": "rectangle"}
CIRCLE = {"id": "circle_001", "type": "shape", "x": 100, "y": 100,
          "width": 200, "height": 100, "z": 1, "shape_type": "circle"}
LINE = {"id": "line_001", "type": "shape", "x": 100, "y": 100,
        "width": 200, "height": 200, "z": 1, "shape_type": "line"}
ARROW = {"id": "arrow_001", "type": "shape", "x": 100, "y": 100,
         "width": 200, "height": 200, "z": 1, "shape_type": "arrow"}
TRIANGLE = {"id": "triangle_001", "type": "shape", "x": 100, "y": 100,
            "width": 200, "height": 100, "z": 1, "shape_type": "triangle"}
DRAWING = {"id": "drawing_001", "type": "drawing", "x": 96, "y": 106,
           "width": 728, "height": 118, "z": 5,
           "strokes": [{"points": [{"x": 100.0, "y": 140.0}, {"x": 820.0, "y": 220.0}],
                        "width": 8, "color": "#FFFFFF"}]}


def test_text_like_elements_use_rectangle_containment() -> None:
    heading = {"id": "heading_001", "type": "heading", "x": 160, "y": 80,
               "width": 800, "height": 96, "z": 1}
    text = {"id": "text_001", "type": "text", "x": 160, "y": 200,
            "width": 600, "height": 120, "z": 1}
    equation = {"id": "equation_001", "type": "text", "x": 160, "y": 376,
                "width": 320, "height": 80, "z": 1, "equation_style": True}
    assert heading_hit(heading, 160.0, 80.0) is True
    assert heading_hit(heading, 159.0, 80.0) is False
    assert text_hit(text, 400.0, 250.0) is True
    assert text_hit(text, 761.0, 250.0) is False
    assert equation_hit(equation, 200.0, 400.0) is True
    assert equation_hit(equation, 200.0, 457.0) is False


def test_shape_primitives_use_rendered_geometry() -> None:
    assert shape_hit(RECTANGLE, 150.0, 150.0) is True
    assert shape_hit(RECTANGLE, 301.0, 150.0) is False
    assert shape_hit(CIRCLE, 200.0, 150.0) is True
    assert shape_hit(CIRCLE, 100.0, 100.0) is False
    assert shape_hit(LINE, 100.0, 105.0) is True
    assert shape_hit(LINE, 100.0, 150.0) is False
    assert shape_hit(ARROW, 100.0, 105.0) is True
    assert shape_hit(ARROW, 290.0, 302.0) is True
    assert shape_hit(ARROW, 150.0, 250.0) is False
    assert shape_hit(TRIANGLE, 200.0, 180.0) is True
    assert shape_hit(TRIANGLE, 290.0, 110.0) is False
    unknown = dict(RECTANGLE, shape_type="hexagon")
    assert shape_hit(unknown, 150.0, 150.0) is True
    assert shape_hit(unknown, 301.0, 150.0) is False


def test_drawing_uses_proximity_or_expanded_bounds() -> None:
    assert drawing_hit(DRAWING, 100.0, 145.0) is True
    assert drawing_hit(DRAWING, 100.0, 200.0) is False
    # Inside the expanded bounding box but away from ink.
    assert element_hit(DRAWING, 500.0, 110.0) is True
    assert element_hit(DRAWING, 95.0, 106.0) is False


def test_dispatch_preserves_topmost_and_empty_space() -> None:
    lower = {"id": "text_001", "type": "text", "x": 100, "y": 100,
             "width": 200, "height": 200, "z": 1}
    upper = {"id": "shape_001", "type": "shape", "x": 150, "y": 150,
             "width": 200, "height": 200, "z": 2, "shape_type": "rectangle"}
    assert select_at([lower, upper], 175.0, 175.0) == "shape_001"
    assert select_at([lower, upper], 110.0, 110.0) == "text_001"
    assert select_at([lower, upper], 500.0, 500.0) is None
    assert select_at([], 10.0, 10.0) is None


def test_malformed_elements_do_not_raise() -> None:
    malformed = {"id": "malformed_001"}
    assert heading_hit(malformed, 10.0, 10.0) is False
    assert text_hit(malformed, 10.0, 10.0) is False
    assert equation_hit(malformed, 10.0, 10.0) is False
    assert shape_hit(malformed, 10.0, 10.0) is False
    assert drawing_hit(malformed, 10.0, 10.0) is False
    assert element_hit(malformed, 10.0, 10.0) is False
    assert select_at([malformed], 10.0, 10.0) is None


def test_handle_detection_expands_with_viewport_scale() -> None:
    selected = {"id": "text_001", "type": "text", "x": 100, "y": 100,
                "width": 200, "height": 200, "z": 1}
    assert handle_at(selected, 100.0, 100.0, 1.0) == "nw"
    assert handle_at(selected, 300.0, 300.0, 1.0) == "se"
    assert handle_at(selected, 150.0, 100.0, 1.0) is None
    # At quarter scale, 24 screen pixels cover 96 canvas units.
    assert handle_at(selected, 130.0, 100.0, 0.25) == "nw"
    assert handle_at(selected, 100.0, 100.0, 0.0) == "nw"
    assert handle_at({"id": "bad"}, 100.0, 100.0, 1.0) is None
    assert TOLERANCE == 6.0


def test_malformed_objects_and_unknown_types_do_not_raise() -> None:
    class BadType:
        @property
        def type(self) -> str:
            raise ValueError("bad type")

    class BadExtra:
        type = "shape"
        x = y = 0.0
        width = height = 100.0

        @property
        def extra(self) -> dict:
            raise ValueError("bad extra")

    assert element_hit(BadType(), 10.0, 10.0) is False
    assert element_hit(BadExtra(), 10.0, 10.0) is True
    assert element_hit({"id": "mystery", "type": "mystery"}, 10.0, 10.0) is False
    assert drawing_hit({"extra": {"strokes": [0]}}, 10.0, 10.0) is False
    assert shape_hit({"id": "degenerate", "type": "shape", "x": 0, "y": 0,
                      "width": 0, "height": 100, "shape_type": "circle"}, 0.0, 0.0) is False
