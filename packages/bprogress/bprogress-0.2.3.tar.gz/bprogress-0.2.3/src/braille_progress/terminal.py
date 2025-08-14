from __future__ import annotations
import os, sys
from typing import List, Optional
from .util import env_true, term_columns, term_rows

def _enable_vt_mode_windows() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes  # type: ignore
        kernel32 = ctypes.windll.kernel32  # type: ignore
        for std in (-11, -12):
            h = kernel32.GetStdHandle(std)  # type: ignore
            mode = ctypes.c_uint32()  # type: ignore
            if kernel32.GetConsoleMode(h, ctypes.byref(mode)):  # type: ignore
                kernel32.SetConsoleMode(h, mode.value | 0x0004 | 0x0001)  # type: ignore
    except Exception:
        pass

class TerminalIO:
    def __init__(self, *, force_tty: Optional[bool] = None, auto_vt: bool = True) -> None:
        if auto_vt: _enable_vt_mode_windows()
        if force_tty is None and env_true("BP_FORCE_TTY"):
            force_tty = True
        self._tty = (force_tty if force_tty is not None else self._isatty())
        self._prev_height = 0
    @staticmethod
    def _isatty() -> bool:
        try:
            if sys.stdout.isatty():
                return True
        except Exception:
            pass
        env = os.environ
        indicators = ("WT_SESSION","PYCHARM_HOSTED","TERM_SESSION_ID","VSCODE_PID","ConEmuANSI","ANSICON")
        return any(k in env for k in indicators)
    @property
    def is_tty(self) -> bool:
        return self._tty
    @property
    def columns(self) -> int:
        return term_columns()
    @property
    def rows(self) -> int:
        return term_rows()
    def write_frame(self, lines: List[str]) -> None:
        if not self._tty:
            sys.stdout.write("\n".join(lines) + "\n")
            sys.stdout.flush()
            self._prev_height = 0
            return
        sys.stdout.write("\x1b[?7l")
        if self._prev_height > 0:
            sys.stdout.write("\r")
            sys.stdout.write(f"\x1b[{self._prev_height}A")
        target = len(lines)
        for ln in lines:
            sys.stdout.write("\x1b[G")
            sys.stdout.write("\x1b[2K")
            sys.stdout.write(ln)
            sys.stdout.write("\n")
        if self._prev_height > target:
            extra = self._prev_height - target
            for _ in range(extra):
                sys.stdout.write("\x1b[2K\n")
            sys.stdout.write(f"\x1b[{extra}A")
        sys.stdout.write("\x1b[?7h")
        sys.stdout.flush()
        self._prev_height = target
    def close(self) -> None:
        if self._tty and self._prev_height:
            sys.stdout.write("\n")
            sys.stdout.flush()
            self._prev_height = 0
