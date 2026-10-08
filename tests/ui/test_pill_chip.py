"""T011: status pill — 5 state triples, never color alone."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui import theme
from smartboard.ui.status_pill import STATES, StatusPill


def test_states_complete() -> None:
    assert STATES == ("Idle", "Listening", "Processing", "Validating", "Executing")


def test_triples_distinct_and_complete(qapp: object) -> None:
    pill = StatusPill()
    seen: set[tuple[str, str, str]] = set()
    for state in STATES:
        pill.set_state(state)
        triple = (pill.text(), pill.color(), pill.icon_name())
        assert all(triple), state  # icon AND text AND color always present
        seen.add(triple)
    assert len(seen) == len(STATES)


def test_colors_come_from_theme(qapp: object) -> None:
    pill = StatusPill()
    mapping = {"Idle": "idle", "Listening": "listening", "Processing": "processing",
               "Validating": "validating", "Executing": "executing"}
    for label, key in mapping.items():
        pill.set_state(label)
        assert pill.color() == theme.STATE_COLORS[key]
        assert pill.icon_name() == theme.STATE_ICONS[key]


def test_unknown_state_rejected(qapp: object) -> None:
    pill = StatusPill()
    with pytest.raises(ValueError):
        pill.set_state("Napping")


# -- T015: transcription strip + result chip ---------------------------------

from smartboard.ui.main_window import MainWindow
from smartboard.ui.result_chip import (
    OUTCOMES,
    PLACEHOLDER,
    ResultChip,
    outcome_for_result,
)


def test_outcomes_complete() -> None:
    assert OUTCOMES == ("done", "needs_confirmation", "needs_clarification", "error")


def test_result_mapping() -> None:
    assert outcome_for_result({"ok": True}) == "done"
    assert outcome_for_result({"ok": False, "needs_confirmation": True}) == "needs_confirmation"
    assert outcome_for_result({"ok": False, "needs_clarification": True}) == "needs_clarification"
    assert outcome_for_result({"ok": False, "error_code": "E_SCHEMA"}) == "error"


def test_chip_triples_complete(qapp: object) -> None:
    chip = ResultChip()
    seen: set[tuple[str, str, str]] = set()
    for outcome in OUTCOMES:
        chip.set_outcome(outcome)
        triple = (chip.text(), chip.color(), chip.icon_name())
        assert all(triple), outcome
        seen.add(triple)
    assert len(seen) == len(OUTCOMES)


def test_chip_colors_from_theme(qapp: object) -> None:
    chip = ResultChip()
    for outcome in OUTCOMES:
        chip.set_outcome(outcome)
        assert chip.color() == theme.OUTCOME_COLORS[outcome]
        assert chip.icon_name() == theme.OUTCOME_ICONS[outcome]


def test_strip_label_placeholder_and_sizes(qapp: object) -> None:
    window = MainWindow()
    assert window.heard_label.text() == "Heard:"
    assert window.transcription_label.text() == PLACEHOLDER
    assert PLACEHOLDER == "Hold the mic and speak a command"
    assert window.transcription_label.font().pointSize() >= 18  # 007 slim strip
    assert theme.FONT_TRANSCRIPT >= 20
    assert window.result_chip is not None
