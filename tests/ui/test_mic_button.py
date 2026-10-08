"""T010: mic button — 112px circle, 5 state appearances, listening pulse."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui import theme
from smartboard.ui.mic_button import VOICE_STATES, MicButton


def test_voice_states_complete() -> None:
    assert VOICE_STATES == ("idle", "listening", "processing", "validating", "executing")


def test_fixed_circle_geometry(qapp: object) -> None:
    btn = MicButton()
    assert btn.minimumWidth() >= 64 and btn.minimumHeight() >= 64
    assert theme.MIC_DIAMETER == 64  # 004 compact mic


def test_state_property_and_ring_colors(qapp: object) -> None:
    btn = MicButton()
    assert btn.voiceState == "idle"
    rings = set()
    for state in VOICE_STATES:
        btn.set_voice_state(state)
        assert btn.voiceState == state
        rings.add(btn.ring_color())
    assert len(rings) == len(VOICE_STATES)  # pairwise distinct appearances
    assert btn.ring_color() == theme.STATE_COLORS["executing"]


def test_pulse_runs_only_while_listening(qapp: object) -> None:
    from PyQt6.QtCore import QAbstractAnimation

    btn = MicButton()
    btn.set_voice_state("listening")
    assert btn.pulse_anim.state() == QAbstractAnimation.State.Running
    btn.set_voice_state("idle")
    assert btn.pulse_anim.state() != QAbstractAnimation.State.Running


def test_bad_state_rejected(qapp: object) -> None:
    btn = MicButton()
    with pytest.raises(ValueError):
        btn.set_voice_state("teleporting")


def test_qss_state_blocks_present() -> None:
    qss = theme.build_stylesheet()
    for selector in (
        "QPushButton:hover",
        "QPushButton:pressed",
        "QPushButton:disabled",
        "QPushButton:focus",
    ):
        assert selector in qss
