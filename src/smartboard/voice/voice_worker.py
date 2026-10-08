"""Background voice-model loading and transcription worker (Qt signals only)."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from .voice_config import VoiceConfig
from .whisper_service import Telemetry, WhisperService


class VoiceWorker(QObject):
    """Loads and uses one transcription model without blocking the UI thread."""

    statusChanged = pyqtSignal(str)
    modelReady = pyqtSignal()
    transcribeRequested = pyqtSignal(object)
    transcriptReady = pyqtSignal(str, float)
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(
        self,
        config: VoiceConfig | None = None,
        model_factory: Callable[[str, str, str], Any] | None = None,
        transcriber: Callable[[NDArray[np.float32]], tuple[str, float]] | None = None,
        telemetry: Telemetry | None = None,
        service: WhisperService | None = None,
        parent: Any = None,
    ) -> None:
        super().__init__(parent)
        self._service = service or WhisperService(
            model=(config or VoiceConfig()).model,
            device=(config or VoiceConfig()).device,
            model_factory=model_factory,
            telemetry=telemetry,
        )
        self._transcriber = transcriber
        self._model_lock = threading.RLock()
        self.transcribeRequested.connect(self.transcribe_samples)

    @pyqtSlot()
    def load_model(self) -> None:
        """Construct the configured model once and announce readiness."""
        with self._model_lock:
            if self._service._model is not None:
                return
            self.statusChanged.emit("loading")
            self._service.ensure_loaded()
        self.modelReady.emit()

    @pyqtSlot(object)
    def transcribe_samples(self, samples: NDArray[np.float32]) -> None:
        """Finalize one utterance and transcribe it off the UI thread."""
        self.statusChanged.emit("processing")
        try:
            if self._transcriber is not None:
                text, duration_ms = self._transcriber(samples)
            else:
                text, duration_ms = self._service.transcribe_samples(samples)
            if text:
                self.transcriptReady.emit(text, duration_ms)
            else:
                from .audio_cleanup import EMPTY_MESSAGE

                self.failed.emit(EMPTY_MESSAGE)
        except Exception as exc:  # noqa: BLE001 - transcription faults emit failure
            self.failed.emit(f"Transcription failed: {exc}")
        finally:
            self.finished.emit()
