from __future__ import annotations
from typing import Any
from .progress import Progress

class QueueBinder:
    def __init__(
        self,
        progress: Progress,
        queue,
        *,
        id_key: str = "i",
        stage_key: str = "stage",
        done_key: str = "case_done",
        total_key: str = "case_total",
        label_key: str = "case_label",
        error_key: str = "error",
    ):
        self.p = progress
        self.q = queue
        self.id_key = id_key
        self.stage_key = stage_key
        self.done_key = done_key
        self.total_key = total_key
        self.label_key = label_key
        self.error_key = error_key

    def drain(self) -> int:
        changed = 0
        while True:
            try:
                m: dict[str, Any] = self.q.get_nowait()
            except Exception:
                break
            tid = m.get(self.id_key)
            if tid is None or tid not in self.p._tasks:
                continue
            stage = m.get(self.stage_key)
            done = m.get(self.done_key)
            total = m.get(self.total_key)
            label = m.get(self.label_key)
            err = m.get(self.error_key)
            finished = None
            failed = None
            if stage in ("DONE", "ERROR"):
                finished = True
                failed = stage == "ERROR"
            self.p.update(tid, done=done, total=total, stage=stage, label=label, finished=finished, failed=failed)
            if failed and err is not None:
                self.p._tasks[tid].error = str(err)
            changed += 1
        return changed
