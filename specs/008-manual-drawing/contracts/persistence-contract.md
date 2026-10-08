# Persistence Contract

- Drawings serialize INSIDE the existing board JSON (element dict with
  `strokes`, `width`, `color`); no new tables, no migration.
- Save/reopen round-trips MUST be byte-identical for points (x, y,
  pressure-or-absent), color, width, id, and z.
- Autosave fires on drawing commit exactly like any state-changing
  command.
