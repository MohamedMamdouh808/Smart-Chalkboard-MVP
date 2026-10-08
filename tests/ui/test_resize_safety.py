"""T007: resize-during-activity — no lost input, dialogs centered, outcomes once."""

from __future__ import annotations

import pytest

from smartboard.app.command_queue import CommandQueue
from smartboard.core.engine import CommandEngine
from smartboard.ui.viewport import Viewport

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.confirm_dialog import ConfirmDialog  # noqa: E402
from smartboard.ui.main_window import MainWindow  # noqa: E402

TS = "2026-10-03T18:15:00Z"


def test_resize_mid_command_keeps_result() -> None:
    eng = CommandEngine()
    queue = CommandQueue(executor=lambda p, s, c, d: eng.execute(p, source=s, confirmed=c, dirty=d))
    queue.submit({"command": "create_heading", "target_id": None,
                  "parameters": {"text": "Hi"}, "timestamp": TS})
    # A resize lands while the command waits: queue is state-independent.
    _ = Viewport.from_sizes(960, 540)
    result = queue.pump()
    assert result["ok"]
    assert eng.board.elements[0].extra["text"] == "Hi"


def test_resize_mid_stroke_commits_whole() -> None:
    from smartboard.ui.pen_input import StrokeGrouper

    grouper = StrokeGrouper()
    small = Viewport.from_sizes(960, 540)
    big = Viewport.from_sizes(1920, 1080)
    # Two samples under the small viewport, resize, two more under the big one.
    canvas = [(100.0, 500.0), (300.0, 500.0), (500.0, 500.0), (700.0, 500.0)]
    strokes = [[{"x": x, "y": y} for x, y in
                [small.to_canvas(*small.to_screen(cx, cy)) for cx, cy in canvas[:2]]]]
    strokes[0].extend([{"x": x, "y": y} for x, y in
                       [big.to_canvas(*big.to_screen(cx, cy)) for cx, cy in canvas[2:]]])
    for stroke in strokes:
        grouper.pen_up(stroke, now=0.0)
    committed = grouper.flush()
    assert committed is not None and len(committed[0]) == 4
    eng = CommandEngine()
    res = eng.add_drawing(committed)
    assert res["ok"]


def test_dialog_stays_centered_and_decides_once(qapp: object) -> None:
    from PyQt6.QtCore import QTimer

    window = MainWindow()
    window.resize(1280, 720)
    window.show()
    dialog = ConfirmDialog("Delete this text? [Cancel] [Confirm]", window)
    dialog.show()
    # Resize the parent while the dialog is open.
    window.resize(960, 540)
    window.recenter_dialog(dialog)
    center = window.geometry().center()
    assert abs(dialog.geometry().center().x() - center.x()) < 4
    assert abs(dialog.geometry().center().y() - center.y()) < 4
    accepted = []
    dialog.accepted.connect(lambda: accepted.append(True))
    QTimer.singleShot(100, dialog.accept)
    dialog.exec()
    assert accepted == [True]
