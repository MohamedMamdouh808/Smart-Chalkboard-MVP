# Contracts: Direct Manipulation

Normative for `/speckit.tasks` and implementation. Engine, viewport, theme, persistence, queue, and AI contracts remain binding.

- `geometry-contract.md` — drawing bounds, previews, resizing, clamping, and commit quantization.
- `hit-test-contract.md` — per-type selection geometry and handle detection.
- `gesture-contract.md` — widget states, input handling, previews, cursors, cancellation, and commit routing.
- `history-contract.md` — one reversible UI-sourced history entry and no-history cancellation.
- `test-matrix.md` — required `pytest`/`pytest-qt` coverage.
