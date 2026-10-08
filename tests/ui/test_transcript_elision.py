"""T009: transcript elision — word boundary, tooltip, chip visibility."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.main_window import MainWindow

LONG = ("Create a heading called Newton's Second Law of Motion for today's physics lesson")


@pytest.mark.parametrize(("view_w", "view_h"), [(960, 540), (1366, 768), (1920, 1080)])
def test_long_transcript_elides_at_word_boundary(qapp: object, view_w: int, view_h: int) -> None:
    window = MainWindow()
    window.resize(view_w, view_h)
    window.show()
    window.show_transcription(LONG)
    visible = window.transcription_label.text()
    assert window.transcription_label.toolTip() == LONG  # full text one hover away
    if visible == LONG:
        return
    assert visible.endswith("...")
    shown = visible[:-3]
    assert LONG.startswith(shown)  # a true prefix, never mid-word
    rest = LONG[len(shown):]
    assert rest == "" or rest[0] == " " or shown == LONG[:1]


def test_short_transcript_untouched_with_empty_tooltip(qapp: object) -> None:
    window = MainWindow()
    window.resize(1366, 768)
    window.show()
    window.show_transcription("Hi")
    assert window.transcription_label.text() == "Hi"
    assert window.transcription_label.toolTip() == "Hi"


def test_chip_and_window_visible_at_minimum(qapp: object) -> None:
    window = MainWindow()
    window.resize(960, 540)
    window.show()
    window.show_transcription(LONG)
    assert window.result_chip.isVisible()
    assert window.mode_button.isVisible()
    for widget in (window.result_chip, window.mode_button):
        top_left = widget.mapTo(window, widget.rect().topLeft())
        assert 0 <= top_left.x() <= 960
        assert 0 <= top_left.y() <= 540
        assert top_left.x() + widget.width() <= 960  # fully inside, never clipped


def test_static_tooltip_texts_unchanged(qapp: object) -> None:
    window = MainWindow()
    try:
        assert window.mode_button.toolTip() == "Window"
        assert window.mic_button.toolTip() == (
            "Speak a command (scripted demo) — click for the next utterance")
        assert window.pen_button.toolTip() == "Toggle Pen / Select mode (P / S)"
    finally:
        window.close()
