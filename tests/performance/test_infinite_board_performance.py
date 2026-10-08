"""Infinite-board 200-element performance check (viewport filtering + pan/zoom smoke)."""

from __future__ import annotations

import time

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ai.context_builder import build_context
from smartboard.app.camera import normalize_camera
from smartboard.app.exporter import content_bounds
from smartboard.core.command_schema import COMMANDS
from smartboard.core.engine import CommandEngine
from smartboard.ui.board_paint import visible_elements
from smartboard.ui.board_view import BoardView

TS = "2026-10-03T18:15:00Z"


def _board_with_200() -> CommandEngine:
    eng = CommandEngine()
    for i in range(200):
        x = (i % 20) * 500 - 2500
        y = (i // 20) * 500 - 2500
        result = eng.execute(
            {
                "command": "create_text",
                "target_id": None,
                "parameters": {"text": f"line {i}", "position": {"x": x, "y": y}},
                "timestamp": TS,
            }
        )
        assert result["ok"]
    return eng


def test_viewport_filtering_paints_only_visible_subset(qapp) -> None:
    eng = _board_with_200()
    elements = eng.board.to_dict()["elements"]
    view = BoardView()
    view.resize(960, 540)
    view.show()
    view.set_camera(normalize_camera(0.0, 0.0, 1.0))
    visible = visible_elements(elements, view.visible_world_rect())
    assert 0 < len(visible) < 200
    start = time.perf_counter()
    for _ in range(20):
        view.pan_by_screen(37.0, -11.0)
        visible_elements(elements, view.visible_world_rect())
    elapsed = time.perf_counter() - start
    assert elapsed < 5.0
    view.close()


def test_ai_context_stays_bounded_with_200_elements() -> None:
    eng = _board_with_200()
    viewport = {"x": 0.0, "y": 0.0, "width": 960.0, "height": 540.0, "zoom": 1.0}
    context = build_context("hi", eng.board.to_dict(), list(COMMANDS), viewport=viewport)
    assert len(context["elements"]) <= 50


def test_export_bounds_computed_for_200_elements() -> None:
    eng = _board_with_200()
    start = time.perf_counter()
    bounds = content_bounds(eng.board.to_dict())
    elapsed = time.perf_counter() - start
    assert bounds is not None
    assert elapsed < 5.0
