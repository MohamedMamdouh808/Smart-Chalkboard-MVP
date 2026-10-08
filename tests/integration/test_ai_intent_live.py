"""T006 probes + T012 matrix: live intent path with recorded fake providers.

No network, no keys. Each case asserts board/history deltas AND the
strip/chip outcome mapping.
"""

from __future__ import annotations

import json
import os

import pytest

from smartboard.ai.config import get_provider, load_config
from smartboard.app.orchestrator import build_app
from smartboard.core import errors
from smartboard.ui.result_chip import outcome_for_result

TS = "2026-10-03T18:15:00Z"
FIX = "tests/fixtures/ai_responses"


def _load(name: str) -> str:
    with open(f"{FIX}/{name}") as handle:
        return handle.read()


class FakeProvider:
    """Recorded responses in sequence (then repeats the last)."""

    def __init__(self, *raws: str) -> None:
        self.raws = list(raws)
        self.calls = 0

    def interpret(self, transcript: str, context: dict) -> dict[str, str]:
        self.calls += 1
        index = min(self.calls - 1, len(self.raws) - 1)
        raw = self.raws[index]
        if isinstance(raw, Exception):
            raise raw
        return {"raw_text": raw}


def _heading(text: str = "Newton's Second Law") -> str:
    return json.dumps({"command": "create_heading", "target_id": None,
                       "parameters": {"text": text}, "timestamp": TS})


def test_valid_commands_change_board_and_chip() -> None:
    app = build_app()
    res = app.handle_live_transcript("Create a heading", FakeProvider(_heading()))
    assert res["ok"] and outcome_for_result(res) == "done"
    assert app.engine.board.elements[0].extra["text"] == "Newton's Second Law"
    assert app.transcription == "Create a heading"


def test_malformed_then_valid_regenerates_once() -> None:
    app = build_app()
    provider = FakeProvider("{oops", _heading())
    res = app.handle_live_transcript("heading please", provider)
    assert res["ok"] and provider.calls == 2


def test_malformed_twice_shows_exact_error_without_mutation() -> None:
    app = build_app()
    before = app.engine.board.to_dict()
    res = app.handle_live_transcript("blah", FakeProvider("{oops", "{still bad"))
    assert res["message"] == "Unable to understand the command. Please try again."
    assert outcome_for_result(res) == "error"
    assert app.engine.board.to_dict() == before
    assert len(app.engine.history.entries) == 0


def test_unsupported_command_rejected() -> None:
    app = build_app()
    before = app.engine.board.to_dict()
    res = app.handle_live_transcript("teleport", FakeProvider(_load("unsupported.json")))
    assert res["error_code"] == errors.E_UNSUPPORTED_COMMAND
    assert app.engine.board.to_dict() == before


def test_invalid_target_reported() -> None:
    app = build_app()
    app.handle_live_transcript("make heading", FakeProvider(_heading()))
    before = app.engine.board.to_dict()
    res = app.handle_live_transcript("delete it", FakeProvider(_load("invalid_target.json")))
    assert res["error_code"] == errors.E_TARGET_NOT_FOUND
    assert app.engine.board.to_dict() == before


def test_clarification_shows_question_without_mutation() -> None:
    app = build_app()
    before = app.engine.board.to_dict()
    res = app.handle_live_transcript("delete that", FakeProvider(_load("clarification.json")))
    assert res.get("needs_clarification") is True
    assert outcome_for_result(res) == "needs_clarification"
    assert "Which object" in res["clarification_question"]
    assert app.engine.board.to_dict() == before


def test_timeout_keeps_board_and_pen_with_retry() -> None:
    app = build_app()
    before = app.engine.board.to_dict()
    provider = FakeProvider(TimeoutError("timed out"), TimeoutError("timed out"))
    res = app.handle_live_transcript("do something", provider)
    assert res.get("retry") is True and "connection" in res["message"]
    assert app.engine.board.to_dict() == before
    pen = app.commit_pen([[{"x": 1, "y": 1}]])
    assert pen["ok"]  # pen keeps working through the outage


def test_no_selection_this_reference_asks_to_select() -> None:
    app = build_app()
    app.handle_live_transcript("make heading", FakeProvider(_heading()))
    app.engine.board.selected_element_id = None
    before = app.engine.board.to_dict()
    contextual = json.dumps({"command": "resize_item", "target_id": None,
                             "parameters": {"scale_factor": 1.25, "use_selection": True},
                             "timestamp": TS})
    res = app.handle_live_transcript("make this bigger", FakeProvider(contextual))
    assert res["error_code"] in (errors.E_TARGET_MISSING, errors.E_AMBIGUOUS)
    assert app.engine.board.to_dict() == before


def test_key_hygiene_on_forced_failure() -> None:
    from smartboard.ai.providers import GroqProvider

    def boom(transcript: str, context: dict) -> str:
        raise RuntimeError("provider exploded")

    provider = GroqProvider(api_key="DUMMY_KEY_XYZ", caller=boom)
    app = build_app()
    res = app.handle_live_transcript("hi", provider)
    assert "DUMMY_KEY_XYZ" not in json.dumps(res)
    assert res.get("retry") is True


def test_unknown_provider_fails_fast() -> None:
    from smartboard.ai.config import AIConfig

    with pytest.raises(ValueError, match="Supported"):
        get_provider(AIConfig(provider="telepathy"))


def test_load_config_defaults_without_env(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    for key in ("AI_PROVIDER", "GROQ_API_KEY", "GROQ_MODEL"):
        monkeypatch.delenv(key, raising=False)
    empty = tmp_path / "empty.env"
    empty.write_text("")
    config = load_config(env_file=str(empty))
    assert config.provider == "groq" and config.groq_api_key is None


@pytest.mark.skipif(os.environ.get("SMARTBOARD_LIVE_GROQ") != "1",
                    reason="opt-in live Groq call (needs real GROQ_API_KEY)")
def test_live_groq_creates_heading() -> None:
    app = build_app()
    provider = get_provider(load_config())
    res = app.handle_live_transcript("Create a heading called Live", provider)
    assert res["ok"], res
