"""T018: chrome contrast + minima + no-overlap at 960x540."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.main_window import MIN_TARGET_PX, MainWindow  # noqa: E402


def _luminance(hex_color: str) -> float:
    hex_color = hex_color.lstrip("#")
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio(fg: str, bg: str) -> float:
    lighter, darker = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_button_palette_meets_4_5_to_1() -> None:
    from smartboard.ui import theme

    for bg in theme.BUTTON_BACKGROUNDS:
        assert _ratio(theme.BUTTON_TEXT, bg) >= 4.5, bg


def test_controls_meet_48px_minima(qapp: object) -> None:
    # 004 compact layout: 44px minima for secondary controls (mic stays 64).
    assert MIN_TARGET_PX == 48
    window = MainWindow()
    window.resize(960, 540)
    window.show()
    assert window.mic_button.minimumHeight() >= 64
    for btn in (window.undo_button, window.redo_button):
        assert btn.minimumHeight() >= 44
        assert btn.isVisible()
    assert 32 <= window.mode_button.height() <= 36  # 007 compact toggle


def test_chrome_never_overlaps_board(qapp: object) -> None:
    window = MainWindow()
    window.resize(960, 540)
    window.show()
    board = window.board_view.geometry()
    bar = window.control_bar.geometry()
    strip = window.transcription_label.geometry()
    assert bar.bottom() <= window.height()
    assert window.strip.height() >= 44  # 007 slim strip
    assert strip.height() >= 18  # transcript text still readable
    assert board.height() > 0
    # Siblings in a vertical layout: board sits between strip and bar.
    assert strip.bottom() <= board.top() + 1
    assert board.bottom() <= bar.top() + 1
