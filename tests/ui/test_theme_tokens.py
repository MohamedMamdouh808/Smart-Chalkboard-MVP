"""T004: theme contract — full token table, generated QSS, no stray literals."""

from __future__ import annotations

import pathlib
import re

from smartboard.ui import theme

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")


def test_token_groups_present() -> None:
    for name in (
        "WINDOW_BG",
        "BOARD_SURFACE",
        "BOARD_BORDER",
        "BOARD_SHADOW",
        "TEXT",
        "TEXT_MUTED",
        "TEXT_ON_ACCENT",
        "STATE_COLORS",
        "OUTCOME_COLORS",
        "FONT_FAMILY",
        "FONT_TRANSCRIPT",
        "FONT_STATUS",
        "FONT_BUTTON",
        "FONT_BOARD_HEADING",
        "FONT_BOARD_BODY",
        "MIC_DIAMETER",
        "COMPACT_CONTROL_H",
        "PILL_H",
        "DIALOG_BUTTON_H",
        "BOARD_RADIUS",
        "CONTROL_RADIUS",
        "SPACING",
        "TOOLTIP_PAD_V",
        "TOOLTIP_PAD_H",
        "TOOLTIP_WAKEUP_DELAY_MS",
        "CONTRAST_PAIRS",
    ):
        assert hasattr(theme, name), f"missing token {name}"


def test_state_and_outcome_keys_complete() -> None:
    assert set(theme.STATE_COLORS) == {"idle", "listening", "processing", "validating", "executing"}
    assert set(theme.OUTCOME_COLORS) == {
        "done",
        "needs_confirmation",
        "needs_clarification",
        "error",
    }


def test_type_scale_minima() -> None:
    assert theme.FONT_TRANSCRIPT >= 20 and theme.FONT_STATUS >= 20
    assert theme.FONT_BUTTON >= 18
    assert theme.FONT_BOARD_HEADING >= 64 and theme.FONT_BOARD_BODY >= 36
    assert theme.MIC_DIAMETER >= 64 and theme.COMPACT_CONTROL_H >= 44
    assert theme.PILL_H >= 36
    assert theme.DIALOG_BUTTON_H >= 48


def test_stylesheet_generated_from_tokens() -> None:
    qss = theme.build_stylesheet()
    for selector in (
        "QPushButton",
        "QPushButton:hover",
        "QPushButton:pressed",
        "QPushButton:disabled",
        "QPushButton:focus",
        "QDialog",
        "QLabel",
        "QToolTip",
    ):
        assert selector in qss, f"missing selector {selector}"
    assert theme.BUTTON_TEXT in qss  # token values actually land in the QSS


def test_no_visual_literals_outside_theme() -> None:
    ui_dir = pathlib.Path("src/smartboard/ui")
    offenders: list[str] = []
    for path in ui_dir.glob("*.py"):
        if path.name in ("theme.py",):
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if HEX_RE.search(line):
                offenders.append(f"{path.name}:{i}: {line.strip()}")
    assert offenders == [], "visual literals outside theme.py:\n" + "\n".join(offenders)
