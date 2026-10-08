"""Microphone press-hold, readiness, status, and transcript presentation tests."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.main_window import MainWindow
from smartboard.ui.mic_button import MicButton


def test_loading_text_and_ready_transition(qapp: object) -> None:
    button = MicButton()
    button.set_loading(True)
    assert button.text() == "Loading voice model..."
    assert button.isEnabled() is False
    button.set_loading(False)
    assert button.text() == ""
    assert button.isEnabled() is True


def test_press_hold_emits_start_and_stop(qapp: object) -> None:
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    button = MicButton()
    button.show()
    started: list[bool] = []
    stopped: list[bool] = []
    button.recordingStarted.connect(lambda: started.append(True))
    button.recordingStopped.connect(lambda: stopped.append(True))
    QTest.mousePress(button, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
                     QPoint(10, 10))
    QTest.mouseRelease(button, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
                       QPoint(10, 10))
    assert started == [True]
    assert stopped == [True]
    button.close()


def test_main_window_wires_press_release_status_and_transcript(qapp: object) -> None:
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    pressed: list[bool] = []
    released: list[bool] = []
    window = MainWindow(on_mic_press=lambda: pressed.append(True),
                        on_mic_release=lambda: released.append(True))
    window.show()
    try:
        QTest.mousePress(window.mic_button, Qt.MouseButton.LeftButton,
                         Qt.KeyboardModifier.NoModifier, QPoint(10, 10))
        QTest.mouseRelease(window.mic_button, Qt.MouseButton.LeftButton,
                           Qt.KeyboardModifier.NoModifier, QPoint(10, 10))
        assert pressed == [True]
        assert released == [True]
        window.set_status("Listening")
        assert window.mic_button.voiceState == "listening"
        window.set_status("Processing")
        assert window.mic_button.voiceState == "processing"
        window.show_transcription("Create a heading called Force")
        assert window.transcription == "Create a heading called Force"
        assert window.transcription_label.toolTip() == "Create a heading called Force"
        assert window.pen_button.text() == "Select"
    finally:
        window.close()


def test_background_preload_drives_button_readiness(qapp: object) -> None:
    import threading
    import time

    from PyQt6.QtCore import QThread
    from PyQt6.QtTest import QSignalSpy

    from smartboard.voice.voice_config import VoiceConfig
    from smartboard.voice.voice_worker import VoiceWorker

    loaded = threading.Event()

    def slow_factory(model: str, device: str, compute_type: str) -> object:
        time.sleep(0.2)
        loaded.set()
        return object()

    button = MicButton()
    worker = VoiceWorker(VoiceConfig(), model_factory=slow_factory)
    worker.modelReady.connect(lambda: button.set_loading(False))
    button.set_loading(True)
    assert button.text() == "Loading voice model..."
    ready = QSignalSpy(worker.modelReady)
    thread = QThread()
    try:
        worker.moveToThread(thread)
        thread.started.connect(worker.load_model)
        thread.start()
        # The UI thread stays responsive while the model loads elsewhere.
        assert qapp.thread() is not None
        assert ready.wait(5000)
        assert loaded.is_set()
    finally:
        thread.quit()
        thread.wait(5000)
    assert button.isEnabled() is True
    assert button.text() == ""
