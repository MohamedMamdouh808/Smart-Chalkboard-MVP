"""Voice microphone integration tests: loader, capture, worker, wiring, and failures."""

from __future__ import annotations

from pathlib import Path

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.voice.voice_config import VoiceConfig
from smartboard.voice.voice_worker import VoiceWorker


def test_background_model_loader_constructs_once_and_signals(qapp: object) -> None:
    from PyQt6.QtCore import QThread
    from PyQt6.QtTest import QSignalSpy

    calls: list[tuple[str, str, str]] = []

    def fake_factory(model: str, device: str, compute_type: str) -> object:
        calls.append((model, device, compute_type))
        return object()

    worker = VoiceWorker(VoiceConfig(), model_factory=fake_factory)
    loading = QSignalSpy(worker.statusChanged)
    ready = QSignalSpy(worker.modelReady)
    thread = QThread()
    try:
        worker.moveToThread(thread)
        thread.started.connect(worker.load_model)
        thread.start()
        assert ready.wait(5000)
        assert len(loading) >= 1
        assert list(loading[0]) == ["loading"]
    finally:
        thread.quit()
        thread.wait(5000)
    worker.load_model()
    assert calls == [("base.en", "cpu", "int8")]


def test_press_hold_recorder_buffers_memory_only_audio(tmp_path) -> None:
    import numpy as np

    from smartboard.voice.recorder import SoundRecorder

    frames = [np.zeros(16000, dtype=np.float32), np.ones(8000, dtype=np.float32)]
    recorder = SoundRecorder(backend=lambda: frames)
    recorder.start()
    recording = recorder.stop()
    assert recording is not None
    assert recording.samples.dtype == np.float32
    assert recording.samples.shape == (24000,)
    assert recording.sample_rate == 16000
    assert list(tmp_path.glob("*.wav")) == []
    assert list(tmp_path.glob("*.mp3")) == []


def test_recorder_enforces_fifteen_second_cap() -> None:
    import numpy as np

    from smartboard.voice.recorder import SoundRecorder

    recorder = SoundRecorder(backend=lambda: [np.zeros(16 * 16000, dtype=np.float32)])
    recorder.start()
    recording = recorder.stop()
    assert recording is not None
    assert recording.samples.shape == (15 * 16000,)


def test_recorder_reports_missing_or_denied_microphones() -> None:
    import pytest

    from smartboard.voice.recorder import (
        MicrophoneDeniedError,
        MicrophoneUnavailableError,
        SoundRecorder,
    )

    def missing() -> object:
        raise MicrophoneUnavailableError("No microphone was found.")

    def denied() -> object:
        raise MicrophoneDeniedError("Microphone access was denied.")

    with pytest.raises(MicrophoneUnavailableError, match="No microphone was found"):
        SoundRecorder(backend=missing).stop()
    with pytest.raises(MicrophoneDeniedError, match="Microphone access was denied"):
        SoundRecorder(backend=denied).stop()


def test_array_transcription_uses_required_settings_and_telemetry(tmp_path) -> None:
    import numpy as np

    from smartboard.voice.whisper_service import WhisperService

    calls: list[tuple[object, str, int, bool]] = []
    telemetry: list[dict] = []

    class FakeModel:
        def transcribe(self, audio, language: str, beam_size: int, vad_filter: bool):
            calls.append((audio, language, beam_size, vad_filter))
            return ([type("Segment", (), {"text": "  hello  "})()], None)

    service = WhisperService(
        model="base.en",
        device="cpu",
        model_factory=lambda model, device, compute: FakeModel(),
        telemetry=telemetry.append,
    )
    samples = np.zeros(16000, dtype=np.float32)
    text, duration_ms = service.transcribe_samples(samples)
    assert text == "hello"
    assert duration_ms >= 0.0
    assert len(calls) == 1
    audio, language, beam_size, vad_filter = calls[0]
    assert isinstance(audio, np.ndarray) and audio.dtype == np.float32
    assert (language, beam_size, vad_filter) == ("en", 1, True)
    assert telemetry == [
        {"duration_ms": duration_ms, "model": "base.en", "device": "cpu", "outcome": "transcript"}
    ]
    assert list(tmp_path.glob("*.wav")) == []


def test_worker_transcribes_in_background_and_emits_signals(qapp: object, tmp_path) -> None:
    import numpy as np
    from PyQt6.QtCore import QThread
    from PyQt6.QtTest import QSignalSpy

    def fake_transcribe(samples):
        assert samples.shape == (16000,)
        return ("create heading", 12.5)

    worker = VoiceWorker(
        VoiceConfig(),
        model_factory=lambda model, device, compute: object(),
        transcriber=fake_transcribe,
    )
    status = QSignalSpy(worker.statusChanged)
    transcripts = QSignalSpy(worker.transcriptReady)
    finished = QSignalSpy(worker.finished)
    thread = QThread()
    try:
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.transcribe_samples(np.zeros(16000, dtype=np.float32)))
        thread.start()
        assert finished.wait(5000)
    finally:
        thread.quit()
        thread.wait(5000)
    assert list(status[0]) == ["processing"]
    assert list(transcripts[0]) == ["create heading", 12.5]
    assert list(tmp_path.glob("*.wav")) == []


