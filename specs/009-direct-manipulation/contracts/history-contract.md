# History Contract

## One entry per accepted gesture

- Each accepted manual drag records exactly one `move_item` history entry.
- Each accepted manual resize records exactly one `resize_item` history entry.
- Both entries use source `"ui"`.
- Fixed-corner metadata is engine-method input only; it is not part of the persisted public resize-command shape.
- No additional AI-addressable command is introduced.

## History accounting

A successful gesture must:

- increment applied history by exactly one;
- increment board version through the normal engine path;
- retain an inverse sufficient for one Undo;
- retain forward state sufficient for one Redo;
- leave the manipulated element selected.

## No-history paths

The following must not change board state, board version, or history:

- gesture previews;
- selection and deselection;
- cursor movement or hover;
- Escape cancellation;
- mode-change cancellation;
- release without movement;
- invalid final geometry;
- rejected bounds or minimum-size commits;
- blocked or queue-full commits;
- failed commit execution.

## Undo/Redo behavior

- One Undo reverses the complete accepted drag or resize, including transformed drawing points and recalculated bounds.
- One Redo reapplies the complete accepted drag or resize.
- Subsequent unrelated commands follow existing history-pointer behavior.
