"""Application configuration — API keys from environment only."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    gemini_api_key: str | None
    groq_api_key: str | None
    whisper_model: str = "small.en"
    ai_timeout_s: float = 2.0
    queue_max: int = 5
    autosave_interval_s: int = 30


def load_config() -> Config:
    return Config(
        gemini_api_key=os.environ.get("GEMINI_API_KEY"),
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        whisper_model=os.environ.get("WHISPER_MODEL", "small.en"),
    )


def require_gemini_key(config: Config) -> str:
    if not config.gemini_api_key:
        raise RuntimeError("Missing GEMINI_API_KEY. Set it in the environment; never commit keys.")
    return config.gemini_api_key