def test_finished_voice_transcript_uses_developer_text_path() -> None:
    from types import SimpleNamespace

    from smartboard.app import main as main_module
    from smartboard.app.orchestrator import build_app

    calls: list[tuple[object, object, str]] = []
    marked: list[bool] = []
    app = build_app()
    holder: dict[str, object] = {}
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(
            main_module,
            "submit_dev_transcript",
            lambda orchestrator, window_holder, transcript: calls.append(
                (orchestrator, window_holder, transcript)
            ),
        )
        grouper = SimpleNamespace(mark_interaction=lambda: marked.append(True))
        main_module.handle_voice_transcript(app, holder, grouper, "Create a heading")
    finally:
        monkeypatch.undo()
    assert marked == [True]
    assert calls == [(app, holder, "Create a heading")]


def test_short_silent_failed_and_unavailable_audio_stays_private(tmp_path) -> None:
    import numpy as np
    from PyQt6.QtCore import QThread
    from PyQt6.QtTest import QSignalSpy

    from smartboard.voice.audio_cleanup import EMPTY_MESSAGE
    from smartboard.voice.recorder import (
        MicrophoneDeniedError,
        MicrophoneUnavailableError,
        SoundRecorder,
    )
    from smartboard.voice.whisper_service import WhisperService

    short = SoundRecorder(backend=lambda: [np.zeros(1000, dtype=np.float32)])
    short.start()
    assert short.stop() is None

    silent = WhisperService(model_factory=lambda model, device, compute: FakeArrayModel(""))
    text, _ = silent.transcribe_samples(np.zeros(16000, dtype=np.float32))
    assert text == ""

    def failing_array(samples):
        raise RuntimeError("inference exploded")

    worker = VoiceWorker(
        VoiceConfig(),
        model_factory=lambda model, device, compute: object(),
        transcriber=failing_array,
    )
    failed = QSignalSpy(worker.failed)
    transcripts = QSignalSpy(worker.transcriptReady)
    finished = QSignalSpy(worker.finished)
    thread = QThread()
    try:
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.transcribe_samples(np.zeros(16000, dtype=np.float32)))
        thread.start()
        assert finished.wait(5000)
    finally:
        thread.quit()
        thread.wait(5000)
    assert len(transcripts) == 0
    assert list(failed[0]) == ["Transcription failed: inference exploded"]
    assert EMPTY_MESSAGE == "I couldn't understand the audio. Please try again."

    def missing() -> object:
        raise MicrophoneUnavailableError("No microphone was found.")

    def denied() -> object:
        raise MicrophoneDeniedError("Microphone access was denied.")

    with pytest.raises(MicrophoneUnavailableError):
        SoundRecorder(backend=missing).stop()
    with pytest.raises(MicrophoneDeniedError):
        SoundRecorder(backend=denied).stop()
    assert list(tmp_path.glob("*.wav")) == []
    assert list(tmp_path.glob("*.mp3")) == []


class FakeArrayModel:
    def __init__(self, text: str) -> None:
        self._text = text

    def transcribe(self, audio, language: str, beam_size: int, vad_filter: bool):
        assert language == "en" and beam_size == 1 and vad_filter is True
        return ([type("Segment", (), {"text": self._text})()], None)


def _fixture_samples() -> object:
    import wave

    import numpy as np
    from scipy.signal import resample

    fixture = Path(__file__).resolve().parent.parent / "fixtures" / "audio" / "command.wav"
    with wave.open(str(fixture), "rb") as handle:
        assert handle.getnchannels() == 1 and handle.getsampwidth() == 2
        rate = handle.getframerate()
        frames = handle.readframes(handle.getnframes())
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    count = round(len(audio) * 16000 / rate)
    return resample(audio, count).astype(np.float32)


def test_real_fixture_transcription() -> None:
    from smartboard.voice.whisper_service import WhisperService

    samples = _fixture_samples()
    service = WhisperService()
    text, duration_ms = service.transcribe_samples(samples)
    assert "heading" in text.lower()
    assert duration_ms >= 0.0


def test_transcription_telemetry_carries_no_content() -> None:
    import numpy as np

    from smartboard.voice.whisper_service import WhisperService

    events: list[dict] = []
    service = WhisperService(
        model_factory=lambda model, device, compute: FakeArrayModel("hi"), telemetry=events.append
    )
    text, _ = service.transcribe_samples(np.zeros(16000, dtype=np.float32))
    assert text == "hi"
    assert len(events) == 1
    assert set(events[0]) == {"duration_ms", "model", "device", "outcome"}
    assert events[0]["outcome"] == "transcript"
    assert isinstance(events[0]["duration_ms"], float)

    failing = WhisperService(
        model_factory=lambda model, device, compute: FakeArrayModel("hi"), telemetry=events.append
    )
    failing._model = _ExplodingModel()
    with pytest.raises(RuntimeError, match="inference exploded"):
        failing.transcribe_samples(np.zeros(16000, dtype=np.float32))
    assert events[-1]["outcome"] == "error"
    assert set(events[-1]) == {"duration_ms", "model", "device", "outcome"}


class _ExplodingModel:
    def transcribe(self, audio, language: str, beam_size: int, vad_filter: bool):
        raise RuntimeError("inference exploded")
