"""Application entry point — wires engine, live AI path, dialogs, and board."""

from __future__ import annotations

from typing import Any

TS = "2026-10-03T18:15:00Z"


def _save_state(window: Any) -> None:
    """Persist mode/size/position at close (window_state)."""
    from smartboard.ui.window_state import save_state

    save_state(window)


def _refresh(orchestrator: Any, window_holder: dict[str, Any],
             highlight_id: str | None = None) -> None:
    window = window_holder["window"]
    window.render_board(orchestrator.engine.board.to_dict(), highlight_id)
    window.set_status(orchestrator.status)
    window.show_transcription(orchestrator.transcription)
    window.undo_button.setEnabled(orchestrator.engine.history.can_undo())
    window.redo_button.setEnabled(orchestrator.engine.history.can_redo())


def _deliver_result(future: Any, transcript: str, started: float,
                    orchestrator: Any, window_holder: dict[str, Any]) -> None:
    import time as _time

    from PyQt6.QtCore import QTimer as _QTimer

    from smartboard.ui.confirm_dialog import ConfirmDialog

    window = window_holder["window"]
    if not future.done():
        if _time.monotonic() - started > 15:
            window.set_status("Idle")
            window.show_transcription(f"{transcript}  →  Voice service unavailable.")
            window.show_result({"ok": False})
            window.dev_input.setEnabled(True)
            return
        _QTimer.singleShot(
            100, lambda: _deliver_result(future, transcript, started, orchestrator, window_holder))
        return
    try:
        result = future.result()
    except Exception:
        result = {"ok": False,
                  "message": "Voice service unavailable. Check your connection and retry.",
                  "retry": True}
    if result.get("needs_confirmation"):
        window.set_status("Validating")
        dialog = ConfirmDialog(result.get("message", "Confirm?"), window)
        window.register_dialog(dialog)
        try:
            confirmed = bool(dialog.exec())
        finally:
            window.unregister_dialog(dialog)
        result = orchestrator.queue.resolve_block(confirmed=confirmed)
        if result.get("error_code") == "E_CANCELLED":
            result = {"ok": False, "message": "Cancelled."}
    _refresh(orchestrator, window_holder, result.get("affected_id"))
    window.dev_input.setEnabled(True)
    if result.get("message") == "Cancelled.":
        window.show_result({"ok": True})  # user-chosen cancel is not an error
    else:
        window.show_result(result)
    if not result.get("ok") and "message" in result:
        window.show_transcription(f"{transcript}  →  {result['message']}")


def submit_dev_transcript(orchestrator: Any, window_holder: dict[str, Any],
                          transcript: str) -> None:
    import time as _time

    from smartboard.ai.config import get_provider, load_config
    from smartboard.app import workers as _workers

    window = window_holder["window"]
    if not transcript.strip():
        return
    try:
        provider = get_provider(load_config())
    except ValueError as exc:
        window.set_status("Idle")
        window.show_transcription(str(exc))
        window.show_result({"ok": False})
        return
    window.set_status("Processing")
    window.show_transcription(transcript)
    window.dev_input.setEnabled(False)
    future = _workers.submit(orchestrator.handle_live_transcript, transcript, provider)
    _deliver_result(future, transcript, _time.monotonic(), orchestrator, window_holder)


