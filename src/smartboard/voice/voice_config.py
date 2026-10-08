"""Local transcription configuration (model/device only; no secrets)."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_MODEL = "base.en"
DEFAULT_DEVICE = "cpu"


def _clean(value: object, default: str) -> str:
    text = str(value or "").strip()
    return text if text else default


@dataclass(frozen=True)
class VoiceConfig:
    model: str = DEFAULT_MODEL
    device: str = DEFAULT_DEVICE


def load_voice_config(env: Mapping[str, str] | None = None) -> VoiceConfig:
    """Read transcription settings without loading models or audio libraries."""
    source = env if env is not None else os.environ
    return VoiceConfig(
        model=_clean(source.get("WHISPER_MODEL"), DEFAULT_MODEL),
        device=_clean(source.get("WHISPER_DEVICE"), DEFAULT_DEVICE).lower(),
    )
