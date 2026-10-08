"""US3B viewport AI-context/prompt contract tests (fail-first)."""

from __future__ import annotations

from typing import Any

from smartboard.ai.context_builder import build_context
from smartboard.ai.prompt import build
from smartboard.core.command_schema import COMMANDS


def _state(count: int) -> dict[str, Any]:
    return {
        "lesson_id": "lesson_001",
        "elements": [
            {
                "id": f"text_{i:03d}",
                "type": "text",
                "x": i * 10,
                "y": 0,
                "width": 100,
                "height": 50,
                "color": "#FFFFFF",
                "z": i,
                "text": f"line {i}",
            }
            for i in range(count)
        ],
        "selected_element_id": None,
        "version": 1,
    }


def test_context_uses_viewport_and_caps_elements() -> None:
    viewport = {"x": 0.0, "y": 0.0, "width": 960.0, "height": 540.0, "zoom": 1.0}
    context = build_context("hi", _state(200), list(COMMANDS), viewport=viewport)
    assert context["viewport"] == viewport
    assert "canvas" not in context
    assert len(context["elements"]) <= 50


def test_nearby_elements_included_visible_first() -> None:
    viewport = {"x": 0.0, "y": 0.0, "width": 100.0, "height": 100.0, "zoom": 1.0}
    state = {
        "lesson_id": "lesson_001",
        "elements": [
            {
                "id": "far",
                "type": "text",
                "x": 5000,
                "y": 5000,
                "width": 10,
                "height": 10,
                "color": "#fff",
                "z": 1,
                "text": "far",
            },
            {
                "id": "near",
                "type": "text",
                "x": 10,
                "y": 10,
                "width": 10,
                "height": 10,
                "color": "#fff",
                "z": 2,
                "text": "near",
            },
        ],
        "selected_element_id": None,
        "version": 1,
    }
    context = build_context("hi", state, list(COMMANDS), viewport=viewport)
    ids = [el["id"] for el in context["elements"]]
    assert ids[0] == "near"


def test_prompt_describes_unbounded_world() -> None:
    viewport = {"x": 0.0, "y": 0.0, "width": 960.0, "height": 540.0, "zoom": 1.0}
    context = build_context("add a title", _state(1), list(COMMANDS), viewport=viewport)
    prompt = build("add a title", context)
    assert "unbounded" in prompt
    assert "canvas" not in prompt.lower()
    assert len(COMMANDS) == 12
