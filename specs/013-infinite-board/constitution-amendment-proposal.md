# Constitution Amendment Proposal: Infinite Board

**Feature**: `013-infinite-board`
**Date**: 2026-10-08
**Status**: Proposal only; the constitution has not been amended yet.

## Proposed version

Bump `.specify/memory/constitution.md` from `1.0.0` to `1.1.0`.

A MINOR bump is appropriate: this materially expands product scope and guidance without removing the existing safety principles.

## Proposed changes

1. Amend Principle VIII / Scope Discipline:
   - Retain the locked 12-command AI contract.
   - Approve `013-infinite-board` as an explicit constitutionally authorized scope expansion.
   - Clarify that internal engine operations such as `add_drawing` and `edit_text` are not AI-addressable commands.

2. Amend Additional Constraints:
   - Replace “fixed-size single-page canvas” with “unbounded world-coordinate board.”
   - Replace “every element bounding box MUST lie wholly inside the canvas” with finite numeric sanity limits plus minimum-size validation.
   - Retain legacy lesson coordinate compatibility: old snapshots preserve coordinates and receive a derived 100% viewing camera.

3. Preserve unchanged:
   - AI isolation.
   - Determinism.
   - UI-independent core.
   - Test-first discipline and coverage gates.
   - Security/privacy and least-exposure AI context.
   - Atomic FIFO command execution and offline pen continuity.

## Migration note

- Existing snapshots keep authoritative element coordinates.
- Legacy `canvas` fields are ignored by the new board model.
- Legacy snapshots without camera data reopen at origin/100%.
- Legacy snapshots with canvas dimensions reopen centered at 100%.
- No SQLite schema migration is required because snapshots remain opaque JSON.

## Merge requirement

The `013-infinite-board` implementation PR must ratify this amendment in `.specify/memory/constitution.md`, including the version bump and migration note, before merge.
