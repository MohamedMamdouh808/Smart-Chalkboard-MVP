"""Per-command parameter validation (types, ranges, enums)."""

from __future__ import annotations

import re
from typing import Any

from . import errors
from .board import CANVAS_HEIGHT, CANVAS_WIDTH, MIN_SIZE

SHAPE_TYPES: tuple[str, ...] = ("rectangle", "circle", "line", "arrow", "triangle")

NAMED_COLORS: tuple[str, ...] = (
    "black",
    "white",
    "red",
    "green",
    "blue",
    "yellow",
    "orange",
    "purple",
    "brown",
    "gray",
)

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

DIRECTIONS: tuple[str, ...] = ("up", "down", "left", "right")
DISTANCE_STEPS: dict[str, int] = {"small": 40, "medium": 100, "large": 200}

TARGET_COMMANDS: tuple[str, ...] = ("move_item", "resize_item", "delete_item", "change_color")

_NO_TARGET = (True, "", "")


def _text_ok(value: object, max_len: int) -> bool:
    return isinstance(value, str) and 1 <= len(value.strip()) <= max_len


def validate_color(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if value in NAMED_COLORS:
        return True
    return bool(HEX_RE.match(value))


def validate_params(command: str, params: dict[str, Any]) -> tuple[bool, str, str]:
    """Returns (ok, error_code, message). Unknown keys always fail."""
    allowed: dict[str, set[str]] = {
        "create_heading": {"text", "position"},
        "create_text": {"text", "position", "size", "equation_style"},
        "move_item": {"position", "relative", "use_selection"},
        "resize_item": {"scale_factor", "size", "use_selection"},
        "delete_item": {"use_selection"},
        "clear_board": set(),
        "create_shape": {"shape_type", "position", "size", "color"},
        "change_color": {"color", "use_selection"},
        "undo": set(),
        "redo": set(),
        "save_lesson": set(),
        "new_lesson": {"title"},
    }
    if set(params.keys()) - allowed.get(command, set()):
        return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "unknown key")

    if command == "create_heading":
        if "text" not in params or not _text_ok(params["text"], 200):
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "text")
    elif command == "create_text":
        if "text" not in params or not _text_ok(params["text"], 2000):
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "text")
        if "equation_style" in params and not isinstance(params["equation_style"], bool):
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "equation_style")
    elif command == "create_shape":
        if params.get("shape_type") not in SHAPE_TYPES:
            detail = "shape (supported: rectangle, circle, line, arrow, triangle)"
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, detail)
        if "color" in params and not validate_color(params["color"]):
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "color")
    elif command == "change_color":
        if "color" not in params or not validate_color(params["color"]):
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "color")
    elif command == "move_item":
        if "position" in params and "relative" in params:
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "move")
        if "position" in params:
            pos = params["position"]
            if not isinstance(pos, dict) or not isinstance(pos.get("x"), (int, float)):
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "position")
            if not isinstance(pos.get("y"), (int, float)):
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "position")
        elif "relative" in params:
            rel = params["relative"]
            if not isinstance(rel, dict) or rel.get("direction") not in DIRECTIONS:
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "direction")
            dist = rel.get("distance")
            if isinstance(dist, str) and dist not in DISTANCE_STEPS:
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "distance")
            if not isinstance(dist, (int, float, str)):
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "distance")
        else:
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "move")
    elif command == "resize_item":
        if "scale_factor" in params and "size" in params:
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "resize")
        if "scale_factor" in params:
            try:
                scale = float(params["scale_factor"])
            except (TypeError, ValueError):
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "scale")
            if not 0.25 <= scale <= 4.0:
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "scale")
        elif "size" in params:
            size = params["size"]
            if not isinstance(size, dict):
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "size")
            try:
                w, h = float(size["w"]), float(size["h"])
            except (KeyError, TypeError, ValueError):
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "size")
            if w < MIN_SIZE or h < MIN_SIZE:
                return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "size")
        else:
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "resize")
    elif command == "new_lesson":
        if "title" in params and not _text_ok(params["title"], 200):
            return False, errors.E_PARAM_INVALID, errors.message_for(errors.E_PARAM_INVALID, "title")
    return _NO_TARGET


def resolve_move(params: dict[str, Any], cur_x: int, cur_y: int) -> tuple[int, int]:
    if "position" in params:
        return int(params["position"]["x"]), int(params["position"]["y"])
    rel = params["relative"]
    dist = rel["distance"]
    steps = DISTANCE_STEPS[dist] if isinstance(dist, str) else int(dist)
    direction = rel["direction"]
    if direction == "up":
        return cur_x, cur_y - steps
    if direction == "down":
        return cur_x, cur_y + steps
    if direction == "left":
        return cur_x - steps, cur_y
    return cur_x + steps, cur_y


def fits_canvas(x: int, y: int, w: int, h: int) -> bool:
    return (
        x >= 0 and y >= 0 and w >= MIN_SIZE and h >= MIN_SIZE and x + w <= CANVAS_WIDTH and y + h <= CANVAS_HEIGHT
    )
