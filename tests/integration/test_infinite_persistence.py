"""US3C camera persistence integration tests (fail-first)."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.camera import CameraState
from smartboard.app.lesson_document import build_snapshot, restore_snapshot
from smartboard.core.board import Board
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


def test_camera_saves_and_restores_with_lesson() -> None:
    lessons, _ = _repos()
    lessons.create("lesson_001", "Physics")
    eng = CommandEngine()
    eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "hi", "position": {"x": 50, "y": -600}},
            "timestamp": TS,
        }
    )
    camera = CameraState(pan_x=500.0, pan_y=-200.0, zoom=0.5)
    lessons.save_snapshot("lesson_001", build_snapshot(eng.board.to_dict(), camera), "manual")
    restored = lessons.latest_snapshot("lesson_001")
    assert restored is not None
    board_dict, restored_camera = restore_snapshot(restored, 960, 540)
    assert Board.from_dict(board_dict).to_dict() == eng.board.to_dict()
    assert restored_camera == camera


def test_reopen_does_not_create_history() -> None:
    lessons, _ = _repos()
    lessons.create("lesson_001", "Physics")
    eng = CommandEngine()
    history_before = len(eng.history.entries)
    lessons.save_snapshot("lesson_001", build_snapshot(eng.board.to_dict(), CameraState()), "auto")
    restored = lessons.latest_snapshot("lesson_001")
    assert restored is not None
    restore_snapshot(restored, 960, 540)
    assert len(eng.history.entries) == history_before
