"""T015: geometry persistence — save on close, restore before paint, safe defaults."""

from __future__ import annotations

import pytest

QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from smartboard.ui.main_window import MainWindow  # noqa: E402
from smartboard.ui.window_state import (  # noqa: E402
    DEFAULT_PEN_WIDTH_NAME,
    PEN_WIDTHS,
    load_mode,
    load_pen_width,
    make_settings,
    restore_state,
    save_pen_width_name,
    save_state,
)


def test_fresh_install_defaults_fullscreen(tmp_path) -> None:
    settings = make_settings(str(tmp_path / "fresh.ini"))
    assert load_mode(settings) == "fullscreen"


def test_round_trip_windowed_geometry(tmp_path, qapp: object) -> None:
    path = str(tmp_path / "geo.ini")
    first = MainWindow()
    first.showNormal()
    first.resize(1100, 650)
    first.move(120, 80)
    save_state(first, make_settings(path))
    first.close()

    second = MainWindow()
    mode = restore_state(second, make_settings(path))
    assert mode == "normal"
    assert (second.width(), second.height()) == (1100, 650)
    assert (second.x(), second.y()) == (120, 80)
    second.close()


def test_fullscreen_round_trip(tmp_path, qapp: object) -> None:
    path = str(tmp_path / "fs.ini")
    first = MainWindow()
    first.showFullScreen()
    save_state(first, make_settings(path))
    first.close()
    assert load_mode(make_settings(path)) == "fullscreen"


def test_corrupt_settings_fall_back_to_fullscreen(tmp_path) -> None:
    bad = tmp_path / "bad.ini"
    bad.write_text("not an ini file at [[[")
    assert load_mode(make_settings(str(bad))) == "fullscreen"


def test_geometry_never_touches_lesson_data(tmp_path) -> None:
    from smartboard.persistence.lesson_repo import LessonRepo
    from smartboard.persistence.migrations import migrate
    from smartboard.persistence.sqlite import connect

    conn = connect(":memory:")
    migrate(conn)
    lessons = LessonRepo(conn)
    lessons.create("lesson_001", "Physics")
    before = lessons.get("lesson_001")
    make_settings(str(tmp_path / "other.ini"))  # separate store, no lesson access
    assert lessons.get("lesson_001") == before
    conn.close()


def test_pen_width_defaults_to_medium_and_round_trips(tmp_path) -> None:
    path = str(tmp_path / "pen.ini")
    settings = make_settings(path)
    assert DEFAULT_PEN_WIDTH_NAME == "medium"
    assert load_pen_width(settings) == 4  # medium default on a fresh install
    assert save_pen_width_name("thick", settings) == 8
    assert load_pen_width(make_settings(path)) == 8
    assert save_pen_width_name("thin", settings) == 2
    assert load_pen_width(make_settings(path)) == 2
    assert PEN_WIDTHS == {"thin": 2, "medium": 4, "thick": 8}


def test_unknown_pen_width_falls_back_to_default(tmp_path) -> None:
    path = str(tmp_path / "odd.ini")
    settings = make_settings(path)
    settings.setValue("pen/width", "enormous")
    assert load_pen_width(settings) == 4
    assert save_pen_width_name("enormous", settings) == 4  # not persisted as-is
    assert load_pen_width(make_settings(path)) == 4


def test_pen_width_is_a_setting_not_a_main_bar_control(qapp: object) -> None:
    """Clarified decision: width lives in settings, never in the toolbar."""
    window = MainWindow()
    window.show()
    labels = [w.text() for w in window.findChildren(QtWidgets.QPushButton)]
    assert not any("thin" in label.lower() or "thick" in label.lower() for label in labels)
    window.close()
