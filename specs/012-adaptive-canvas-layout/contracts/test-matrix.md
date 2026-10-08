# Test Matrix (`pytest` + `pytest-qt`)

All layout tests use synthetic resizes and stored-state fixtures unless a manual headed check is explicitly marked optional.

| # | Case | How |
|---|---|---|
| 1 | Canvas growth | Enlarge available area and verify stored dimensions grow and never shrink on later smaller areas |
| 2 | Element stability | Resize through representative sizes and verify exact coordinates, dimensions, and content |
| 3 | Uniform downscale | Use a smaller window than stored canvas and verify uniform scale, centering, and no clipping |
| 4 | Coordinate mapping | Convert representative points at several sizes and verify exact inverse mapping |
| 5 | Right/bottom bounds | Place and move elements at stored right/bottom edges and verify containment/rejection |
| 6 | Legacy reopen | Restore a snapshot without canvas data and verify 1920×1080 size with unchanged coordinates |
| 7 | Save/reopen | Save stored canvas/state and verify byte-identical restoration |
| 8 | History invariance | Resize repeatedly and verify zero new history entries with unchanged version/content semantics |
| 9 | Window-minus-margins width | Verify board surface width equals available window width minus layout margins at 959×566 |
| 10 | Full regression | Complete suite and applicable coverage gates remain green |

Manual headed verification remains optional after automated gates pass.
