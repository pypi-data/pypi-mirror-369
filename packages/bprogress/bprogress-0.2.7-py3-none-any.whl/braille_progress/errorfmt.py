from __future__ import annotations
import traceback
from typing import Any, Optional, Tuple, Type

def _as_exc_tuple(obj: Any) -> Optional[Tuple[Type[BaseException], BaseException, Optional[object]]]:
    if isinstance(obj, tuple) and len(obj) in (2, 3) and isinstance(obj[1], BaseException):
        et = obj[0] if isinstance(obj[0], type) else type(obj[1])
        exc = obj[1]
        tb = obj[2] if len(obj) == 3 else getattr(exc, "__traceback__", None)
        return et, exc, tb
    return None

def format_error(err: Any, *, with_tb: bool = False, limit: Optional[int] = None) -> str:
    if err is None:
        return ""
    if isinstance(err, BaseException):
        if with_tb and getattr(err, "__traceback__", None):
            return "".join(traceback.format_exception(type(err), err, err.__traceback__, limit=limit)).rstrip()
        return f"{type(err).__name__}: {err}".rstrip()
    t = _as_exc_tuple(err)
    if t:
        et, ex, tb = t
        if with_tb and tb:
            return "".join(traceback.format_exception(et, ex, tb, limit=limit)).rstrip()
        return f"{et.__name__}: {ex}".rstrip()
    try:
        return str(err)
    except Exception:
        return repr(err)
