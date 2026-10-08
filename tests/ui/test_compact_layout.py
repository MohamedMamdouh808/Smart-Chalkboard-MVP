"""T008: compact layout — order, sizes, disjointness, board gain (3 sizes)."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui import theme
from smartboard.ui.main_window import MainWindow

SIZES = [(960, 540), (1366, 768), (1920, 1080)]
# T001 baselines (pre-change board heights at the same window sizes).
BASELINES = {(960, 540): 332, (1366, 768): 560, (1920, 1080): 872}


def _window(view_w: int, view_h: int) -> MainWindow:
    window = MainWindow()
    window.resize(view_w, view_h)
    window.show()
    return window


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_left_group_order_and_sizes(qapp: object, view_w: int, view_h: int) -> None:
    window = _window(view_w, view_h)
    mic, undo, redo = window.mic_button, window.undo_button, window.redo_button
    assert mic.x() < undo.x() < redo.x()  # mic, Undo, Redo — in that order
    assert mic.width() == theme.MIC_DIAMETER == 64
    assert undo.height() >= 44 and redo.height() >= 44
    assert window.status_pill.height() >= 30  # compact pill (~36px)
    # Window toggle lives in the top strip now, not the bottom bar.
    assert window.mode_button.parent() == window.strip


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_no_equal_stretch_and_empty_middle(qapp: object, view_w: int, view_h: int) -> None:
    window = _window(view_w, view_h)
    bar = window.control_bar.layout()
    stretches = {bar.stretch(i) for i in range(bar.count())}
    assert stretches != {1} or bar.count() < 2  # not all-equal stretching
    redo_right = window.redo_button.geometry().right()
    pill_left = window.status_pill.geometry().left()
    assert pill_left - redo_right >= theme.SPACING  # empty middle


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_no_overlaps_and_board_gain(qapp: object, view_w: int, view_h: int) -> None:
    window = _window(view_w, view_h)

    def frame(widget) -> object:
        top_left = widget.mapTo(window, widget.rect().topLeft())
        return (top_left.x(), top_left.y(), widget.width(), widget.height())

    def disjoint(a: tuple, b: tuple) -> bool:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay

    bar_items = [frame(window.mic_button), frame(window.undo_button),
                 frame(window.redo_button), frame(window.status_pill)]
    for i, first in enumerate(bar_items):
        for second in bar_items[i + 1:]:
            assert disjoint(first, second), (first, second)
    strip_items = [frame(window.heard_label), frame(window.transcription_label),
                   frame(window.result_chip), frame(window.mode_button)]
    for i, first in enumerate(strip_items):
        for second in strip_items[i + 1:]:
            assert disjoint(first, second), (first, second)
    assert window.board_view.height() > BASELINES[(view_w, view_h)]


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_window_button_beside_chip(qapp: object, view_w: int, view_h: int) -> None:
    window = _window(view_w, view_h)
    chip_right = window.result_chip.geometry().right()
    mode_left = window.mode_button.geometry().left()
    assert 0 <= mode_left - chip_right <= theme.SPACING * 2 + 8
    assert window.mode_button.width() >= 44
    assert 32 <= window.mode_button.height() <= 36  # 007 compact toggle
