# Quickstart: AI Intent Connection

**Feature**: `005-ai-intent-connection` | **Date**: 2026-10-04
**Verified**: 2026-10-04 — matrix green with recorded fakes; full suite
green (234 passed); core coverage gate holds; no network or keys used.

## Configure (developer)

```powershell
Copy-Item .env.example .env   # then fill GROQ_API_KEY / GROQ_MODEL
$env:PYTHONPATH = "src;C:\sblibs"
$env:SMARTBOARD_DEV_INPUT = "1"   # reveal the dev transcript box
py -3.11 -m smartboard.app.main
```

Type a command phrase in the dev box (e.g. "Create a heading called
Newton's Second Law") and watch the board, strip, and chip. The startup
board is empty; the mic button is inert until speech capture lands.

## Verify (no keys, no network)

```powershell
py -3.11 -m pytest tests/integration/test_ai_intent_live.py -q
py -3.11 -m pytest tests -q   # full suite incl. no-regression gate
```

## Live Groq (opt-in, costs a call)

```powershell
$env:SMARTBOARD_LIVE_GROQ = "1"  # with a real GROQ_API_KEY in .env
py -3.11 -m pytest tests/integration/test_ai_intent_live.py -q -k live_groq
```
