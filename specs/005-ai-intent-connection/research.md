# Research: AI Intent Connection

**Feature**: `005-ai-intent-connection` | **Date**: 2026-10-04
**Input**: spec + user technical brief (AIProvider iface, Groq SDK JSON
mode, dotenv + `.env.example`, provider-by-config, prompt builder,
engine-only mutation, off-UI-thread 4 s timeout, one regen, pytest with
recorded fakes for 7 cases)

No NEEDS CLARIFICATION: the brief prescribes each mechanism; prior
artifacts (`001` contracts, existing `ai/` modules) cover the rest.

## Decisions

### R-01: Reuse and extend the existing `ai/` package (no rewrite)

- **Decision**: Keep `provider_iface.py`, `context_builder.py`,
  `fallback_policy.py`; extend `providers.py` with a real `GroqProvider`
  on the official `groq` SDK and add `prompt.py` (prompt builder) +
  `config.py` (dotenv load, `AI_PROVIDER` selection). `GeminiProvider`
  stays a stub behind the same interface for later.
- **Rationale**: 001 already proved the interface, fallback policy, and
  regen-once rule in tests; rewriting would orphan that coverage.
- **Alternatives rejected**: Fresh parallel package (duplicates the
  tested policy); putting prompt text inside the provider (untestable,
  unreviewable).

### R-02: Configuration via dotenv, example committed, keys never logged

- **Decision**: `python-dotenv` loads `.env` (already gitignored via
  `.env*`); commit `.env.example` with `GROQ_API_KEY=`, `GROQ_MODEL=`,
  `AI_PROVIDER=groq` placeholders only. `config.py` exposes a frozen
  dataclass; provider constructors receive the key as an argument (never
  read env themselves, never log or display it — tested by asserting no
  key material in logs/errors on forced failure).
- **Rationale**: User-brief directive + constitution VI/SEC-01/SEC-02.
- **Alternatives rejected**: OS credential store now (heavier, no test
  seam; documented follow-up); hard-coded defaults (leak risk).

### R-03: Provider selected by `AI_PROVIDER`, Groq first

- **Decision**: `AI_PROVIDER=groq` (only supported value in V1; unknown
  values fail fast with a clear message). Factory returns the provider
  for the orchestrator; adding `GeminiProvider` later means one new
  branch, no interface change.
- **Rationale**: User-brief directive; keeps the Gemini extension point
  from 001 intact.
- **Alternatives rejected**: Auto-fallback chain now (spec scopes this
  feature to the single configured provider path; fallback policy module
  remains for the later dual-provider feature).

### R-04: Prompt builder with schemas + context + JSON-only order

- **Decision**: `prompt.build(transcript, context)` emits: role
  instruction (emit exactly one JSON object, no prose), the 12 command
  schemas (compacted from `contracts/command-schema.json`), the board
  context summary (element IDs, types, short labels, positions,
  `selected_element_id`), the transcript, and the clarification
  envelope spec (`{"clarification_needed": true, "question": "..."}` for
  ambiguous requests). Groq call uses `response_format={"type":
  "json_object"}` with the selected `GROQ_MODEL`.
- **Rationale**: User-brief directive; schemas-in-prompt is what makes
  the 12-command lock hold at the source, with the engine as the
  backstop.
- **Alternatives rejected**: Free-form prompt + hope (hallucinated 13th
  commands); few-shot examples with real lesson data (privacy exposure).

### R-05: 4 s timeout off the UI thread, one regen

- **Decision**: Network call runs on the existing worker pool
  (`app/workers.py`) with a 4 s SDK timeout; malformed JSON → exactly
  one same-request regeneration → then "Unable to understand the
  command. Please try again." Timeout/failure → clear error + Retry,
  board and pen untouched. Note: the 3 s voice target applies to the
  normal path; timeout/fallback paths are exempt by nature (documented,
  same stance as 001 research R-03 which used 2.0 s — this feature
  standardizes on the brief's 4 s).
- **Rationale**: User-brief directive; UI never blocks (constitution
  PERF-04); single regen bounds cost and latency.
- **Alternatives rejected**: UI-thread call (freezes board); unbounded
  retries (latency blowout, cost blowout).

### R-06: Demo content out, dev box in (main window only)

- **Decision**: Delete `DEMO_SCRIPT`/scripted mic flow from
  `app/main.py`; startup board is empty. Mic button keeps its existing
  appearance but is inert until speech capture lands (tooltip says so).
  Add a `QLineEdit`-based dev input, `setVisible(False)` unless
  `SMARTBOARD_DEV_INPUT=1`, submitting text through the identical
  transcript → provider → engine → chip path.
- **Rationale**: Spec FR-009/FR-010; keeps `orchestrator`,
  `command_queue`, and engine byte-identical in behavior.
- **Alternatives rejected**: Keeping demo content alongside (masks real
  path failures — the exact harm spec US5 exists to prevent).

### R-07: Tests with recorded fakes (no network, no keys)

- **Decision**: pytest with fake providers (lambdas/ canned JSON files
  under `tests/fixtures/ai_responses/`) covering all 7 brief cases:
  valid commands, malformed JSON, unsupported command, invalid target,
  clarification response, timeout, no-selection "this" reference. A live
  Groq test is opt-in via env (`SMARTBOARD_LIVE_GROQ=1` + key), skipped
  otherwise — same pattern as the live-mic test.
- **Rationale**: User-brief directive; deterministic CI without secrets.
- **Alternatives rejected**: Live-API tests in CI (secrets, flakiness,
  cost); hand-mocked SDK internals (couples tests to SDK versions).
