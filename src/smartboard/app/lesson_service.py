"""Session lifecycle + lesson service (dirty tracking, autosave hooks)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from smartboard.persistence.lesson_repo import LessonRepo

AUTOSAVE_INTERVAL_S = 30


@dataclass
class Session:
    lesson_id: str
    lessons: LessonRepo
    dirty: bool = False
    last_autosave: float = field(default_factory=time.monotonic)

    def mark_dirty(self) -> None:
        self.dirty = True

    def mark_saved(self) -> None:
        self.dirty = False
        self.last_autosave = time.monotonic()

    def autosave_due(self, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        return self.dirty and (now - self.last_autosave) >= AUTOSAVE_INTERVAL_S

    def save(self, state: dict[str, Any], save_type: str = "manual") -> None:
        self.lessons.save_snapshot(self.lesson_id, state, save_type)
        self.mark_saved()


class LessonService:
    """Lesson CRUD with explicit confirmation on destructive paths."""

    def __init__(self, lessons: LessonRepo) -> None:
        self.lessons = lessons

    def new_lesson(
        self, lesson_id: str, title: str, dirty: bool, confirmed: bool
    ) -> dict[str, str]:
        if dirty and not confirmed:
            return {
                "status": "confirmation_required",
                "message": "You have unsaved changes. Save first? [Cancel] [Confirm]",
            }
        self.lessons.create(lesson_id, title)
        return {"status": "created", "message": f"Lesson '{title}' created."}

    def delete_lesson(self, lesson_id: str, confirmed: bool) -> dict[str, str]:
        if not confirmed:
            return {
                "status": "confirmation_required",
                "message": "Delete this lesson? [Cancel] [Confirm]",
            }
        self.lessons.soft_delete(lesson_id)
        return {"status": "deleted", "message": "Lesson deleted."}
