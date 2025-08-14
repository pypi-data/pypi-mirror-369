from __future__ import annotations
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Union

from .style import AnsiStyler
from .braille import BrailleRenderer
from .ratio import RatioStrategy
from .theme import ProgressTheme
from .model import TaskState
from .stats import TaskRuntime, fmt_hms
from .util import pad_to, trim_plain_to, visible_width, strip_ansi

class RenderContext:
    def __init__(self, theme: ProgressTheme, styler: AnsiStyler, bars: BrailleRenderer, ratio: RatioStrategy, columns: int):
        self.theme = theme
        self.styler = styler
        self.bars = bars
        self.ratio = ratio
        self.columns = columns

class Segment:
    def width(self, t: TaskState, rt: TaskRuntime, ctx: RenderContext) -> Optional[int]:
        return 0
    def render(self, t: TaskState, rt: TaskRuntime, ctx: RenderContext, width: int) -> str:
        return ""

@dataclass
class Text(Segment):
    s: str
    fg: Optional[str] = None
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return visible_width(self.s)
    def render(self, t, rt, ctx, width):
        s = pad_to(self.s, width)
        return ctx.styler.color(s, fg=self.fg, bg=self.bg)

@dataclass
class Gap(Segment):
    n: int = 1
    def width(self, t, rt, ctx): return self.n
    def render(self, t, rt, ctx, width): return " " * self.n

@dataclass
class Spacer(Segment):
    def width(self, t, rt, ctx): return None
    def render(self, t, rt, ctx, width): return " " * width

@dataclass
class Rule(Segment):
    char: str = "─"
    color: Optional[str] = "bright_black"
    def width(self, t, rt, ctx): return None
    def render(self, t, rt, ctx, width):
        s = self.char * max(0, width)
        return ctx.styler.color(s, fg=self.color) if self.color else s

@dataclass
class Now(Segment):
    fmt: str = "%H:%M:%S"
    width_fixed: Optional[int] = None
    color: Optional[str] = None
    bg: Optional[str] = None
    def width(self, t, rt, ctx):
        w = self.width_fixed if self.width_fixed is not None else visible_width(time.strftime(self.fmt))
        return w
    def render(self, t, rt, ctx, width):
        s = time.strftime(self.fmt)
        s = s[:width].rjust(width)
        return ctx.styler.color(s, fg=self.color, bg=self.bg) if (self.color or self.bg) else s

@dataclass
class Name(Segment):
    width_fixed: int
    color: str = "bright_cyan"
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return self.width_fixed
    def render(self, t, rt, ctx, width):
        s = pad_to(t.name[:width], width)
        return ctx.styler.color(s, fg=self.color, bg=self.bg)

@dataclass
class Bar(Segment):
    cells: int
    bracket_color: str = "bright_black"
    empty_color: str = "bright_black"
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return 2 + self.cells
    def render(self, t, rt, ctx, width):
        ratio = ctx.ratio.ratio(t)
        c = ctx.theme.stage_color(t.stage, t.failed, t.finished)
        left = ctx.styler.color("[", fg=self.bracket_color, dim=True, bg=self.bg)
        right = ctx.styler.color("]", fg=self.bracket_color, dim=True, bg=self.bg)
        inner = ctx.bars.bar(ratio, cells=self.cells, fill_color=c, empty_color=self.empty_color)
        inner = ctx.styler.color(inner, bg=self.bg)
        s = left + inner + right
        if visible_width(s) < width:
            s = s + ctx.styler.color(" " * (width - visible_width(s)), bg=self.bg)
        return s

@dataclass
class Percent(Segment):
    width_fixed: int
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return self.width_fixed
    def render(self, t, rt, ctx, width):
        s = pad_to(ctx.bars.pct_text(ctx.ratio.ratio(t)), width)
        return ctx.styler.color(s, bg=self.bg)

@dataclass
class Status(Segment):
    width_fixed: int
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return self.width_fixed
    def render(self, t, rt, ctx, width):
        color = ctx.theme.stage_color(t.stage, t.failed, t.finished)
        if t.failed: s = "✗ FAIL"
        elif t.finished: s = "✓ OK"
        else:
            st = (t.stage or "").lower()
            s = {"writing":"writing","validated":f"validated {t.total}","scanning":"scanning","md_written":"md saved","md_zip":"md packed","no_md":"no md"}.get(st, st)
        s = ctx.styler.color(trim_plain_to(s, width), fg=color, bg=self.bg)
        if visible_width(s) < width:
            s = s + ctx.styler.color(" " * (width - visible_width(s)), bg=self.bg)
        return s

@dataclass
class MiniBar(Segment):
    cells: int
    bracket_color: str = "bright_black"
    empty_color: str = "bright_black"
    fill_color: str = "cyan"
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return 2 + self.cells
    def render(self, t, rt, ctx, width):
        if t.total <= 0:
            return ctx.styler.color(" " * width, bg=self.bg) if self.bg else " " * width
        left = ctx.styler.color("[", fg=self.bracket_color, dim=True, bg=self.bg)
        right = ctx.styler.color("]", fg=self.bracket_color, dim=True, bg=self.bg)
        ratio = 0.0 if t.total <= 0 else (t.done / max(1, t.total))
        inner = ctx.bars.bar(ratio, cells=self.cells, fill_color=self.fill_color, empty_color=self.empty_color)
        inner = ctx.styler.color(inner, bg=self.bg)
        s = left + inner + right
        if visible_width(s) < width:
            s = s + ctx.styler.color(" " * (width - visible_width(s)), bg=self.bg)
        return s

