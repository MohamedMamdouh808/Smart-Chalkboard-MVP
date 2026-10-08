"""Top-level JSON shape validation for the 12 locked commands."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from . import errors

COMMANDS: tuple[str, ...] = (
    "create_heading",
    "create_text",
    "move_item",
    "resize_item",
    "delete_item",
    "clear_board",
    "create_shape",
    "change_color",
    "undo",
    "redo",
    "save_lesson",
    "new_lesson",
)

REQUIRED_FIELDS: tuple[str, ...] = ("command", "target_id", "parameters", "timestamp")


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str):
        return False
    text = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(text)
    except ValueError:
        return False
    return True


def validate_shape(raw: Any) -> tuple[bool, str, str]:
    """Validate the envelope shape. Returns (ok, error_code, message)."""
    if not isinstance(raw, dict):
        return False, errors.E_SCHEMA, errors.message_for(errors.E_SCHEMA, "not an object")
    keys = set(raw.keys())
    if keys != set(REQUIRED_FIELDS):
        return False, errors.E_SCHEMA, errors.message_for(errors.E_SCHEMA, "fields")
    command = raw["command"]
    if command not in COMMANDS:
        return False, errors.E_UNSUPPORTED_COMMAND, errors.message_for(errors.E_UNSUPPORTED_COMMAND)
    target = raw["target_id"]
    if target is not None and not isinstance(target, str):
        return False, errors.E_SCHEMA, errors.message_for(errors.E_SCHEMA, "target_id")
    if not isinstance(raw["parameters"], dict):
        return False, errors.E_SCHEMA, errors.message_for(errors.E_SCHEMA, "parameters")
    if not _valid_timestamp(raw["timestamp"]):
        return False, errors.E_SCHEMA, errors.message_for(errors.E_SCHEMA, "timestamp")
    return True, "", ""
