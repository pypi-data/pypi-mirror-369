from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskRuntime:
    created: float = 0.0
    started: Optional[float] = None
    updated: Optional[float] = None
    finished: Optional[float] = None
    failed: Optional[float] = None
    ewma_rate: float = 0.0
    done_prev: int = 0

    def on_create(self) -> None:
        self.created = time.monotonic()

    def on_progress(self, done: int) -> None:
        now = time.monotonic()
        if self.started is None and done > 0:
            self.started = now
        if self.updated is not None and done >= self.done_prev:
            dt = max(1e-6, now - self.updated)
            inc = max(0, done - self.done_prev)
            inst = inc / dt
            if self.ewma_rate <= 0.0:
                self.ewma_rate = inst
            else:
                self.ewma_rate = 0.3 * inst + 0.7 * self.ewma_rate
        self.done_prev = done
        self.updated = now

    def on_finish(self, failed: bool = False) -> None:
        now = time.monotonic()
        self.finished = now
        if failed:
            self.failed = now

def fmt_hms(sec: float) -> str:
    s = int(max(0, round(sec)))
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
