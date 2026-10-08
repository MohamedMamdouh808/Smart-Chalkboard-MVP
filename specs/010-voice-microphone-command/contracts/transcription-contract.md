# Transcription Contract

## Model configuration

- Default model: `base.en`.
- Default device: `cpu`.
- Fixed compute type: `int8`.
- Environment overrides:
  - `WHISPER_MODEL`;
  - `WHISPER_DEVICE`.
- The model is constructed once and preloaded in a background worker at startup.

## In-memory transcription API

- `WhisperService` accepts either:
  - an in-memory NumPy audio array for live microphone use; or
  - a filesystem path for established compatibility tests.
- Live transcription calls:
  - `model.transcribe` with the NumPy array;
  - `language="en"`;
  - `beam_size=1`;
  - `vad_filter=True`.
- Returned text is stripped before use.

## Empty and failed transcription

- Empty or whitespace-only transcription produces the exact message:
  - `I couldn't understand the audio. Please try again.`
- Failed transcription discards audio, reports an understandable failure, and sends nothing to the AI provider.
- Existing path-based deletion behavior remains for compatibility tests.

## Metrics

- Transcription wall time is measured around model inference.
- Only duration milliseconds plus model/device/result metadata are recorded.
- Metrics never include transcripts, audio, filenames, alternatives, confidence internals, or speaker information.
