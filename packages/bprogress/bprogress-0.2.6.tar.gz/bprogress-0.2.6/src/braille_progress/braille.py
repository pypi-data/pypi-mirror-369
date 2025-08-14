from __future__ import annotations

from .style import AnsiStyler

_DOT_ORDER = (1, 2, 3, 7, 4, 5, 6, 8)
_EMPTY = "\u2800"
_FULL = "\u28FF"


def _cell(dots: int) -> str:
    n = max(0, min(8, int(dots)))
    if n == 0:
        return _EMPTY
    m = 0
    for k in range(n):
        d = _DOT_ORDER[k]
        m |= 1 << (d - 1)
    return chr(0x2800 + m)


class BrailleRenderer:
    def __init__(self, styler: AnsiStyler) -> None:
        self.S = styler

    def bar(self, ratio: float, *, cells: int, fill_color: str, empty_color: str) -> str:
        r = max(0.0, min(1.0, float(ratio)))
        total = int(round(r * cells * 8))
        full, rem = divmod(total, 8)
        fs = (_FULL * full) + (_cell(rem) if rem else "")
        es = _EMPTY * (cells - full - (1 if rem else 0))
        return self.S.color(fs, fg=fill_color) + self.S.color(es, fg=empty_color, dim=True)

    def pct_text(self, ratio: float) -> str:
        pct = f" {int(max(0, min(100, int(round(ratio * 100))))):3d}%"
        return self.S.color(pct, fg="bright_green" if ratio >= 1.0 else "green")
