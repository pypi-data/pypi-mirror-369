# terminal.py
from __future__ import annotations
import os, sys, atexit
from typing import List, Optional
from .util import env_true, term_columns

_ORIG_WIN = {"in": None, "out": None, "err": None}

def _enable_vt_mode_windows() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE  = -12
        STD_INPUT_HANDLE  = -10
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        ENABLE_PROCESSED_OUTPUT = 0x0001
        ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
        ENABLE_EXTENDED_FLAGS = 0x0080
        ENABLE_QUICK_EDIT_MODE = 0x0040
        hout = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        herr = kernel32.GetStdHandle(STD_ERROR_HANDLE)
        hin  = kernel32.GetStdHandle(STD_INPUT_HANDLE)
        om_out = ctypes.c_uint32(); om_err = ctypes.c_uint32(); om_in = ctypes.c_uint32()
        if kernel32.GetConsoleMode(hout, ctypes.byref(om_out)): _ORIG_WIN["out"] = om_out.value
        if kernel32.GetConsoleMode(herr, ctypes.byref(om_err)): _ORIG_WIN["err"] = om_err.value
        if kernel32.GetConsoleMode(hin,  ctypes.byref(om_in)):  _ORIG_WIN["in"]  = om_in.value
        if _ORIG_WIN["out"] is not None:
            kernel32.SetConsoleMode(hout, _ORIG_WIN["out"] | ENABLE_VIRTUAL_TERMINAL_PROCESSING | ENABLE_PROCESSED_OUTPUT)
        if _ORIG_WIN["err"] is not None:
            kernel32.SetConsoleMode(herr, _ORIG_WIN["err"] | ENABLE_VIRTUAL_TERMINAL_PROCESSING | ENABLE_PROCESSED_OUTPUT)
        if _ORIG_WIN["in"] is not None:
            new_in = (_ORIG_WIN["in"] | ENABLE_VIRTUAL_TERMINAL_INPUT | ENABLE_EXTENDED_FLAGS) & ~ENABLE_QUICK_EDIT_MODE
            kernel32.SetConsoleMode(hin, new_in)
    except Exception:
        pass

def _restore_vt_mode_windows() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE  = -12
        STD_INPUT_HANDLE  = -10
        if _ORIG_WIN["out"] is not None:
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), _ORIG_WIN["out"])
        if _ORIG_WIN["err"] is not None:
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-12), _ORIG_WIN["err"])
        if _ORIG_WIN["in"] is not None:
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), _ORIG_WIN["in"])
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
        out = sys.__stdout__
        out.write("\x1b[?1049h\x1b[?25l"); out.flush(); self._alt = True

    def exit_alt(self) -> None:
        if not self._tty or not self._alt: return
        if self._mouse: self.disable_mouse()
        out = sys.__stdout__
        out.write("\x1b[?25h\x1b[?1049l"); out.flush(); self._alt = False

    def enable_mouse(self) -> None:
        if not self._tty or self._mouse: return
        out = sys.__stdout__
        out.write("\x1b[?1002h\x1b[?1006h"); out.flush(); self._mouse = True

    def disable_mouse(self) -> None:
        if not self._tty or not self._mouse: return
        out = sys.__stdout__
        out.write("\x1b[?1006l\x1b[?1002l"); out.flush(); self._mouse = False

    def write_frame(self, lines: List[str]) -> None:
        out = sys.__stdout__
        out.write("\x1b[?7l")
        if not self._tty:
            out.write("\n".join(lines) + "\n"); out.flush(); self._prev_height = 0; return
        if self._prev_height > 0:
            out.write("\r"); out.write(f"\x1b[{self._prev_height}A")
        for idx, ln in enumerate(lines):
            out.write("\x1b[G"); out.write("\x1b[2K"); out.write(ln)
            out.write("\n")
        out.write("\x1b[?7h"); out.flush(); self._prev_height = len(lines)

    def _restore_all(self) -> None:
        try:
            self.disable_mouse()
        except Exception:
            pass
        try:
            self.exit_alt()
        except Exception:
            pass
        _restore_vt_mode_windows()

    def close(self) -> None:
        if self._tty and self._prev_height:
            sys.__stdout__.write("\n"); sys.__stdout__.flush(); self._prev_height = 0
        self._restore_all()
