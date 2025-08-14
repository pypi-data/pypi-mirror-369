from __future__ import annotations
import os, sys
from typing import List, Optional
from .util import env_true, term_columns

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
        ENABLE_QUICK_EDIT_MODE = 0x0040  # off

        for std in (STD_OUTPUT_HANDLE, STD_ERROR_HANDLE):
            h = kernel32.GetStdHandle(std)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                kernel32.SetConsoleMode(h, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING | ENABLE_PROCESSED_OUTPUT)

        hin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
        imode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(hin, ctypes.byref(imode)):
            new = (imode.value | ENABLE_VIRTUAL_TERMINAL_INPUT | ENABLE_EXTENDED_FLAGS) & ~ENABLE_QUICK_EDIT_MODE
            kernel32.SetConsoleMode(hin, new)
    except Exception:
        pass

class TerminalIO:
    def __init__(self, *, force_tty: Optional[bool] = None, auto_vt: bool = True) -> None:
        if auto_vt:
            _enable_vt_mode_windows()
        if force_tty is None and env_true("BP_FORCE_TTY"):
            force_tty = True
        self._tty = force_tty if force_tty is not None else self._isatty()
        self._prev_height = 0
        self._alt = False
        self._mouse = False

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

    def enter_alt(self) -> None:
        if not self._tty or self._alt:
            return
        sys.stdout.write("\x1b[?1049h\x1b[?25l")
        sys.stdout.flush()
        self._alt = True

    def exit_alt(self) -> None:
        if not self._tty or not self._alt:
            return
        if self._mouse:
            self.disable_mouse()
        sys.stdout.write("\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()
        self._alt = False

    def enable_mouse(self) -> None:
        if not self._tty or self._mouse:
            return
        sys.stdout.write("\x1b[?1002h\x1b[?1006h")
        sys.stdout.flush()
        self._mouse = True

    def disable_mouse(self) -> None:
        if not self._tty or not self._mouse:
            return
        sys.stdout.write("\x1b[?1006l\x1b[?1002l")
        sys.stdout.flush()
        self._mouse = False

    def write_frame(self, lines: List[str]) -> None:
        out = sys.__stdout__
        out.write("\x1b[?7l")
        if not self._tty:
            out.write("\n".join(lines) + "\n");
            out.flush();
            self._prev_height = 0;
            return
        if self._prev_height > 0:
            out.write("\r");
            out.write(f"\x1b[{self._prev_height}A")
        for ln in lines:
            out.write("\x1b[G");
            out.write("\x1b[2K");
            out.write(ln);
            out.write("\n")
        out.write("\x1b[?7h");
        out.flush();
        self._prev_height = len(lines)

    def close(self) -> None:
        if self._tty and self._prev_height:
            sys.stdout.write("\n")
            sys.stdout.flush()
            self._prev_height = 0
        if self._alt:
            self.exit_alt()
