"""Local Whisper service (lazy import; preloaded at startup; English-only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .audio_cleanup import EMPTY_MESSAGE, delete_audio


class WhisperService:
    """Wraps faster-whisper. Model preloaded off the UI thread via `preload`."""

    def __init__(self, model: str = "small.en", transcriber: Callable[[str], str] | None = None) -> None:
        self.model_name = model
        self._transcriber = transcriber
        self._model: Any = None

    def preload(self) -> None:
        if self._transcriber is not None or self._model is not None:
            return
        from faster_whisper import WhisperModel  # lazy: heavy dependency

        self._model = WhisperModel(self.model_name)

    def transcribe(self, audio_path: str | Path) -> str:
        try:
            if self._transcriber is not None:
                return self._transcriber(str(audio_path)).strip()
            if self._model is None:
                self.preload()
            segments, _ = self._model.transcribe(str(audio_path), language="en")  # type: ignore[union-attr]
            return "".join(seg.text for seg in segments).strip()
        finally:
            delete_audio(audio_path)

    def transcribe_or_retry_message(self, audio_path: str | Path) -> str:
        text = self.transcribe(audio_path)
        return text if text else EMPTY_MESSAGE
