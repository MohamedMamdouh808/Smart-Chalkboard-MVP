# Test Matrix (recorded fakes — no network, no keys)

All in `tests/integration/test_ai_intent_live.py` (+ fixtures in
`tests/fixtures/ai_responses/`), each asserting board/history deltas AND
strip/chip outcomes:

| # | Case | Provider returns | Must happen |
|---|---|---|---|
| 1 | Valid commands | one valid JSON per locked command used | board changes, Done chip |
| 2 | Malformed JSON | garbage, then valid on regen | one regen, then applies |
| 3 | Malformed twice | garbage, garbage | exact error message, zero mutation |
| 4 | Unsupported command | 13th command JSON | rejected w/ supported list, zero mutation |
| 5 | Invalid target | unknown `target_id` | target-missing message, zero mutation |
| 6 | Clarification | clarification envelope | question shown, zero mutation |
| 7 | Timeout | SDK timeout twice | clear error + Retry, board/pen intact |
| 8 | No-selection "this" | contextual command, empty selection | asked to select, zero mutation |
| 9 | Key hygiene | forced failures with dummy key | key string absent from all outputs |
| 10 | Live Groq (opt-in) | real API (`SMARTBOARD_LIVE_GROQ=1`) | one heading created; skipped otherwise |
