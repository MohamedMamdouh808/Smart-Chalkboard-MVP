"""Infinite-board persistence: save/reopen, legacy migration, export, context, history."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ai.context_builder import build_context
from smartboard.app.camera import CameraState
from smartboard.app.exporter import content_bounds, export_png
from smartboard.app.lesson_document import build_snapshot, restore_snapshot
from smartboard.core.board import Board
from smartboard.core.command_schema import COMMANDS
from smartboard.core.engine import CommandEngine
from smartboard.persistence.history_repo import HistoryRepo
from smartboard.persistence.lesson_repo import LessonRepo
from smartboard.persistence.migrations import migrate
from smartboard.persistence.sqlite import connect

TS = "2026-10-03T18:15:00Z"


def _repos() -> tuple[LessonRepo, HistoryRepo]:
    conn = connect(":memory:")
    migrate(conn)
    return LessonRepo(conn), HistoryRepo(conn)


def test_saved_json_includes_camera_and_reopens_identically() -> None:
    lessons, _ = _repos()
    lessons.create("lesson_001", "Physics")
    eng = CommandEngine()
    eng.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Hi", "position": {"x": -400, "y": 2500}},
            "timestamp": TS,
        }
    )
    camera = CameraState(pan_x=33.0, pan_y=44.0, zoom=2.0)
    snapshot = build_snapshot(eng.board.to_dict(), camera)
    assert "canvas" not in snapshot
    lessons.save_snapshot("lesson_001", snapshot, "manual")
    restored = lessons.latest_snapshot("lesson_001")
    assert restored is not None
    board_dict, restored_camera = restore_snapshot(restored, 960, 540)
    assert Board.from_dict(board_dict).to_dict() == eng.board.to_dict()
    assert restored_camera == camera


def test_legacy_snapshot_reopens_with_coordinates_preserved() -> None:
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
    del legacy["canvas"]
    board_dict, camera = restore_snapshot(legacy, 960, 540)
    board = Board.from_dict(board_dict)
    assert camera == CameraState(pan_x=0.0, pan_y=0.0, zoom=1.0)
    element = board.find("text_001")
    assert element is not None
    assert (element.x, element.y, element.width, element.height) == (160, 200, 600, 120)


def test_export_uses_content_bounds(tmp_path) -> None:
    from PyQt6.QtGui import QImage

    eng = CommandEngine()
    eng.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Hi", "position": {"x": 0, "y": 0}},
            "timestamp": TS,
        }
    )
    out = export_png(eng.board.to_dict(), str(tmp_path / "lesson.png"))
    image = QImage(str(out))
    assert (image.width(), image.height()) == (800 + 96, 96 + 96)
    assert content_bounds(eng.board.to_dict()) == (0.0, 0.0, 800.0, 96.0)


def test_ai_context_includes_viewport() -> None:
    eng = CommandEngine()
    viewport = {"x": 10.0, "y": 20.0, "width": 960.0, "height": 540.0, "zoom": 2.0}
    context = build_context("hi", eng.board.to_dict(), list(COMMANDS), viewport=viewport)
    assert context["viewport"] == viewport


def test_camera_motion_records_no_history_and_keeps_undo_chain() -> None:
    from smartboard.app.orchestrator import Orchestrator

    orch = Orchestrator(CommandEngine())
    orch.engine.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Hi", "position": {"x": 0, "y": 0}},
            "timestamp": TS,
        }
    )
    entries_before = len(orch.engine.history.entries)
    orch.set_view_size(1920, 1080)
    orch.pan_by_screen(400.0, 300.0)
    orch.zoom_about(100.0, 100.0, 2.0)
    orch.reset_zoom()
    assert len(orch.engine.history.entries) == entries_before
    assert orch.engine.execute(
        {"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS}
    )["ok"]
    assert orch.engine.board.find("heading_001") is None
