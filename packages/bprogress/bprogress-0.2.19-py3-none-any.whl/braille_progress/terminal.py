from __future__ import annotations
import os, sys, atexit
from typing import List, Optional
from .util import env_true, term_columns, cut_visible_preserve_ansi

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
        out = sys.__stdout__; out.write("\x1b[?1049h\x1b[?25l"); out.flush(); self._alt = True

    def exit_alt(self) -> None:
        if not self._tty or not self._alt: return
        if self._mouse: self.disable_mouse()
        out = sys.__stdout__; out.write("\x1b[?25h\x1b[?1049l"); out.flush(); self._alt = False

    def enable_mouse(self) -> None:
        if not self._tty or self._mouse: return
        out = sys.__stdout__; out.write("\x1b[?1002h\x1b[?1006h"); out.flush(); self._mouse = True

    def disable_mouse(self) -> None:
        if not self._tty or not self._mouse: return
        out = sys.__stdout__; out.write("\x1b[?1006l\x1b[?1002l"); out.flush(); self._mouse = False

    def write_frame(self, lines: List[str]) -> None:
        out = sys.__stdout__
        cols = term_columns()
        eff = max(1, cols - 1)  # guard column
        safe = [cut_visible_preserve_ansi(ln, eff) for ln in lines]

        out.write("\x1b[?7l")  # autowrap off(임시)

        if not self._tty:
            out.write("\n".join(safe) + "\n")
            out.flush()
            self._prev_height = 0
            return

        if self._prev_height > 0:
            out.write("\r")
            out.write(f"\x1b[{self._prev_height}A")

        pad = max(0, self._prev_height - len(safe))
        if pad:
            safe = safe + [(" " * eff)] * pad

        phys_now = len(safe)  # 이번에 실제로 그릴 "물리" 줄 수
        logical_now = len(lines)  # 논리 줄 수(헤더+바디+푸터)

        for i, ln in enumerate(safe):
            out.write("\x1b[G")  # col 1
            out.write("\x1b[2K")  # line clear
            out.write(ln)
            if i < phys_now - 1:
                out.write("\n")

        if pad:
            out.write(f"\x1b[{pad}A")

        # 현재 커서 아래 전부 지우기(잔상 제거)
        out.write("\x1b[J")

        out.write("\x1b[?7h")  # autowrap on(복구)
        out.flush()

        self._prev_height = phys_now

    def _restore_all(self) -> None:
        try: self.disable_mouse()
        except Exception: pass
        try: self.exit_alt()
        except Exception: pass
        _restore_vt_mode_windows()

    def close(self) -> None:
        if self._tty and self._prev_height:
            sys.__stdout__.write("\n"); sys.__stdout__.flush(); self._prev_height = 0
        self._restore_all()
