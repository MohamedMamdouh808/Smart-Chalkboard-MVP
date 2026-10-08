# Provider Contract

## Interface (unchanged from 001, now live)

```python
class AIProvider(Protocol):
    def interpret(self, transcript: str, context: dict) -> dict[str, str]: ...
```

Returns `{"raw_text": ...}` and NOTHING else. No state, DB, UI, or
network access beyond the single model call. Output is untrusted input
to the engine — always.

## GroqProvider

- Official `groq` SDK, `response_format={"type": "json_object"}`,
  model from `GROQ_MODEL`, timeout 4 s. Missing/empty key → fail fast
  at construction with a keyless message ("AI is not configured.").
- Keys MUST NOT appear in logs, errors, tooltips, chip text, metrics, or
  saved data (key-hygiene test forces failures and scans all outputs).

## Configuration

- `.env` (gitignored) via dotenv: `AI_PROVIDER=groq`, `GROQ_API_KEY=`,
  `GROQ_MODEL=`. `.env.example` committed with placeholders only.
- `AI_PROVIDER` unknown → fail fast naming the supported value(s), so
  `GeminiProvider` slots in later without interface change.
