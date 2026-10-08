# Implementation Plan: AI Intent Connection

**Branch**: `005-ai-intent-connection` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification + user technical brief + constitution v1.0.0

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Wire the live AI intent path: dotenv config + `AI_PROVIDER` selection,
real `GroqProvider` (SDK JSON mode), prompt builder with schemas and
context, off-UI-thread 4 s calls with one regen, engine-only execution,
empty startup board, and a flag-gated dev transcript box — proven by
recorded-fake tests for all 7 brief cases plus hygiene and live gates.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `groq` SDK (declared), `python-dotenv` (add), PyQt6 workers (existing), pytest (existing) — engine/voice/persistence untouched
**Storage**: `.env` (gitignored) + committed `.env.example` (placeholders); no schema changes
**Testing**: pytest with recorded fake providers (no network/keys); opt-in live Groq test behind env
**Target Platform**: Windows desktop (same classroom machine)
**Project Type**: desktop-app (existing single project)
**Performance Goals**: 4 s provider timeout; UI never blocks; single regen bounds cost; 3 s voice target applies to the normal path only
**Constraints**: `core/` + engine semantics UNCHANGED; keys never logged/displayed; no 13th command anywhere; mic/Whisper capture out of scope
**Scale/Scope**: Single configured provider (`groq`); Gemini slots in later unchanged

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. AI Isolation — provider returns raw text only; only the engine mutates state; pen/demo paths unchanged in effect. PASS.
- [x] II. Determinism — same transcript + same state + same canned response → same board; live calls excluded from determinism claims. PASS.
- [x] III. Separation — all work in `ai/` + `app/main.py` wiring (+ tests); `core/` + `persistence/` unmodified. PASS.
- [x] IV. Code quality — typed small modules, prompt as reviewable asset, no eval/exec. PASS.
- [x] V. Test-first — 10-case matrix with fakes before wiring; full suite must pass unchanged. PASS.
- [x] VI. Security/privacy — dotenv + gitignored `.env`, example placeholders, key-hygiene test, least-exposure context. PASS.
- [x] VII. Reliability — timeouts/errors preserve board + pen with retry; regen bounded at one; no duplicate applies. PASS.
- [x] VIII. Scope — 12 locked commands, prompt + engine both enforce; mic/Whisper/Gemini explicitly out. PASS.

Re-check after Phase 1 design (research/data-model/contracts/quickstart above): no new violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/005-ai-intent-connection/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── README.md
│   ├── provider-contract.md
│   ├── prompt-contract.md
│   ├── wiring-contract.md
│   └── test-matrix.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/smartboard/ai/
├── config.py        # NEW: dotenv load, AIConfig, AI_PROVIDER factory
├── prompt.py        # NEW: prompt builder (schemas + context + JSON-only order)
└── providers.py     # EXTEND: real GroqProvider (SDK, json_object, 4 s timeout)

src/smartboard/app/main.py   # MODIFY: delete demo flow, empty startup, dev box (flag-gated)
pyproject.toml               # MODIFY: add python-dotenv dependency
.env.example                 # NEW: placeholders only (keys never committed)

tests/integration/test_ai_intent_live.py  # NEW: 10-case matrix with fakes
tests/fixtures/ai_responses/              # EXTEND: clarification + invalid-target samples
```

**Structure Decision**: Existing single-project layout extended in place.
`ai/` stays UI-free; `main.py` wiring is the only UI touch; `core/`
semantics frozen.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | — | — |
