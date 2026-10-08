"""Fallback policy: 1 regeneration on same provider, then fallback, then error."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

AI_DOWN_MESSAGE = "Unable to understand the command. Please try again."


class ProviderError(Exception):
    def __init__(self, provider: str, error_type: str) -> None:
        super().__init__(f"{provider}:{error_type}")
        self.provider = provider
        self.error_type = error_type


def interpret_with_fallback(
    transcript: str,
    context: dict[str, Any],
    primary: Callable[[], str],
    fallback: Callable[[], str],
    is_valid_json: Callable[[str], bool] | None = None,
) -> tuple[str | None, str, list[dict[str, str]]]:
    """Returns (raw_text_or_None, provider_used_or_error, log_entries).

    Log entries carry provider + error type only — never keys or content.
    """
    check = is_valid_json or (_parses)
    log: list[dict[str, str]] = []
    try:
        raw = primary()
    except Exception:  # noqa: BLE001 - provider faults degrade to manual mode
        log.append({"provider": "gemini", "error_type": "call_failed"})
        raw = None
    if raw is not None and not check(raw):
        log.append({"provider": "gemini", "error_type": "malformed_json"})
        try:
            raw = primary()  # exactly one regeneration, same provider
        except Exception:  # noqa: BLE001 - provider faults degrade to manual mode
            log.append({"provider": "gemini", "error_type": "call_failed"})
            raw = None
    if raw is not None and check(raw):
        return raw, "gemini", log
    try:
        raw = fallback()
    except Exception:  # noqa: BLE001 - provider faults degrade to manual mode
        log.append({"provider": "groq", "error_type": "call_failed"})
        return None, AI_DOWN_MESSAGE, log
    if not check(raw):
        log.append({"provider": "groq", "error_type": "malformed_json"})
        return None, AI_DOWN_MESSAGE, log
    return raw, "groq", log


def _parses(raw: str) -> bool:
    try:
        parsed = json.loads(raw)
    except ValueError:
        return False
    return isinstance(parsed, dict)
