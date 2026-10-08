# Test Matrix (`pytest` + `pytest-qt`)

All microphone tests avoid real hardware and network access except the one explicitly marked real-model test.

| # | Case | How |
|---|---|---|
| 1 | Press-hold state machine | Fake recorder/transcriber drives idle, listening, processing, validation, execution, and idle transitions |
| 2 | Full transcript path | Fake transcript enters the same developer-text submission function and produces the typed-command outcome |
| 3 | Real transcription | Checked-in command WAV is transcribed by real `base.en` with the required language/beam/VAD settings |
| 4 | Short recording | Sub-0.4-second buffer is ignored before transcription, provider use, state change, or history change |
| 5 | Silence | Silent fixture produces the exact unintelligible-audio message and no provider call |
| 6 | No microphone | Missing/denied recorder errors preserve board, pen, developer input, state, and history |
| 7 | Queueing | A finished transcript waits behind in-progress work and executes in FIFO order |
| 8 | No disk audio | Recording, success, failure, silence, and unavailable-microphone paths create no audio files |
| 9 | Startup readiness | Background preload transitions the microphone from loading text to ready without blocking startup interaction |
| 10 | Metrics | Transcription duration is recorded with model/device metadata and no transcript or audio content |
| 11 | Full regression | Complete suite and applicable coverage gates remain green |

Manual headed verification remains optional after automated gates pass.
