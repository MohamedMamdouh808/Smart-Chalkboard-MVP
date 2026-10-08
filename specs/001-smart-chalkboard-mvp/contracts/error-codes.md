# Error Codes

Normative mapping (engine is the source of truth; UI renders `message`
verbatim in the status area until dismissed or superseded).

| Code | When | Teacher message |
|---|---|---|
| `E_SCHEMA` | JSON unparsable, missing/extra top-level fields, wrong types | That command can't be applied: malformed request. |
| `E_UNSUPPORTED_COMMAND` | command not in locked 12 | That command can't be applied: unsupported action. |
| `E_PARAM_INVALID` | bad text length, scale out of 0.25–4.0, unknown shape/color, unknown param keys | That command can't be applied: invalid value. |
| `E_TARGET_MISSING` | target-requiring command, no id and no selection | Select an object first, then try again. |
| `E_TARGET_NOT_FOUND` | id does not exist | That object no longer exists. Please select again. |
| `E_OUT_OF_BOUNDS` | result leaves canvas or violates min size / no-room | That would move it off the board, so it was not applied. / There is no room on the board. |
| `E_NOTHING_TO_UNDO` | empty undo stack | Nothing to undo. |
| `E_NOTHING_TO_REDO` | empty redo stack | Nothing to redo. |
| `E_CONFIRMATION_REQUIRED` | destructive without confirmation | Shows modal: e.g. "Delete this equation? [Cancel] [Confirm]". |
| `E_AMBIGUOUS` | "that/this" unresolvable | Which object would you like me to [action]? |

Service-level messages (not engine codes): empty audio → "I couldn't
understand the audio. Please try again."; AI down → "Unable to understand
the command. Please try again." with Retry; offline → "No internet
connection. Voice commands are unavailable; drawing still works."; save
fail → "Couldn't save your lesson. Your board is still open."; render
fail → "Display problem. Recovering the board."
