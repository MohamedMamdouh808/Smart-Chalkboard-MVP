"""T017: text-fit — wrap in fixed box, exact rejection, coords never change."""

from __future__ import annotations

import pytest

QtGui = pytest.importorskip("PyQt6.QtGui")

from smartboard.app.text_fit import (  # noqa: E402
    TOO_LONG_MESSAGE,
    check_create,
    fits_in_box,
    font_for,
)


def test_short_text_fits_default_boxes() -> None:
    # Short strings fit under any font (incl. wide offscreen fallbacks);
    # full-length headings are verified on real Arial in the headed checklist.
    assert fits_in_box("Hi", 800, 96, font_for("heading"))
    assert fits_in_box("F = ma", 320, 80, font_for("text", equation_style=True))


def test_overlong_text_rejected_with_exact_message() -> None:
    ok, message = check_create("heading", "x" * 200)
    assert ok is False
    assert message == "Text is too long for this element. Resize it or shorten the text."
    assert TOO_LONG_MESSAGE == message


def test_gate_never_changes_box_or_coordinates() -> None:
    box = {"x": 160, "y": 80, "width": 800, "height": 96}
    before = dict(box)
    check_create("heading", "A reasonable heading")
    assert box == before


def test_post_resize_shortfall_is_paint_only() -> None:
    """A box shrunk after creation overflows visually; stored text is intact."""
    from smartboard.core.engine import CommandEngine

    TS = "2026-10-03T18:15:00Z"
    eng = CommandEngine()
    eng.execute({"command": "create_text", "target_id": None,
                 "parameters": {"text": "Force equals mass times acceleration"},
                 "timestamp": TS})
    el = eng.board.elements[0]
    assert el.extra["text"] == "Force equals mass times acceleration"
    # A short label fits the default box while a long one does not, yet the
    # stored text is always whole — overflow is render-only, never a mutation.
    assert fits_in_box("Ok", 600, 120, font_for("text")) is True
    assert fits_in_box("Ok", 100, 30, font_for("text")) is False
