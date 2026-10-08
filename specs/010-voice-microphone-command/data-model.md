# Data Model: Voice Microphone Command

**Feature**: `010-voice-microphone-command` | **Date**: 2026-10-06
**Sources**: Approved `spec.md`, follow-up technical direction, `research.md`, constitution v1.0.0

Board, command, history, lesson, queue, provider, and metrics-table shapes remain unchanged. This feature adds microphone capture lifecycle, transcription configuration, worker signaling, and transcript submission; it does not add stored audio fields or AI commands.

## Voice transcription configuration

- `model`: transcription model name; default `base.en`.
- `device`: execution device; default `cpu`.
- `compute_type`: fixed classroom value `int8`.
- `language`: fixed classroom value `en`.
- `beam_size`: fixed classroom value `1`.
- `vad_filter`: fixed enabled value.
- Configuration comes from environment variables; model/device names are the only configurable transcription settings.

## In-memory recording

- `samples`: mono 32-bit floating-point audio at 16,000 Hz.
- `sample_rate`: fixed `16000`.
- `channels`: fixed mono.
- `duration`: derived as `sample_count / 16000`.
- `minimum_duration`: `0.4` seconds.
- `maximum_duration`: `15` seconds.
- Recording exists only in process memory from press until transcription completes or fails.
- No filename, file handle, file path, upload payload, or retained buffer survives transcription.

## Transcription result

- `transcript`: stripped English text, possibly empty.
- `outcome`: `transcript`, `unintelligible`, or `error`.
- `duration_ms`: measured model-transcription time.
- `model` and `device`: metric metadata only.
- The result never carries audio, filenames, transcripts in metrics, or recognition alternatives.

## Microphone readiness and interaction state

- `recognition_readiness`: `loading`, `ready`, `unavailable`, or `denied`.
- `interaction_state`: `idle`, `listening`, or `processing`.
- While loading, the microphone displays `Loading voice model...`.
- While held, the application status is `Listening`.
- After release and during transcription, the application status is `Processing`.
- Transcripts use the existing `Validating`, `Executing`, result-chip, transcription-strip, queue, and history behavior.

## Worker signaling

A background worker emits only:

- status changes;
- readiness changes;
- finished transcript plus transcription duration;
- failure or unintelligible-audio outcome;
- completion.

The worker never mutates widgets, board state, history, persistence, or provider state directly. Finished transcripts enter the existing developer-text submission function.

## Queued voice operation

A finished transcript becomes the same transcript object used by typed input. Provider interpretation, schema validation, FIFO queueing, execution, confirmation, clarification, history, and result display are unchanged.

## State transitions

```text
startup -> loading recognition in background -> ready
idle -- press-and-hold --> listening
listening -- release before 0.4s --> idle with no transcript
listening -- release at 15s or earlier --> processing
processing -- intelligible transcript --> existing AI pipeline
processing -- empty/failed transcript --> exact retry message --> idle
any recording/transcription completion --> discard audio --> idle
microphone unavailable/denied --> message --> manual and typed modes remain available
```

## Entity-to-story mapping

- US1 spoken commands: press-hold lifecycle, in-memory recording, transcription result, worker signaling, queued voice operation.
- US2 unsuccessful/unavailable input: duration bounds, unintelligible outcome, exact failure messages, memory-only disposal, continued manual/typed operation.
- US3 startup readiness: transcription configuration, background loading, recognition readiness, first-command behavior.
