"""Lesson export — V1 minimum is a PNG board image (Qt required)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def export_png(state: dict[str, Any], path: str | Path, width: int = 1920, height: int = 1080) -> Path:
    try:
        from PyQt6.QtGui import QColor, QImage, QPainter
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyQt6 is required for PNG export.") from exc
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor("#1a1a2e"))
    painter = QPainter(image)
    try:
        for el in state.get("elements", []):
            painter.fillRect(el["x"], el["y"], el["width"], el["height"], QColor(el.get("color", "#FFFFFF")))
    finally:
        painter.end()
    out = Path(path)
    if not image.save(str(out), "PNG"):
        raise RuntimeError(f"Could not write export to {out}")
    return out
