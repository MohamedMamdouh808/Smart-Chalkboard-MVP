# Test Matrix (pytest + pytest-qt, synthetic events, offscreen)

All headless; no pen hardware, no network:

| # | Case | How |
|---|---|---|
| 1 | Synthetic mouse draw | `QTest` press/move/release → StrokeFinished with canvas points |
| 2 | Synthetic tablet draw | constructed `QTabletEvent` (position + pressure) → pressure kept |
| 3 | Mapping at 3 sizes | same stroke at 960×540, 1366×768, 1920×1080 → identical canvas points |
| 4 | Grouping timing | two strokes <1.5 s apart → one element; gap >1.5 s → two |
| 5 | Undo/redo drawing | commit → undo removes → redo restores byte-identical points |
| 6 | Voice move/resize/recolor/delete | engine commands on a drawing incl. confirmed delete + undo |
| 7 | Off-canvas strokes | start-outside ignored; outside points clipped to edge |
| 8 | Resize mid-stroke | viewport swap between samples → committed shape matches |
| 9 | Save/reopen round-trip | snapshot → restore → byte-identical drawing |
| 10 | Single-pointer rule | second contact mid-stroke ignored |
| 11 | Select-mode click | click near stroke selects with outline + handles |
| 12 | Offline draw | engine commit with providers down — board + history correct |
