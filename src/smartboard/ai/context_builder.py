"""Minimal board-context builder (least exposure: summaries only)."""

from __future__ import annotations

from typing import Any


def _short_label(el: dict[str, Any]) -> str:
    text = str(el.get("text", "") or el.get("shape_type", "") or "")
    text = " ".join(text.split())
    return text[:40]


def build_context(transcript: str, state: dict[str, Any], commands: list[str]) -> dict[str, Any]:
    elements = [
        {"id": el["id"], "type": el["type"], "label": _short_label(el),
         "x": el["x"], "y": el["y"]}
        for el in state.get("elements", [])
    ]
    return {
        "transcript": transcript,
        "elements": elements,
        "selected_element_id": state.get("selected_element_id"),
        "commands": commands,
    }
