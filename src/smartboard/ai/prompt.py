"""Prompt builder: schemas + context + transcript + JSON-only order.

Committed, reviewable, golden-file tested. Never requests or accepts a
13th command, code, or side effects.
"""

from __future__ import annotations

from typing import Any

from smartboard.core.command_schema import COMMANDS


def _schema_block(viewport: dict[str, Any] | None = None) -> str:
    block = """Supported commands (nothing else is valid):
- create_heading {text 1-200 chars}
- create_text {text 1-2000 chars, equation_style bool; equations are equation-styled text}
- move_item {target, position {x,y} OR relative {direction up|down|left|right, distance small|medium|large|number}}
- resize_item {target, scale_factor 0.25-4.0 OR size {w,h}, min 24x24}
- delete_item {target} (needs confirmation)
- clear_board {} (needs confirmation, board must be non-empty)
- create_shape {shape_type rectangle|circle|line|arrow|triangle}
- change_color {target, color named palette or #RRGGBB}
- undo {} | redo {} | save_lesson {} | new_lesson {optional title}
Targets: explicit element id, or {"use_selection": true} to use the selected element.
"""
    if viewport is not None:
        return (
            block + "Coordinates: unbounded world units. Prefer positions inside the "
            f"visible viewport x={viewport.get('x')}, y={viewport.get('y')}, "
            f"w={viewport.get('width')}, h={viewport.get('height')}. "
            "Relative distances are screen-relative at the current zoom."
        )
    return block + "Coordinates: unbounded world units."


def _context_block(context: dict[str, Any]) -> str:
    lines = []
    for el in context.get("elements", []):
        lines.append(
            f"- {el.get('id')} [{el.get('type')}] \"{el.get('label', '')}\""
            f" at ({el.get('x')},{el.get('y')})"
        )
    elements = "\n".join(lines) if lines else "(board is empty)"
    selected = context.get("selected_element_id")
    viewport = context.get("viewport")
    if viewport is not None:
        scope = (
            f"Visible viewport: x={viewport.get('x')}, y={viewport.get('y')}, "
            f"w={viewport.get('width')}, h={viewport.get('height')}, "
            f"zoom={viewport.get('zoom')}"
        )
    else:
        canvas = context.get("canvas", {})
        scope = f"Canvas size: {canvas.get('width', 1920)}x{canvas.get('height', 1080)}"
    return (
        f"Board elements:\n{elements}\n"
        f"{scope}\n"
        f"Selected element: {selected if selected else '(none)'}"
    )


def build(transcript: str, context: dict[str, Any]) -> str:
    """Assemble the full model prompt for one transcript."""
    commands = ", ".join(context.get("commands", list(COMMANDS)))
    return "\n\n".join(
        [
            (
                "You convert a teacher's spoken board instruction into EXACTLY ONE JSON object. "
                "Output the object only: no prose, no markdown fences, no commentary."
            ),
            f"Allowed commands: {commands}\n{_schema_block(context.get('viewport'))}",
            _context_block(context),
            f'Transcript (verbatim): "{transcript}"',
            (
                "Reply with EITHER a command object "
                '{"command": ..., "target_id": ...|null, "parameters": {...}, "timestamp": ...} '
                'OR, when the request is ambiguous, ONLY {"clarification_needed": true, "question": "..."}. '
                '"This/that/the ..." refers to the selected element above; with no selection, '
                "ask the teacher to select one instead of guessing."
            ),
        ]
    )
