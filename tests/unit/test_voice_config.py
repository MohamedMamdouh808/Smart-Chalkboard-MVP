"""Voice transcription configuration tests."""

from __future__ import annotations

import pytest

from smartboard.voice.voice_config import (
    DEFAULT_DEVICE,
    DEFAULT_MODEL,
    VoiceConfig,
    load_voice_config,
)


def test_defaults_select_base_english_on_cpu() -> None:
    assert DEFAULT_MODEL == "base.en"
    assert DEFAULT_DEVICE == "cpu"
    config = VoiceConfig()
    assert (config.model, config.device) == ("base.en", "cpu")


def test_environment_overrides_model_and_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHISPER_MODEL", "small.en")
    monkeypatch.setenv("WHISPER_DEVICE", "cuda")
    config = load_voice_config()
    assert (config.model, config.device) == ("small.en", "cuda")


def test_blank_values_fall_back_to_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHISPER_MODEL", "   ")
    monkeypatch.setenv("WHISPER_DEVICE", "")
    config = load_voice_config()
    assert (config.model, config.device) == ("base.en", "cpu")
