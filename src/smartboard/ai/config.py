"""AI configuration: dotenv load, AIConfig, provider factory (key hygiene first)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

SUPPORTED_PROVIDERS: tuple[str, ...] = ("groq",)
DEFAULT_MODEL = "openai/gpt-oss-20b"
TIMEOUT_S = 4.0


@dataclass(frozen=True)
class AIConfig:
    provider: str = "groq"
    groq_api_key: str | None = None
    groq_model: str = DEFAULT_MODEL
    timeout_s: float = TIMEOUT_S


def load_config(env_file: str | None = None) -> AIConfig:
    """Load `.env` (gitignored) into the process, then read AI settings.

    The key travels as a constructor argument only — this module never
    logs, prints, or includes it in errors.
    """
    from dotenv import load_dotenv

    load_dotenv(env_file)
    return AIConfig(
        provider=os.environ.get("AI_PROVIDER", "groq").strip().lower(),
        groq_api_key=os.environ.get("GROQ_API_KEY") or None,
        groq_model=os.environ.get("GROQ_MODEL", DEFAULT_MODEL),
        timeout_s=TIMEOUT_S,
    )


def get_provider(config: AIConfig, **overrides: Any) -> Any:
    """Build the configured provider. Unknown names fail fast."""
    from .providers import GroqProvider

    if config.provider == "groq":
        if not config.groq_api_key:
            raise ValueError("AI is not configured (missing GROQ_API_KEY).")
        return GroqProvider(
            api_key=config.groq_api_key,
            model=config.groq_model,
            timeout_s=config.timeout_s,
            **overrides,
        )
    supported = ", ".join(SUPPORTED_PROVIDERS)
    raise ValueError(f"Unknown AI provider '{config.provider}'. Supported: {supported}.")
