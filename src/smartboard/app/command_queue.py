"""FIFO command queue with a single executor (only writer path to the engine).

Semantics: `submit` enqueues (context is snapshotted at *dequeue* time).
`pump` executes the head of the queue. A result needing confirmation or
clarification blocks the queue: later items wait until the head resolves.
Failures never clear the queue.
"""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Executor = Callable[..., dict[str, Any]]


@dataclass
class QueuedCommand:
    payload: dict[str, Any]
    source: str = "voice"
    confirmed: bool = False
    dirty: bool = False
    #: Caller-private identity tag, never sent to the engine. Lets a producer
    #: recognise its own item when several producers share one queue.
    tag: Any = None


@dataclass
class CommandQueue:
    executor: Executor
    max_waiting: int = 5
    waiting: deque[QueuedCommand] = field(default_factory=deque)
    blocked: bool = False
    _pending: QueuedCommand | None = None
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def submit(
        self,
        payload: dict[str, Any],
        source: str = "voice",
        confirmed: bool = False,
        dirty: bool = False,
        tag: Any = None,
    ) -> dict[str, Any]:
        with self._lock:
            if self.depth() >= self.max_waiting:
                return {"ok": False, "error_code": "E_QUEUE_FULL", "message": "Please wait."}
            self.waiting.append(
                QueuedCommand(
                    payload=payload, source=source, confirmed=confirmed, dirty=dirty, tag=tag
                )
            )
            return {"ok": True, "queued": True, "depth": self.depth()}

    def pump(self) -> dict[str, Any]:
        """Execute exactly one queued command (the head)."""
        with self._lock:
            if self.blocked:
                return {"ok": False, "error_code": "E_BLOCKED", "message": "Awaiting confirmation."}
            if not self.waiting:
                return {"ok": False, "error_code": "E_EMPTY", "message": "Queue empty."}
            item = self.waiting.popleft()
            snapshot = dict(item.payload)  # dequeue-time context snapshot
            result = self.executor(snapshot, item.source, item.confirmed, item.dirty)
            if result.get("needs_confirmation") or result.get("needs_clarification"):
                self.blocked = True
                self._pending = item
            return result

    def resolve_block(self, confirmed: bool) -> dict[str, Any]:
        """Resolve the blocking head with the teacher's confirm/cancel choice."""
        with self._lock:
            pending = self._pending
            if not self.blocked or pending is None:
                return {
                    "ok": False,
                    "error_code": "E_EMPTY",
                    "message": "Nothing awaiting confirmation.",
                }
            self.blocked = False
            self._pending = None
            if not confirmed:
                return {"ok": False, "error_code": "E_CANCELLED", "message": "Cancelled."}
            pending.confirmed = True
            snapshot = dict(pending.payload)
            return self.executor(snapshot, pending.source, True, pending.dirty)

    def depth(self) -> int:
        with self._lock:
            return len(self.waiting)

    def peek(self) -> QueuedCommand | None:
        """The next item that ``pump`` would execute (None when empty)."""
        with self._lock:
            return self.waiting[0] if self.waiting else None

    def submit_and_run_if_idle(
        self,
        payload: dict[str, Any],
        source: str = "voice",
        confirmed: bool = False,
        dirty: bool = False,
    ) -> dict[str, Any]:
        """Queue one item only when no other work is waiting or blocked.

        The queue lock is held from the idle check through this item’s
        execution, so a concurrently submitted command cannot interleave with
        it. A busy or full queue leaves nothing queued for the caller to retry.
        """
        tag = object()
        with self._lock:
            if len(self.waiting) >= self.max_waiting:
                return {"ok": False, "error_code": "E_QUEUE_FULL", "message": "Please wait."}
            if self.blocked or self.waiting:
                return {
                    "ok": False,
                    "error_code": "E_BUSY",
                    "message": "Another command is running. The gesture is waiting.",
                }
            self.waiting.append(
                QueuedCommand(
                    payload=payload, source=source, confirmed=confirmed, dirty=dirty, tag=tag
                )
            )
            while not self.blocked:
                head = self.waiting[0] if self.waiting else None
                if head is None:
                    break
                result = self.pump()
                if head.tag is tag:
                    return result
            return {"ok": False, "error_code": "E_BLOCKED", "message": "Awaiting confirmation."}

    def submit_and_run(
        self,
        payload: dict[str, Any],
        source: str = "voice",
        confirmed: bool = False,
        dirty: bool = False,
    ) -> dict[str, Any]:
        """Queue one item and drive the queue until that item has run.

        Items queued before ours (another producer's work) execute first, as
        FIFO requires; their results are discarded because the caller asked for
        its own command's outcome. Stops if a command needs a decision, since
        only the UI can resolve that.
        """
        tag = object()
        queued = self.submit(payload, source=source, confirmed=confirmed, dirty=dirty, tag=tag)
        if not queued.get("ok"):
            return queued
        while not self.blocked:
            head = self.peek()
            if head is None:
                break
            result = self.pump()
            if head.tag is tag:
                return result
        return {"ok": False, "error_code": "E_BLOCKED", "message": "Awaiting confirmation."}
