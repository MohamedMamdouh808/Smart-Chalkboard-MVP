# Contracts: Adaptive Canvas Layout

Normative for `/speckit.tasks` and implementation. Engine, viewport, theme, persistence, queue, AI, export, and existing gesture contracts remain binding.

- `canvas-state-contract.md` — stored dimensions, migration, state serialization, and AI context.
- `mapping-contract.md` — board-area mapping, uniform scale, centering, and shared input/output geometry.
- `growth-contract.md` — internal growth validation, version/history behavior, and UI/engine routing.
- `persistence-export-contract.md` — saved JSON, reopen behavior, and export dimensions.
- `test-matrix.md` — required `pytest`/`pytest-qt` coverage.
