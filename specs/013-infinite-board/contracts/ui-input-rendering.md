# Contract: Board Input, Editing, and Rendering

## Pointer and wheel input

| Input | Mode behavior |
|---|---|
| Wheel vertical/horizontal | Pans the camera; creates no history |
| `Shift+wheel` | Pans horizontally; creates no history |
| `Ctrl+wheel` | Zooms about the cursor within 10%–400% |
| Pinch or native zoom gesture | Normalized into cursor-anchored zoom |
| Middle-button drag | Pans the camera |
| Space+drag | Pans in Select and Pen modes without changing the active mode |
| Select-mode empty drag | Pans the camera |
| Select-mode empty click | Clears selection without panning |
| Pen press/move/release without Space | Draws in world coordinates |

Space-pan, middle-button pan, wheel pan/zoom, and pinch zoom must not create history entries or alter board content.

## Double-click and inline editing

| Gesture | Behavior |
|---|---|
| Double-click empty Select-mode space | Opens a provisional text overlay anchored to the clicked world point |
| Double-click heading/text/equation | Opens an overlay containing existing content |
| Enter | Commits valid text |
| `Shift+Enter` in multiline text | Inserts a newline |
| Click outside with valid text | Commits valid text |
| Escape or empty new text | Discards provisional text with no engine/history change |
| Clearing existing text | Reverts to original text with no history change |

Commit behavior:

- Accepted new text creates exactly one public `create_text` history entry.
- Accepted existing-text changes create exactly one internal `edit_text` history entry.
- Internal `edit_text` is unavailable to AI and absent from the public command schema.

## Rendering contract

- Only elements intersecting the visible world rectangle are painted.
- World content is painted under the active camera transform.
- Dot-grid spacing changes by powers of two with zoom.
- Dot size remains constant in screen pixels.
- Selection outlines, resize handles, and highlight rings are painted in screen space at constant size.
- Hit tolerance is derived from a constant screen-pixel tolerance divided by zoom.
- PNG export reuses the same read-only element painting as interactive rendering.
