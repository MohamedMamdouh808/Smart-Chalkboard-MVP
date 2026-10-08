# Quickstart: Smart Chalkboard MVP

**Feature**: `001-smart-chalkboard-mvp` | **Date**: 2026-10-03

## Prerequisites

- Python 3.11+, Windows 10/11, microphone, HID/stylus pen (mouse works as fallback).
- Set keys (never commit them): `setx GEMINI_API_KEY "..."` / `setx GROQ_API_KEY "..."`.

## Setup

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install  # lint + format gates
```

## Run

```powershell
python -m smartboard.app.main          # fullscreen board (Esc opens lesson panel)
python -m smartboard.app.main --lesson demo  # open a saved lesson
```

Press-and-hold the mic button (≥96×96 px), speak, release. Watch
Listening → Processing → Validating → Executing → Idle plus the
transcription strip. Draw anytime with the pen; pen works with no network.

## Verify (constitution gates)

```powershell
pytest tests/unit -q                                   # engine, headless
pytest tests -q --cov=src/smartboard/core --cov-report=term-missing  # ≥95% on validation/history
pytest tests/e2e/test_newton_scenario.py -q            # acceptance scenario
pytest tests/integration -q                            # fixtures: tests/fixtures/audio/*, tests/fixtures/ai_responses/*
pytest tests/performance -q                            # 100-command latency breakdown
```

## Layout

- `src/smartboard/core/` — board, commands, validation, engine, history (no PyQt6).
- `src/smartboard/{persistence,voice,ai,app,ui}/` — adapters around the core.
- `specs/001-smart-chalkboard-mvp/contracts/` — schema, engine, AI, SQL, errors, E2E script.

## Failure drills

- Kill network mid-voice → clear error, pen keeps working, Retry appears.
- Cancel a delete → state+history byte-identical.
- Empty recording → "I couldn't understand the audio. Please try again."
