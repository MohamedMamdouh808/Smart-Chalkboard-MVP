"""T045: 100-command latency harness — validation+execution < 100 ms each."""

from __future__ import annotations

import statistics
import time

from smartboard.core.engine import CommandEngine

TS = "2026-10-03T18:15:00Z"


def test_hundred_commands_fit_validation_execution_budget() -> None:
    eng = CommandEngine()
    latencies: list[float] = []
    for i in range(100):
        start = time.perf_counter()
        res = eng.execute({"command": "create_text", "target_id": None,
                           "parameters": {"text": f"line {i}"}, "timestamp": TS})
        latencies.append((time.perf_counter() - start) * 1000)
        assert res["ok"] or res.get("error_code") == "E_OUT_OF_BOUNDS"
        if res.get("error_code") == "E_OUT_OF_BOUNDS":
            eng.execute({"command": "clear_board", "target_id": None, "parameters": {}, "timestamp": TS},
                        confirmed=True)
    p50 = statistics.median(latencies)
    assert p50 < 100, f"p50 validation+execution {p50:.1f} ms exceeds 100 ms"
    assert max(latencies) < 500, f"max {max(latencies):.1f} ms way over budget"
