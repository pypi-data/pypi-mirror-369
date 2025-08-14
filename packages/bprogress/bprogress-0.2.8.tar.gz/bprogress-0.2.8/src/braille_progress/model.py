from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class TaskState:
    name: str
    total: int = 0
    done: int = 0
    stage: str = "queue"
    label: str = ""
    finished: bool = False
    failed: bool = False
    error: str = ""

class TaskHandle:
    def __init__(self, board: "Progress", tid: int):
        self._board = board
        self._tid = tid
    def advance(self, n: int = 1, *, label: Optional[str] = None, stage: Optional[str] = None) -> "TaskHandle":
        self._board.update(self, advance=n, label=label, stage=stage)
        return self
    def update(
        self,
        *,
        done: Optional[int] = None,
        total: Optional[int] = None,
        stage: Optional[str] = None,
        label: Optional[str] = None,
        finished: Optional[bool] = None,
        failed: Optional[bool] = None,
    ) -> "TaskHandle":
        self._board.update(
            self,
            done=done,
            total=total,
            stage=stage,
            label=label,
            finished=finished,
            failed=failed,
        )
        return self
    def complete(self) -> None:
        self._board.done(self)
    def fail(self, stage: str = "error", error: Optional[Any] = None, error_tb: bool = False) -> None:
        self._board.fail(self, stage=stage, error=error, error_tb=error_tb)
