# Test Matrix (`pytest` + `pytest-qt`)

| # | Case | How |
|---|---|---|
| 1 | Generated stylesheet | Assert `build_stylesheet()` contains the `QToolTip` rule with token background, foreground, size, border, radius, and padding values |
| 2 | Delay style hint | Assert the proxy style returns 500 for `SH_ToolTip_WakeUpDelay` and delegates other hints |
| 3 | Tooltip contrast | Assert the tooltip text/background pair meets normal-text WCAG AA contrast and is never white |
| 4 | Text preservation | Reuse the existing transcript-tooltip test proving complete tooltip text |
| 5 | Full regression | Complete suite and applicable coverage gates remain green |

Manual headed verification remains optional after automated gates pass.
