# Contracts: Voice Microphone Command

Normative for `/speckit.tasks` and implementation. AI, engine, queue, persistence, viewport, theme, and existing voice contracts remain binding.

- `audio-contract.md` — capture format, duration bounds, memory-only handling, and test fixture.
- `transcription-contract.md` — model configuration, in-memory API, transcription behavior, and metrics.
- `threading-contract.md` — background loading/transcription, signals, UI-thread boundaries, and pipeline reuse.
- `ui-contract.md` — button behavior, readiness text, statuses, transcript display, results, and unavailable-microphone behavior.
- `test-matrix.md` — required `pytest`/`pytest-qt` coverage.
