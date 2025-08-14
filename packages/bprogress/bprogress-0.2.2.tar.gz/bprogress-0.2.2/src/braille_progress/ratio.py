from __future__ import annotations

from typing import Protocol

from .model import TaskState


class RatioStrategy(Protocol):
    def ratio(self, t: TaskState) -> float:
        ...


class DefaultRatio:
    def ratio(self, t: TaskState) -> float:
        if t.failed or t.finished:
            return 1.0
        s = (t.stage or "").lower()
        if s in ("opening", "scanning"):
            return 0.05
        if s == "validated":
            return 0.10
        if s == "writing" and t.total > 0:
            return 0.10 + 0.80 * (t.done / t.total)
        if s in ("md_zip", "md_written", "no_md"):
            return 0.95
        return 0.0
