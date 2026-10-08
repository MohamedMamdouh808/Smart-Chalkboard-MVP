"""T013: prompt golden-file test — five sections, 12-lock, no side effects."""

from __future__ import annotations

from smartboard.ai.prompt import build
from smartboard.core.command_schema import COMMANDS

CONTEXT = {
    "transcript": "Make this bigger",
    "elements": [{"id": "text_001", "type": "text", "label": "F = ma", "x": 160, "y": 200}],
    "selected_element_id": "text_001",
    "commands": list(COMMANDS),
}


def test_prompt_has_all_five_sections() -> None:
    prompt = build("Make this bigger", CONTEXT)
    assert "EXACTLY ONE JSON object" in prompt
    assert "Allowed commands:" in prompt
    assert "Board elements:" in prompt
    assert 'Transcript (verbatim): "Make this bigger"' in prompt
    assert "clarification_needed" in prompt


def test_prompt_locks_twelve_commands() -> None:
    prompt = build("hi", CONTEXT)
    assert len(COMMANDS) == 12
    for name in COMMANDS:
        assert name in prompt


def test_prompt_carries_selection_rule() -> None:
    prompt = build("delete that", {**CONTEXT, "selected_element_id": None})
    assert "text_001" in prompt
    assert "(none)" in prompt
    assert "instead of guessing" in prompt


def test_prompt_requests_no_side_effects() -> None:
    prompt = build("hi", CONTEXT).lower()
    assert "side effect" not in prompt
    assert "execute code" not in prompt
    assert "13th" not in prompt
