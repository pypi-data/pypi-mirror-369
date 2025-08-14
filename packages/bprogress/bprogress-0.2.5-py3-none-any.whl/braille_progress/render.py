from __future__ import annotations

from typing import Tuple

from .util import pad_to, trim_plain_to, visible_width, strip_ansi
from .style import AnsiStyler
from .braille import BrailleRenderer
from .ratio import RatioStrategy
from .theme import ProgressTheme
from .model import TaskState

try:
    from wcwidth import wcwidth as _wcwidth
    _HAS_WCWIDTH = True
except Exception:
    _HAS_WCWIDTH = False
    _wcwidth = None  # type: ignore


class LineRenderer:
    def __init__(self, theme: ProgressTheme, styler: AnsiStyler, bars: BrailleRenderer, ratio: RatioStrategy) -> None:
        self.T = theme
        self.S = styler
        self.B = bars
        self.R = ratio
        self._left_br = self.S.color("[", fg="bright_black", dim=True)
        self._right_br = self.S.color("]", fg="bright_black", dim=True)

    def _status_text(self, t: TaskState) -> Tuple[str, str]:
        color = self.T.stage_color(t.stage, t.failed, t.finished)
        if t.failed:
            return "✗ FAIL", color
        if t.finished:
            return "✓ OK", color
        s = (t.stage or "").lower()
        rtxt = {
            "writing": "writing",
            "validated": f"validated {t.total}",
            "scanning": "scanning",
            "md_written": "md saved",
            "md_zip": "md packed",
            "no_md": "no md",
        }.get(s, s)
        return rtxt, color

    def render_line(self, t: TaskState) -> str:
        th = self.T
        name = pad_to(self.S.color(t.name[: th.name_w], fg="bright_cyan"), th.name_w)

        ratio = self.R.ratio(t)
        status_text, color = self._status_text(t)

        bar_in = self.B.bar(ratio, cells=th.bar_cells, fill_color=color, empty_color="bright_black")
        bar_block = pad_to(self._left_br + bar_in + self._right_br, 2 + th.bar_cells)
        pct_block = pad_to(self.B.pct_text(ratio), th.pct_w)

        rtxt = trim_plain_to(status_text, th.right_w)
        right_col = pad_to(self.S.color(rtxt, fg=color), th.right_w)

        if t.total > 0:
            mini_in = self.B.bar((t.done / t.total), cells=th.mini_cells, fill_color="cyan", empty_color="bright_black")
            mini_block = pad_to(self._left_br + mini_in + self._right_br, 2 + th.mini_cells)
            d = max(1, len(str(t.total)))
            nums = f" {t.done:>{d}}/{t.total:<{d}}"
            mini_nums = pad_to(self.S.color(nums, fg="bright_black"), 1 + d + 1 + d)
        else:
            mini_block = " " * (2 + th.mini_cells)
            mini_nums = " " * 3

        lbl = t.label or ""
        if visible_width(lbl) > th.label_w:
            plain = strip_ansi(lbl)
            if _HAS_WCWIDTH and _wcwidth is not None:
                acc = []
                w = 0
                for ch in reversed(plain):
                    cw = _wcwidth(ch) or 0  # type: ignore
                    if w + cw > th.label_w - 1:
                        break
                    acc.append(ch)
                    w += cw
                lbl = "…" + "".join(reversed(acc))
            else:
                lbl = "…" + plain[-(th.label_w - 1) :]
        label_col = pad_to(self.S.color(lbl, fg="bright_black"), th.label_w)

        return f"{name} | {bar_block}{pct_block}  {right_col} | {mini_block}{mini_nums}  {label_col}"
