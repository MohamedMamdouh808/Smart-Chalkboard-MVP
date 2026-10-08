# Audio Contract

## Capture format

- Microphone input is 16 kHz mono 32-bit floating-point audio.
- Frames accumulate in an in-memory NumPy buffer while the microphone button is held.
- The buffer is passed directly to `model.transcribe`; live recordings are never written to disk.
- No filename, temporary file, upload, retained buffer, or audio reference survives transcription success or failure.

## Duration bounds

- Recordings shorter than 0.4 seconds are ignored before transcription.
- Recording stops at or before 15 seconds.
- Ignored recordings produce no transcript, provider call, board change, history entry, or transcription metric.

## Failure and unavailable-microphone behavior

- Missing-microphone and denied-access conditions are reported through injectable recorder errors, not audio data.
- The board, pen, and developer input remain available.
- Error text is user-facing and contains no device paths, keys, audio content, or stack traces.

## Recorded test fixture

- One checked-in recorded command WAV lives under `tests/fixtures/audio/`.
- It contains synthetic/non-sensitive speech suitable for one real-model transcription test.
- `.gitignore` gains a narrow exception for the approved fixture directory without permitting runtime audio artifacts.
