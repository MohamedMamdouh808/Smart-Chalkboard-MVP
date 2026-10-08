# Feature Specification: Voice Microphone Command

**Feature Branch**: `010-voice-microphone-command`  
**Created**: 2026-10-06  
**Status**: Draft  
**Input**: User description: "Connect the microphone to the Smart Chalkboard so a spoken command goes through the full pipeline. The teacher presses and holds the microphone button to record and releases to stop; while holding, status shows Listening. On release, the recording is transcribed locally with Whisper (English only), status shows Processing, and the transcript appears in the "Heard:" strip. The transcript then goes through the existing AI intent step, deterministic validation and execution, with the existing Validating and Executing statuses and result chip. Audio stays in memory only and is never saved to disk or uploaded; it is discarded right after transcription, including on errors. Recordings shorter than 0.4 seconds are ignored, and recordings are capped at 15 seconds. Silent or unintelligible audio shows "I couldn't understand the audio. Please try again." and sends nothing to the AI. If no microphone is found or access is denied, show a clear message and keep the board, pen and dev input working. Voice commands wait in the existing command queue if one is already processing. The Whisper model is loaded in the background at startup so the first command is not slow, with a "Loading voice model..." state on the mic button until it is ready. Out of scope: continuous listening, wake word, other languages, voice confirmation, noise cancellation, saving audio."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Speak a board command (Priority: P1)

A teacher presses and holds the microphone button, speaks a classroom command, and releases the button. The board shows Listening while recording, Processing afterward, displays the heard transcript, and then applies the same result that typing the same command would produce.

**Why this priority**: Hands-free command entry is the central value; without reliable press-hold recording and full-pipeline execution, spoken teaching commands cannot be trusted.

**Independent Test**: Can be fully tested by speaking representative commands with a microphone and comparing board state, transcript display, statuses, and result feedback against typed-command behavior.

**Acceptance Scenarios**:

1. **Given** the microphone is available, **When** the teacher presses and holds the microphone button, **Then** recording starts and the status shows Listening.
2. **Given** a completed recording of at least 0.4 seconds, **When** the teacher releases the button, **Then** the status shows Processing and the transcript appears in the “Heard:” strip.
3. **Given** an intelligible English command, **When** transcription completes, **Then** the existing intent, validation, execution, status, and result behavior process it exactly as if the transcript had been typed.
4. **Given** a command issued while another command is processing, **When** the spoken command finishes transcription, **Then** it waits in the existing command queue and executes in order.

---

### User Story 2 - Trust unsuccessful or unavailable voice input (Priority: P1)

A teacher receives clear feedback when audio cannot be used, understood, or transcribed. The board never sends silent or unintelligible audio for interpretation, never saves audio, and remains fully usable for manual and typed commands.

**Why this priority**: Classroom privacy and predictable failure behavior are as important as successful recognition; unclear or unsafe failures would prevent microphone use.

**Independent Test**: Can be fully tested with too-short recordings, silence, unintelligible audio, transcription failures, missing microphones, and denied access, without requiring successful recognition.

**Acceptance Scenarios**:

1. **Given** a recording shorter than 0.4 seconds, **When** recording stops, **Then** it is ignored and no transcript is sent for interpretation.
2. **Given** silent or unintelligible audio, **When** transcription completes unsuccessfully, **Then** the board shows “I couldn't understand the audio. Please try again.” and sends nothing for interpretation.
3. **Given** any completed or failed transcription, **When** the transcription step finishes, **Then** no audio remains saved on disk or uploaded, and only the transcript result remains available to the command pipeline.
4. **Given** no microphone or denied microphone access, **When** the teacher attempts voice input, **Then** a clear message appears while the board, pen, and developer input continue working.

---

### User Story 3 - Start the first voice command without a cold-start delay (Priority: P2)

A teacher sees whether voice recognition is ready before speaking. The recognition capability prepares in the background at startup, and the microphone clearly indicates while it is still loading.

**Why this priority**: A slow first command undermines confidence in classroom timing, while an explicit loading state prevents teachers from speaking before the system can hear them.

**Independent Test**: Can be fully tested by launching the app, observing the microphone loading state, and comparing the responsiveness of the first command with later commands.

**Acceptance Scenarios**:

