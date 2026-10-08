"""Voice status states + mic button constants (Qt-agnostic)."""

from __future__ import annotations

STATUS_STATES: tuple[str, ...] = ("Listening", "Processing", "Validating", "Executing", "Idle")

MIC_MIN_PX = 96
MAX_UTTERANCE_S = 15
