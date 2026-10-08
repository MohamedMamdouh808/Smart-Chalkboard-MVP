"""T020: visual regression — offscreen grabs at 1366x768 + 1920x1080.

Reference PNGs live in tests/ui/refs/ and regenerate ONLY with the
explicit `--regen-refs` run (commit the result deliberately). The diff
gate allows ≤0.5% differing pixels; structural assertions below catch
layout drift deterministically regardless of font rendering.
"""

from __future__ import annotations

from pathlib import Path

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.orchestrator import build_app  # noqa: E402
from smartboard.ui import theme  # noqa: E402
from smartboard.ui.main_window import MainWindow  # noqa: E402
from smartboard.ui.viewport import Viewport  # noqa: E402

REFS = Path("tests/ui/refs")
SIZES = [(1366, 768), (1920, 1080)]
TS = "2026-10-03T18:15:00Z"


def _seeded_window() -> MainWindow:
    app = build_app()
    app.engine.execute({"command": "create_heading", "target_id": None,
                        "parameters": {"text": "Newton's Second Law"}, "timestamp": TS})
    app.engine.execute({"command": "create_text", "target_id": None,
                        "parameters": {"text": "F = ma", "equation_style": True}, "timestamp": TS})
    app.commit_pen([[{"x": 900, "y": 700}, {"x": 1100, "y": 560}]])
    eq = [el for el in app.engine.board.elements if el.extra.get("equation_style")][0]
    app.engine.board.selected_element_id = eq.id
    window = MainWindow()
    window.render_board(app.engine.board.to_dict(), eq.id)
    window.show_transcription("Add the equation F = ma below it.")
    window.show_result({"ok": True})
    window.set_status("Idle")
    return window


def _grab_image(window: MainWindow, view_w: int, view_h: int):
    window.resize(view_w, view_h)
    window.show()
    window.repaint()
    return window.grab().toImage()


def _diff_ratio(a, b) -> float:
    assert a.width() == b.width() and a.height() == b.height()
    different = 0
    total = a.width() * a.height()
    step = max(1, total // 20000)  # sample ~20k pixels for speed
    sampled = 0
    for y in range(0, a.height(), max(1, a.height() // 150)):
        for x in range(0, a.width(), max(1, a.width() // 150)):
            sampled += 1
            if a.pixelColor(x, y).name() != b.pixelColor(x, y).name():
                different += 1
    del step
    return different / max(sampled, 1)


@pytest.mark.parametrize(("view_w", "view_h"), SIZES, ids=["1366x768", "1920x1080"])
def test_window_structure(qapp: object, view_w: int, view_h: int) -> None:
    window = _seeded_window()
    image = _grab_image(window, view_w, view_h)
    # Board surface centered: canvas center pixel is the surface color.
    board = window.board_view
    vp = Viewport.from_sizes(board.width(), board.height())
    origin = board.mapTo(window, board.rect().topLeft())
    sx, sy = vp.to_screen(960, 540)
    assert image.pixelColor(origin.x() + int(sx), origin.y() + int(sy)).name().upper() == (
        theme.BOARD_SURFACE.upper())
    # Chrome present: strip, chip, pill, buttons with minima.
    assert window.heard_label.text() == "Heard:"
    assert window.result_chip.text() == "Done"
    assert window.status_pill.text() == "Idle"
    assert window.mic_button.width() >= 64
    assert window.status_pill.height() >= 30
    for btn in (window.undo_button, window.redo_button):
        assert btn.minimumHeight() >= 44  # 004 compact controls
    assert 32 <= window.mode_button.height() <= 36  # 007 compact toggle


@pytest.mark.parametrize(("view_w", "view_h"), SIZES, ids=["1366x768", "1920x1080"])
def test_reference_match(qapp: object, view_w: int, view_h: int,
                         pytestconfig: pytest.Config) -> None:
    from PyQt6.QtGui import QImage

    window = _seeded_window()
    image = _grab_image(window, view_w, view_h)
    ref = REFS / f"window-{view_w}x{view_h}.png"
    if pytestconfig.getoption("regen_refs"):
        image.save(str(ref))
        return
    assert ref.is_file(), f"missing reference {ref} — regenerate with --regen-refs"
    expected = QImage(str(ref))
    assert (expected.width(), expected.height()) == (view_w, view_h)
    assert _diff_ratio(image, expected) <= 0.005
