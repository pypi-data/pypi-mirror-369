from __future__ import annotations
import os, re, shutil

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]")

try:
    from wcwidth import wcswidth as _wcswidth, wcwidth as _wcwidth
    _HAS_WCWIDTH = True
except Exception:
    _HAS_WCWIDTH = False
    _wcswidth = None  # type: ignore
    _wcwidth = None  # type: ignore

def strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)

def visible_width(s: str) -> int:
    p = strip_ansi(s)
    if _HAS_WCWIDTH and _wcswidth is not None:
        w = _wcswidth(p)  # type: ignore
        return max(0, w)
    return len(p)

def pad_to(s: str, width: int) -> str:
    pad = max(0, width - visible_width(s))
    return s + (" " * pad)

def trim_plain_to(s: str, width: int) -> str:
    p = strip_ansi(s)
    if _HAS_WCWIDTH and _wcwidth is not None:
        acc: list[str] = []
        w = 0
        for ch in p:
            cw = _wcwidth(ch) or 0  # type: ignore
            if w + cw > width:
                break
            acc.append(ch)
            w += cw
        return "".join(acc) + (" " * max(0, width - w))
    return (p[:width] if len(p) > width else p + " " * (width - len(p)))

def env_true(name: str) -> bool:
    v = os.environ.get(name)
    return v is not None and v not in ("0", "false", "False", "")

def term_columns(default: int = 120) -> int:
    try:
        cols = shutil.get_terminal_size().columns
        return cols if cols and cols > 0 else default
    except Exception:
        return default

def term_rows(default: int = 40) -> int:
    try:
        rows = shutil.get_terminal_size().lines
        return rows if rows and rows > 0 else default
    except Exception:
        return default
