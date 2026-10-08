"""T005: WCAG luminance gate over every declared CONTRAST_PAIRS entry."""

from __future__ import annotations

from smartboard.ui import theme


def _luminance(hex_color: str) -> float:
    hex_color = hex_color.lstrip("#")
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> float:
    lighter, darker = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def test_all_pairs_meet_wcag_aa() -> None:
    assert theme.CONTRAST_PAIRS, "CONTRAST_PAIRS must not be empty"
    for fg, bg, kind in theme.CONTRAST_PAIRS:
        minimum = 4.5 if kind == "normal" else 3.0
        assert ratio(fg, bg) >= minimum, f"{fg} on {bg} ({kind}): {ratio(fg, bg):.2f}"


def test_state_and_outcome_colors_all_paired() -> None:
    paired = {(fg, bg) for fg, bg, _ in theme.CONTRAST_PAIRS}
    for color in (*theme.STATE_COLORS.values(), *theme.OUTCOME_COLORS.values()):
        assert any(bg == color or fg == color for fg, bg in paired), f"unpaired color {color}"
