# Research: Voice Microphone Command

**Feature**: `010-voice-microphone-command` | **Date**: 2026-10-06
**Input**: Approved `spec.md`, follow-up technical direction, constitution v1.0.0, existing voice/UI/app implementation

No NEEDS CLARIFICATION remains. The specification fixes behavior and privacy boundaries; the technical direction fixes the transcription stack, threading model, configuration, and test doubles.

## Decisions

### R-01: Use faster-whisper `base.en` on CPU with int8 compute

- **Decision**: Load `base.en` once with `device="cpu"` and `compute_type="int8"`, transcribe with `language="en"`, `beam_size=1`, and `vad_filter=True`.
- **Rationale**: Matches the approved English-only classroom requirement and the requested startup/readiness behavior while minimizing CPU/memory cost.
- **Alternatives rejected**: Larger or multilingual models, GPU execution, wider beams, and network transcription—all conflict with local-only, bounded classroom behavior.

### R-02: Capture 16 kHz mono float32 audio into memory only

- **Decision**: Use `sounddevice` at 16 kHz mono float32, accumulate frames in an in-memory NumPy buffer, cap capture at 15 seconds, and pass the array directly to `model.transcribe`.
- **Rationale**: This preserves the constitution’s no-audio-on-disk requirement and avoids temporary-file lifecycle bugs.
- **Alternatives rejected**: WAV files plus cleanup, which the new path must not use for live recordings; lower sample rates or stereo capture, which add resampling/channel-handling complexity without a specified benefit.

### R-03: Keep file-path transcription only as a compatibility seam

- **Decision**: Extend `WhisperService` to accept either an in-memory NumPy array or a filesystem path. Live microphone audio always uses the in-memory path; existing path-based tests and failure semantics remain supported.
- **Rationale**: The requested implementation changes live capture without needlessly breaking established transcription tests.
- **Alternatives rejected**: Removing path support immediately, which would churn existing tests without user benefit; writing memory buffers to temporary files, which would violate the privacy requirement.

### R-04: Run recording finalization and transcription in a QThread worker

- **Decision**: Move recording finalization and transcription to a `QThread` worker exposing status, transcript, error, and finished signals. The UI thread handles only button state, status display, transcript display, and submission of finished transcripts.
- **Rationale**: Model loading and transcription must not block painting, pointer input, or dialogs.
- **Alternatives rejected**: Direct UI-thread transcription; `concurrent.futures` callbacks that still require UI-thread polling or manual thread marshaling for widget updates.

### R-05: Reuse the developer-text submission path

- **Decision**: Feed finished voice transcripts into the same `submit_dev_transcript` function used by developer text input.
- **Rationale**: This creates one audited path to provider interpretation, validation, queueing, execution, status updates, and result display.
- **Alternatives rejected**: A parallel microphone submission path, which could diverge in queueing, confirmation, status, history, or error behavior.

### R-06: Configure model and device through environment variables

- **Decision**: Read `WHISPER_MODEL` and `WHISPER_DEVICE`, defaulting to `base.en` and `cpu`; retain fixed classroom transcription behavior unless explicitly configured.
- **Rationale**: Follows the project’s existing environment-based configuration pattern and permits controlled hardware/model changes without code edits.
- **Alternatives rejected**: Hard-coded model/device values, settings-file secrets, command-line-only configuration, and exposing model selection in classroom UI.

### R-07: Record transcription duration as metrics-only telemetry

- **Decision**: Measure transcription wall time around model inference and emit duration milliseconds with model/device/result metadata through an injectable telemetry callback backed by structured logging. Never store transcripts, audio, filenames, or recognition content.
- **Rationale**: The technical direction explicitly requires performance metrics, while avoiding a new production database connection keeps persistence scope unchanged.
- **Alternatives rejected**: Opening a production metrics database solely for voice telemetry; logging transcripts or audio references; omitting duration telemetry after being explicitly requested.

### R-08: Test with fakes, one real fixture, and disk-absence assertions

- **Decision**:
  - Use fake recorder/transcriber doubles for the press-hold, status, queueing, short-recording, silence, missing-microphone, and failure state machine.
  - Add one checked-in recorded command WAV under `tests/fixtures/audio/`.
  - Test real `base.en` transcription against that fixture.
  - Assert that recording, transcription, success, and failure paths create no audio files.
  - Add a `.gitignore` exception for the approved test fixture without weakening the ban on runtime audio artifacts.
- **Rationale**: Fast deterministic tests cover classroom behavior; one real-model test guards the actual transcription contract; filesystem assertions enforce privacy.
- **Alternatives rejected**: Real microphone/network tests in CI; generated tones as a substitute for a real speech fixture; leaving the fixture ignored by version control.

## Performance notes

- Model preloading happens once in a background worker; classroom interaction remains available during loading.
- Short recordings are rejected before transcription.
- Transcription duration telemetry excludes queueing, provider interpretation, validation, and execution.
