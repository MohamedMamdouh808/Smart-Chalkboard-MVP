"""T003/T022: core + persistence must be untouched by feature 002 (UI-layer only)."""

from __future__ import annotations

import shutil
import subprocess

import pytest

GUARDED = ["src/smartboard/core", "src/smartboard/persistence"]
BASE_REF = "001-smart-chalkboard-mvp"


def _changed_files() -> list[str] | None:
    if shutil.which("git") is None:
        return None
    try:
        # Working tree vs base: catches committed AND uncommitted 002 changes.
        out = subprocess.run(
            ["git", "diff", "--name-only", BASE_REF, "--", *GUARDED],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None  # base ref unavailable (e.g., shallow CI) — skip, don't fail
    return [line for line in out.stdout.splitlines() if line.strip()]


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


def test_core_and_persistence_untouched() -> None:
    if not _branch_has_snapshot():
        pytest.skip("guard base has no unique branch snapshot; cannot verify untouched core")
    changed = _changed_files()
    if changed is None:
        pytest.skip("git base ref unavailable; cannot verify untouched core")
    assert changed == [], f"002 must not modify core/persistence, changed: {changed}"
