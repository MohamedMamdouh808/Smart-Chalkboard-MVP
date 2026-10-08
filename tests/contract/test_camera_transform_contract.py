"""US1 camera-transform contract tests (fail-first)."""

from __future__ import annotations

from smartboard.app.camera import CameraState
from smartboard.app.orchestrator import Orchestrator
from smartboard.core.engine import CommandEngine
from smartboard.ui.camera_transform import CameraTransform

TS = "2026-10-03T18:15:00Z"


def test_camera_json_round_trip() -> None:
    camera = CameraState(pan_x=120.0, pan_y=-40.0, zoom=1.5)
    assert CameraState.from_dict(camera.to_dict()) == camera


def test_transform_invariants() -> None:
    transform = CameraTransform(pan_x=33.0, pan_y=-17.0, zoom=2.0, view_w=960, view_h=540)
    assert transform.to_world(*transform.to_screen(10.0, 20.0)) == (10.0, 20.0)
    assert transform.visible_rect() == (33.0, -17.0, 480.0, 270.0)


def test_orchestrator_camera_ops_preserve_board() -> None:
    orch = Orchestrator(CommandEngine())
    orch.engine.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "anchor", "position": {"x": -200, "y": 9000}},
            "timestamp": TS,
        }
    )
    before = orch.engine.board.to_dict()
    orch.set_view_size(960, 540)
    orch.pan_by_screen(50.0, 25.0)
    orch.zoom_about(100.0, 100.0, 2.0)
    orch.reset_zoom()
    orch.fit_all()
    assert orch.engine.board.to_dict() == before
    x, y, w, h = orch.visible_rect()
    assert x <= -200.0 and y <= 9000.0
    assert x + w >= 400.0 and y + h >= 9120.0
