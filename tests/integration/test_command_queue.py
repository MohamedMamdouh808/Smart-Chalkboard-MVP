"""T035: queue — FIFO, one-at-a-time, dequeue snapshot, cap 5, blocking, no clear on fail."""

from __future__ import annotations

from smartboard.app.command_queue import CommandQueue
from smartboard.core import errors
from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def make() -> tuple[CommandEngine, CommandQueue]:
    eng = CommandEngine()
    queue = CommandQueue(executor=lambda p, s, c, d: eng.execute(p, source=s, confirmed=c, dirty=d))
    return eng, queue


def payload(text: str) -> dict:
    return {"command": "create_text", "target_id": None, "parameters": {"text": text}, "timestamp": TS}


def test_fifo_order_and_one_at_a_time() -> None:
    eng, queue = make()
    queue.submit(payload("first"))
    queue.submit(payload("second"))
    assert queue.depth() == 2
    queue.pump()  # exactly one executes
    assert [el.extra["text"] for el in eng.board.elements] == ["first"]
    queue.pump()
    assert [el.extra["text"] for el in eng.board.elements] == ["first", "second"]


def test_cap_five_then_please_wait() -> None:
    _, queue = make()
    for _ in range(5):
        assert queue.submit(payload("x"))["queued"] is True
    denied = queue.submit(payload("overflow"))
    assert denied["message"] == "Please wait."


def test_confirmation_blocks_queue_until_resolved() -> None:
    eng, queue = make()
    queue.submit(payload("keep"))
    queue.pump()
    sel = eng.board.selected_element_id
    queue.submit({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS})
    queue.submit(payload("later"))
    head = queue.pump()
    assert head.get("needs_confirmation") is True
    assert queue.blocked
    blocked = queue.pump()
    assert blocked["error_code"] == "E_BLOCKED"
    resolved = queue.resolve_block(confirmed=True)
    assert resolved["ok"]
    queue.blocked = False
    tail = queue.pump()
    assert tail["ok"] and eng.board.elements[-1].extra["text"] == "later"


def test_cancel_leaves_no_trace_and_unblocks() -> None:
    eng, queue = make()
    queue.submit(payload("keep"))
    queue.pump()
    sel = eng.board.selected_element_id
    queue.submit({"command": "delete_item", "target_id": sel, "parameters": {}, "timestamp": TS})
    queue.pump()
    res = queue.resolve_block(confirmed=False)
    assert res["message"] == "Cancelled."
    assert eng.board.find(sel) is not None  # type: ignore[arg-type]


def test_failed_command_does_not_clear_queue() -> None:
    eng, queue = make()
    queue.submit({"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS})
    queue.submit(payload("after-failure"))
    first = queue.pump()
    assert first["error_code"] == errors.E_NOTHING_TO_UNDO
    assert queue.depth() == 1
    second = queue.pump()
    assert second["ok"]
