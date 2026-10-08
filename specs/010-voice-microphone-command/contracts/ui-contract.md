# UI Contract

## Microphone button

- The microphone supports press-and-hold recording and release-to-stop.
- Existing click behavior remains available only where it does not conflict with press-hold semantics.
- During background model preparation, the button displays:
  - `Loading voice model...`
- When ready, normal microphone appearance and behavior return.

## Statuses and transcript display

- Holding shows `Listening`.
- Release/transcription shows `Processing`.
- Finished transcripts appear in the `Heard:` strip.
- Transcripts then use existing `Validating`, `Executing`, result-chip, transcription-strip, and queue behavior.
- Existing pen, board, gesture, dialog, and developer-input behavior remain unchanged.

## Unavailable or failed voice input

- Missing-microphone and denied-access attempts show clear messages.
- Too-short recordings are ignored without transcript or pipeline activity.
- Silent or unintelligible recordings show:
  - `I couldn't understand the audio. Please try again.`
- Transcription errors show an understandable failure without exposing paths, keys, audio, stack traces, or provider internals.
