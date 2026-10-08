"""T027/T028: push-to-talk recorder + Whisper fixtures (audio always deleted)."""

from __future__ import annotations

from pathlib import Path

from smartboard.ui.status import MAX_UTTERANCE_S
from smartboard.voice.audio_cleanup import EMPTY_MESSAGE, delete_audio, sweep_temp_audio
from smartboard.voice.recorder import PushToTalk, Recording
from smartboard.voice.whisper_service import WhisperService


def test_press_and_hold_release_submits() -> None:
    ptt = PushToTalk(backend=lambda: Recording(audio=b"\x00" * 100, duration_s=1.0))
    ptt.press()
    rec = ptt.release()
    assert rec is not None and rec.audio


def test_release_without_press_yields_nothing() -> None:
    ptt = PushToTalk(backend=lambda: Recording(audio=b"x", duration_s=0.5))
    assert ptt.release() is None


def test_empty_recording_yields_retry_not_ai_call() -> None:
    ptt = PushToTalk(backend=lambda: Recording(audio=b"", duration_s=0.0))
    ptt.press()
    assert ptt.release() is None


def test_utterance_cap_is_fifteen_seconds() -> None:
    assert MAX_UTTERANCE_S == 15


def test_whisper_fixture_transcribes_and_deletes_audio(tmp_path: Path) -> None:
    audio = tmp_path / "utt_001.wav"
    audio.write_bytes(b"fake-audio")
    svc = WhisperService(transcriber=lambda _p: "Create a heading called Force")
    assert svc.transcribe(audio) == "Create a heading called Force"
    assert not audio.exists()  # deleted after transcription


def test_whisper_failure_still_deletes_audio(tmp_path: Path) -> None:
    audio = tmp_path / "utt_002.wav"
    audio.write_bytes(b"fake-audio")

    def boom(_p: str) -> str:
        raise RuntimeError("whisper crashed")

    svc = WhisperService(transcriber=boom)
    try:
        svc.transcribe(audio)
        raised = False
    except RuntimeError:
        raised = True
    assert raised and not audio.exists()


def test_empty_transcription_shows_retry_message(tmp_path: Path) -> None:
    audio = tmp_path / "utt_003.wav"
    audio.write_bytes(b"silence")
    svc = WhisperService(transcriber=lambda _p: "   ")
    assert svc.transcribe_or_retry_message(audio) == EMPTY_MESSAGE


def test_startup_sweep_clears_temp_audio(tmp_path: Path) -> None:
    (tmp_path / "utt_a.wav").write_bytes(b"x")
    (tmp_path / "keep.txt").write_bytes(b"x")
    assert sweep_temp_audio(tmp_path) == 1
    assert (tmp_path / "keep.txt").exists()
    delete_audio(tmp_path / "missing.wav")  # no error on absent file
