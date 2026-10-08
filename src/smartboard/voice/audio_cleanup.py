"""Audio cleanup — raw audio deleted after transcription, incl. on failure."""

from __future__ import annotations

from pathlib import Path


def delete_audio(path: str | Path) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        pass


def sweep_temp_audio(directory: str | Path, pattern: str = "utt_*.wav") -> int:
    removed = 0
    for candidate in Path(directory).glob(pattern):
        try:
            candidate.unlink()
            removed += 1
        except OSError:
            continue
    return removed


EMPTY_MESSAGE = "I couldn't understand the audio. Please try again."
