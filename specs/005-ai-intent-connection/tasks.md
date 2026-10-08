# Tasks: AI Intent Connection

**Input**: Design documents from `/specs/005-ai-intent-connection/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Tests**: The 10-case recorded-fake matrix is REQUIRED by the plan (constitution V); written LAST per user order.
**Constraints**: `core/` engine semantics UNCHANGED; keys never logged; no 13th command; mic/Whisper/Gemini out of scope.

**Organization**: Ordered per user instruction — demo removal → provider + Groq → prompt builder → engine/UI wiring → dev input → tests — grouped by spec user story so each story stays independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single desktop-app project: `src/smartboard/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Secrets hygiene and dependency declaration before any provider code

- [X] T001 Add `python-dotenv` to dependencies in `pyproject.toml` and commit `.env.example` with `AI_PROVIDER=`, `GROQ_API_KEY=`, `GROQ_MODEL=` placeholders only (verify `.gitignore` already covers `.env*`)
- [X] T002 [P] Add clarification + invalid-target fixtures in `tests/fixtures/ai_responses/` (clarification envelope, unknown-`target_id` sample) for the later matrix

**Checkpoint**: No keys in the tree; dotenv importable; fixtures on disk.

---

## Phase 2: Foundational — Demo Removal (Blocking Prerequisites)

**Purpose**: Empty startup board so nothing masks the real path. BLOCKS wiring phases.

- [X] T003 [US5] Delete `DEMO_SCRIPT` and the scripted mic flow from `src/smartboard/app/main.py`; startup board empty; mic button inert with an honest "speech capture coming" tooltip

**Checkpoint**: Fresh launch shows an empty board; no static demo content anywhere.

---

## Phase 3: User Story 1 - Provider Interface + Groq (Priority: P1)

**Goal**: Typed transcript in, raw text out, Groq live behind config with key hygiene.

**Independent Test**: Fake providers drive valid/malformed/timeout paths with zero network; key string absent from all outputs on forced failure (verified in Phase 7).

- [X] T004 [US1] Implement `AIConfig`, dotenv load, and the `AI_PROVIDER` factory in `src/smartboard/ai/config.py` (fail fast on unknown provider; key passed as constructor arg, never logged)
- [X] T005 [US1] Implement the real `GroqProvider` in `src/smartboard/ai/providers.py` (official SDK, `json_object` mode, `GROQ_MODEL`, 4 s timeout; keep `GeminiProvider` a same-interface stub)
- [X] T006 [P] [US1] Key-hygiene probes (forced failures scanned for key material; unknown-provider fail-fast message) in `tests/integration/test_ai_intent_live.py` — placeholders only, full cases in Phase 7

**Checkpoint**: Provider selectable by config; keys never surface.

---

## Phase 4: Prompt Builder (serves US1–US3)

**Goal**: Schemas + context + transcript + JSON-only order in one reviewable asset.

**Independent Test**: Golden-file test pins all five prompt sections; 12-command lock visible in text (verified in Phase 7).

- [X] T007 Implement the prompt builder in `src/smartboard/ai/prompt.py` per `contracts/prompt-contract.md` (role + JSON-only order, compacted 12 schemas, board summary with selection rule, verbatim transcript, clarification envelope)

**Checkpoint**: Prompt builds deterministically from (transcript, context).

---

## Phase 5: User Stories 1–4 - Engine + UI Wiring (Priority: P1)

**Goal**: Raw response → parse → regen-once → engine → board + strip + chip, off the UI thread.

**Independent Test**: Each outcome class shows the right board delta + chip text with zero unprescribed mutation (verified in Phase 7).

- [X] T008 [US1] Wire transcript → provider → parse → `CommandEngine.execute` in `src/smartboard/app/orchestrator.py` (or current wiring module), keeping the single-writer rule: no state assignment outside the engine
- [X] T009 [US2] [US3] Wire contextual selection + clarification display: selection-sourced targets, `E_AMBIGUOUS`/envelope questions to the teacher with zero mutation, confirmation flow unchanged
- [X] T010 [US4] Wire outage path (4 s timeout, exact regeneration-exhausted and failure messages, Retry, board + pen intact) and strip/chip outcome mapping for all four outcome classes

