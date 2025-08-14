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
    def __init__(
        self,
        path: str,
        *,
        ramp: str = " .:-=+*#%@",
        invert: bool = False,
        alpha_bg: int = 0,          # 0=검정 바탕에 합성 (투명부가 어두워짐 → 과포화 방지)
        autocontrast: bool = True,
        gamma: float = 1.0
    ):
        self.path = path
        self.ramp = ramp[::-1] if invert else ramp
        self.alpha_bg = max(0, min(255, int(alpha_bg)))
        self.autocontrast = autocontrast
        self.gamma = max(0.2, float(gamma))

    def render(self, styler: AnsiStyler, columns: int, rows: int) -> List[str]:
        if not _HAS_PIL:
            return [" " * columns for _ in range(rows)]
        try:
            from PIL import Image, ImageOps
            im = Image.open(self.path)
            if im.mode not in ("RGB", "RGBA", "L"):
                im = im.convert("RGBA")
            if im.mode == "RGBA":
                bg = Image.new("RGBA", im.size, (self.alpha_bg, self.alpha_bg, self.alpha_bg, 255))
                im = Image.alpha_composite(bg, im).convert("RGB")
            if im.mode != "L":
                im = im.convert("L")
            if self.autocontrast:
                im = ImageOps.autocontrast(im)
            if abs(self.gamma - 1.0) > 1e-3:
                lut = [int(pow(x / 255.0, 1.0 / self.gamma) * 255.0 + 0.5) for x in range(256)]
                im = im.point(lut, mode="L")
        except Exception:
            return [" " * columns for _ in range(rows)]

        target_h = max(1, rows // 2)
        target_w = max(1, columns)
        im = im.resize((target_w, target_h))
        n = len(self.ramp) - 1
        lines: List[str] = []
        for y in range(im.size[1]):
            row = []
            for x in range(im.size[0]):
                v = im.getpixel((x, y)) / 255.0
                idx = int(round(v * n))
                idx = max(0, min(n, idx))
                row.append(self.ramp[idx])
            line = "".join(row)
            if len(line) < columns:
                line = line + (" " * (columns - len(line)))
            else:
                line = line[:columns]
            lines.append(line)
        top = max(0, (rows // 2) - (len(lines) // 2))
        canvas = [" " * columns for _ in range(rows)]
        for i, ln in enumerate(lines):
            j = top + i
            if j >= rows:
                break
            canvas[j] = ln
        return canvas
