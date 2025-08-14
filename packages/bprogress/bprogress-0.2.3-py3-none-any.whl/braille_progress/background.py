from __future__ import annotations
from typing import List, Optional, Sequence, Tuple
try:
    from PIL import Image  # type: ignore
    _HAS_PIL = True
except Exception:
    _HAS_PIL = False

from .style import AnsiStyler
from .util import pad_to, visible_width

class Background:
    def render(self, styler: AnsiStyler, columns: int, rows: int) -> List[str]:
        return [" " * columns for _ in range(rows)]

class SolidBackground(Background):
    def __init__(self, color: Optional[str] = None):
        self.color = color
    def render(self, styler: AnsiStyler, columns: int, rows: int) -> List[str]:
        line = styler.color(" " * columns, bg=self.color) if self.color else " " * columns
        return [line for _ in range(rows)]

class TextBackground(Background):
    def __init__(self, lines: Sequence[str], *, fg: Optional[str] = None, bg: Optional[str] = None, dim: bool = True):
        self.lines = list(lines)
        self.fg = fg
        self.bg = bg
        self.dim = dim
    def render(self, styler: AnsiStyler, columns: int, rows: int) -> List[str]:
        canvas = [" " * columns for _ in range(rows)]
        th = len(self.lines)
        tw = max([visible_width(s) for s in self.lines] or [0])
        top = max(0, (rows // 2) - (th // 2))
        left = max(0, (columns // 2) - (tw // 2))
        for i, raw in enumerate(self.lines):
            if top + i >= rows: break
            s = raw
            if visible_width(s) > columns:
                s = s[:columns]
            s = pad_to(s, min(columns - left, visible_width(s)))
            s = styler.color(s, fg=self.fg, bg=self.bg, dim=self.dim)
            pre = canvas[top + i][:left]
            post_len = max(0, columns - (left + len(s)))
            canvas[top + i] = pre + s + (" " * post_len)
        return canvas

class ImageBackground(Background):
    def __init__(self, path: str, *, ramp: str = " .:-=+*#%@", invert: bool = False):
        self.path = path
        self.ramp = ramp[::-1] if invert else ramp
    def render(self, styler: AnsiStyler, columns: int, rows: int) -> List[str]:
        if not _HAS_PIL:
            return [" " * columns for _ in range(rows)]
        try:
            im = Image.open(self.path).convert("L")
        except Exception:
            return [" " * columns for _ in range(rows)]
        target_h = max(1, rows // 2)
        target_w = max(1, columns)
        im = im.resize((target_w, target_h))
        chars = []
        n = len(self.ramp) - 1
        for y in range(im.size[1]):
            row = []
            for x in range(im.size[0]):
                v = im.getpixel((x, y)) / 255.0
                idx = int(v * n)
                row.append(self.ramp[idx])
            line = "".join(row)
            if visible_width(line) < columns:
                line = pad_to(line, columns)
            else:
                line = line[:columns]
            chars.append(line)
        top = max(0, (rows // 2) - (len(chars) // 2))
        canvas = [" " * columns for _ in range(rows)]
        for i, ln in enumerate(chars):
            if top + i >= rows: break
            canvas[top + i] = ln
        return canvas
