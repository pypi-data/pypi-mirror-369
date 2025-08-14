from __future__ import annotations

import atexit
import os
import sys
from typing import List, Optional

from .util import env_true, term_columns

_ORIG_WIN = {"in": None, "out": None, "err": None}

def _enable_vt_mode_windows() -> None:
    if os.name != "nt": return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        OUT, ERR, IN = -11, -12, -10
        EVTP, EPO, EVTI, EEF, EQE = 0x0004, 0x0001, 0x0200, 0x0080, 0x0040
        hout, herr, hin = k.GetStdHandle(OUT), k.GetStdHandle(ERR), k.GetStdHandle(IN)
        mo, me, mi = ctypes.c_uint32(), ctypes.c_uint32(), ctypes.c_uint32()
        if k.GetConsoleMode(hout, ctypes.byref(mo)): _ORIG_WIN["out"] = mo.value
        if k.GetConsoleMode(herr, ctypes.byref(me)): _ORIG_WIN["err"] = me.value
        if k.GetConsoleMode(hin,  ctypes.byref(mi)): _ORIG_WIN["in"]  = mi.value
        if _ORIG_WIN["out"] is not None: k.SetConsoleMode(hout, _ORIG_WIN["out"] | EVTP | EPO)
        if _ORIG_WIN["err"] is not None: k.SetConsoleMode(herr, _ORIG_WIN["err"] | EVTP | EPO)
        if _ORIG_WIN["in"]  is not None: k.SetConsoleMode(hin,  (_ORIG_WIN["in"] | EVTI | EEF) & ~EQE)
    except Exception:
        pass

def _restore_vt_mode_windows() -> None:
    if os.name != "nt": return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        OUT, ERR, IN = -11, -12, -10
        if _ORIG_WIN["out"] is not None: k.SetConsoleMode(k.GetStdHandle(OUT), _ORIG_WIN["out"])
        if _ORIG_WIN["err"] is not None: k.SetConsoleMode(k.GetStdHandle(ERR), _ORIG_WIN["err"])
        if _ORIG_WIN["in"]  is not None: k.SetConsoleMode(k.GetStdHandle(IN),  _ORIG_WIN["in"])
    except Exception:
        pass

def _flush_input_buffer() -> None:
    try:
        if os.name == "nt":
            import ctypes
            k = ctypes.windll.kernel32
            STD_INPUT_HANDLE = -10
            h = k.GetStdHandle(STD_INPUT_HANDLE)
            k.FlushConsoleInputBuffer(h)
        else:
            import termios
            fd = sys.stdin.fileno()
            termios.tcflush(fd, termios.TCIFLUSH)
    except Exception:
        pass

class TerminalIO:
    def __init__(self, *, force_tty: Optional[bool] = None, auto_vt: bool = True) -> None:
        if auto_vt: _enable_vt_mode_windows()
        if force_tty is None and env_true("BP_FORCE_TTY"): force_tty = True
        self._tty = (force_tty if force_tty is not None else self._isatty())
        self._prev_height = 0
        self._alt = False
        self._mouse = False
        self._anchored = False
        atexit.register(self._restore_all)

    @staticmethod
    def _isatty() -> bool:
        try:
            if sys.stdout.isatty(): return True
        except Exception:
            pass
        env = os.environ
        return any(k in env for k in ("WT_SESSION","PYCHARM_HOSTED","TERM_SESSION_ID","VSCODE_PID","ConEmuANSI","ANSICON"))

    @property
    def is_tty(self) -> bool: return self._tty
    @property
    def columns(self) -> int: return term_columns()

    def enter_alt(self) -> None:
        if not self._tty or self._alt: return
        out = sys.__stdout__; out.write("\x1b[?1049h\x1b[?25l"); out.flush(); self._alt = True

    def exit_alt(self) -> None:
        if not self._tty or not self._alt: return
        if self._mouse: self.disable_mouse()
        out = sys.__stdout__; out.write("\x1b[?25h\x1b[?1049l"); out.flush(); self._alt = False

    def enable_mouse(self) -> None:
        if not self._tty or self._mouse: return
        out = sys.__stdout__
        out.write("\x1b[?1002h\x1b[?1006h")  # 버튼+드래그, SGR
        out.flush()
        self._mouse = True

    def disable_mouse(self) -> None:
        if not self._tty or not self._mouse:
            out = sys.__stdout__
            out.write("\x1b[?1006l\x1b[?1002l\x1b[?1000l\x1b[?1015l\x1b[?1004l\x1b[?2004l")
            out.flush()
            return
        out = sys.__stdout__
        out.write("\x1b[?1006l\x1b[?1002l\x1b[?1000l\x1b[?1015l\x1b[?1004l\x1b[?2004l")
        out.flush()
        self._mouse = False

    def write_frame(self, lines: List[str]) -> None:
        out = sys.__stdout__
        cols = term_columns()
        eff = max(1, cols - 1)  # guard column
        from .util import cut_visible_preserve_ansi
        safe = [cut_visible_preserve_ansi(ln, eff) for ln in lines]
        phys_now = len(safe)

        out.write("\x1b[?7l")  # autowrap off

        if not self._tty:
            out.write("\n".join(safe) + "\n")
            out.flush()
            self._prev_height = 0
            return

        if self._prev_height > 0:
            if self._prev_height > 1:
                out.write(f"\x1b[{self._prev_height - 1}F")
            else:
                out.write("\r")

        for i, ln in enumerate(safe):
            out.write("\x1b[2K")
            out.write(ln)
            if i < phys_now - 1:
                out.write("\x1b[E")

        extra = max(0, self._prev_height - phys_now)
        if extra:
            for _ in range(extra):
                out.write("\x1b[E")
                out.write("\x1b[2K")
            out.write(f"\x1b[{extra}F")
            if phys_now > 1:
                out.write(f"\x1b[{phys_now - 1}E")

        out.write("\x1b[?7h")
        out.flush()
        self._prev_height = phys_now

    def _restore_all(self) -> None:
        try:
            self.disable_mouse()
        except Exception:
            pass
        try:
            sys.__stdout__.write("\x1b[?7h\x1b[?25h")
            sys.__stdout__.flush()
        except Exception:
            pass
        try:
            _flush_input_buffer()
        except Exception:
            pass
        try:
            self.exit_alt()
        except Exception:
            pass
        _restore_vt_mode_windows()

    def close(self) -> None:
        if self._tty and self._prev_height:
            sys.__stdout__.write("\n"); sys.__stdout__.flush()
        self._prev_height = 0
        self._anchored = False
        self._restore_all()
