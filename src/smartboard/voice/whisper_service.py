"""Local Whisper service (lazy import; preloaded at startup; English-only)."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .audio_cleanup import EMPTY_MESSAGE, delete_audio
from .voice_config import DEFAULT_DEVICE, DEFAULT_MODEL

Telemetry = Callable[[dict[str, Any]], None]


def _default_model_factory(model: str, device: str, compute_type: str) -> Any:
    from faster_whisper import WhisperModel  # type: ignore[import-untyped]

    return WhisperModel(model, device=device, compute_type=compute_type)


class WhisperService:
    """Wraps faster-whisper. Model preloaded off the UI thread via `preload`."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        device: str = DEFAULT_DEVICE,
        transcriber: Callable[[str], str] | None = None,
        model_factory: Callable[[str, str, str], Any] | None = None,
        telemetry: Telemetry | None = None,
    ) -> None:
        self.model_name = model
        self.device = device
        self._transcriber = transcriber
        self._model_factory = model_factory or _default_model_factory
        self._telemetry = telemetry
        self._model: Any = None

    def ensure_loaded(self) -> None:
        if self._transcriber is not None or self._model is not None:
            return
        self._model = self._model_factory(self.model_name, self.device, "int8")

    def preload(self) -> None:
        self.ensure_loaded()

    def transcribe(self, audio_path: str | Path) -> str:
        try:
            if self._transcriber is not None:
                return self._transcriber(str(audio_path)).strip()
            self.ensure_loaded()
            segments, _ = self._model.transcribe(str(audio_path), language="en")
            return "".join(seg.text for seg in segments).strip()
        finally:
            delete_audio(audio_path)

    def transcribe_samples(self, samples: NDArray[np.float32]) -> tuple[str, float]:
        """Transcribe an in-memory array; the caller retains ownership."""
        self.ensure_loaded()
        start = time.perf_counter()
        try:
            segments, _ = self._model.transcribe(
                samples, language="en", beam_size=1, vad_filter=True
            )
            text = "".join(segment.text for segment in segments).strip()
            outcome = "transcript" if text else "unintelligible"
            duration_ms = (time.perf_counter() - start) * 1000.0
            if self._telemetry is not None:
                self._telemetry(
                    {
                        "duration_ms": duration_ms,
                        "model": self.model_name,
                        "device": self.device,
                        "outcome": outcome,
                    }
                )
            return text, duration_ms
        except Exception:
            if self._telemetry is not None:
                self._telemetry(
                    {
                        "duration_ms": (time.perf_counter() - start) * 1000.0,
                        "model": self.model_name,
                        "device": self.device,
                        "outcome": "error",
                    }
                )
            raise

    def transcribe_or_retry_message(self, audio_path: str | Path) -> str:
        text = self.transcribe(audio_path)
        return text if text else EMPTY_MESSAGE
