"""US2 inline-text widget tests (fail-first)."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.app.orchestrator import Orchestrator
from smartboard.core.engine import CommandEngine
from smartboard.ui.board_view import BoardView
from smartboard.ui.text_overlay import TextOverlay

TS = "2026-10-03T18:15:00Z"


def _overlay(qapp: object, parent: object = None) -> TextOverlay:
    from PyQt6.QtWidgets import QWidget

    host = QWidget() if parent is None else parent
    host.show()
    overlay = TextOverlay(host)
    overlay._host = host  # keep the host alive for the overlay lifetime
    return overlay


def test_overlay_enter_commits_new_text(qapp: object) -> None:
    from PyQt6.QtCore import QRect, Qt
    from PyQt6.QtGui import QFont
    from PyQt6.QtTest import QTest

    overlay = _overlay(qapp)
    committed: list = []
    overlay.Committed.connect(committed.append)
    overlay.begin_new(10.0, 20.0, QRect(0, 0, 200, 60), QFont())
    QTest.keyClicks(overlay._editor, "hello")
    QTest.keyClick(overlay._editor, Qt.Key.Key_Return)
    assert len(committed) == 1
    assert committed[0]["text"] == "hello"
    assert committed[0]["target_id"] is None
    assert overlay.is_open is False


def test_overlay_escape_discards_without_commit(qapp: object) -> None:
    from PyQt6.QtCore import QRect, Qt
    from PyQt6.QtGui import QFont
    from PyQt6.QtTest import QTest

    overlay = _overlay(qapp)
    committed: list = []
    discarded: list = []
    overlay.Committed.connect(committed.append)
    overlay.Discarded.connect(discarded.append)
    overlay.begin_new(10.0, 20.0, QRect(0, 0, 200, 60), QFont())
    QTest.keyClick(overlay._editor, Qt.Key.Key_Escape)
    assert committed == []
    assert len(discarded) == 1


def test_overlay_empty_commit_discards(qapp: object) -> None:
    from PyQt6.QtCore import QRect
    from PyQt6.QtGui import QFont

    overlay = _overlay(qapp)
    committed: list = []
    discarded: list = []
    overlay.Committed.connect(committed.append)
    overlay.Discarded.connect(discarded.append)
    overlay.begin_existing("text_001", "text", "original", QRect(0, 0, 200, 60), QFont())
    overlay._editor.setPlainText("   ")
    overlay._commit()
    assert committed == []
    assert len(discarded) == 1


def test_double_click_empty_board_requests_inline_edit(qapp: object) -> None:
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    view = BoardView()
    view.resize(960, 540)
    view.show()
    view.set_mode("select")
    view.render_state({"elements": [], "selected_element_id": None})
    requested: list = []
    view.InlineEditRequested.connect(requested.append)
    QTest.mouseDClick(
        view, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(480, 270)
    )
    assert len(requested) == 1
    assert requested[0]["target_id"] is None
    assert requested[0]["world_x"] == pytest.approx(480.0)
    view.close()


def test_double_click_existing_text_requests_edit(qapp: object) -> None:
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtTest import QTest

    eng = CommandEngine()
    created = eng.execute(
        {
            "command": "create_text",
            "target_id": None,
            "parameters": {"text": "edit me", "position": {"x": 400, "y": 200}},
            "timestamp": TS,
        }
    )
    assert created["ok"]
    view = BoardView()
    view.resize(960, 540)
    view.show()
    view.set_mode("select")
    view.render_state(eng.board.to_dict())
    requested: list = []
    view.InlineEditRequested.connect(requested.append)
    sx, sy = view.transform().to_screen(450.0, 250.0)
    QTest.mouseDClick(
        view, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, QPoint(int(sx), int(sy))
    )
    assert len(requested) == 1
    assert requested[0]["target_id"] == created["affected_id"]
    view.close()


def test_orchestrator_text_commits_record_one_entry_each() -> None:
    orch = Orchestrator(CommandEngine())
    created = orch.commit_text_create(10.0, 20.0, "hello")
    assert created["ok"]
    assert len(orch.engine.history.entries) == 1
    edited = orch.commit_text_edit(created["affected_id"], "hello world")
    assert edited["ok"]
    assert len(orch.engine.history.entries) == 2
    assert orch.engine.board.find(created["affected_id"]).extra["text"] == "hello world"
