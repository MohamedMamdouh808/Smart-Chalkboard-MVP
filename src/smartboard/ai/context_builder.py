"""Minimal board-context builder (least exposure: summaries only)."""

from __future__ import annotations

from typing import Any

MAX_AI_ELEMENTS = 50


def _short_label(el: dict[str, Any]) -> str:
    text = str(el.get("text", "") or el.get("shape_type", "") or "")
    text = " ".join(text.split())
    return text[:40]


def _rect_of(el: dict[str, Any]) -> tuple[float, float, float, float] | None:
    try:
        return (float(el["x"]), float(el["y"]), float(el["width"]), float(el["height"]))
    except (KeyError, TypeError, ValueError):
        return None


def _intersects(
    rect: tuple[float, float, float, float], other: tuple[float, float, float, float]
) -> bool:
    ax, ay, aw, ah = rect
    bx, by, bw, bh = other
    return ax <= bx + bw and bx <= ax + aw and ay <= by + bh and by <= ay + ah


def _summarize(el: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": el["id"],
        "type": el["type"],
        "label": _short_label(el),
        "x": el["x"],
        "y": el["y"],
    }


def build_context(
    transcript: str,
    state: dict[str, Any],
    commands: list[str],
    viewport: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build least-exposure context: visible/nearby summaries capped at 50.

    Without a viewport (legacy callers), all element summaries are included
    with the stored canvas block preserved.
    """
    elements = state.get("elements", [])
    if viewport is None:
        return {
            "transcript": transcript,
            "canvas": {
                "width": state.get("canvas", {}).get("width", 1920),
                "height": state.get("canvas", {}).get("height", 1080),
            },
            "elements": [_summarize(el) for el in elements],
            "selected_element_id": state.get("selected_element_id"),
            "commands": commands,
        }
    vx = float(viewport["x"])
    vy = float(viewport["y"])
    vw = float(viewport["width"])
    vh = float(viewport["height"])
    visible_rect = (vx, vy, vw, vh)
    nearby_rect = (vx - vw, vy - vh, vw * 3.0, vh * 3.0)
    visible: list[dict[str, Any]] = []
    nearby: list[dict[str, Any]] = []
    for el in elements:
        rect = _rect_of(el)
        if rect is None:
            continue
        if _intersects(rect, visible_rect):
            visible.append(el)
        elif _intersects(rect, nearby_rect):
            nearby.append(el)
    selected: list[dict[str, Any]] = []
    selected_id = state.get("selected_element_id")
    if selected_id is not None:
        selected = [
            el
            for el in elements
            if el.get("id") == selected_id and el not in visible and el not in nearby
        ]
    ordered = visible + nearby + selected
    return {
        "transcript": transcript,
        "viewport": {
            "x": vx,
            "y": vy,
            "width": vw,
            "height": vh,
            "zoom": float(viewport.get("zoom", 1.0)),
        },
        "elements": [_summarize(el) for el in ordered[:MAX_AI_ELEMENTS]],
        "selected_element_id": state.get("selected_element_id"),
        "commands": commands,
    }