**Checkpoint**: End-to-end intent path live; failures degrade exactly as specced.

---

## Phase 6: User Story 6 - Developer Text Input (Priority: P2)

**Goal**: Hidden transcript box exercising the identical path, invisible by default.

**Independent Test**: Normal launch shows nothing; flag on shows a working box (verified in Phase 7).

- [X] T011 [US6] Add the flag-gated dev transcript input in `src/smartboard/ui/main_window.py` (and minimal wiring in `src/smartboard/app/main.py`): `setVisible(False)` unless `SMARTBOARD_DEV_INPUT=1`, submits through the same transcript path

**Checkpoint**: Teachers never see it; developers type the full path.

---

## Phase 7: Verification — Recorded Matrix + Regression (Final)

**Purpose**: The requested tests LAST: all 10 matrix cases, then the full suite

- [X] T012 Create the recorded-fake matrix in `tests/integration/test_ai_intent_live.py` (cases 1–8: valid, malformed-then-valid, malformed-twice, unsupported, invalid target, clarification, timeout, no-selection "this" — each asserting board/history deltas AND strip/chip outcomes)
- [X] T013 [P] Add prompt golden-file test in `tests/contract/test_prompt_contract.py` (five sections present, no 13th command, no code/side-effect language) and the opt-in live-Groq test (skipped without `SMARTBOARD_LIVE_GROQ=1`)
- [X] T014 Run the matrix plus the FULL suite green with `core/` semantics untouched and record outcomes in `specs/005-ai-intent-connection/quickstart.md`

**Checkpoint**: All acceptance scenarios verified; no behavior regressions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Demo removal (Phase 2)**: Depends on Setup — BLOCKS wiring (empty board first)
- **Provider (Phase 3, US1)**: Depends on Phase 2 (nothing masked when it lands)
- **Prompt (Phase 4)**: Depends on Phase 3 (needs provider + config shapes)
- **Wiring (Phase 5, US1–US4)**: Depends on Phases 2–4
- **Dev input (Phase 6, US6)**: Depends on Phase 5 (exercises the wired path)
- **Verification (Phase 7)**: Depends on all implementation phases

### User Story Dependencies

- **US5 (P1)**: After Setup — first, so fakes can never hide behind demo
- **US1 (P1)**: After US5 — provider + prompt + wiring, no dependencies on other stories
- **US2/US3 (P1)**: After US1 path exists (selection + clarification ride it)
- **US4 (P1)**: After US1 path exists (failure branches of the same wiring)
- **US6 (P2)**: After US1–US4 wiring (thin UI over the proven path)

### Within Each Phase

- Config before provider (T004 → T005); prompt before wiring (T007 → T008–T010)
- One writer at a time for `main.py` (T003 → T011 strictly sequential)
- Tests last: T012–T013 written after all implementation, then T014 full run

### Parallel Opportunities

- T001 and T002 overlap (different files, no dependency)
- T006 probes and T013 golden/live tests can draft early (different files), finalized in Phase 7
- All other tasks are sequential (provider → prompt → wiring chain, shared `main.py`)

---

## Implementation Strategy

### MVP First (US5 + US1 intent path)

1. Complete Phases 1–2 (secrets hygiene + empty board)
2. Complete Phases 3–5 (provider → prompt → wired engine/UI)
3. **STOP and VALIDATE**: typed phrase → validated board change + Done chip

### Incremental Delivery

1. Setup + empty board → nothing masked
2. + Provider/Groq → typed transcript in, raw text out
3. + Prompt builder → constrained, reviewable requests
4. + Wiring → board deltas + chip outcomes + failure behavior
5. + Dev input → hidden, flag-gated typing
6. + Verification → 10-case matrix green, full suite green

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to spec user story for traceability (US1–US6)
- Engine rule: parsed responses go to `CommandEngine.execute` (or the queue) ONLY — enforced by review + T014
- Key rule: `GROQ_API_KEY` never in tree/logs/errors/exports — enforced by T006 probes
- Commit after each task or logical group; stop at any checkpoint to validate independently
- Avoid: 13th commands, prompt side-effect language, UI-thread network, demo leftovers, mic/Whisper/Gemini scope creep
