from __future__ import annotations
from typing import Dict, List, Optional

_COLOR_TABLE: Dict[str, int] = {
    "black":30,"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37,
    "bright_black":90,"bright_red":91,"bright_green":92,"bright_yellow":93,"bright_blue":94,
    "bright_magenta":95,"bright_cyan":96,"bright_white":97,
}
_BG_TABLE: Dict[str, int] = {
    "black":40,"red":41,"green":42,"yellow":43,"blue":44,"magenta":45,"cyan":46,"white":47,
    "bright_black":100,"bright_red":101,"bright_green":102,"bright_yellow":103,"bright_blue":104,
    "bright_magenta":105,"bright_cyan":106,"bright_white":107,
}

class AnsiStyler:
    def __init__(self, *, enabled: Optional[bool] = None) -> None:
        self.enabled = True if enabled is None else bool(enabled)
    def color(self, s: str, *, fg: Optional[str] = None, bg: Optional[str] = None, bold: bool = False, dim: bool = False, invert: bool = False) -> str:
        if not self.enabled:
            return s
        seq: List[str] = []
        if bold: seq.append("1")
        if dim: seq.append("2")
        if invert: seq.append("7")
        if fg in _COLOR_TABLE: seq.append(str(_COLOR_TABLE[fg]))
        if bg in _BG_TABLE: seq.append(str(_BG_TABLE[bg]))
        return f"\x1b[{';'.join(seq)}m{s}\x1b[0m" if seq else s
