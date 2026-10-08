"""Deterministic validation and execution engine (sole board-state writer)."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any, Callable

from . import errors
from .board import Board, Element
from .command_schema import validate_shape
from .element_ids import IdGenerator
from .history import History
from .validators import TARGET_COMMANDS, fits_canvas, resolve_move, validate_params

EngineResult = dict[str, Any]
HistoryHook = Callable[[dict[str, Any]], None]

CONFIRM_COMMANDS: tuple[str, ...] = ("delete_item", "clear_board")
TOP_MARGIN_Y = 80
DEFAULT_X = 160
SLOT_GAP = 40


class CommandEngine:
    """Single-writer engine. No randomness, no network, no wall-clock reads
    except the authoritative history timestamp (monotonic seq owns order)."""

    def __init__(self, board: Board | None = None, hook: HistoryHook | None = None) -> None:
        self.board: Board = board or Board()
        self.history: History = History()
        self.ids = IdGenerator()
        self.ids.seed_from_ids([el.id for el in self.board.elements])
        self.hook = hook

    # -- public API ----------------------------------------------------
    def execute(
        self,
        raw: Any,
        source: str = "voice",
        confirmed: bool = False,
        dirty: bool = False,
    ) -> EngineResult:
        if isinstance(raw, str):
            import json as _json

            try:
                raw = _json.loads(raw)
            except ValueError:
                return self._fail(errors.E_SCHEMA, errors.message_for(errors.E_SCHEMA, "json"))
        ok, code, msg = validate_shape(raw)
        if not ok:
            return self._fail(code, msg)
        command: str = raw["command"]
        target_id = raw["target_id"]
        params: dict[str, Any] = raw["parameters"]

        ok, code, msg = validate_params(command, params)
        if not ok:
            return self._fail(code, msg)

        if command in ("undo", "redo", "save_lesson", "new_lesson"):
            return self._execute_meta(command, params, raw, source, confirmed, dirty)

        target: Element | None = None
        if command in TARGET_COMMANDS:
            target = self._resolve_target(target_id, params)
            if target is None:
                if target_id is None and not params.get("use_selection") and "position" not in params:
                    return self._clarify(command)
                missing = self.board.selected_element_id is None and target_id is None
                if missing:
                    return self._fail(errors.E_TARGET_MISSING, errors.message_for(errors.E_TARGET_MISSING))
                return self._fail(errors.E_TARGET_NOT_FOUND, errors.message_for(errors.E_TARGET_NOT_FOUND))

        if command in CONFIRM_COMMANDS and not confirmed:
            return {
                "ok": False,
                "error_code": errors.E_CONFIRMATION_REQUIRED,
                "message": self._confirm_prompt(command, target),
                "needs_confirmation": True,
            }

        snapshot = self.board.snapshot()
        try:
            inverse: dict[str, Any]
            affected: str | None
            if command == "create_heading":
                affected, inverse = self._do_create("heading", params)
            elif command == "create_text":
                affected, inverse = self._do_create("text", params)
            elif command == "create_shape":
                affected, inverse = self._do_create("shape", params)
            elif command == "move_item":
                affected, inverse = self._do_move(target, params)
            elif command == "resize_item":
                affected, inverse = self._do_resize(target, params)
            elif command == "delete_item":
                affected, inverse = self._do_delete(target)
            elif command == "clear_board":
                affected, inverse = self._do_clear()
            elif command == "change_color":
                affected, inverse = self._do_color(target, params)
            else:  # pragma: no cover - schema blocks unknown commands
                return self._fail(errors.E_UNSUPPORTED_COMMAND, errors.message_for(errors.E_UNSUPPORTED_COMMAND))
        except _Reject as exc:
            self.board.restore(snapshot)
            return self._fail(exc.code, exc.message)

        self.board.version += 1
        entry = self.history.record(copy.deepcopy(raw), inverse, source)
        if self.hook is not None:
            self.hook(
                {
                    "seq": entry.seq,
                    "command_json": copy.deepcopy(raw),
                    "inverse_json": copy.deepcopy(inverse),
                    "source": source,
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        return {"ok": True, "state_version": self.board.version, "affected_id": affected}

    def add_drawing(
        self, strokes: list[list[dict[str, Any]]], color: str = "#FFFFFF", width: int = 4,
        source: str = "pen",
    ) -> EngineResult:
        """Internal pen-commit path (not an AI command). Same validation/history."""
        from .board import (DRAWING_WIDTHS, DEFAULT_DRAWING_WIDTH, clip_point,
                            drawing_bbox, reduce_points)

        if width not in DRAWING_WIDTHS:
            width = DEFAULT_DRAWING_WIDTH
        wrapped: list[dict[str, Any]] = []
        for stroke in strokes:
            points = []
            for point in stroke:
                try:
                    x, y = clip_point(float(point["x"]), float(point["y"]))
                except (KeyError, TypeError, ValueError):
                    continue
                kept: dict[str, Any] = {"x": x, "y": y}
                if "pressure" in point:
                    kept["pressure"] = point["pressure"]
                points.append(kept)
            if points:
                wrapped.append({"points": reduce_points(points), "width": width, "color": color})
        if not wrapped:
            return self._fail(errors.E_OUT_OF_BOUNDS, "The drawing is outside the board.")
        new_id = self.ids.next("drawing")
        x, y, w, h = drawing_bbox([s["points"] for s in wrapped])
        element = Element(
            id=new_id,
            type="drawing",
            x=x,
            y=y,
            width=w,
            height=h,
            color=color,
            z=self.board.top_z() + 1,
            extra={"strokes": copy.deepcopy(wrapped), "width": width},
        )
        if not element.bbox_inside_canvas():
            return self._fail(errors.E_OUT_OF_BOUNDS, "There is no room on the board for this drawing.")
        self.board.elements.append(element)
        self.board.version += 1
        raw = {"command": "add_drawing", "target_id": None, "parameters": {"color": color}}
        inverse: dict[str, Any] = {"op": "remove", "id": new_id, "element": element.to_dict()}
        entry = self.history.record(raw, inverse, source)
        if self.hook is not None:
            self.hook(
                {
                    "seq": entry.seq,
                    "command_json": copy.deepcopy(raw),
                    "inverse_json": copy.deepcopy(inverse),
                    "source": source,
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        return {"ok": True, "state_version": self.board.version, "affected_id": new_id}

    def select(self, element_id: str | None) -> EngineResult:
        """Internal selection intent (not an AI command, not a history entry).

        Selection is transient view state, so this does not bump the board
        version or notify the history hook.
        """
        if element_id is not None and self.board.find(element_id) is None:
            element_id = None
        self.board.selected_element_id = element_id
        return {"ok": True, "state_version": self.board.version, "affected_id": element_id}

    # -- meta commands --------------------------------------------------
    def _execute_meta(
        self,
        command: str,
        params: dict[str, Any],
        raw: dict[str, Any],
        source: str,
        confirmed: bool,
        dirty: bool,
    ) -> EngineResult:
        if command == "undo":
            if not self.history.can_undo():
                return self._fail(errors.E_NOTHING_TO_UNDO, errors.message_for(errors.E_NOTHING_TO_UNDO))
            entry = self.history.undo_entry()
            assert entry is not None
            self._apply_inverse(entry.inverse)
            self.board.version += 1
            return {"ok": True, "state_version": self.board.version, "affected_id": None}
        if command == "redo":
            if not self.history.can_redo():
                return self._fail(errors.E_NOTHING_TO_REDO, errors.message_for(errors.E_NOTHING_TO_REDO))
            entry = self.history.redo_entry()
            assert entry is not None
            self._apply_forward(entry.command, entry.inverse)
            self.board.version += 1
            return {"ok": True, "state_version": self.board.version, "affected_id": None}
        if command == "save_lesson":
            return {"ok": True, "state_version": self.board.version, "affected_id": None, "saved": True}
        # new_lesson: persistence action, never mutates board here
        if dirty and not confirmed:
            return {
                "ok": False,
                "error_code": errors.E_CONFIRMATION_REQUIRED,
                "message": "You have unsaved changes. Save first? [Cancel] [Confirm]",
                "needs_confirmation": True,
            }
        return {"ok": True, "state_version": self.board.version, "affected_id": None, "new_lesson": True}

    # -- creators --------------------------------------------------------
    def _slot_y(self, height: int) -> int:
        if not self.board.elements:
            return TOP_MARGIN_Y
        return self.board.lowest_bottom() + SLOT_GAP

    def _do_create(self, kind: str, params: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        text = str(params["text"]).strip() if kind in ("heading", "text") else ""
        if kind == "heading":
            width, height = 800, 96
        elif kind == "text":
            width, height = (320, 80) if params.get("equation_style") else (600, 120)
        else:
            size = params.get("size", {})
            width = int(size.get("w", 200))
            height = int(size.get("h", 200))
        pos = params.get("position", {})
        x = int(pos.get("x", DEFAULT_X))
        y = int(pos.get("y", self._slot_y(height)))
        color = str(params.get("color", "#FFFFFF"))
        extra: dict[str, Any] = {}
        if kind in ("heading", "text"):
            extra["text"] = text
        if kind == "text" and params.get("equation_style"):
            extra["equation_style"] = True
        if kind == "shape":
            extra["shape_type"] = str(params["shape_type"])
        new_id = self.ids.next(kind)
        element = Element(
            id=new_id, type=kind, x=x, y=y, width=width, height=height,
            color=color, z=self.board.top_z() + 1, extra=extra,
        )
        if not element.bbox_inside_canvas():
            if kind == "heading":
                raise _Reject(errors.E_OUT_OF_BOUNDS, "There is no room on the board for this heading.")
            raise _Reject(errors.E_OUT_OF_BOUNDS, errors.message_for(errors.E_OUT_OF_BOUNDS))
        self.board.elements.append(element)
        self.board.selected_element_id = new_id
        return new_id, {"op": "remove", "id": new_id, "element": element.to_dict()}

    @staticmethod
    def _drawing_point_lists(target: Element) -> list[list[dict[str, Any]]]:
        """Live references to a drawing's stored point lists (mutation sticks)."""
        lists = []
        for stroke in target.extra.get("strokes", []):
            if isinstance(stroke, dict) and isinstance(stroke.get("points"), list):
                lists.append(stroke["points"])
            elif isinstance(stroke, list):
                lists.append(stroke)
        return lists

    @staticmethod
    def _swap_inverse(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
        """Snapshot inverse for drawing transforms: undo restores `before`,
        redo restores `after` (point data included)."""
        return {"op": "swap", "id": before["id"], "element": before, "forward": after}

    def _do_move(self, target: Element | None, params: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        from .board import translate_points

        assert target is not None
        old = (target.x, target.y)
        new_x, new_y = resolve_move(params, target.x, target.y)
        if not fits_canvas(new_x, new_y, target.width, target.height):
            raise _Reject(errors.E_OUT_OF_BOUNDS, errors.message_for(errors.E_OUT_OF_BOUNDS))
        if target.type == "drawing":
            before = copy.deepcopy(target.to_dict())
            dx, dy = new_x - target.x, new_y - target.y
            target.x, target.y = new_x, new_y
            translate_points(self._drawing_point_lists(target), dx, dy)
            self.board.selected_element_id = target.id
            return target.id, self._swap_inverse(before, target.to_dict())
        target.x, target.y = new_x, new_y
        self.board.selected_element_id = target.id
        return target.id, {"op": "move", "id": target.id, "x": old[0], "y": old[1]}

    def _do_resize(self, target: Element | None, params: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        from .board import scale_points

        assert target is not None
        old = (target.width, target.height)
        if "scale_factor" in params:
            scale = float(params["scale_factor"])
            new_w, new_h = int(target.width * scale), int(target.height * scale)
        else:
            new_w, new_h = int(params["size"]["w"]), int(params["size"]["h"])
        if not fits_canvas(target.x, target.y, new_w, new_h):
            raise _Reject(errors.E_OUT_OF_BOUNDS, errors.message_for(errors.E_OUT_OF_BOUNDS))
        if target.type == "drawing" and old[0] > 0 and old[1] > 0:
            before = copy.deepcopy(target.to_dict())
            ox, oy = target.x, target.y
            target.width, target.height = new_w, new_h
            scale_points(self._drawing_point_lists(target), ox, oy,
                         new_w / old[0], new_h / old[1])
            self.board.selected_element_id = target.id
            return target.id, self._swap_inverse(before, target.to_dict())
        target.width, target.height = new_w, new_h
        self.board.selected_element_id = target.id
        return target.id, {"op": "resize", "id": target.id, "w": old[0], "h": old[1]}

    def _do_delete(self, target: Element | None) -> tuple[str, dict[str, Any]]:
        assert target is not None
        saved = target.to_dict()
        self.board.elements = [el for el in self.board.elements if el.id != target.id]
        if self.board.selected_element_id == target.id:
            self.board.selected_element_id = None
        return target.id, {"op": "restore", "element": saved}

    def _do_clear(self) -> tuple[None, dict[str, Any]]:
        if not self.board.elements:
            raise _Reject(errors.E_PARAM_INVALID, "The board is already empty.")
        saved = [el.to_dict() for el in self.board.elements]
        self.board.elements = []
        self.board.selected_element_id = None
        return None, {"op": "restore_all", "elements": saved}

    def _do_color(self, target: Element | None, params: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        assert target is not None
        if target.type == "drawing":
            # Strokes carry their own colour and win at render time, so a
            # drawing recolor must rewrite every stroke too.
            before = copy.deepcopy(target.to_dict())
            new_color = str(params["color"])
            target.color = new_color
            for stroke in target.extra.get("strokes", []):
                if isinstance(stroke, dict):
                    stroke["color"] = new_color
            self.board.selected_element_id = target.id
            return target.id, self._swap_inverse(before, target.to_dict())
        old = target.color
        target.color = str(params["color"])
        self.board.selected_element_id = target.id
        return target.id, {"op": "recolor", "id": target.id, "color": old}

    # -- undo plumbing -----------------------------------------------------
    def _apply_inverse(self, inverse: dict[str, Any]) -> None:
        op = inverse.get("op")
        if op == "remove":
            self.board.elements = [el for el in self.board.elements if el.id != inverse["id"]]
            if self.board.selected_element_id == inverse["id"]:
                self.board.selected_element_id = None
        elif op == "restore":
            self.board.elements.append(Element.from_dict(inverse["element"]))
        elif op == "restore_all":
            self.board.elements = [Element.from_dict(d) for d in inverse["elements"]]
        elif op == "move":
            el = self.board.find(str(inverse["id"]))
            if el is not None:
                el.x, el.y = int(inverse["x"]), int(inverse["y"])
        elif op == "resize":
            el = self.board.find(str(inverse["id"]))
            if el is not None:
                el.width, el.height = int(inverse["w"]), int(inverse["h"])
        elif op == "recolor":
            el = self.board.find(str(inverse["id"]))
            if el is not None:
                el.color = str(inverse["color"])
        elif op == "swap":
            self._replace_element(inverse["element"])

    def _replace_element(self, snapshot: dict[str, Any]) -> None:
        """Swap in a stored element snapshot (undo/redo of point transforms),
        preserving list position so z-order is stable."""
        replacement = Element.from_dict(snapshot)
        self.board.elements = [
            replacement if el.id == replacement.id else el for el in self.board.elements
        ]

    def _apply_forward(self, command: dict[str, Any], inverse: dict[str, Any]) -> None:
        op = inverse.get("op")
        name = str(command.get("command", ""))
        if op == "remove":
            # Redo a creation: restore the exact element snapshot so IDs
            # and positions survive undo/redo cycles deterministically.
            forward = inverse.get("element")
            if forward is not None:
                if self.board.find(str(forward["id"])) is None:
                    self.board.elements.append(Element.from_dict(forward))
            elif name == "add_drawing":
                self.board.elements.append(
                    Element(
                        id=str(inverse["id"]), type="drawing", x=DEFAULT_X, y=TOP_MARGIN_Y,
                        width=320, height=120, color="#FFFFFF",
                        z=self.board.top_z() + 1, extra={"strokes": []},
                    )
                )
        elif op == "restore":
            self.board.elements = [el for el in self.board.elements if el.id != str(inverse["element"]["id"])]
        elif op == "restore_all":
            self.board.elements = []
        elif op == "move":
            el = self.board.find(str(inverse["id"]))
            if el is not None:
                params = command.get("parameters", {})
                el.x, el.y = resolve_move(params, el.x, el.y)
        elif op == "resize":
            el = self.board.find(str(inverse["id"]))
            if el is not None:
                params = command.get("parameters", {})
                if "scale_factor" in params:
                    el.width = int(el.width * float(params["scale_factor"]))
                    el.height = int(el.height * float(params["scale_factor"]))
                else:
                    el.width, el.height = int(params["size"]["w"]), int(params["size"]["h"])
        elif op == "recolor":
            el = self.board.find(str(inverse["id"]))
            if el is not None:
                el.color = str(command.get("parameters", {}).get("color", el.color))
        elif op == "swap":
            self._replace_element(inverse["forward"])

    # -- helpers -------------------------------------------------------------
    def _resolve_target(self, target_id: str | None, params: dict[str, Any]) -> Element | None:
        if isinstance(target_id, str):
            return self.board.find(target_id)
        if params.get("use_selection") and self.board.selected_element_id:
            return self.board.find(self.board.selected_element_id)
        return None

    def _confirm_prompt(self, command: str, target: Element | None) -> str:
        if command == "delete_item" and target is not None:
            return f"Delete this {target.type}? [Cancel] [Confirm]"
        if command == "clear_board":
            return "Clear the entire board? [Cancel] [Confirm]"
        return "Confirm this action? [Cancel] [Confirm]"

    def _clarify(self, command: str) -> EngineResult:
        action = command.replace("_item", "").replace("_", " ")
        return {
            "ok": False,
            "error_code": errors.E_AMBIGUOUS,
            "message": f"Which object would you like me to {action}?",
            "needs_clarification": True,
            "clarification_question": f"Which object would you like me to {action}?",
        }

    def _fail(self, code: str, message: str) -> EngineResult:
        if not message:
            message = errors.message_for(code)
        return {"ok": False, "error_code": code, "message": message}


class _Reject(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
