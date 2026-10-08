"""US3C lesson-document unit tests (fail-first)."""

from __future__ import annotations

from smartboard.app.camera import CameraState
from smartboard.app.lesson_document import build_snapshot, restore_snapshot
from smartboard.core.board import Board
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def test_new_snapshot_round_trip() -> None:
    eng = CommandEngine()
    eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "hi", "position": {"x": -300, "y": 7000}},
            "timestamp": TS,
        }
    )
    camera = CameraState(pan_x=12.0, pan_y=-34.0, zoom=2.0)
    snapshot = build_snapshot(eng.board.to_dict(), camera)
    assert "canvas" not in snapshot
    board_dict, restored_camera = restore_snapshot(snapshot, 960, 540)
    assert Board.from_dict(board_dict).to_dict() == eng.board.to_dict()
    assert restored_camera == camera


def test_legacy_bare_board_defaults_camera() -> None:
    legacy = {
        "lesson_id": "lesson_001",
        "elements": [
            {
                "id": "text_001",
                "type": "text",
                "x": 160,
                "y": 200,
                "width": 600,
                "height": 120,
                "color": "#FFFFFF",
                "z": 1,
            }
        ],
        "selected_element_id": None,
        "version": 2,
    }
    board_dict, camera = restore_snapshot(legacy, 960, 540)
    board = Board.from_dict(board_dict)
    assert (board.find("text_001").x, board.find("text_001").y) == (160, 200)
    assert camera == CameraState(pan_x=0.0, pan_y=0.0, zoom=1.0)


def test_legacy_canvas_centers_at_full_zoom() -> None:
    legacy = {
        "lesson_id": "lesson_001",
        "canvas": {"width": 1920, "height": 1080, "unit": "px"},
        "elements": [
            {
                "id": "text_001",
                "type": "text",
                "x": 160,
                "y": 200,
                "width": 600,
                "height": 120,
                "color": "#FFFFFF",
                "z": 1,
            }
        ],
        "selected_element_id": None,
        "version": 2,
    }
    board_dict, camera = restore_snapshot(legacy, 960, 540)
    board = Board.from_dict(board_dict)
    assert (board.find("text_001").x, board.find("text_001").y) == (160, 200)
    assert camera.zoom == 1.0
    assert (camera.pan_x, camera.pan_y) == (480.0, 270.0)


def test_corrupt_camera_falls_back() -> None:
    snapshot = {
        "lesson_id": "lesson_001",
        "elements": [],
        "selected_element_id": None,
        "version": 1,
        "camera": {"pan_x": "bad", "zoom": 99.0},
    }
    _, camera = restore_snapshot(snapshot, 960, 540)
    assert camera == CameraState(pan_x=0.0, pan_y=0.0, zoom=4.0)
