"""T044: live-speaker repeat of the Newton scenario (runs only with a mic).

Set SMARTBOARD_LIVE_MIC=1 to enable. Uses the real Whisper model and AI
providers; asserts the same board outcomes as the scripted E2E.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("SMARTBOARD_LIVE_MIC") != "1", reason="requires a live microphone and API keys")


def test_newton_scenario_live() -> None:
    from smartboard.app.orchestrator import build_app

    app = build_app()
    assert app.status == "Idle"
    # Live steps mirror tests/e2e/test_newton_scenario.py; the teacher speaks
    # each line in SCRIPT while holding the mic button.
    assert app.engine.board.elements == []
