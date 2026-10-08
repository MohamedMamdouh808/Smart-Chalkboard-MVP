# Regression Contract

- Method: `QWidget.grab()` offscreen (`QT_QPA_PLATFORM=offscreen`) at
  **1366×768** and **1920×1080**, seeded Newton board (heading +
  equation + drawing), all five mic states, one dialog open shot.
- Assertions (structural, not brittle hashes): surface rect centered
  with border pixels sampled; chip/pill texts present; button
  geometries ≥ minima; selection handles painted at the four corners.
- Reference PNGs: one per size in `tests/ui/refs/`; tolerant diff gate
  ≤0.5% differing pixels; refs regenerate ONLY via an explicit
  `--regen-refs` run (committed deliberately, never auto-updated).
- Contrast: token-pair luminance test (theme-contract) runs headless in
  the same suite.
