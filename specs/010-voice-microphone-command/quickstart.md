# Quickstart: Voice Microphone Command

**Feature**: `010-voice-microphone-command` | **Date**: 2026-10-06
**Status**: Implemented and verified offscreen on 2026-10-06: full suite
`383 passed, 4 skipped`; full-suite core coverage `97.24%` against the required `95%`.

## Run

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m smartboard.app.main
```

In the classroom app:

1. Start the app and confirm the microphone shows `Loading voice model...` until recognition is ready.
2. Press and hold the microphone, speak an English command, release, and confirm `Listening` followed by `Processing`.
3. Confirm the transcript appears in the `Heard:` strip and produces the same result as typing it.
4. Try a very short press, silence, and unavailable-microphone behavior, confirming the required messages and unchanged board/history.

## Verify

```powershell
$env:PYTHONPATH = "src;C:\sblibs"
$env:QT_QPA_PLATFORM = "offscreen"
py -3.11 -m pytest tests/integration/test_voice_microphone.py tests/ui/test_microphone_button_voice.py -q
py -3.11 -m pytest tests -q --cov=src/smartboard/core --cov-report=term-missing --cov-fail-under=95
```

The voice-specific test matrix is in [contracts/test-matrix.md](contracts/test-matrix.md). Required coverage includes:

- fake-recorder state machine;
- shared transcript submission path;
- one real fixture transcription;
- short recording and silence;
- missing or denied microphone;
- queueing;
- no audio written to disk;
- startup readiness;
- transcription-duration metrics.

## Manual headed checklist

- [ ] Holding the microphone shows Listening without freezing the board.
- [ ] A spoken command appears in `Heard:` and produces the typed-command result.
- [ ] Failed or unavailable voice attempts show clear messages.
- [ ] No audio files remain after successful or failed attempts.

Automated offscreen verification is complete, including synthetic press-hold,
fake transcription, real-fixture transcription, bounds, silence, unavailable
microphone, queueing, no-disk-audio, readiness, and metrics coverage. Headed
checks were not performed in this offscreen-only execution environment; the
two historical no-change branch guards and two pre-existing environment
skips account for the 4 skipped tests.
