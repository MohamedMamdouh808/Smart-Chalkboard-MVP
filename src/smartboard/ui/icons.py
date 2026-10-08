"""Cached SVG icon loader with theme tinting (missing file fails loudly)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import theme

ICON_DIR = Path(__file__).parent / "icons"
_cache: dict[tuple[str, str], Any] = {}


def icon_path(name: str) -> Path:
    path = ICON_DIR / f"{name}.svg"
    if not path.is_file():
        raise FileNotFoundError(f"Bundled icon missing: {path}")
    return path


def load_icon(name: str, color: str = theme.TEXT) -> Any:
    """Return a QIcon for a bundled SVG, strokes tinted to `color`."""
    key = (name, color)
    if key in _cache:
        return _cache[key]
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtGui import QIcon, QImage, QPainter, QPixmap
    from PyQt6.QtSvg import QSvgRenderer

    data = icon_path(name).read_bytes().replace(b"currentColor", color.encode())
    image = QImage(64, 64, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    QSvgRenderer(QByteArray(data)).render(painter)
    painter.end()
    icon = QIcon(QPixmap.fromImage(image))
    _cache[key] = icon
    return icon


def clear_cache() -> None:
    _cache.clear()
