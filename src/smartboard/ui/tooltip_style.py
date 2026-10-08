"""Application style adjustments confined to tooltip timing."""

from __future__ import annotations

from typing import Any

from . import theme

try:
    from PyQt6.QtWidgets import QProxyStyle, QStyle

    _QT = True
except ImportError:  # pragma: no cover - headless CI
    _QT = False


class TooltipStyle(QProxyStyle if _QT else object):  # type: ignore[misc]
    """Return the themed tooltip delay while delegating all other style hints."""

    def styleHint(
        self, hint: Any, option: Any = None, widget: Any = None, returnData: Any = None
    ) -> int:
        if not _QT:  # pragma: no cover - headless CI
            raise RuntimeError("PyQt6 is required for the tooltip style.")
        if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
            return int(theme.TOOLTIP_WAKEUP_DELAY_MS)
        result: int = super().styleHint(hint, option, widget, returnData)
        return result
