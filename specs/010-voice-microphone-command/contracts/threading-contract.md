# Threading Contract

## Background work

- Model preloading, recording finalization, and transcription run off the UI thread.
- Recording capture uses non-UI audio callbacks or an injectable fake recorder.
- A `QThread` worker emits signals for:
  - recognition readiness;
  - status changes;
  - finished transcripts;
  - transcription duration;
  - unintelligible or failed outcomes;
  - worker completion.

## UI-thread boundaries

- Only the UI thread changes widgets, button text/state, status, transcript display, dialogs, or result chips.
- Worker objects never mutate board state, history, persistence, provider clients, or widgets.
- Finished transcripts are handed to the same developer-text submission function used by typed input.
- Existing provider interpretation, validation, FIFO queueing, execution, confirmation, and history behavior are unchanged.

## Cancellation and failure isolation

- Worker failure reports an understandable message and returns the UI to `Idle`.
- Failed work discards audio and never submits a transcript.
- Short, silent, missing-microphone, denied-access, blocked-queue, and full-queue outcomes never change board state or history.
