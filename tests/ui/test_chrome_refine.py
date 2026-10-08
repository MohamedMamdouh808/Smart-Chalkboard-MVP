"""T007: chrome refinement — input fill, input contrast, board-width rule."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui import theme
from smartboard.ui.main_window import MainWindow

SIZES = [(960, 540), (1366, 768), (1920, 1080)]


def _window(monkeypatch: pytest.MonkeyPatch, view_w: int, view_h: int) -> MainWindow:
    monkeypatch.setenv("SMARTBOARD_DEV_INPUT", "1")
    window = MainWindow()
    window.resize(view_w, view_h)
    window.show()
    return window


def _frame(window: MainWindow, widget) -> tuple:
    top_left = widget.mapTo(window, widget.rect().topLeft())
    return (top_left.x(), top_left.y(), widget.width(), widget.height())


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_input_fills_gap_both_sides(
    monkeypatch: pytest.MonkeyPatch, qapp: object, view_w: int, view_h: int
) -> None:
    window = _window(monkeypatch, view_w, view_h)
    _, _, _redo_w, _ = _frame(window, window.redo_button)
    anchor_right = _frame(window, window.pen_button)[0] + _frame(window, window.pen_button)[2]
    dev = _frame(window, window.dev_input)
    pill = _frame(window, window.status_pill)
    gap = 8  # theme 8px neighbor gaps (+ layout spacing tolerance)
    assert abs(dev[0] - anchor_right) <= gap + window.control_bar.layout().spacing()
    assert abs(pill[0] - (dev[0] + dev[2])) <= gap + window.control_bar.layout().spacing()
    assert dev[3] >= 40  # ~44px compact height
    window.close()


def test_input_text_contrast() -> None:
    from tests.ui.test_theme_contrast import ratio

    assert ("#F5F5F5", theme.INPUT_BG, "normal") in theme.CONTRAST_PAIRS
    assert ratio("#F5F5F5", theme.INPUT_BG) >= 4.5


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_board_width_rule(
    monkeypatch: pytest.MonkeyPatch, qapp: object, view_w: int, view_h: int
) -> None:
    window = _window(monkeypatch, view_w, view_h)
    board_w = window.board_view.width()
    # Infinite layout: the board fills the layout area regardless of aspect.
    assert view_w - board_w <= 2 * theme.BOARD_MARGIN
    # Camera transform is exact and invertible at any window size.
    transform = window.board_view.transform()
    assert transform.to_world(*transform.to_screen(100, 100)) == (100, 100)
    window.close()
