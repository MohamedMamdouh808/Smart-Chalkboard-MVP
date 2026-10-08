# Acceptance Scenario (Newton's Second Law E2E)

Constitution gate + spec SC-001. Scripted with fixtures (recorded audio +
recorded AI JSON), then repeated live with a human speaker.

1. Say "Create a heading called Newton's Second Law." → `heading_001`
   appears; transcription visible; highlight on new element.
2. Say "Add the equation F = ma below it." → `create_text` with
   `equation_style: true` creates the equation below the heading.
3. Select the equation; say "Make the equation bigger." → `resize_item`
   `scale_factor: 1.25` via selection; element stays in bounds.
4. Draw with the pen → `drawing_001` committed through the engine with a
   unique ID; selectable.
5. Say "Delete the equation." → `E_CONFIRMATION_REQUIRED`; modal shown;
   Confirm → equation removed and recorded.
6. Press Undo → equation restored with original ID and position; Redo
   removes it again.

Pass criteria: all six steps green, every rejection path in the run
leaves state+history unchanged, p50 step latency < 3 s on primary path.
