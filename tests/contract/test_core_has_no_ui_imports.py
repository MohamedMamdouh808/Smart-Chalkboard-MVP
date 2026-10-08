"""T018: UI-independence guard — core/persistence import with PyQt6 blocked."""

from __future__ import annotations

import importlib
import sys


class _PyQtBlocker:
    def find_module(self, name: str, path: object = None) -> object:
        if name == "PyQt6" or name.startswith("PyQt6."):
            return self
        return None

    def load_module(self, name: str) -> object:
        raise ImportError(f"Blocked for UI-independence test: {name}")


def test_core_imports_without_pyqt() -> None:
    blocker = _PyQtBlocker()
    before = {m for m in sys.modules if m == "PyQt6" or m.startswith("PyQt6.")}
    sys.meta_path.insert(0, blocker)  # type: ignore[arg-type]
    try:
        for mod in (
            "smartboard.core.board",
            "smartboard.core.command_schema",
            "smartboard.core.validators",
            "smartboard.core.element_ids",
            "smartboard.core.errors",
            "smartboard.core.history",
            "smartboard.core.engine",
            "smartboard.persistence.sqlite",
            "smartboard.persistence.migrations",
            "smartboard.persistence.lesson_repo",
            "smartboard.persistence.history_repo",
            "smartboard.persistence.metrics",
        ):
            sys.modules.pop(mod, None)
        for mod in ("smartboard.core.engine", "smartboard.persistence.migrations"):
            importlib.import_module(mod)
        # Importing core/persistence must not pull in any NEW PyQt6 modules
        # (the blocker would raise if they tried).
        after = {m for m in sys.modules if m == "PyQt6" or m.startswith("PyQt6.")}
        assert after == before
    finally:
        sys.meta_path.remove(blocker)
        for mod in list(sys.modules):
            if mod.startswith("smartboard."):
                sys.modules.pop(mod, None)
