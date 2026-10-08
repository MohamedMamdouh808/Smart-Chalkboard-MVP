"""Application entry point — wires engine, live AI path, dialogs, and board."""

from __future__ import annotations

import logging
from typing import Any

TS = "2026-10-03T18:15:00Z"
VOICE_LOG = logging.getLogger("smartboard.voice")


def _save_state(window: Any) -> None:
    """Persist mode/size/position at close (window_state)."""
    from smartboard.ui.window_state import save_state

    save_state(window)


def _refresh(
    orchestrator: Any, window_holder: dict[str, Any], highlight_id: str | None = None
) -> None:
    window = window_holder["window"]
    window.render_board(orchestrator.engine.board.to_dict(), highlight_id, orchestrator.camera)
    window.set_zoom_label(orchestrator.camera.zoom)
    window.set_status(orchestrator.status)
    window.show_transcription(orchestrator.transcription)
    window.undo_button.setEnabled(orchestrator.engine.history.can_undo())
    window.redo_button.setEnabled(orchestrator.engine.history.can_redo())


def _deliver_result(
    future: Any, transcript: str, started: float, orchestrator: Any, window_holder: dict[str, Any]
) -> None:
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
            100, lambda: _deliver_result(future, transcript, started, orchestrator, window_holder)
        )
        return
    try:
        result = future.result()
    except Exception:  # noqa: BLE001 - worker faults degrade to manual mode
        result = {
            "ok": False,
            "message": "Voice service unavailable. Check your connection and retry.",
            "retry": True,
        }
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


def handle_voice_transcript(
    orchestrator: Any, window_holder: dict[str, Any], grouper: Any, transcript: str
) -> None:
    """Submit a finished voice transcript through the developer-text path."""
    grouper.mark_interaction()
    submit_dev_transcript(orchestrator, window_holder, transcript)


