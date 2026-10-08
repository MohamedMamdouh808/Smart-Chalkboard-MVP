"""tests/ui package: Qt widget tests (pytest-qt) + headless math tests.

Qt tests import Qt modules via `pytest.importorskip("PyQt6.QtWidgets")` so
the suite stays green where PyQt6 is absent. Widget tests need a display
or `QT_QPA_PLATFORM=offscreen` (set in CI; see quickstart for local use).
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--regen-refs",
        action="store_true",
        default=False,
        help="Regenerate visual-regression reference PNGs (explicit only, then commit).",
    )


@pytest.fixture(
    params=[(960, 540), (1280, 720), (1920, 1080), (800, 1000)],
    ids=["min-960x540", "hd-1280x720", "full-1920x1080", "portrait-800x1000"],
)
def view_size(request: pytest.FixtureRequest) -> tuple[int, int]:
    """Representative view sizes incl. minimum, HD, fullscreen, portrait."""
    return request.param  # type: ignore[no-any-return]
