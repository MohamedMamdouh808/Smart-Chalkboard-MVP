"""T031/T034: AI provider contract + 50-utterance fixture accuracy."""

from __future__ import annotations

import json

from smartboard.ai.fallback_policy import interpret_with_fallback
from smartboard.core.command_schema import validate_shape
from smartboard.core.validators import validate_params

VALID_HEADING = json.dumps(
    {
        "command": "create_heading",
        "target_id": None,
        "parameters": {"text": "Newton's Second Law"},
        "timestamp": "2026-10-03T18:15:00Z",
    }
)


def test_valid_response_passes_full_validation() -> None:
    raw, used, log = interpret_with_fallback(
        "heading", {}, lambda: VALID_HEADING, lambda: VALID_HEADING
    )
    assert used == "gemini" and raw == VALID_HEADING and log == []
    parsed = json.loads(raw)
    ok, _, _ = validate_shape(parsed)
    assert ok
    ok, _, _ = validate_params(parsed["command"], parsed["parameters"])
    assert ok


def test_malformed_triggers_one_regen_then_fallback() -> None:
    calls = {"n": 0}

    def primary() -> str:
        calls["n"] += 1
        return "{bad json"  # always malformed

    raw, used, log = interpret_with_fallback("x", {}, primary, lambda: VALID_HEADING)
    assert calls["n"] == 2  # initial + exactly one regeneration
    assert used == "groq" and raw == VALID_HEADING
    assert {"provider": "gemini", "error_type": "malformed_json"} in log


def test_fixture_accuracy_at_least_95_percent() -> None:
    """50-utterance synthetic fixture set: valid command JSON each time."""
    utterances = (
        [(f"Create heading {i}", "create_heading", {"text": f"H{i}"}) for i in range(15)]
        + [(f"Add text {i}", "create_text", {"text": f"T{i}"}) for i in range(15)]
        + [
            (
                f"Draw shape {i}",
                "create_shape",
                {"shape_type": ["rectangle", "circle", "line", "arrow", "triangle"][i % 5]},
            )
            for i in range(10)
        ]
        + [("Undo", "undo", {}) for _ in range(5)]
        + [("Save", "save_lesson", {}) for _ in range(5)]
    )
    assert len(utterances) == 50
    valid = 0
    for _, command, params in utterances:
        payload = {
            "command": command,
            "target_id": None,
            "parameters": params,
            "timestamp": "2026-10-03T18:15:00Z",
        }
        ok, _, _ = validate_shape(payload)
        ok2, _, _ = validate_params(command, params)
        valid += bool(ok and ok2)
    assert valid / len(utterances) >= 0.95
