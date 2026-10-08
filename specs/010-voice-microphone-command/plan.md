# Implementation Plan: Voice Microphone Command

**Branch**: `010-voice-microphone-command` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)
**Input**: Approved feature specification plus user-supplied faster-whisper, capture, threading, configuration, telemetry, and test directives

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Connect press-hold microphone input to the existing transcript pipeline using in-memory faster-whisper transcription. Capture 16 kHz mono float32 audio while held, transcribe the NumPy array once in a QThread worker with `base.en` on CPU/int8, discard audio immediately, and submit finished transcripts through the existing developer-text path. Cover behavior with fake-recorder/transcriber tests, one real fixture transcription, duration bounds, silence, unavailable-microphone, queueing, and no-disk-audio tests.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyQt6/QThread and signals, faster-whisper 1.2.1, NumPy, sounddevice to be added, existing provider/validation/queue/history/UI infrastructure
**Storage**: No audio persistence; existing metrics schema unchanged; one approved WAV test fixture with a narrow `.gitignore` exception
**Testing**: `pytest`, `pytest-qt`, offscreen Qt, fake recorder/transcriber doubles, one checked-in speech fixture, filesystem-absence assertions, no live hardware or network tests
**Target Platform**: Windows desktop classroom machine
**Project Type**: desktop-app, existing single-project layout
**Performance Goals**: Background model preload preserves startup interaction; existing p50 voice target remains applicable after transcription; short recordings skip inference; transcription duration is logged without transcript/audio content
**Constraints**: Memory-only audio; English-only transcription; 0.4-second minimum; 15-second maximum; exact unintelligible-audio message; clear unavailable-microphone behavior; existing statuses/result behavior; FIFO queueing; twelve locked AI commands unchanged; continuous listening, wake word, other languages, voice confirmation, noise cancellation, and audio saving excluded
**Scale/Scope**: One press-hold utterance at a time; one shared transcript pipeline; four representative failure classes plus readiness and metrics coverage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — Transcription produces text only. Finished transcripts enter existing provider interpretation and validation; only the engine mutates board state. PASS.
- [x] II. Determinism — Existing command/state determinism is unchanged; transcription output remains informational input to the deterministic pipeline. PASS.
- [x] III. Separation — Capture/transcription details stay out of board, schema, validation, engine, history, and persistence logic. Widgets manage interaction/presentation; workers emit signals without mutating UI or state. PASS.
- [x] IV. Code quality — Typed small voice/UI/app modules, injectable recorder/transcriber/telemetry seams, no `eval`/`exec`, no untrusted dynamic behavior. PASS.
- [x] V. Test-first — Fake state-machine tests, fixture transcription, bounds/silence/unavailable/queue/no-disk tests, full suite, and applicable coverage gates precede and verify implementation. PASS.
- [x] VI. Security/privacy — Memory-only audio, immediate disposal including on failure, no uploads, no saved artifacts, no keys in code/logs, transcript-only provider context. PASS.
- [x] VII. Reliability — Atomic engine behavior preserved; FIFO queueing preserved; voice failure degrades to manual/typed operation without crashing or state loss. PASS.
- [x] VIII. Scope — No new AI-addressable command; existing twelve-command schema unchanged; all stated exclusions remain excluded. PASS.

Re-check after Phase 1 design (`research.md`, `data-model.md`, `contracts/`, `quickstart.md` above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/010-voice-microphone-command/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── audio-contract.md
│   ├── transcription-contract.md
│   ├── threading-contract.md
│   ├── ui-contract.md
│   └── test-matrix.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/voice/voice_config.py     # NEW: WHISPER_MODEL/WHISPER_DEVICE defaults and validation
src/smartboard/voice/recorder.py          # MODIFY: in-memory 16 kHz mono float32 capture with injectable backend
src/smartboard/voice/whisper_service.py   # MODIFY: NumPy-array transcription path plus compatibility path
src/smartboard/voice/voice_worker.py      # NEW: QThread preload/transcription worker and signals
src/smartboard/ui/mic_button.py           # MODIFY: press-hold behavior and loading/ready presentation
src/smartboard/ui/main_window.py          # MODIFY: microphone press/release wiring and status propagation
src/smartboard/app/main.py                # MODIFY: background preload, transcript reuse, status/result handling
pyproject.toml                            # MODIFY: add sounddevice runtime dependency
tests/fixtures/audio/command.wav          # NEW: approved real-speech fixture with narrow ignore exception
tests/integration/test_voice_microphone.py # NEW: fake state machine, queueing, failures, no-disk assertions
tests/ui/test_microphone_button_voice.py  # NEW: hold/release, readiness text, status/transcript behavior
tests/unit/test_voice_config.py           # NEW: model/device defaults and environment overrides
```

**Structure Decision**: Extend the existing single-project layout in place. Voice capture/transcription remains isolated in `voice/`; Qt threading/presentation remains in `ui/` and `app/main.py`; provider, validation, queue, engine, history, and persistence semantics stay untouched.

## Implementation flow

1. **Configuration and service seams**
   - Add environment-backed model/device configuration with `base.en` and `cpu` defaults.
   - Extend transcription to accept in-memory NumPy audio while retaining the established compatibility path.
   - Add an injectable telemetry callback for transcription duration without transcript/audio content.

2. **Capture and worker threading**
   - Implement press-hold 16 kHz mono float32 buffering with 15-second cutoff and injectable missing/denied-microphone errors.
   - Implement a QThread worker for one-time background preload and per-utterance finalization/transcription.
   - Emit readiness, status, transcript/duration, failure, and completion signals without worker-side UI or state mutation.

3. **UI and pipeline integration**
   - Add microphone loading text and press-hold behavior while preserving unrelated button behavior.
   - Show Listening during capture and Processing during transcription.
   - Display finished transcripts in `Heard:` and submit them through the existing developer-text function.
   - Ignore sub-0.4-second audio, show exact silence/failure messages, preserve manual/typed operation, and queue transcribed commands normally.

4. **Verification**
   - Add fake-recorder/transcriber tests for state transitions, shared pipeline behavior, bounds, silence, unavailable hardware, queueing, readiness, metrics, and filesystem absence.
   - Add the approved speech fixture and one real `base.en` transcription test.
   - Retain the full regression suite and applicable coverage gates.
   - Leave optional real-display checks in `quickstart.md`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