def submit_dev_transcript(
    orchestrator: Any, window_holder: dict[str, Any], transcript: str
) -> None:
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
    from smartboard.ui.tooltip_style import TooltipStyle

    app.setStyle(TooltipStyle())
    app.setStyleSheet(build_stylesheet())
    orchestrator = build_app()
    window_holder: dict[str, Any] = {}
    from smartboard.ui.pen_input import StrokeGrouper

    grouper = StrokeGrouper()
    pending: list[list[list[dict[str, Any]]]] = []
    pending_manual: list[dict[str, Any]] = []

    def _pen_width() -> int:
        from smartboard.ui.window_state import load_pen_width

        return load_pen_width()

    def refresh(highlight_id: str | None = None) -> None:
        _refresh(orchestrator, window_holder, highlight_id)

    from smartboard.voice.recorder import (
        MicrophoneDeniedError,
        MicrophoneUnavailableError,
        SoundRecorder,
    )
    from smartboard.voice.voice_config import load_voice_config
    from smartboard.voice.voice_worker import VoiceWorker

    def _record_voice_metric(event: dict[str, Any]) -> None:
        VOICE_LOG.info(
            "voice_transcription duration_ms=%s model=%s device=%s outcome=%s",
            event.get("duration_ms"),
            event.get("model"),
            event.get("device"),
            event.get("outcome"),
        )

    voice_recorder = SoundRecorder()
    voice_worker = VoiceWorker(load_voice_config(), telemetry=_record_voice_metric)
    voice_ready = False

    def on_mic_press() -> None:
        window = window_holder["window"]
        if not voice_ready:
            window.show_transcription("Voice model is still loading. Please wait a moment.")
            return
        window.set_status("Listening")
        try:
            voice_recorder.start()
        except MicrophoneUnavailableError:
            window.set_status("Idle")
            window.show_transcription(
                "No microphone was found. Board, pen and developer input still work."
            )
        except MicrophoneDeniedError:
            window.set_status("Idle")
            window.show_transcription(
                "Microphone access was denied. Board, pen and developer input still work."
            )

    def on_mic_release() -> None:
        window = window_holder["window"]
        try:
            recording = voice_recorder.stop()
        except MicrophoneUnavailableError:
            window.set_status("Idle")
            window.show_transcription(
                "No microphone was found. Board, pen and developer input still work."
            )
            return
        except MicrophoneDeniedError:
            window.set_status("Idle")
            window.show_transcription(
                "Microphone access was denied. Board, pen and developer input still work."
            )
            return
        if recording is None:
            window.set_status("Idle")
            return
        window.set_status("Processing")
        voice_worker.transcribeRequested.emit(recording.samples)

    def on_voice_ready() -> None:
        nonlocal voice_ready
        voice_ready = True
        window_holder["window"].mic_button.set_loading(False)
        window_holder["window"].set_status("Idle")

    def on_voice_transcript(text: str, duration_ms: float) -> None:
        del duration_ms  # duration is already reported through telemetry.
        window_holder["window"].show_transcription(text)
        handle_voice_transcript(orchestrator, window_holder, grouper, text)

    def on_voice_failed(message: str) -> None:
        window = window_holder["window"]
        window.set_status("Idle")
        window.show_transcription(message)
        window.show_result({"ok": False})

    def on_undo() -> None:
        grouper.mark_interaction()  # commands break stroke grouping
        result = orchestrator.engine.execute(
            {"command": "undo", "target_id": None, "parameters": {}, "timestamp": TS}, source="ui"
        )
        refresh()
        if not result.get("ok"):
            window_holder["window"].show_transcription(result["message"])

    def on_redo() -> None:
        grouper.mark_interaction()  # commands break stroke grouping
        result = orchestrator.engine.execute(
            {"command": "redo", "target_id": None, "parameters": {}, "timestamp": TS}, source="ui"
        )
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

    def _arm_manual_retry() -> None:
        from PyQt6.QtCore import QTimer as _QTimer

        _QTimer.singleShot(100, _retry_manual_gestures)

    def _retry_manual_gestures() -> None:
        while pending_manual:
            payload = pending_manual.pop(0)
            result = orchestrator.commit_manual_gesture(payload)
            if result.get("error_code") in ("E_BUSY", "E_QUEUE_FULL"):
                pending_manual.insert(0, payload)
                break
            refresh(result.get("affected_id"))
            if not result.get("ok"):
                window_holder["window"].show_transcription(
                    str(result.get("message", "That gesture could not be applied."))
                )
        if pending_manual:
            _arm_manual_retry()

    def on_gesture_finished(payload: dict[str, Any]) -> None:
        grouper.mark_interaction()  # gestures break stroke grouping
        result = orchestrator.commit_manual_gesture(payload)
        if result.get("error_code") in ("E_BUSY", "E_QUEUE_FULL"):
            # The queue was busy or full, so nothing was submitted yet. Hold
            # the unsigned payload and retry without duplicating the gesture.
            pending_manual.append(payload)
            window_holder["window"].show_transcription(
                "Another command is running. The gesture is waiting."
            )
            _arm_manual_retry()
            return
        refresh(result.get("affected_id"))
        if not result.get("ok"):
            window_holder["window"].show_transcription(
                str(result.get("message", "That gesture could not be applied."))
            )

    def on_view_size(view_w: int, view_h: int) -> None:
        orchestrator.set_view_size(view_w, view_h)

    def on_camera_changed(camera: Any) -> None:
        orchestrator.set_camera(camera)
        refresh()
        session = text_overlay.session
        if session is not None:
            if session.get("target_id") is None:
                anchor = {
                    "world_x": session.get("world_x", 0.0),
                    "world_y": session.get("world_y", 0.0),
                    "target_id": None,
                }
            else:
                anchor = {"target_id": session.get("target_id")}
            text_overlay.follow_camera(_overlay_rect(anchor))

    def on_zoom_in() -> None:
        view = window_holder["window"].board_view
        orchestrator.zoom_about(view.width() / 2, view.height() / 2, 1.25)
        refresh()

    def on_zoom_out() -> None:
        view = window_holder["window"].board_view
        orchestrator.zoom_about(view.width() / 2, view.height() / 2, 1 / 1.25)
        refresh()

    def on_zoom_reset() -> None:
        orchestrator.reset_zoom()
        refresh()

    def on_zoom_fit() -> None:
        orchestrator.fit_all()
        refresh()

    def on_close() -> None:
        voice_thread.quit()
        voice_thread.wait(5000)
        _save_state(window_holder["window"])

    window = MainWindow(
        on_mic_press=on_mic_press,
        on_mic_release=on_mic_release,
        on_undo=on_undo,
        on_redo=on_redo,
        on_close=on_close,
        on_dev_text=on_dev_text,
        on_zoom_in=on_zoom_in,
        on_zoom_out=on_zoom_out,
        on_zoom_reset=on_zoom_reset,
        on_zoom_fit=on_zoom_fit,
    )
    window_holder["window"] = window
    window.board_view.StrokeFinished.connect(on_stroke_finished)
    window.board_view.SelectionChanged.connect(on_selection_changed)
    window.board_view.GestureFinished.connect(on_gesture_finished)
    window.board_view.CameraChanged.connect(on_camera_changed)
    window.board_view.ViewSizeChanged.connect(on_view_size)

    from smartboard.ui.text_overlay import TextOverlay

    text_overlay = TextOverlay(window.board_view)

    def _overlay_font(kind: str, equation: bool, zoom: float) -> Any:
        from smartboard.app.text_fit import font_for as _font_for

        font = _font_for(kind if kind != "equation" else "text", equation)
        try:
            font.setPointSize(max(1, round(font.pointSize() * zoom)))
        except (AttributeError, TypeError, ValueError):
            pass
        return font

    def _element_text(element: Any) -> str:
        if not isinstance(element, dict):
            return ""
        text = element.get("text", "")
        if not text and isinstance(element.get("extra"), dict):
            text = element["extra"].get("text", "")
        return str(text)

    def _overlay_rect(payload: dict[str, Any]) -> Any:
        from PyQt6.QtCore import QRect as _QRect

        view = window_holder["window"].board_view
        target_id = payload.get("target_id")
        if target_id is not None:
            return view.element_screen_rect(target_id)
        sx, sy = view.transform().to_screen(float(payload["world_x"]), float(payload["world_y"]))
        zoom = view.camera_state().zoom
        return _QRect(int(sx), int(sy), max(int(600 * zoom), 1), max(int(120 * zoom), 1))

    def on_inline_edit_requested(payload: dict[str, Any]) -> None:
        grouper.mark_interaction()
        view = window_holder["window"].board_view
        target_id = payload.get("target_id")
        zoom = view.camera_state().zoom
        if target_id is None:
            text_overlay.begin_new(
                float(payload["world_x"]),
                float(payload["world_y"]),
                _overlay_rect(payload),
                _overlay_font("text", False, zoom),
            )
            return
        element = next(
            (el for el in view._state.get("elements", []) if el.get("id") == target_id), None
        )
        if element is None or element.get("type") not in ("heading", "text"):
            return
        equation = bool(element.get("equation_style"))
        if not equation and isinstance(element.get("extra"), dict):
            equation = bool(element["extra"].get("equation_style"))
        kind = "heading" if element.get("type") == "heading" else "text"
        text_overlay.begin_existing(
            target_id,
            kind,
            _element_text(element),
            _overlay_rect(payload),
            _overlay_font(kind, equation, zoom),
        )

    def on_text_committed(payload: dict[str, Any]) -> None:
        grouper.mark_interaction()
        if payload.get("target_id") is None:
            result = orchestrator.commit_text_create(
                float(payload["world_x"]), float(payload["world_y"]), str(payload.get("text", ""))
            )
        else:
            result = orchestrator.commit_text_edit(
                payload.get("target_id"), str(payload.get("text", ""))
            )
        refresh(result.get("affected_id"))
        if not result.get("ok"):
            window_holder["window"].show_transcription(
                str(result.get("message", "That text could not be applied."))
            )

    def on_text_discarded(payload: dict[str, Any]) -> None:
        del payload
        grouper.mark_interaction()
        refresh()

    def on_focus_changed(old: Any, new: Any) -> None:
        del old
        if not text_overlay.is_open:
            return
        editor = text_overlay.editor_widget
        widget = new
        while widget is not None:
            if widget is editor:
                return
            widget = widget.parentWidget() if hasattr(widget, "parentWidget") else None
        text_overlay.focus_out_commit()

    window.board_view.InlineEditRequested.connect(on_inline_edit_requested)
    text_overlay.Committed.connect(on_text_committed)
    text_overlay.Discarded.connect(on_text_discarded)
    app.focusChanged.connect(on_focus_changed)
    window.mic_button.set_loading(True)

    from PyQt6.QtCore import QThread as _QThread

    voice_thread = _QThread()
    voice_worker.moveToThread(voice_thread)
    voice_thread.started.connect(voice_worker.load_model)
    voice_worker.modelReady.connect(on_voice_ready)
    voice_worker.transcriptReady.connect(on_voice_transcript)
    voice_worker.failed.connect(on_voice_failed)
    voice_thread.start()

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
