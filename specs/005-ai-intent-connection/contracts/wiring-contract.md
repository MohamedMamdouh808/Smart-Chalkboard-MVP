# Wiring Contract

- Threading: the provider call runs on `app/workers.py` (never the UI
  thread); UI updates (strip, chip, pill, board) happen on result
  delivery only.
- Timeout/regen: 4 s SDK timeout; malformed JSON → exactly ONE
  regeneration → then "Unable to understand the command. Please try
  again." Timeout/failure → clear error + Retry; board, pen, history
  untouched.
- Engine boundary: parsed responses go to `CommandEngine.execute` (or
  the queue); NO other code path may assign board state. Clarification
  envelopes render as questions and stop.
- Demo removal: `DEMO_SCRIPT` and scripted mic flow deleted from
  `app/main.py`; startup board empty; mic button inert with an honest
  tooltip until speech capture lands (next feature).
- Dev box: hidden `QLineEdit` (+Send), `setVisible(False)` unless
  `SMARTBOARD_DEV_INPUT=1`; submits through the identical transcript
  path; never in teacher-facing layouts by default.