1. **Given** application startup, **When** voice recognition is still preparing, **Then** the microphone button shows “Loading voice model...”.
2. **Given** completed background preparation, **When** the loading indicator clears, **Then** the first spoken command proceeds without requiring a separate warm-up command.

---

### Edge Cases

- What happens when the teacher releases before 0.4 seconds? The recording is ignored with no transcript, AI call, board change, or history entry.
- What happens when recording reaches 15 seconds? Recording stops at the cap and only the capped audio is transcribed.
- What happens when audio contains silence or cannot be understood? The exact unintelligible-audio message appears and the pipeline stops before interpretation.
- What happens when transcription itself errors? Audio is discarded, an understandable failure message appears, and nothing is sent for interpretation.
- What happens when microphone hardware or permission is unavailable? A clear message appears and manual/typed workflows continue unchanged.
- What happens when another command is processing? The transcribed voice command queues normally and does not execute concurrently.
- What happens when the teacher speaks another language? Only English is supported; non-English input is outside this feature’s acceptance scope.
- What happens when continuous listening or a wake word is expected? Those behaviors remain explicitly out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Pressing and holding the microphone button MUST start recording and display Listening.
- **FR-002**: Releasing the microphone button MUST stop recording and begin local transcription with a Processing status.
- **FR-003**: Completed transcripts MUST appear in the “Heard:” strip.
- **FR-004**: Intelligible transcripts MUST use the existing intent, validation, execution, status, and result behavior without changing command semantics.
- **FR-005**: Recordings MUST remain in memory only, MUST never be saved to disk or uploaded, and MUST be discarded immediately after transcription, including after errors.
- **FR-006**: Recordings shorter than 0.4 seconds MUST be ignored without interpretation, board changes, or history entries.
- **FR-007**: Recordings MUST stop no later than 15 seconds after starting.
- **FR-008**: Silent or unintelligible audio MUST display “I couldn't understand the audio. Please try again.” and MUST NOT be sent for interpretation.
- **FR-009**: Missing-microphone and denied-access conditions MUST display clear messages while board, pen, and developer-input workflows continue working.
- **FR-010**: A transcribed voice command issued during another operation MUST wait in the existing command queue and MUST NOT execute concurrently.
- **FR-011**: Voice recognition MUST prepare in the background at startup, and the microphone MUST display “Loading voice model...” until ready.
- **FR-012**: Out of scope: continuous listening, wake word, non-English language support, voice confirmation, noise cancellation, and audio saving.

### Key Entities *(include if feature involves data)*

- **Voice command**: A press-hold-release utterance intended to produce one classroom board action.
- **Recording lifecycle**: Listening capture bounded by the 0.4-second minimum and 15-second maximum, followed by transcription and immediate audio disposal.
- **Transcript**: The text produced from a recording and shown in the “Heard:” strip.
- **Recognition readiness**: The microphone’s ready/loading state before the first command.
- **Queued voice operation**: A transcribed command waiting behind an in-progress command under existing queue behavior.
- **Voice result**: The existing validation/execution outcome and result-chip feedback for a spoken transcript.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Teachers successfully complete representative spoken board commands without assistance in at least 9 out of 10 trials.
- **SC-002**: At least 95 of 100 intelligible English commands produce the same board outcome as typing the corresponding transcript.
- **SC-003**: Every too-short, silent, unintelligible, failed-transcription, missing-microphone, and denied-access trial produces the required message and leaves board state and history unchanged.
- **SC-004**: No audio file, temporary audio artifact, upload, or recoverable recording remains after any successful or failed voice trial.
- **SC-005**: The first spoken command after startup proceeds without requiring a separate warm-up command once readiness is indicated.
- **SC-006**: Teachers rate spoken-command feedback—Listening, Processing, transcript display, validation/execution status, and result—as clear and predictable in at least 9 out of 10 trials.

## Assumptions

- The existing AI interpretation, deterministic validation, command queue, history, status, and result-chip behavior are reused unchanged.
- Push-to-hold interaction is the only supported recording interaction.
- Only English commands are supported; behavior for other languages is not specified.
- “Silent or unintelligible” means transcription produces no usable command text or reports transcription failure.
- Background preparation does not delay startup interaction with the board, pen, or developer input.
- No change to the twelve-command AI schema is required because spoken transcripts enter the existing interpretation path.
