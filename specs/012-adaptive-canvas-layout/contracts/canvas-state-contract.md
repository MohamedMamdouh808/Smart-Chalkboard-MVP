# Canvas-State Contract

## Stored dimensions

- `Board` owns integer `canvas_width` and `canvas_height`.
- New in-memory boards start at the `960 × 540` minimum.
- Snapshots without canvas data migrate to `1920 × 1080`.
- Migration never moves, rescales, deletes, or rewrites elements.
- `Board.to_dict()`, saved JSON, and AI context use stored dimensions.
- `Board.restore()` copies canvas dimensions alongside lesson, elements, selection, and version.

## Validation and placement

- Bounds validation, drag clamping, resize clamping, default placement, and export use stored dimensions.
- Default horizontal origin derives from canvas width while preserving the legacy origin at legacy width.
- Default element dimensions retain legacy sizes as maximums.
- Minimum element dimensions and canvas containment remain enforced.

## Determinism

- Identical commands applied to identical board states, including canvas size, produce identical results.
- Stored canvas size is never inferred from window size during command validation or AI interpretation.
