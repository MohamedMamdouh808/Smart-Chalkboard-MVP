"""Orchestrator — wires voice/AI/pen through the queue into the engine."""

from __future__ import annotations

import json
import threading
from typing import Any, Callable

from smartboard.ai.fallback_policy import interpret_with_fallback
from smartboard.app.command_queue import CommandQueue
from smartboard.core.command_schema import COMMANDS
from smartboard.core.engine import CommandEngine


class Orchestrator:
    """Application layer: calls layers in order, owns no business rules."""

    def __init__(self, engine: CommandEngine) -> None:
        self.engine = engine
        self.queue = CommandQueue(executor=self._execute)
        self.status = "Idle"
        self.transcription = ""
        # Serialises every engine write. Voice commands arrive on worker
        # threads while pen commits arrive on the UI thread, so this lock is
        # what makes the engine a genuinely single-writer: two producers can
        # never mutate board state at the same time.
        self._engine_lock = threading.RLock()

    def _execute(self, payload: dict[str, Any], source: str, confirmed: bool, dirty: bool) -> dict[str, Any]:
        with self._engine_lock:
            self.status = "Validating"
            if payload.get("command") == "__pen_commit__":
                # Internal pen item: dispatched to the engine's own entry point,
                # never through the public command schema (no 13th AI command).
                params = payload.get("parameters", {})
                result = self.engine.add_drawing(
                    params.get("strokes", []), color=str(params.get("color", "#FFFFFF")),
                    width=int(params.get("width", 4)), source=source)
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
            return {"ok": False, "message": "Unable to understand the command. Please try again.",
                    "retry": True}
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
        context = build_context(transcript, self.engine.board.to_dict(), list(COMMANDS))
        try:
            raw = provider.interpret(transcript, context)["raw_text"]
        except Exception:
            self.status = "Idle"
            return {"ok": False,
                    "message": "Voice service unavailable. Check your connection and retry.",
                    "retry": True}
        payload = self._parse_or_regen(raw, provider, transcript, context)
        if payload is None:
            self.status = "Idle"
            return {"ok": False,
                    "message": "Unable to understand the command. Please try again.",
                    "retry": True}
        if isinstance(payload, dict) and payload.get("clarification_needed"):
            self.status = "Idle"
            question = str(payload.get("question") or "Which object did you mean?")
            return {"ok": False, "needs_clarification": True,
                    "clarification_question": question, "message": question}
        result = self.queue.submit_and_run(payload, source="voice")
        if result.get("error_code") in ("E_QUEUE_FULL", "E_BLOCKED"):
            self.status = "Idle"
        return result

    @staticmethod
    def _parse_or_regen(raw: str, provider: Any, transcript: str,
                        context: dict[str, Any]) -> dict[str, Any] | None:
        """Parse raw JSON; exactly one regeneration on failure."""
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            return parsed
        try:
            raw = provider.interpret(transcript, context)["raw_text"]
        except Exception:
            return None
        try:
            parsed = json.loads(raw)
        except ValueError:
            return None
        return parsed if isinstance(parsed, dict) else None

    def commit_pen_drawing(self, group: list[list[dict[str, Any]]], color: str = "#FFFFFF",
                           width: int = 4) -> dict[str, Any]:
        """Commit a grouped stroke set as one internal drawing.

        The commit is queued like any other item, so it waits behind voice work
        already in flight, and it runs under the same engine lock — a pen
        commit can never interleave with a voice command.
        """
        payload = {"command": "__pen_commit__", "target_id": None,
                   "parameters": {"strokes": group, "color": color, "width": width}}
        return self.queue.submit_and_run(payload, source="pen")

    def commit_pen(self, strokes: list[list[dict[str, Any]]], color: str = "#FFFFFF") -> dict[str, Any]:
        """Pen path: internal op through the same engine (works offline)."""
        return self.commit_pen_drawing(strokes, color=color)


def build_app() -> Orchestrator:
    return Orchestrator(CommandEngine())
