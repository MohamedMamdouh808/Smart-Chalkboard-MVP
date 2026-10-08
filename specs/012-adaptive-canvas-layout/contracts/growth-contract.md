# Growth Contract

## Internal operation

- `grow_canvas(width, height)` is an internal engine operation, not one of the twelve AI-addressable commands.
- Dimensions must be integers at or above the canvas minimum.
- Invalid dimensions are rejected with typed validation errors.
- Requests at or below stored size succeed as no-ops without changing version, state, history, or hooks.
- Each dimension grows independently to the requested available size.

## State and history effects

- Actual growth updates stored canvas dimensions and board version.
- Growth records no history entry and invokes no history hook.
- Growth requires no confirmation or clarification.
- Growth never moves, rescales, deletes, or rewrites elements.

## UI and concurrency routing

- The board widget emits available-area dimensions on show and resize without mutating state.
- The application calls growth only when available dimensions exceed stored dimensions.
- Engine-lock serialization prevents growth from racing queued voice/manual operations.
- Failed growth refreshes unchanged state without history effects.