def main() -> None:
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError as exc:
        raise RuntimeError("PyQt6 is required to run the desktop app.") from exc
    from smartboard.app.orchestrator import build_app
    from smartboard.ui.main_window import MainWindow

    app = QApplication([])
    from smartboard.ui.theme import build_stylesheet

    app.setStyleSheet(build_stylesheet())
    orchestrator = build_app()
    window_holder: dict[str, Any] = {}
    from smartboard.ui.pen_input import StrokeGrouper

    grouper = StrokeGrouper()
    pending: list[list[list[dict[str, Any]]]] = []

    def _pen_width() -> int:
        from smartboard.ui.window_state import load_pen_width

        return load_pen_width()

    def refresh(highlight_id: str | None = None) -> None:
        _refresh(orchestrator, window_holder, highlight_id)

    def on_mic() -> None:
        # Speech capture lands in the next feature; until then the mic is
        # inert and says so honestly. Typed transcripts go via dev input.
        window = window_holder["window"]
        window.set_status("Idle")
        window.show_transcription(
            "Speech capture is coming soon — enable the developer input to type commands.")

    def on_undo() -> None:
        grouper.mark_interaction()  # commands break stroke grouping
        result = orchestrator.engine.execute(
            {"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS}, source="ui")
        refresh()
        if not result.get("ok"):
            window_holder["window"].show_transcription(result["message"])

    def on_redo() -> None:
        grouper.mark_interaction()  # commands break stroke grouping
        result = orchestrator.engine.execute(
            {"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS}, source="ui")
        refresh()
        if not result.get("ok"):
            window_holder["window"].show_transcription(result["message"])

    def _deliver(future: Any, transcript: str, started: float) -> None:
        _deliver_result(future, transcript, started, orchestrator, window_holder)

    def on_dev_text(transcript: str) -> None:
        grouper.mark_interaction()  # commands break stroke grouping
        submit_dev_transcript(orchestrator, window_holder, transcript)

    def on_stroke_finished(points: list[dict[str, Any]]) -> None:
        # Feed the grouper; commit any group the gap/interaction just closed.
        grouper.pen_up(points)
        while grouper.groups:
            _commit_group(grouper.groups.pop(0))
        _arm_idle_commit()

    def _arm_idle_commit() -> None:
        from PyQt6.QtCore import QTimer as _QTimer

        _QTimer.singleShot(1600, _commit_idle_group)

    def _commit_idle_group() -> None:
        group = grouper.flush()
        if group is None:
            return
        _commit_group(group)

    def _commit_group(group: list[list[dict[str, Any]]]) -> None:
        from PyQt6.QtCore import QTimer as _QTimer

        if orchestrator.queue.depth() > 0 or orchestrator.queue.blocked:
            # Voice work in flight: hold and retry shortly; never concurrent.
            pending.append(group)
            _QTimer.singleShot(100, _drain_pending)
            return
        result = orchestrator.commit_pen_drawing(group, width=_pen_width())
        if not result.get("ok") and result.get("error_code") == "E_BLOCKED":
            pending.append(group)
            _QTimer.singleShot(100, _drain_pending)
            return
        refresh(result.get("affected_id"))

    def _drain_pending() -> None:
        while pending and orchestrator.queue.depth() == 0 and not orchestrator.queue.blocked:
            group = pending.pop(0)
            result = orchestrator.commit_pen_drawing(group, width=_pen_width())
            if not result.get("ok"):
                pending.insert(0, group)
                break
            refresh(result.get("affected_id"))
        if pending:
            from PyQt6.QtCore import QTimer as _QTimer

            _QTimer.singleShot(100, _drain_pending)

    def on_selection_changed(element_id: Any) -> None:
        grouper.mark_interaction()  # selection breaks stroke grouping
        orchestrator.engine.select(element_id)  # engine stays the only writer
        refresh()

    window = MainWindow(on_mic=on_mic, on_undo=on_undo, on_redo=on_redo,
                        on_close=lambda: _save_state(window),
                        on_dev_text=on_dev_text)
    window_holder["window"] = window
    window.board_view.StrokeFinished.connect(on_stroke_finished)
    window.board_view.SelectionChanged.connect(on_selection_changed)

    def on_pen_mode(mode: str) -> None:
        grouper.mark_interaction()
        _commit_idle_group()  # leaving Pen mode closes the open group

    window.pen_mode_changed = on_pen_mode
    refresh()
    from smartboard.ui.window_state import restore_state

    restore_state(window)  # geometry + mode before first paint
    window.board_view.live_width = _pen_width()  # settings-only pen width
    app.exec()


if __name__ == "__main__":
    main()
