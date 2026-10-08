"""T030: Whisper latency probe — service overhead must fit the 1.0 s slice."""

from __future__ import annotations

import time
from pathlib import Path

from smartboard.voice.whisper_service import WhisperService


def test_transcribe_path_overhead_fits_budget(tmp_path: Path) -> None:
    """Fake backend (instant inference): path overhead must be negligible.

    Real-model benchmark (small.en vs base.en on the HP EliteBook) runs on
    hardware in Phase 5; this test pins the surrounding path cost.
    """
    svc = WhisperService(transcriber=lambda _p: "Move this down")
    latencies = []
    for i in range(20):
        audio = tmp_path / f"utt_{i}.wav"
        audio.write_bytes(b"fake")
        start = time.perf_counter()
        assert svc.transcribe(audio) == "Move this down"
        latencies.append(time.perf_counter() - start)
    assert max(latencies) < 0.5  # path overhead far inside the 1.0 s slice
