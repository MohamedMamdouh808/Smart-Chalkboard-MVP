# Test Matrix (`pytest` + `pytest-qt`)

All gesture tests are headless/offscreen with synthetic events unless a manual headed check is explicitly marked optional.

| # | Case | How |
|---|---|---|
| 1 | Drawing-box regression | Width-8 scribble-plus-line model test expects `(96,106,728,118)` |
| 2 | Box recalculation | Add, move, resize, undo, redo, and reopen paths retain complete ink coverage |
| 3 | Per-type hit testing | Heading, text, equation, rectangle, circle, line, arrow, triangle, and drawing cases |
| 4 | Drag every element type | Synthetic press/move/release changes only position and records one history entry |
| 5 | All four resize corners | Parameterized `nw`, `ne`, `sw`, and `se` gestures retain the opposite fixed corner |
| 6 | Bounds clamping | Edge-directed drag and resize remain completely inside the canvas |
| 7 | Minimum size | Resize attempts below 24 canvas units retain the minimum valid geometry |
| 8 | One history entry | Applied-history count increases by one; Undo/Redo reverse and restore the gesture |
| 9 | Escape cancellation | Widget-level Escape leaves state, version, and history unchanged |
| 10 | Window-size independence | Representative gestures pass at 960×540, 1280×720, 1920×1080, and 800×1000 |
| 11 | Mixed voice/manual | Voice resize followed by manual drag preserves points, bounds, selection, and history order |
| 12 | Full regression | Complete suite and 95%-plus core-coverage gate remain green |

Manual headed verification remains optional after automated gates pass.
