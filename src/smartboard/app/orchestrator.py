"""Orchestrator — wires voice/AI/pen through the queue into the engine."""

from __future__ import annotations

import copy
import json
import threading
from collections.abc import Callable
from datetime import UTC
from typing import Any

from smartboard.ai.fallback_policy import interpret_with_fallback
from smartboard.app.camera import (
    CameraState,
    default_camera,
    fit_camera_for_bounds,
    normalize_camera,
    visible_world_rect,
)
from smartboard.app.camera import (
    pan_by_screen as _pan_camera,
)
from smartboard.app.camera import (
    reset_zoom as _reset_camera_zoom,
)
from smartboard.app.camera import (
    zoom_about_cursor as _zoom_camera_about,
)
from smartboard.app.command_queue import CommandQueue
from smartboard.app.placement import find_placement
from smartboard.core.board import drawing_bounds_for_element
from smartboard.core.command_schema import COMMANDS
from smartboard.core.engine import CommandEngine
from smartboard.core.validators import DISTANCE_STEPS


class Orchestrator:
    """Application layer: calls layers in order, owns no business rules."""

    def __init__(self, engine: CommandEngine) -> None:
        self.engine = engine
        self.queue = CommandQueue(executor=self._execute)
        self.status = "Idle"
        self.transcription = ""
        # Authoritative infinite-board camera. View size is transient widget
        # state; camera motion never touches board state, version, or history.
        self.camera: CameraState = default_camera()
        self.view_w: int = 960
        self.view_h: int = 540
        # Serialises every engine write. Voice commands arrive on worker
        # threads while pen commits arrive on the UI thread, so this lock is
        # what makes the engine a genuinely single-writer: two producers can
        # never mutate board state at the same time.
        self._engine_lock = threading.RLock()

    def _execute(
        self, payload: dict[str, Any], source: str, confirmed: bool, dirty: bool
    ) -> dict[str, Any]:
        with self._engine_lock:
            self.status = "Validating"
            if payload.get("command") == "__pen_commit__":
                # Internal pen item: dispatched to the engine's own entry point,
                # never through the public command schema (no 13th AI command).
                params = payload.get("parameters", {})
                result = self.engine.add_drawing(
                    params.get("strokes", []),
                    color=str(params.get("color", "#FFFFFF")),
                    width=int(params.get("width", 4)),
                    source=source,
                )
                self.status = "Idle"
                return result
            if payload.get("command") == "__edit_text__":
                # Internal inline-edit item: validated engine edit, never through
                # the public command schema (no 13th AI command).
                params = payload.get("parameters", {})
                result = self.engine.edit_text(
                    payload.get("target_id"), params.get("text"), source=source
                )
                self.status = "Idle"
                return result
            if (
                payload.get("command") == "__manual_resize__"
            ):  # Internal manual-resize item: fixed-corner metadata stays in the
                # application/engine call and is absent from AI command history.
                params = payload.get("parameters", {})
                anchor = payload.get("anchor")
                result = self.engine.manual_resize(
                    payload.get("target_id"),
                    params,
                    anchor,
                    str(payload.get("timestamp", "")),
                    source=source,
                )
                self.status = "Idle"
                return result
            result = self.engine.execute(payload, source=source, confirmed=confirmed, dirty=dirty)
            self.status = "Executing" if result.get("ok") else "Idle"
            if result.get("ok"):
                self.status = "Idle"
            return result

    def handle_transcript(
        self,
        transcript: str,
        primary: Callable[[], str],
        fallback: Callable[[], str],
    ) -> dict[str, Any]:
        """AI pipeline: interpret (regen → fallback) → queue → engine."""
        self.status = "Processing"
        self.transcription = transcript
        context = {"transcript": transcript, "commands": list(COMMANDS)}
        raw, used, _log = interpret_with_fallback(transcript, context, primary, fallback)
        if raw is None:
            self.status = "Idle"
            return {"ok": False, "message": used, "retry": True}
        try:
            payload = json.loads(raw)
        except ValueError:
            self.status = "Idle"
            return {
                "ok": False,
                "message": "Unable to understand the command. Please try again.",
                "retry": True,
            }
        payload = self.normalize_command(payload)
        result = self.queue.submit_and_run(payload, source="voice")
        if result.get("error_code") in ("E_QUEUE_FULL", "E_BLOCKED"):
            self.status = "Idle"
        return result

    def handle_live_transcript(self, transcript: str, provider: Any) -> dict[str, Any]:
        """Live AI path: provider → parse → regen-once → queue → engine.

        Single configured provider (no fallback chain here); the provider
        call itself runs on a worker thread via the caller. The engine
        remains the only state writer; clarification envelopes display
        and stop.
        """
        from smartboard.ai.context_builder import build_context

        self.status = "Processing"
        self.transcription = transcript
        vx, vy, vw, vh = self.visible_rect()
        viewport = {"x": vx, "y": vy, "width": vw, "height": vh, "zoom": self.camera.zoom}
        context = build_context(
            transcript, self.engine.board.to_dict(), list(COMMANDS), viewport=viewport
        )
        try:
            raw = provider.interpret(transcript, context)["raw_text"]
        except Exception:  # noqa: BLE001 - provider faults degrade to manual mode
            self.status = "Idle"
            return {
                "ok": False,
                "message": "Voice service unavailable. Check your connection and retry.",
                "retry": True,
            }
        payload = self._parse_or_regen(raw, provider, transcript, context)
        if payload is None:
            self.status = "Idle"
            return {
                "ok": False,
                "message": "Unable to understand the command. Please try again.",
                "retry": True,
            }
        if isinstance(payload, dict) and payload.get("clarification_needed"):
            self.status = "Idle"
            question = str(payload.get("question") or "Which object did you mean?")
            return {
                "ok": False,
                "needs_clarification": True,
                "clarification_question": question,
                "message": question,
            }
        payload = self.normalize_command(payload)
        result = self.queue.submit_and_run(payload, source="voice")
        if result.get("error_code") in ("E_QUEUE_FULL", "E_BLOCKED"):
            self.status = "Idle"
        return result

    @staticmethod
    def _parse_or_regen(
        raw: str, provider: Any, transcript: str, context: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Parse raw JSON; exactly one regeneration on failure."""
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            return parsed
        try:
            raw = provider.interpret(transcript, context)["raw_text"]
        except Exception:  # noqa: BLE001 - provider faults degrade to manual mode
            return None
        try:
            parsed = json.loads(raw)
        except ValueError:
            return None
        return parsed if isinstance(parsed, dict) else None

    def commit_text_create(self, world_x: float, world_y: float, text: str) -> dict[str, Any]:
        """Commit provisional double-click text as one public UI-origin creation."""
        from datetime import datetime

        payload = {
            "command": "create_text",
            "target_id": None,
            "parameters": {
                "text": text,
                "position": {"x": round(float(world_x)), "y": round(float(world_y))},
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return self.queue.submit_and_run(payload, source="ui")

    def commit_text_edit(self, target_id: str | None, text: str) -> dict[str, Any]:
        """Commit an inline edit as one internal UI-origin text operation."""
        from datetime import datetime

        payload = {
            "command": "__edit_text__",
            "target_id": target_id,
            "parameters": {"text": text},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return self.queue.submit_and_run(payload, source="ui")

    def normalize_command(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Make a voice/UI command self-contained using the current viewport.

        Missing creation positions become explicit visible-area world
        positions; relative distances become explicit world distances scaled
        by the active zoom. The normalized payload is what history records,
        so replay never needs camera state.
        """
        normalized = copy.deepcopy(payload)
        command = normalized.get("command")
        params = normalized.get("parameters")
        if not isinstance(params, dict):
            return normalized
        if command in ("create_heading", "create_text", "create_shape"):
            if "position" not in params:
                kind = {"create_heading": "heading", "create_text": "text"}.get(command, "shape")
                elements = [el.to_dict() for el in self.engine.board.elements]
                x, y = find_placement(kind, params, self.visible_rect(), elements)
                params["position"] = {"x": x, "y": y}
        elif command == "move_item" and isinstance(params.get("relative"), dict):
            rel = params["relative"]
            dist = rel.get("distance")
            base: float | None
            if isinstance(dist, str):
                base = DISTANCE_STEPS.get(dist)
            else:
                try:
                    base = float(dist)
                except (TypeError, ValueError):
                    base = None
            if base is not None:
                rel["distance"] = int(float(base) / self.camera.zoom)
        return normalized

    def commit_manual_gesture(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Route one validated manual gesture through the FIFO queue.

        Drag payloads use the public move operation. Resize payloads use an
        internal manual-resize operation whose recorded history command is
        still the existing resize operation. The engine lock prevents
        concurrent voice/manual writes.
        """
        return self.queue.submit_and_run_if_idle(payload, source="ui")

    def set_view_size(self, width: int, height: int) -> dict[str, int]:
        """Track transient widget dimensions for viewport-derived behavior."""
        try:
            view_w, view_h = int(width), int(height)
        except (TypeError, ValueError):
            return {"view_w": self.view_w, "view_h": self.view_h}
        if view_w > 0 and view_h > 0:
            self.view_w, self.view_h = view_w, view_h
        return {"view_w": self.view_w, "view_h": self.view_h}

    def visible_rect(self) -> tuple[float, float, float, float]:
        return visible_world_rect(self.camera, self.view_w, self.view_h)

    def pan_by_screen(self, dx: float, dy: float) -> CameraState:
        self.camera = _pan_camera(self.camera, dx, dy)
        return self.camera

    def zoom_about(self, sx: float, sy: float, factor: float) -> CameraState:
        self.camera = _zoom_camera_about(self.camera, sx, sy, factor)
        return self.camera

    def reset_zoom(self) -> CameraState:
        self.camera = _reset_camera_zoom(self.camera)
        return self.camera

    def content_bounds(self) -> tuple[float, float, float, float] | None:
        boxes: list[tuple[float, float, float, float]] = []
        for element in self.engine.board.elements:
            if element.type == "drawing":
                x, y, w, h = drawing_bounds_for_element(element)
            else:
                x, y, w, h = element.x, element.y, element.width, element.height
            boxes.append((float(x), float(y), float(w), float(h)))
        if not boxes:
            return None
        x0 = min(box[0] for box in boxes)
        y0 = min(box[1] for box in boxes)
        x1 = max(box[0] + box[2] for box in boxes)
        y1 = max(box[1] + box[3] for box in boxes)
        return (x0, y0, x1 - x0, y1 - y0)

    def fit_all(self) -> CameraState:
        self.camera = fit_camera_for_bounds(self.content_bounds(), self.view_w, self.view_h)
        return self.camera

    def set_camera(self, camera: CameraState) -> CameraState:
        self.camera = normalize_camera(camera.pan_x, camera.pan_y, camera.zoom)
        return self.camera

    def commit_pen_drawing(
        self, group: list[list[dict[str, Any]]], color: str = "#FFFFFF", width: int = 4
    ) -> dict[str, Any]:
        """Commit a grouped stroke set as one internal drawing.

        The commit is queued like any other item, so it waits behind voice work
        already in flight, and it runs under the same engine lock — a pen
        commit can never interleave with a voice command.
        """
        payload = {
            "command": "__pen_commit__",
            "target_id": None,
            "parameters": {"strokes": group, "color": color, "width": width},
        }
        return self.queue.submit_and_run(payload, source="pen")

    def commit_pen(
        self, strokes: list[list[dict[str, Any]]], color: str = "#FFFFFF"
    ) -> dict[str, Any]:
        """Pen path: internal op through the same engine (works offline)."""
        return self.commit_pen_drawing(strokes, color=color)


def build_app() -> Orchestrator:
    return Orchestrator(CommandEngine())
