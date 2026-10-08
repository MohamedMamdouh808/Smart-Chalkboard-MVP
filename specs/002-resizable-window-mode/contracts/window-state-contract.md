# Window-State Contract

- Storage: local settings store, keys `window/mode`
  (`fullscreen|normal|maximized`), `window/rect` (`[x, y, width, height]`
  of the normal window). Fresh install (no keys) → `fullscreen`.
- Save: on close (all modes; geometry meaningful for normal/maximized).
  Restore: before first paint; corrupt/missing → fullscreen default.
- Toggle: visible button + F11 work at any time (lesson open or not,
  command processing, stroke in progress, dialog open — none may lose
  input or corrupt state).
- Minimum window size 960×540 (whole window incl. chrome).
- Geometry restore MUST NOT alter board state, lesson data, or exports
  (verified by state comparison across SC-001/SC-002 trials).
