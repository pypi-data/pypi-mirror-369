from __future__ import annotations
from typing import Any, Dict, Optional
from .errorfmt import format_error

def progress_message(
    i: int,
    *,
    stage: Optional[str] = None,
    done: Optional[int] = None,
    total: Optional[int] = None,
    label: Optional[str] = None,
    final: bool = False,
    failed: bool = False,
    error: Optional[Any] = None,
    error_tb: bool = False,
) -> Dict[str, Any]:
    m: Dict[str, Any] = {"i": int(i)}
    if stage is not None:
        m["stage"] = stage
    if done is not None:
        m["case_done"] = int(done)
    if total is not None:
        m["case_total"] = int(total)
    if label is not None:
        m["case_label"] = str(label)
    if error is not None:
        m["error"] = format_error(error, with_tb=error_tb)
    if final:
        m["stage"] = "ERROR" if failed else "DONE"
    return m
