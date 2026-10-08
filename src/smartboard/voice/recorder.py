"""Push-to-talk recorder (backend-agnostic; 15 s cap; no continuous listen)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

SAMPLE_RATE = 16000
MAX_SECONDS = 15.0
MIN_SECONDS = 0.4


@dataclass
class Recording:
    audio: bytes
    duration_s: float


@dataclass
class RecordingSamples:
    samples: NDArray[np.float32]
    sample_rate: int = SAMPLE_RATE

    @property
    def duration_s(self) -> float:
        return float(self.samples.shape[0]) / float(self.sample_rate)


class MicrophoneUnavailableError(RuntimeError):
    """No usable microphone was found."""


class MicrophoneDeniedError(RuntimeError):
    """Microphone access was denied."""


class PushToTalk:
    """Press-and-hold control. Release submits. Backend injected for tests."""

    def __init__(self, backend: Callable[[], Recording] | None = None, max_s: float = 15.0) -> None:
        self._backend = backend
        self._holding = False

    def press(self) -> None:
        self._holding = True

    def release(self) -> Recording | None:
        if not self._holding:
            return None
        self._holding = False
        if self._backend is None:
            raise RuntimeError("No audio backend configured.")
        rec = self._backend()
        if not rec.audio or rec.duration_s <= 0:
            return None
        return rec


class SoundRecorder:
    """Press-hold 16 kHz mono float32 capture entirely in process memory."""

    def __init__(
        self,
        backend: Callable[[], list[NDArray[np.float32]]] | None = None,
        sample_rate: int = SAMPLE_RATE,
        max_seconds: float = MAX_SECONDS,
    ) -> None:
        self._backend = backend
        self._sample_rate = sample_rate
        self._max_seconds = max_seconds
        self._frames: list[NDArray[np.float32]] = []
        self._stream: Any = None
        self._holding = False

    def start(self) -> None:
        """Begin buffering; real hardware is opened lazily and only on demand."""
        self._holding = True
        self._frames = []
        if self._backend is not None:
            return
        try:
            import sounddevice as sd  # type: ignore[import-untyped]
        except ImportError as exc:
            raise MicrophoneUnavailableError("No microphone was found.") from exc
        try:
            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=1,
                dtype="float32",
                callback=self._append_frame,
            )
            self._stream.start()
        except Exception as exc:
            raise MicrophoneDeniedError("Microphone access was denied.") from exc

    def _append_frame(
        self, indata: NDArray[np.float32], frames: int, time: Any, status: Any
    ) -> None:
        del frames, time, status  # PortAudio callback metadata is not audio content.
        self._frames.append(np.array(indata, dtype=np.float32, copy=True).reshape(-1))

    def stop(self) -> RecordingSamples | None:
        """Finalize one utterance, capped at 15 seconds, without touching disk."""
        self._holding = False
        if self._backend is None:
            if self._stream is None:
                raise MicrophoneUnavailableError("No microphone was found.")
            try:
                self._stream.stop()
                self._stream.close()
            finally:
                self._stream = None
            frames = self._frames
        else:
            frames = self._backend()
        samples = np.concatenate(frames) if frames else np.zeros(0, dtype=np.float32)
        samples = np.asarray(samples, dtype=np.float32).reshape(-1)
        max_samples = int(self._sample_rate * self._max_seconds)
        recording = RecordingSamples(samples=samples[:max_samples], sample_rate=self._sample_rate)
        if recording.duration_s < MIN_SECONDS:
            return None
        return recording
