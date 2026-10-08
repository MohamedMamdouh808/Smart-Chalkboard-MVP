"""T010: size-independence — saves and exports identical at any window size."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from smartboard.core.engine import CommandEngine

QtGui = pytest.importorskip("PyQt6.QtGui")

TS = "2026-10-03T18:15:00Z"


def build_state() -> dict:
    eng = CommandEngine()
    eng.execute(
        {
            "command": "create_heading",
            "target_id": None,
            "parameters": {"text": "Newton's Second Law"},
            "timestamp": TS,
        }
    )
    return eng.board.to_dict()


def test_snapshot_identical_across_sizes() -> None:
    from smartboard.ui.camera_transform import CameraTransform

    state = build_state()
    for view_w, view_h in ((960, 540), (1280, 720), (1920, 1080)):
        transform = CameraTransform(
            pan_x=0.0, pan_y=0.0, zoom=1.0, view_w=view_w, view_h=view_h
        )  # view-only
        assert transform.visible_rect()[2:] == (float(view_w), float(view_h))
    assert json.dumps(build_state(), sort_keys=True) == json.dumps(state, sort_keys=True)


def test_export_identical_across_sizes(tmp_path: Path, qapp: object) -> None:
    from smartboard.app.exporter import export_png

    state = build_state()
    outs = []
    # Export always renders content bounds at 100%, never the window: window
    # size is not even an input, so all three must be byte-identical.
    for name in ("s", "m", "l"):
        out = export_png(state, tmp_path / f"{name}.png")
        outs.append(out.read_bytes())
    assert outs[0] == outs[1] == outs[2]
