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


def test_core_and_persistence_untouched() -> None:
    changed = _changed_files()
    if changed is None:
        pytest.skip("git base ref unavailable; cannot verify untouched core")
    assert changed == [], f"002 must not modify core/persistence, changed: {changed}"
