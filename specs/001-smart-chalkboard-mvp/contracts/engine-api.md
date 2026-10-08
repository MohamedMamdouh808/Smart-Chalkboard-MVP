# Engine API

## Single-writer rule

Only `CommandEngine.execute(raw: dict | str, *, source: str) -> EngineResult`
may mutate `Board`. UI, AI, and persistence layers never mutate directly.
Pen commits enter as internal `add_drawing` ops through the same method.

```python
class EngineResult(TypedDict, total=False):
    ok: bool
    state_version: int
    affected_id: str | None
    error_code: str        # on failure, one of the typed codes below
    message: str           # teacher-friendly text
    needs_confirmation: bool
    confirmation_prompt: str
    needs_clarification: bool
    clarification_question: str
```

## Pipeline (all steps, in order)

1. Parse JSON (if str) → 2. schema shape → 3. supported command →
   4. params → 5. target (or selection) → 6. board-state (bounds/capacity/
   history preconditions) → 7. allowed-ops → 8. destructive? (confirm) →
   9. resolve defaults (positions, ×1.25/×0.8, palette/hex, shape enum) →
   10. reject (typed error, zero mutation) or 11. execute atomically →
   12. version+state → 13. history (with inverse; undo/redo pointer moves
   only) → 14. render event.

## Queue

`CommandQueue`: FIFO, max 5 waiting ("Please wait" beyond), exactly one
command validated/executed at a time, context snapshotted at dequeue,
confirmation/clarification blocks the queue, failures never clear it.
Pen commits serialize through the same queue.

## Error codes → teacher messages

| Code | Message |
|---|---|
| `E_SCHEMA` | That command can't be applied: malformed request. |
| `E_UNSUPPORTED_COMMAND` | That command can't be applied: unsupported action. Supported: 12 listed commands. |
| `E_PARAM_INVALID` | That command can't be applied: invalid value. |
| `E_TARGET_MISSING` | Select an object first, then try again. |
| `E_TARGET_NOT_FOUND` | That object no longer exists. Please select again. |
| `E_OUT_OF_BOUNDS` | That would move it off the board, so it was not applied. |
| `E_NOTHING_TO_UNDO` | Nothing to undo. |
| `E_NOTHING_TO_REDO` | Nothing to redo. |
| `E_CONFIRMATION_REQUIRED` | Confirmation needed (dialog shown). |
| `E_AMBIGUOUS` | Which object would you like me to [action]? |

Rejected/cancelled/timed-out commands change neither state nor history
(verified by state-comparison tests).
