"""US3C content-bounds export tests (fail-first)."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.exporter import export_png
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def test_export_renders_content_bounds_plus_margin(tmp_path, qapp) -> None:
    from PyQt6.QtGui import QImage

    eng = CommandEngine()
    eng.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Hi", "position": {"x": 0, "y": 0}},
            "timestamp": TS,
        }
    )
    eng.execute(
        {
            "command": "create_shape",
            "target_id": None,
            "parameters": {"shape_type": "rectangle", "position": {"x": 0, "y": 200}},
            "timestamp": TS,
        }
    )
    out = export_png(eng.board.to_dict(), str(tmp_path / "lesson.png"))
    image = QImage(str(out))
    # Content spans y=0..400 (heading 96 + shape 200..400); x=0..800.
    assert (image.width(), image.height()) == (800 + 96, 400 + 96)
    # Left edge of the shape outline must differ from the background.
    assert image.pixelColor(48, 48 + 200 + 100) != image.pixelColor(0, 0)


def test_export_empty_lesson_is_valid(tmp_path, qapp) -> None:
    from PyQt6.QtGui import QImage

    eng = CommandEngine()
    out = export_png(eng.board.to_dict(), str(tmp_path / "empty.png"))
    image = QImage(str(out))
    assert (image.width(), image.height()) == (960, 540)
    assert not image.isNull()


def test_export_failure_raises_without_mutation(tmp_path, qapp) -> None:
    eng = CommandEngine()
    before = eng.board.to_dict()
    with pytest.raises(RuntimeError):
        export_png(eng.board.to_dict(), str(tmp_path / "missing-dir" / "lesson.png"))
    assert eng.board.to_dict() == before
