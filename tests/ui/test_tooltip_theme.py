"""Tooltip theme tests: generated QSS, delay hint, and text preservation."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui import theme
from smartboard.ui.main_window import MainWindow
from smartboard.ui.tooltip_style import TooltipStyle


def test_tooltip_rule_uses_theme_tokens() -> None:
    qss = theme.build_stylesheet()
    assert "QToolTip" in qss
    assert theme.BUTTON_BG in qss
    assert theme.TEXT in qss
    assert theme.BUTTON_BORDER in qss
    assert f"font-size: {theme.FONT_BUTTON}px" in qss
    assert f"border-radius: {theme.CONTROL_RADIUS}px" in qss
    assert f"padding: {theme.TOOLTIP_PAD_V}px {theme.TOOLTIP_PAD_H}px" in qss
    assert theme.TOOLTIP_PAD_V == 6
    assert theme.TOOLTIP_PAD_H == 10
    assert theme.TOOLTIP_WAKEUP_DELAY_MS == 500


def test_proxy_style_returns_themed_delay_only(qapp: object) -> None:
    from PyQt6.QtWidgets import QProxyStyle, QStyle

    style = TooltipStyle()
    assert style.styleHint(QStyle.StyleHint.SH_ToolTip_WakeUpDelay) == 500
    hint = QStyle.StyleHint.SH_EtchDisabledText
    assert style.styleHint(hint) == QProxyStyle().styleHint(hint)


def test_tooltip_texts_unchanged(qapp: object) -> None:
    window = MainWindow()
    try:
        assert window.mode_button.toolTip() == "Window"
        assert window.pen_button.toolTip() == "Toggle Pen / Select mode (P / S)"
        window.show_transcription("Create a heading called Force")
        assert window.transcription_label.toolTip() == "Create a heading called Force"
    finally:
        window.close()
