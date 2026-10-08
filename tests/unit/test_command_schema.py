"""T005: schema tests for all 12 commands (shape-level validation)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from smartboard.core import errors
from smartboard.core.command_schema import COMMANDS, validate_shape

TS = "2026-10-03T18:15:00Z"


def cmd(name: str, **kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = {"command": name, "target_id": None, "parameters": {}, "timestamp": TS}
    base.update(kw)
    return base


def test_all_twelve_commands_pass_shape() -> None:
    for name in COMMANDS:
        assert len(COMMANDS) == 12
        ok, _, _ = validate_shape(cmd(name))
        assert ok, name


def test_equation_uses_create_text_path() -> None:
    ok, _, _ = validate_shape(cmd("create_text", parameters={"text": "F = ma", "equation_style": True}))
    assert ok


def test_missing_field_rejected() -> None:
    raw = cmd("undo")
    del raw["timestamp"]
    ok, code, _ = validate_shape(raw)
    assert not ok and code == errors.E_SCHEMA


def test_extra_top_level_field_rejected() -> None:
    raw = cmd("undo")
    raw["extra"] = 1
    ok, code, _ = validate_shape(raw)
    assert not ok and code == errors.E_SCHEMA


def test_unsupported_command_rejected() -> None:
    ok, code, _ = validate_shape(cmd("teleport_item"))
    assert not ok and code == errors.E_UNSUPPORTED_COMMAND


def test_non_object_rejected() -> None:
    ok, code, _ = validate_shape([1, 2])
    assert not ok and code == errors.E_SCHEMA


def test_bad_timestamp_rejected() -> None:
    ok, code, _ = validate_shape(cmd("undo", timestamp="yesterday"))
    assert not ok and code == errors.E_SCHEMA


def test_bad_target_type_rejected() -> None:
    ok, code, _ = validate_shape(cmd("undo", target_id=123))
    assert not ok and code == errors.E_SCHEMA


def test_parameters_must_be_object() -> None:
    ok, code, _ = validate_shape(cmd("undo", parameters=[]))
    assert not ok and code == errors.E_SCHEMA


def test_recorded_fixtures_match_schema() -> None:
    from smartboard.core.validators import validate_params

    fix = Path("tests/fixtures/ai_responses")
    valid = json.loads((fix / "valid_create_heading.json").read_text())
    ok, _, _ = validate_shape(valid)
    assert ok
    # extra top-level field / unsupported command fail the envelope …
    for name, code in (("unsupported.json", errors.E_UNSUPPORTED_COMMAND),):
        raw = json.loads((fix / name).read_text())
        ok, got, _ = validate_shape(raw)
        assert not ok and got == code
    # … while unknown *parameter* keys pass the envelope but fail params.
    extra = json.loads((fix / "extra_field.json").read_text())
    ok, _, _ = validate_shape(extra)
    assert ok
    ok, code, _ = validate_params(extra["command"], extra["parameters"])
    assert not ok and code == errors.E_PARAM_INVALID
    # malformed JSON never parses at all.
    with pytest.raises(ValueError):
        json.loads((fix / "malformed.json").read_text())


def test_command_names_are_case_sensitive() -> None:
    ok, code, _ = validate_shape(cmd("Undo"))
    assert not ok and code == errors.E_UNSUPPORTED_COMMAND
