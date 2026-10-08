# Move Contract

- The `QLineEdit` is REMOVED from the top-strip layout and INSERTED in
  the bottom-bar `QHBoxLayout` between the Redo button and the status
  pill, with `stretch=1`, `setMaximumWidth(700)`, centered by the
  surrounding stretch space.
- Visibility stays tied to the existing check
  (`SMARTBOARD_DEV_INPUT == "1"`, evaluated at construction); flag off
  → `setVisible(False)`, and the bar matches the current layout exactly.
- Size/font from theme: 44px height, ≥18px font, placeholder unchanged,
  visible focus outline per the shared focus styling.
- Submit/clear/tooltip wiring moves with the widget, byte-identical in
  behavior; disabled-while-processing reuses the button-disabled visual
  language.
- Top strip after the move: exactly Heard label, transcript, chip,
  Window button.
- No overlap with any control at 960×540 and up; board geometry
  identical on/off at the same window size.
