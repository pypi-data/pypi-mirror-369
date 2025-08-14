from __future__ import annotations

from typing import Dict, List, Optional


_COLOR_TABLE: Dict[str, int] = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "bright_black": 90,
    "bright_red": 91,
    "bright_green": 92,
    "bright_yellow": 93,
    "bright_blue": 94,
    "bright_magenta": 95,
    "bright_cyan": 96,
    "bright_white": 97,
}


class AnsiStyler:
    def __init__(self, *, enabled: Optional[bool] = None) -> None:
        self.enabled = True if enabled is None else bool(enabled)

    def color(self, s: str, *, fg: Optional[str] = None, bold: bool = False, dim: bool = False) -> str:
        if not self.enabled:
            return s
        seq: List[str] = []
        if bold:
            seq.append("1")
        if dim:
            seq.append("2")
        if fg in _COLOR_TABLE:
            seq.append(str(_COLOR_TABLE[fg]))
        return f"\x1b[{';'.join(seq)}m{s}\x1b[0m" if seq else s