class Counter(Segment):
    bg: Optional[str] = None
    def __init__(self, bg: Optional[str] = None):
        self.bg = bg
    def width(self, t, rt, ctx):
        d = max(1, len(str(max(1, t.total))))
        return 1 + d + 1 + d
    def render(self, t, rt, ctx, width):
        d = max(1, len(str(max(1, t.total))))
        s = f" {t.done:>{d}}/{t.total:<{d}}"
        s = pad_to(ctx.styler.color(s, fg="bright_black"), width)
        return ctx.styler.color(s, bg=self.bg) if self.bg else s

@dataclass
class Label(Segment):
    color: str = "bright_black"
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return None
    def render(self, t, rt, ctx, width):
        lbl = t.label or ""
        if visible_width(lbl) > width:
            p = strip_ansi(lbl)
            lbl = "…" + p[-(max(1, width - 1)):] if width > 0 else ""
        s = pad_to(ctx.styler.color(lbl, fg=self.color), width)
        return ctx.styler.color(s, bg=self.bg) if self.bg else s

@dataclass
class Elapsed(Segment):
    width_fixed: int = 8
    prefix: str = ""
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return self.width_fixed if self.width_fixed > 0 else visible_width(self.prefix) + 5
    def render(self, t, rt, ctx, width):
        now = rt.updated or rt.created
        base = rt.started or rt.created
        sec = max(0.0, (now - base) if now and base else 0.0)
        s = f"{self.prefix}{fmt_hms(sec)}" if self.prefix else fmt_hms(sec)
        s = pad_to(s, width)
        return ctx.styler.color(s, bg=self.bg) if self.bg else s

@dataclass
class AvgRate(Segment):
    width_fixed: int = 10
    unit: str = "it/s"
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return self.width_fixed
    def render(self, t, rt, ctx, width):
        r = rt.ewma_rate if rt.ewma_rate > 0 else 0.0
        s = f"{r:.2f} {self.unit}"
        s = pad_to(s, width)
        return ctx.styler.color(s, bg=self.bg) if self.bg else s

@dataclass
class ETA(Segment):
    width_fixed: int = 8
    bg: Optional[str] = None
    def width(self, t, rt, ctx): return self.width_fixed
    def render(self, t, rt, ctx, width):
        if t.total > 0 and rt.ewma_rate > 0:
            rem = max(0, t.total - t.done)
            sec = rem / rt.ewma_rate if rem > 0 else 0.0
            s = fmt_hms(sec)
        else:
            s = "--:--"
        s = pad_to(s, width)
        return ctx.styler.color(s, bg=self.bg) if self.bg else s

class Layout:
    def __init__(self, segments: Sequence[Segment]):
        self.segments = list(segments)
    def _assign_widths(self, t: TaskState, rt: TaskRuntime, ctx: RenderContext) -> List[int]:
        fixed: List[Tuple[int, int]] = []
        flex_idx: List[int] = []
        for i, seg in enumerate(self.segments):
            w = seg.width(t, rt, ctx)
            if w is None:
                flex_idx.append(i)
                fixed.append((i, 0))
            else:
                fixed.append((i, max(0, int(w))))
        used = sum(w for _, w in fixed)
        remain = max(0, ctx.columns - used)
        if flex_idx:
            per = remain // len(flex_idx)
            extra = remain % len(flex_idx)
            for k, idx in enumerate(flex_idx):
                fixed[idx] = (idx, per + (1 if k < extra else 0))
        else:
            if used > ctx.columns:
                over = used - ctx.columns
                for i, seg in enumerate(self.segments):
                    if isinstance(seg, Label):
                        w = max(0, fixed[i][1] - over)
                        fixed[i] = (i, w)
                        break
        return [w for _, w in fixed]
    def render_line(self, t: TaskState, rt: TaskRuntime, ctx: RenderContext) -> str:
        widths = self._assign_widths(t, rt, ctx)
        parts = [seg.render(t, rt, ctx, widths[i]) for i, seg in enumerate(self.segments)]
        return "".join(parts)

def default_layout(theme: ProgressTheme) -> Layout:
    return Layout([
        Name(theme.name_w),
        Text(" | "),
        Bar(theme.bar_cells),
        Percent(theme.pct_w),
        Gap(2),
        Status(theme.right_w),
        Text(" | "),
        MiniBar(theme.mini_cells),
        Counter(),
        Gap(2),
        Label(),
    ])

@dataclass
class VGap:
    n: int = 1

Row = Union[Layout, VGap, Sequence[Segment]]

class VLayout:
    def __init__(self, rows: Sequence[Row]):
        self.rows: List[Union[Layout, VGap]] = []
        for r in rows:
            if isinstance(r, VGap) or isinstance(r, Layout):
                self.rows.append(r)
            else:
                self.rows.append(Layout(list(r)))
    def render(self, ctx: RenderContext) -> List[str]:
        dummy_t = TaskState(name="")
        dummy_rt = TaskRuntime()
        out: List[str] = []
        for r in self.rows:
            if isinstance(r, VGap):
                out.extend([" " * ctx.columns] * max(0, r.n))
            else:
                out.append(r.render_line(dummy_t, dummy_rt, ctx))
        return out
