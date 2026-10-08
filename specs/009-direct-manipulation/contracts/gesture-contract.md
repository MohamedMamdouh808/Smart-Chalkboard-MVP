# Gesture Contract

## Interaction states

`BoardView` must maintain exactly these Select-mode interaction states:

- `idle`: no active gesture;
- `dragging`: an element body is being moved;
- `resizing`: a selected corner handle is being moved.

Pen-mode input, single-pointer handling, and `StrokeFinished` behavior remain unchanged.

## Input handling

- Mouse, tablet, and touch presses use the existing handlers and pointer keys.
- Every gesture sample uses the viewport current at sample time.
- Presses in Pen mode continue drawing and never enter gesture states.
- Select-mode press order:
  1. handle of the currently selected element;
  2. type-specific element hit;
  3. empty-space deselection.
- Movement below a small canvas threshold remains click-selection behavior.
- Crossing the threshold enters `dragging` or `resizing`.
- Mode changes clear any active press candidate, preview, and gesture state.

## Preview rendering

- Capture the original element geometry and copied drawing points at gesture start.
- Suppress the underlying committed element while its preview is displayed.
- Translate the snapshot for drags.
- Scale the snapshot about the fixed corner for resizes.
- Repaint on pointer movement without writing board state, history, persistence, or command payloads.
- Cursor behavior:
  - diagonal resize cursor over or during an active handle gesture;
  - normal Select-mode cursor otherwise.

## Cancellation

The following must clear previews and gesture state without mutation:

- Escape during an active candidate, drag, or resize;
- mode change;
- release without movement;
- invalid final geometry;
- rejected, blocked, or queue-full commit.

Cancellation must preserve or refresh the original rendering and leave the applicable selection available. `BoardView` must accept widget-level Escape while a gesture is active without changing unrelated MainWindow Escape behavior.

## Commit routing

- On a valid release, the widget emits one gesture payload:
  - drag: standard `move_item`;
  - resize: existing `resize_item` dimensions plus fixed-corner engine metadata.
- The application routes the payload through the existing FIFO queue with source `"ui"`.
- The queue and engine lock preserve FIFO order and prevent concurrent writes.
- After a successful commit, the app clears the preview and refreshes from engine state.
- After an unsuccessful commit, the app clears the preview, refreshes the unchanged board, and reports the engine/queue outcome without creating history.
