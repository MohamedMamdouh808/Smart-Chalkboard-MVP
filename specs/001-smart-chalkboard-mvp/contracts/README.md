# Contracts: Smart Chalkboard MVP

This directory holds the implementation contracts for the MVP. All are
normative for `/speckit.tasks` and implementation.

- `command-schema.json` — JSON Schema for the 12 locked commands (validation source of truth).
- `aiprovider-interface.md` — `AIProvider` abstraction, context envelope, fallback/regeneration policy.
- `engine-api.md` — deterministic engine public API, queue semantics, error-code table.
- `persistence-schema.sql` — SQLite DDL (migrations, lessons, board_states, command_history, metrics_events).
- `error-codes.md` — typed error codes with teacher-facing messages.
- `acceptance-scenario.md` — Newton's Second Law E2E script (spec SC-001 / constitution gate).
