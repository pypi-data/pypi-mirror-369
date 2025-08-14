from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .util import term_columns


@dataclass
class ProgressTheme:
    name_w: int = 22
    bar_cells: int = 18
    pct_w: int = 5
    right_w: int = 16
    mini_cells: int = 10
    label_w: int = 34
    color: bool = True
    colors: Dict[str, str] = field(
        default_factory=lambda: {
            "queue": "bright_black",
            "opening": "bright_blue",
            "scanning": "bright_blue",
            "validated": "bright_yellow",
            "writing": "green",
            "md_zip": "bright_green",
            "md_written": "bright_green",
            "no_md": "bright_black",
            "done": "bright_green",
            "error": "bright_red",
        }
    )

    def stage_color(self, stage: str, failed: bool, finished: bool) -> str:
        if failed:
            return self.colors["error"]
        if finished:
            return self.colors["done"]
        return self.colors.get((stage or "").lower(), "bright_white")

    @classmethod
    def auto_fit(cls, columns: Optional[int] = None) -> "ProgressTheme":
        columns = columns or term_columns()
        base = cls()
        fixed = (
            base.name_w
            + 3
            + (2 + base.bar_cells)
            + base.pct_w
            + 2
            + base.right_w
            + 3
            + (2 + base.mini_cells)
            + 7
            + 2
        )
        base.label_w = max(20, columns - fixed)
        return base
