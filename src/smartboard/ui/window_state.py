"""Window geometry persistence (local settings only — never lesson data)."""

from __future__ import annotations

from typing import Any

ORG_NAME = "SmartChalkboard"
APP_NAME = "SmartChalkboard"
MODE_KEY = "window/mode"
RECT_KEY = "window/rect"  # [x, y, width, height] of the normal window
PEN_WIDTH_KEY = "pen/width"

MODE_FULLSCREEN = "fullscreen"
MODE_NORMAL = "normal"
MODE_MAXIMIZED = "maximized"

#: Pen width is a settings-only preference (no main-bar control).
PEN_WIDTHS: dict[str, int] = {"thin": 2, "medium": 4, "thick": 8}
DEFAULT_PEN_WIDTH_NAME = "medium"


def make_settings(path: str | None = None) -> Any:
    """Default user-scope settings, or a file-backed store for tests."""
    from PyQt6.QtCore import QSettings

    if path is not None:
        return QSettings(path, QSettings.Format.IniFormat)
    return QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, ORG_NAME, APP_NAME)


def _mode_of(window: Any) -> str:
    if window.isFullScreen():
        return MODE_FULLSCREEN
    if window.isMaximized():
        return MODE_MAXIMIZED
    return MODE_NORMAL


def load_mode(settings: Any | None = None) -> str:
    settings = settings or make_settings()
    try:
        mode = str(settings.value(MODE_KEY, MODE_FULLSCREEN))
    except Exception:  # noqa: BLE001 - settings faults fall back to defaults
        return MODE_FULLSCREEN
    return mode if mode in (MODE_FULLSCREEN, MODE_NORMAL, MODE_MAXIMIZED) else MODE_FULLSCREEN


def load_pen_width(settings: Any | None = None) -> int:
    """Pen width in canvas units; thin/medium/thick stored by name."""
    from smartboard.core.board import DEFAULT_DRAWING_WIDTH

    settings = settings or make_settings()
    try:
        name = str(settings.value(PEN_WIDTH_KEY, DEFAULT_PEN_WIDTH_NAME))
    except Exception:  # noqa: BLE001 - settings faults fall back to defaults
        return DEFAULT_DRAWING_WIDTH
    return PEN_WIDTHS.get(name, DEFAULT_DRAWING_WIDTH)


def save_pen_width_name(name: str, settings: Any | None = None) -> int:
    """Persist a thin/medium/thick choice; unknown names keep the default."""

    if name not in PEN_WIDTHS:
        name = DEFAULT_PEN_WIDTH_NAME
    settings = settings or make_settings()
    settings.setValue(PEN_WIDTH_KEY, name)
    settings.sync()
    return PEN_WIDTHS[name]


def save_state(window: Any, settings: Any | None = None) -> None:
    settings = settings or make_settings()
    settings.setValue(MODE_KEY, _mode_of(window))
    geo = window.geometry()
    settings.setValue(RECT_KEY, [geo.x(), geo.y(), geo.width(), geo.height()])
    settings.sync()


def restore_state(window: Any, settings: Any | None = None) -> str:
    """Apply persisted size/position/mode. Returns the mode."""
    settings = settings or make_settings()
    mode = load_mode(settings)
    window.show_restored(mode)
    try:
        rect = settings.value(RECT_KEY)
        if rect is not None and mode != MODE_FULLSCREEN:
            x, y, w, h = (int(v) for v in rect)
            window.setGeometry(x, y, max(w, 0), max(h, 0))
    except Exception:  # noqa: BLE001, S110 - geometry restore faults are silently ignored
        pass
    return mode
