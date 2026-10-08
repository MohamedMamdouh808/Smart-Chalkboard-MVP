"""Foundation camera-ownership tests (fail-first)."""

from __future__ import annotations

from smartboard.app.orchestrator import Orchestrator
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def test_camera_operations_do_not_touch_board_or_history() -> None:
    orch = Orchestrator(CommandEngine())
    orch.engine.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "anchor", "position": {"x": 10, "y": 20}},
            "timestamp": TS,
        }
    )
    before = orch.engine.board.to_dict()
    history_before = len(orch.engine.history.entries)
    version_before = orch.engine.board.version
    selected_before = orch.engine.board.selected_element_id

    orch.set_view_size(960, 540)
    orch.pan_by_screen(120.0, -40.0)
    orch.zoom_about(480.0, 270.0, 2.0)
    orch.reset_zoom()
    assert orch.camera.zoom == 1.0
    orch.fit_all()

    assert orch.engine.board.to_dict() == before
    assert orch.engine.board.version == version_before
    assert orch.engine.board.selected_element_id == selected_before
    assert len(orch.engine.history.entries) == history_before
