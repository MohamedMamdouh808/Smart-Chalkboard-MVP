"""T005: dev input bar — placement, gating, sizes, board identity, behavior."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.orchestrator import build_app
from smartboard.ui.main_window import MainWindow

SIZES = [(960, 540), (1366, 768), (1920, 1080)]


def _window(monkeypatch: pytest.MonkeyPatch, dev_on: bool) -> MainWindow:
    if dev_on:
        monkeypatch.setenv("SMARTBOARD_DEV_INPUT", "1")
    else:
        monkeypatch.delenv("SMARTBOARD_DEV_INPUT", raising=False)
    window = MainWindow()
    window.resize(1366, 768)
    window.show()
    return window


def test_hidden_when_flag_off(monkeypatch: pytest.MonkeyPatch, qapp: object) -> None:
    window = _window(monkeypatch, dev_on=False)
    assert window.dev_input.isVisible() is False
    # Bar matches the pre-move layout: mic, Undo, Redo, stretch, pill.
    assert window.mode_button.parent() == window.strip
    assert window.strip.findChildren(QtWidgets.QLineEdit) == []
    window.close()


def test_visible_in_bar_when_flag_on(monkeypatch: pytest.MonkeyPatch, qapp: object) -> None:
    window = _window(monkeypatch, dev_on=True)
    assert window.dev_input.isVisible() is True
    assert window.dev_input.parent() == window.control_bar
    assert window.dev_input.placeholderText().startswith("Dev transcript")
    assert window.dev_input.height() >= 40  # ~44px compact height
    assert window.dev_input.width() > 200  # fills the gap after zoom controls
    assert window.dev_input.font().pointSize() >= 18
    # Order: mic, Undo, Redo, zoom controls, input, pill.
    xs = [
        window.mic_button.x(),
        window.undo_button.x(),
        window.redo_button.x(),
        window.zoom_in_button.x(),
        window.dev_input.x(),
        window.status_pill.x(),
    ]
    assert xs == sorted(xs)


@pytest.mark.parametrize(("view_w", "view_h"), SIZES)
def test_no_overlap_and_board_identity(
    monkeypatch: pytest.MonkeyPatch, qapp: object, view_w: int, view_h: int
) -> None:
    on = _window(monkeypatch, dev_on=True)
    on.resize(view_w, view_h)
    off = MainWindow()
    off.resize(view_w, view_h)
    off.show()
    qapp.processEvents()

    def frame(window: MainWindow, widget) -> tuple:
        top_left = widget.mapTo(window, widget.rect().topLeft())
        return (top_left.x(), top_left.y(), widget.width(), widget.height())

    def disjoint(a: tuple, b: tuple) -> bool:
        return (
            a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1]
        )

    bar_items = [
        frame(on, w)
        for w in (on.mic_button, on.undo_button, on.redo_button, on.dev_input, on.status_pill)
    ]
    for i, first in enumerate(bar_items):
        for second in bar_items[i + 1 :]:
            assert disjoint(first, second), (first, second)
    assert on.board_view.height() == off.board_view.height()  # canvas geometry identical
    on.close()
    off.close()


def test_submit_clears_and_disables_during_processing(
    monkeypatch: pytest.MonkeyPatch, qapp: object
) -> None:
    import concurrent.futures
    import json

    from smartboard.app import main as main_module
    from smartboard.app import workers as workers_module

    heading = json.dumps(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Hi"},
            "timestamp": "2026-10-03T18:15:00Z",
        }
    )

    class FakeProvider:
        def interpret(self, transcript: str, context: dict) -> dict[str, str]:
            return {"raw_text": heading}

    monkeypatch.setenv("SMARTBOARD_DEV_INPUT", "1")
    monkeypatch.setattr("smartboard.ai.config.get_provider", lambda config: FakeProvider())
    pending: concurrent.futures.Future = concurrent.futures.Future()
    monkeypatch.setattr(workers_module, "submit", lambda fn, *args, **kwargs: pending)

    app = build_app()
    holder = {}
    window = MainWindow(
        on_dev_text=lambda text: main_module.submit_dev_transcript(app, holder, text)
    )
    holder["window"] = window
    window.show()
    window.dev_input.setText("Create a heading")
    window.dev_input.returnPressed.emit()
    assert window.dev_input.text() == ""  # cleared right after submit
    assert window.dev_input.isEnabled() is False  # disabled while processing
    pending.set_result(app.handle_live_transcript("Create a heading", FakeProvider()))
    import time as _time

    deadline = _time.monotonic() + 5
    while not window.dev_input.isEnabled() and _time.monotonic() < deadline:
        _time.sleep(0.05)
        qapp.processEvents()
    assert window.dev_input.isEnabled() is True  # re-enabled on delivery
    assert app.engine.board.elements[0].extra["text"] == "Hi"
    window.close()


def test_dev_input_absent_from_strip(monkeypatch: pytest.MonkeyPatch, qapp: object) -> None:
    window = _window(monkeypatch, dev_on=True)
    assert window.strip.findChildren(QtWidgets.QLineEdit) == []
    window.close()
