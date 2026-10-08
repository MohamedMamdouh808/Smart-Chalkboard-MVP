"""Selection model (pure logic; Qt-agnostic)."""

from __future__ import annotations


class Selection:
    """Tracks the selected element id. UI widgets notify; engine owns truth."""

    def __init__(self) -> None:
        self.selected_id: str | None = None

    def select(self, element_id: str | None) -> None:
        self.selected_id = element_id

    def clear(self) -> None:
        self.selected_id = None

    def sync_from_board(self, board_selected: str | None, existing_ids: set[str]) -> None:
        if board_selected is not None and board_selected in existing_ids:
            self.selected_id = board_selected
        else:
            self.selected_id = None
