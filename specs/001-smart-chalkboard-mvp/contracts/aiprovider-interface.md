# AIProvider Interface

## Interface

```python
class RawResponse(TypedDict):
    raw_text: str  # exactly what the provider returned

class AIProvider(Protocol):
    def interpret(self, transcript: str, context: BoardContext) -> RawResponse: ...
```

- `BoardContext`: `{transcript, elements: [{id, type, label, x, y}],
  selected_element_id, commands: <12 schemas>}`. No audio, no keys, no
  full lesson content.
- Engine parses `raw_text` as JSON and validates against
  `command-schema.json`. Parse failure → regeneration path, never a bypass.

## Implementations

- `GeminiProvider` (primary): JSON/structured-output mode, timeout 2.0 s.
- `GroqProvider` (fallback): same interface, engaged on timeout, network
  error, HTTP 5xx, or rate-limit.

## Policy (normative)

1. Malformed JSON → exactly 1 regeneration on the SAME provider.
2. Still malformed/failing → fallback provider, one attempt.
3. Still failing → teacher-facing error "Unable to understand the command.
   Please try again." + Retry; board and pen unaffected.
4. Regeneration never bypasses validation; every AI output is untrusted
   input to the engine.
5. Provider failures logged as `{provider, error_type}` only.

## Env

`GEMINI_API_KEY`, `GROQ_API_KEY` from environment. Missing primary key →
fail-fast at startup with a clear message.
