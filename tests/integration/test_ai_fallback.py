"""T032: fallback on timeout/network/5xx/rate-limit; both-down keeps board."""

from __future__ import annotations

from smartboard.ai.fallback_policy import AI_DOWN_MESSAGE, ProviderError, interpret_with_fallback
from smartboard.app.orchestrator import build_app

VALID = '{"command": "undo", "target_id": null, "parameters": {}, "timestamp": "2026-10-03T18:15:00Z"}'


def _fail(kind: str):
    def go() -> str:
        raise ProviderError("gemini", kind)
    return go


def test_each_failure_mode_reaches_fallback() -> None:
    for kind in ("timeout", "network_error", "http_5xx", "rate_limit"):
        raw, used, log = interpret_with_fallback("undo", {}, _fail(kind), lambda: VALID)
        assert used == "groq" and raw == VALID
        assert {"provider": "gemini", "error_type": "call_failed"} in log


def test_both_providers_down_returns_retry_and_clean_log() -> None:
    raw, used, log = interpret_with_fallback("undo", {}, _fail("timeout"), _fail("timeout"))
    assert raw is None and used == AI_DOWN_MESSAGE
    for entry in log:  # provider + type only — never keys or content
        assert set(entry) == {"provider", "error_type"}


def test_orchestrator_degrades_to_manual_only() -> None:
    app = build_app()
    res = app.handle_transcript("do something", _fail("timeout"), _fail("timeout"))
    assert res == {"ok": False, "message": AI_DOWN_MESSAGE, "retry": True}
    assert app.status == "Idle"
    pen = app.commit_pen([[{"x": 0, "y": 0}]])
    assert pen["ok"]  # board and pen stay functional

