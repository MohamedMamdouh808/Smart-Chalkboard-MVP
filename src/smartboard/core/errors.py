"""Typed error codes and teacher-friendly messages."""

from __future__ import annotations

E_SCHEMA = "E_SCHEMA"
E_UNSUPPORTED_COMMAND = "E_UNSUPPORTED_COMMAND"
E_PARAM_INVALID = "E_PARAM_INVALID"
E_TARGET_MISSING = "E_TARGET_MISSING"
E_TARGET_NOT_FOUND = "E_TARGET_NOT_FOUND"
E_OUT_OF_BOUNDS = "E_OUT_OF_BOUNDS"
E_NOTHING_TO_UNDO = "E_NOTHING_TO_UNDO"
E_NOTHING_TO_REDO = "E_NOTHING_TO_REDO"
E_CONFIRMATION_REQUIRED = "E_CONFIRMATION_REQUIRED"
E_AMBIGUOUS = "E_AMBIGUOUS"

MESSAGES: dict[str, str] = {
    E_SCHEMA: "That command can't be applied: malformed request.",
    E_UNSUPPORTED_COMMAND: "That command can't be applied: unsupported action.",
    E_PARAM_INVALID: "That command can't be applied: invalid value.",
    E_TARGET_MISSING: "Select an object first, then try again.",
    E_TARGET_NOT_FOUND: "That object no longer exists. Please select again.",
    E_OUT_OF_BOUNDS: "That would move it off the board, so it was not applied.",
    E_NOTHING_TO_UNDO: "Nothing to undo.",
    E_NOTHING_TO_REDO: "Nothing to redo.",
    E_CONFIRMATION_REQUIRED: "Confirmation needed.",
    E_AMBIGUOUS: "Which object would you like me to act on?",
}


def message_for(code: str, detail: str = "") -> str:
    base = MESSAGES.get(code, "That command can't be applied.")
    if detail:
        return f"{base} ({detail})"
    return base
