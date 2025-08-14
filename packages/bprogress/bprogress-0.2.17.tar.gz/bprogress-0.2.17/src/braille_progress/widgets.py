from __future__ import annotations
import time
from typing import List, Optional
from .style import AnsiStyler
from .util import pad_to, visible_width, trim_plain_to

class DetailRenderer:
    def render(self, *, width: int, height: int, styler: AnsiStyler, title: str, lines: List[str]) -> List[str]:
        return [""] * height

class ConsoleRenderer(DetailRenderer):
    def __init__(self, title_fg: str = "bright_cyan") -> None:
        self.title_fg = title_fg
    def render(self, *, width: int, height: int, styler: AnsiStyler, title: str, lines: List[str]) -> List[str]:
        out: List[str] = []
        hdr = pad_to(styler.color(title, fg=self.title_fg), width)
        out.append(hdr)
        if height <= 1:
            return out[:height]
        body_h = height - 1
        tail = lines[-body_h:] if len(lines) > body_h else lines
        for ln in tail:
            out.append(pad_to(trim_plain_to(ln, width), width))
        while len(out) < height:
            out.append(" " * width)
        return out[:height]

class StaticRenderer(DetailRenderer):
    def __init__(self, lines: List[str]) -> None:
        self._lines = list(lines)
    def render(self, *, width: int, height: int, styler: AnsiStyler, title: str, lines: List[str]) -> List[str]:
        out = [pad_to(trim_plain_to(s, width), width) for s in self._lines[:height]]
        while len(out) < height:
            out.append(" " * width)
        return out
