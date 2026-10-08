# Smart Chalkboard

A deterministic, voice-driven classroom whiteboard desktop app. Teachers speak commands, draw with a pen, and manipulate content directly on an **infinite, pannable, zoomable board** — while a single deterministic engine owns every board mutation, keeping behavior predictable, reversible, and testable.

Built with **Python 3.11**, **PyQt6**, local **Whisper** speech-to-text, **Groq** language-model command interpretation, and **SQLite** persistence.

---

## Table of contents

- [Features](#features)
- [Board controls](#board-controls)
- [AI command contract](#ai-command-contract)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the app](#running-the-app)
- [Testing](#testing)
- [Lint, format, and types](#lint-format-and-types)
- [Project structure](#project-structure)
- [Persistence and migration](#persistence-and-migration)
- [Performance targets](#performance-targets)
- [Security and privacy](#security-and-privacy)
- [Troubleshooting](#troubleshooting)
- [Scope and roadmap](#scope-and-roadmap)

---

## Features

### Infinite board (current)

- **Edgeless world**: elements live in unbounded world coordinates with the origin at `(0,0)` — no page edge, no canvas to outgrow.
- **Application-owned camera**: pan offset plus zoom (`10%–400%`) is view state, never board content. Camera moves never touch the board, version, selection, or Undo history.
- **Pan**: hold `Space` and drag (works in Pen and Select modes), middle-mouse drag, mouse-wheel/touchpad scroll, `Shift`+wheel for horizontal scroll, and empty-space drag in Select mode.
- **Zoom**: `Ctrl`+wheel and pinch zoom around the pointer, zoom buttons, `Ctrl`+`+` / `Ctrl`+`-`, reset to 100% with `Ctrl`+`0`, `Shift`+`1` Fit-all, plus a live zoom-percentage indicator.
- **Dot grid** that pans and zooms with the camera (zoom-dependent spacing, constant dot size).
- **Viewport culling**: only elements intersecting the visible rectangle are painted (200-element performance target).

### Direct text creation and inline editing

- In Select mode, **double-click empty board space** to create a text element at that point and start editing immediately.
- **Double-click existing text, headings, or equations** to edit them in place.
- `Enter` (or clicking outside) commits; `Shift`+`Enter` inserts a newline in multiline text; `Escape` (or committing empty text) discards/reverts with **zero history side effects**.
- Every accepted creation or edit is engine-validated and recorded as **exactly one Undo entry**.

### Voice commands

- **Press-and-hold microphone button**: `Listening` → `Processing` states, local Whisper transcription (`base.en`, CPU/int8 by default), memory-only audio.
- Voice-created elements are placed **in the currently visible area** (near top-left, below nearby content when possible) so they are always visible.
- Relative moves ("move left", "move up") use **zoom-scaled world units**.
- The AI receives a short, viewport-aware context: visible world bounds, selected element, and at most **50 compact visible/nearby element summaries** — never stroke data, audio, or secrets.
- Ambiguous commands ask for clarification instead of guessing; destructive commands require confirmation.

### Pen drawing and direct manipulation

- Pressure-aware pen/stylus/mouse/touch drawing, stroke grouping, and single-commit history entries — fully offline capable.
- Strokes store **world coordinates** with constant world-unit widths at any pan/zoom.
- Select-mode **drag to move** and **corner-handle resize** with live previews, committed as one history entry on release; `Escape` cancels.
- Selection outlines, handles, and highlight rings render at **constant on-screen size** from 10% to 400% zoom.

### Deterministic engine

- One `CommandEngine` is the **sole board-state writer**. AI output, pen input, gestures, and inline edits all pass through validation and a FIFO queue under one engine lock.
- Closed **12-command AI schema** (no 13th command — internal operations like pen commits and text edits are engine entry points, never AI-addressable).
- Atomic commands, snapshot-based Undo/Redo (100-step depth), typed error codes (`E_SCHEMA`, `E_OUT_OF_BOUNDS`, `E_AMBIGUOUS`, …), teacher-friendly messages.

### Lessons, export, and theming

- Lessons persist to SQLite as opaque JSON snapshots containing **board content plus camera**; reopening restores both.
- Legacy fixed/adaptive-canvas lessons migrate with **coordinates preserved** (centered 100% view).
- PNG export renders **all content bounds plus a fixed margin at 100%**; empty lessons export a valid image.
- Dark theme with centralized tokens, styled tooltips (500 ms delay), and high-contrast pairs.

---

## Board controls

| Action | Input |
|---|---|
| Pan | `Space`+drag, middle-mouse drag, wheel scroll, `Shift`+wheel (horizontal), Select-mode empty-space drag |
| Zoom in/out around pointer | `Ctrl`+wheel, pinch gesture, `+`/`-` buttons, `Ctrl`+`+` / `Ctrl`+`-` |
| Reset zoom to 100% | `100%` button or `Ctrl`+`0` |
| Fit all content | `Fit` button or `Shift`+`1` |
| Create text | Double-click empty space (Select mode) |
| Edit text/heading/equation | Double-click the element |
| Commit edit | `Enter` or click outside |
| Cancel edit | `Escape` (empty input discards/reverts silently) |
| Draw | Pen mode: press and drag |
| Move element | Select mode: drag the body |
| Resize element | Select mode: drag a corner handle |
| Cancel gesture | `Escape` |
| Undo / Redo | Buttons or `Ctrl`+`Z` / `Ctrl`+`Y` (where wired) |
| Voice command | Press and hold the microphone button |
| Fullscreen toggle | `F11` |
| Pen / Select mode | `P` / `S` or the mode button |

---

## AI command contract

The AI may emit **exactly one JSON object** per transcript, using only these commands:

| Command | Purpose |
|---|---|
| `create_heading` | Heading text (1–200 chars) |
| `create_text` | Body/equation text (1–2000 chars) |
| `move_item` | Absolute position or relative direction/distance |
| `resize_item` | Scale factor (0.25–4.0) or explicit size (min 24×24) |
| `delete_item` | Delete target (needs confirmation) |
| `clear_board` | Clear all (needs confirmation, board must be non-empty) |
| `create_shape` | rectangle / circle / line / arrow / triangle |
| `change_color` | Named palette color or `#RRGGBB` |
| `undo` / `redo` | History navigation |
| `save_lesson` / `new_lesson` | Lesson persistence actions |

Every envelope requires `{command, target_id, parameters, timestamp}`. Unknown commands, shapes, colors, sizes, and out-of-range world values are rejected with typed errors and leave state and history untouched.

---

## Architecture

```text
src/smartboard/
├── core/          UI-independent model, schema, validation, engine, history
│   ├── board.py        Board/Element, unbounded world geometry, numeric guards
│   ├── engine.py       CommandEngine: sole writer, validation, undo/redo, edit_text
│   ├── validators.py   Per-command validation, finite world-limit checks
│   ├── gesture.py      Drag/resize candidate geometry (no UI, no canvas)
│   ├── hit_test.py     Type-specific hit testing, zoom-scaled tolerance
│   ├── command_schema.py  Locked 12-command envelope validation
│   ├── history.py      100-step inverse-based undo/redo
│   └── errors.py       Typed codes + teacher-friendly messages
├── app/           Application layer: camera ownership, queue, wiring
│   ├── camera.py       CameraState, pan/zoom/fit math, normalization
│   ├── orchestrator.py FIFO queue + engine lock, voice normalization, text commits
│   ├── placement.py    Deterministic visible-viewport default placement
│   ├── lesson_document.py  Board+camera snapshot envelope + legacy migration
│   ├── exporter.py     Content-bounds PNG export (read-only)
│   ├── main.py         App entry point and widget wiring
│   └── ...
├── ai/            Providers, prompt, viewport-scoped context builder
├── voice/         Recorder, Whisper service/worker, config (memory-only audio)
├── ui/            Widgets only: render state, emit intents (no business rules)
│   ├── board_view.py      Edgeless canvas, input routing, culling, grid
│   ├── board_paint.py     Shared read-only element painting (view + export)
│   ├── camera_transform.py Qt-agnostic world/screen transform adapter
│   ├── text_overlay.py    Provisional inline editor (commit/discard intents)
│   └── ...
└── persistence/   SQLite repos (lessons, history, metrics) + migrations
```

Key invariants:

- `core/` and `persistence/` import with **PyQt6 blocked** (enforced by contract test).
- Widgets emit intents (`StrokeFinished`, `GestureFinished`, `CameraChanged`, `InlineEditRequested`, …); the orchestrator applies them through the queue/engine.
- Camera updates never create history entries; normalized voice commands are self-contained so undo/redo never needs camera state.
- Lesson snapshots are opaque JSON — no SQLite schema change was needed for the camera.

---

## Requirements

- **Python 3.11** (`py -3.11` on Windows)
- **PyQt6 ≥ 6.6** (UI)
- **faster-whisper ≥ 1.0**, **sounddevice** (local transcription)
- **groq ≥ 0.5**, **python-dotenv** (command interpretation)
- Dev: `pytest`, `pytest-qt`, `pytest-cov`, `ruff`, `black`, `mypy`

---

## Installation

```powershell
# 1. Clone and enter the repo
git clone <repo-url>
cd chalckboard

# 2. Create and activate a virtual environment (recommended)
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install runtime dependencies
pip install -r requirements.txt

# 4. Install dev/test tooling (optional)
pip install -e ".[dev]"
```

> **Note:** `start.bat` sets `PYTHONPATH=src;C:\sblibs` (a machine-local PyQt6 location). If PyQt6 is installed in your environment instead, `PYTHONPATH=src` is sufficient.

---

## Configuration

Copy the example file and fill in values (`.env` is gitignored — **never commit real keys**):

```powershell
Copy-Item .env.example .env
```

| Variable | Purpose | Default |
|---|---|---|
| `AI_PROVIDER` | Command-interpretation provider | `groq` (only supported provider) |
| `GROQ_API_KEY` | Groq API key (**secret**) | _(empty)_ |
| `GROQ_MODEL` | Model for command JSON | `openai/gpt-oss-20b` |
| `SMARTBOARD_DEV_INPUT` | `1` reveals the developer transcript box | hidden |
| `WHISPER_MODEL` | Local STT model | `base.en` |
| `WHISPER_DEVICE` | STT device | `cpu` |

Without `GROQ_API_KEY`, voice/AI commands report "not configured" while pen, selection, gestures, and inline editing keep working fully offline.

---

## Running the app

```powershell
# Easiest (sets PYTHONPATH and shows the dev transcript box):
.\start.bat

# Or manually (visible window — omit QT_QPA_PLATFORM):
$env:PYTHONPATH = "src"
py -3.11 -m smartboard.app.main
```

On first run the Whisper model loads in the background (microphone button shows loading until ready). Press and hold the mic button, speak a command ("Create a heading Newton's Laws"), release, and watch the transcription strip.

---

## Testing

471 tests: unit, contract, integration, UI (`pytest-qt`, offscreen), end-to-end, and performance.

```powershell
$env:PYTHONPATH = "src"            # add ;C:\sblibs if PyQt6 lives there
$env:QT_QPA_PLATFORM = "offscreen" # headless Qt for automated runs

# Full suite
py -3.11 -m pytest tests -q

# With the enforced core-coverage gate (≥95%)
py -3.11 -m pytest tests -q --cov=src/smartboard/core --cov-report=term --cov-fail-under=95
```

Coverage highlights: engine/geometry/history at ~95–100%; Qt-dependent modules are covered through offscreen widget tests. Visual regression references live in `tests/ui/refs/` and regenerate only via `pytest tests/ui/test_regression.py --regen-refs` (commit the result deliberately).

---

## Lint, format, and types

```powershell
py -3.11 -m ruff check src tests
py -3.11 -m black --check src/smartboard
$env:PYTHONPATH = "src"
py -3.11 -m mypy src/smartboard   # strict mode, must be clean
```

Conventions: complete type hints, small single-purpose modules, no `eval`/`exec`, theme tokens for all UI colors/sizes, and test-first discipline for engine changes.

---

## Project structure

```text
.
├── src/smartboard/        Application source (see Architecture above)
├── tests/
│   ├── unit/              Headless core/math/policy tests
│   ├── contract/          Schema, prompt, transform, UI-independence guards
│   ├── integration/       Queue/engine/persistence/voice/export flows
│   ├── ui/                pytest-qt widget tests + visual refs (tests/ui/refs/)
│   ├── e2e/               Mixed voice/pen/gesture scenarios
│   ├── performance/       Latency budgets + 200-element board checks
│   └── fixtures/          AI responses, synthetic audio
├── specs/                 Feature specs, plans, tasks (001–013)
│   └── 013-infinite-board/  Current infinite-board spec/plan/tasks
├── .specify/              Spec-kit workflow, constitution, extensions
├── requirements.txt       Runtime dependencies
├── start.bat              Windows launcher
└── README.md              This file
```

Development workflow lives in `AGENTS.md` (points at the active plan) and `.specify/memory/constitution.md` (principles, 12-command lock, gates).

---

## Persistence and migration

- SQLite (`WAL` mode, transactional writes): `lessons`, `board_states` (opaque JSON, last 20 kept), `command_history` (undo survives reopen), `metrics_events`.
- New snapshot shape: `{lesson_id, version, elements, selected_element_id, camera: {pan_x, pan_y, zoom}}` — no canvas fields.
- Legacy snapshots: `canvas` data is ignored (coordinates preserved); bare snapshots reopen at origin/100%, canvas snapshots reopen centered at 100%.
- Export: union of canonical world bounds + 48-unit margin at 100%; empty lessons yield a fixed 960×540 image.

---

## Performance targets

- Command validation + execution: **p50 < 100 ms**.
- Smooth pan/zoom with **≥ 200 elements** (linear viewport culling; only intersecting elements painted).
- AI context bounded to **50 compact summaries**; no stroke arrays leave the process.

---

## Security and privacy

- API keys load from `.env`/environment only; never logged, never embedded in errors, prompts, or exports.
- Raw microphone audio stays in memory and is deleted immediately after transcription (plus a temp-audio sweep at startup).
- AI output is untrusted input: strict schema/parameter validation, one regeneration on parse failure, clarification instead of guessing.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `ModuleNotFoundError: PyQt6` | Install requirements or add the local lib dir: `$env:PYTHONPATH = "src;C:\sblibs"` |
| `AI is not configured` | Set `GROQ_API_KEY` in `.env` |
| Mic button stuck on "loading" | Whisper model still downloading/loading; check logs, then retry |
| `No microphone was found` | No input device or OS permission denied; board/pen/dev input still work |
| Widget tests crash without display | Set `$env:QT_QPA_PLATFORM = "offscreen"` |
| `QFontDatabase: Cannot find font directory` | Offscreen Qt ships no fonts; text-rendering pixel assertions are avoided in tests |
| Visual regression mismatch | Board rendering changed legitimately — review, then regenerate refs with `--regen-refs` |

---

## Scope and roadmap

**Deliberately out of scope**: multiple pages, multi-select, rotation, snapping/guides, minimap, collaboration, continuous listening, non-English STT, LMS integration.

**Notes for maintainers**:

- The infinite board intentionally expands the original fixed-canvas V1 scope — see `specs/013-infinite-board/constitution-amendment-proposal.md`; ratify the amendment in `.specify/memory/constitution.md` before merging to a protected branch.
- The internal `edit_text` engine operation follows the pen-commit precedent: validated and history-tracked, but never AI-addressable.
- Three UI defaults are recorded as reversible assumptions in the 013 plan: Space-drag pans in Pen mode, the dot grid is always on, and Fit-all (`Shift+1`) is the only recenter affordance.
#   S m a r t - C h a l k b o a r d - M V P  
 