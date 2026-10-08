"""T003/T019: behavior guard — 003 is a pure restyle of `ui/` only.

Allowed to change vs 002-resizable-window-mode: `src/smartboard/ui/**`,
`tests/**`, `specs/**`, docs/assets. Everything else (core, persistence,
app logic, contracts of behavior) must be byte-identical in effect:
forbidden paths must have NO diff at all.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

# main.py wiring for the new widgets lives here but must stay
# behavior-neutral; all other app modules are fully frozen.
ALLOWED_APP = {"src/smartboard/app/main.py"}
GUARDED_ROOTS = ["src/smartboard/core", "src/smartboard/persistence", "src/smartboard/app",
                 "src/smartboard/voice", "src/smartboard/ai"]
BASE_REF = "002-resizable-window-mode"


def _changed() -> list[str] | None:
    if shutil.which("git") is None:
        return None
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", BASE_REF, "--", *GUARDED_ROOTS],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None
    return [line.replace("\\", "/") for line in out.stdout.splitlines() if line.strip()]


def _branch_has_snapshot() -> bool:
    """True when the guard’s base branch has a unique snapshot to compare."""
    if shutil.which("git") is None:
        return False
    try:
        base = subprocess.run(
            ["git", "rev-parse", BASE_REF],
            capture_output=True,
            text=True,
            check=True,
        )
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return False
    return base.stdout.strip() != head.stdout.strip()


def test_behavior_files_untouched() -> None:
    if not _branch_has_snapshot():
        pytest.skip("guard base has no unique branch snapshot; cannot verify behavior freeze")
    changed = _changed()
    if changed is None:
        pytest.skip("git base ref unavailable; cannot verify behavior freeze")
    unexpected = [p for p in changed if p not in ALLOWED_APP]
    assert unexpected == [], f"003 must not change behavior files: {unexpected}"
