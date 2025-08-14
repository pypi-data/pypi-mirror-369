from __future__ import annotations

import os
import traceback
from typing import Any, Optional, Tuple, Type, List

from .style import AnsiStyler
from .util import strip_ansi


def _as_exc_tuple(obj: Any) -> Optional[Tuple[Type[BaseException], BaseException, Optional[object]]]:
    if isinstance(obj, tuple) and len(obj) in (2, 3) and isinstance(obj[1], BaseException):
        et = obj[0] if isinstance(obj[0], type) else type(obj[1])
        exc = obj[1]
        tb = obj[2] if len(obj) == 3 else getattr(exc, "__traceback__", None)
        return et, exc, tb
    return None

def _shorten(path: str, cwd: Optional[str]) -> str:
    try:
        p = os.path.abspath(path)
        if cwd:
            cwd = os.path.abspath(cwd)
            if p.startswith(cwd + os.sep):
                return "." + os.sep + p[len(cwd) + 1 :]
        return p
    except Exception:
        return path

def _fit_line(s: str, width: Optional[int]) -> str:
    if width is None or width <= 0:
        return s
    plain = strip_ansi(s)
    acc: List[str] = []
    w = 0
    try:
        from wcwidth import wcwidth
        for ch in plain:
            cw = wcwidth(ch) or 0
            if w + cw > width:
                break
            acc.append(ch)
            w += cw
    except Exception:
        acc = list(plain[: width])
    out = "".join(acc)
    if len(plain) > len(out):
        if width >= 1:
            out = (out[:-1] if len(out) >= 1 else "") + "…"
    return s.replace(plain, out, 1)

def format_exception_pretty(
    err: BaseException,
    *,
    width: Optional[int] = None,
    cwd: Optional[str] = None,
    limit: Optional[int] = None,
    styler: Optional[AnsiStyler] = None,
) -> str:
    S = styler or AnsiStyler(enabled=True)
    te = traceback.TracebackException.from_exception(err, limit=limit)
    lines: List[str] = []
    title = "Traceback (most recent call last):"
    lines.append(S.color(title, fg="bright_black"))
    for fs in te.stack:
        path = _shorten(fs.filename, cwd)
        dirn, base = os.path.split(path)
        file_part = (S.color(dirn + os.sep, fg="bright_black") if dirn else "") + S.color(base, fg="bright_cyan")
        loc = S.color(f":{fs.lineno}", fg="bright_black")
        func = S.color(f" in {fs.name}", fg="bright_magenta")
        head = f"  File {file_part}{loc}{func}"
        lines.append(_fit_line(head, width))
        code = (fs.line or "").strip()
        if code:
            lines.append(_fit_line("    " + S.color(code, fg="yellow"), width))
    ex_name = te.exc_type.__name__ if te.exc_type else type(err).__name__
    only = "".join(te.format_exception_only()).strip()
    msg = only[len(ex_name) + 1 :].strip() if only.startswith(ex_name + ":") else str(err)
    tail = S.color(ex_name, fg="bright_red", bold=True) + S.color(f": {msg}", fg="bright_red")
    lines.append(_fit_line(tail, width))
    return "\n".join(lines)

def format_error(
    err: Any,
    *,
    with_tb: bool = False,
    limit: Optional[int] = None,
    pretty: bool = False,
    width: Optional[int] = None,
    cwd: Optional[str] = None,
) -> str:
    if err is None:
        return ""
    if isinstance(err, BaseException):
        if with_tb and pretty:
            return format_exception_pretty(err, width=width, cwd=cwd)
        if with_tb and getattr(err, "__traceback__", None):
            return "".join(traceback.format_exception(type(err), err, err.__traceback__, limit=limit)).rstrip()
        return f"{type(err).__name__}: {err}".rstrip()
    t = _as_exc_tuple(err)
    if t:
        et, ex, tb = t
        if with_tb and pretty and tb:
            try:
                te = et if isinstance(et, BaseException) else ex
                return format_exception_pretty(ex, width=width, cwd=cwd)
            except Exception:
                pass
        if with_tb and tb:
            return "".join(traceback.format_exception(et, ex, tb, limit=limit)).rstrip()
        return f"{et.__name__}: {ex}".rstrip()
    try:
        return str(err)
    except Exception:
        return repr(err)
