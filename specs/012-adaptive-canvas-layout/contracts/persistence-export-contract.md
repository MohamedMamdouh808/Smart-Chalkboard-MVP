# Persistence and Export Contract

## Saved lessons

- Saved board JSON includes stored `canvas_width` and `canvas_height`.
- Reopening restores stored dimensions, elements, selection, version, and history compatibility.
- Snapshots without canvas data reopen at `1920 × 1080` with unchanged coordinates.
- No database schema migration is required; canvas data travels inside existing board JSON.

## Exports

- PNG export dimensions derive from the lesson’s stored canvas size.
- Snapshots without canvas data export at legacy `1920 × 1080`.
- Export rendering uses stored-canvas coordinates without stretching.
