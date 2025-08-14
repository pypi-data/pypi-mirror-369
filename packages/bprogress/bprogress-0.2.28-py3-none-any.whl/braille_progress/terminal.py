# terminal.py
from __future__ import annotations
import os, sys, atexit
from typing import List, Optional
from .util import env_true, term_columns, cut_visible_preserve_ansi

_ORIG_WIN = {"in": None, "out": None, "err": None}

def _enable_vt_mode_windows() -> None:
    if os.name != "nt":
        return
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
    if os.name != "nt":
        return
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
            h = k.GetStdHandle(-10)
            k.FlushConsoleInputBuffer(h)
        else:
            import termios
            termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
    except Exception:
        pass

class TerminalIO:
    def __init__(self, *, force_tty: Optional[bool] = None, auto_vt: bool = True, panel_mode: str = "overlay") -> None:
        if auto_vt: _enable_vt_mode_windows()
        if force_tty is None and env_true("BP_FORCE_TTY"): force_tty = True
        self._tty = (force_tty if force_tty is not None else self._isatty())
        self._prev_height = 0
        self._alt = False
        self._mouse = False
        self._panel_opened = False
        self._reserved_height = 0
        self._reserve_hint = 0
        self._reserve_block = 8
        self._panel_mode = panel_mode  # "overlay"|"reserve"|"overlay_space"
        atexit.register(self._restore_all)

    def set_panel_mode(self, mode: str) -> None:
        m = (mode or "").lower()
        self._panel_mode = "overlay_space" if m == "overlay_space" else ("reserve" if m == "reserve" else "overlay")

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

    def set_reserve_hint(self, n: int) -> None:
        self._reserve_hint = max(0, int(n))

    def set_reserve_block(self, n: int) -> None:
        self._reserve_block = max(1, int(n))

    def enter_alt(self) -> None:
        if not self._tty or self._alt: return
        sys.__stdout__.write("\x1b[?1049h\x1b[?25l"); sys.__stdout__.flush(); self._alt = True

    def exit_alt(self) -> None:
        if not self._tty or not self._alt: return
        if self._mouse: self.disable_mouse()
        sys.__stdout__.write("\x1b[?25h\x1b[?1049l"); sys.__stdout__.flush(); self._alt = False

    def enable_mouse(self) -> None:
        if not self._tty or self._mouse: return
        sys.__stdout__.write("\x1b[?1002h\x1b[?1006h"); sys.__stdout__.flush(); self._mouse = True

    def disable_mouse(self) -> None:
        out = sys.__stdout__
        out.write("\x1b[?1006l\x1b[?1002l\x1b[?1000l\x1b[?1015l\x1b[?1004l\x1b[?2004l")
        out.flush()
        self._mouse = False

    def write_frame(self, lines: List[str]) -> None:
        cols = term_columns()
        eff = max(1, cols - 1)  # guard column
        safe = [cut_visible_preserve_ansi(ln, eff) for ln in lines]
        if self._panel_mode == "reserve":
            self._render_reserve(safe, eff)
        elif self._panel_mode == "overlay_space":
            self._render_overlay_space(safe)
        else:
            self._render_overlay(safe)

    def _render_overlay(self, safe: List[str]) -> None:
        out = sys.__stdout__
        phys_now = len(safe)
        out.write("\x1b[?7l")  # autowrap off
        if not self._tty:
            out.write("\n".join(safe) + "\n");
            out.flush();
            self._prev_height = 0;
            return
        if self._prev_height > 0:
            if self._prev_height > 1:
                out.write(f"\x1b[{self._prev_height - 1}F")
            else:
                out.write("\r")
        for i, ln in enumerate(safe):
            out.write("\x1b[2K");
            out.write(ln)
            if i < phys_now - 1: out.write("\x1b[E")
        extra = max(0, self._prev_height - phys_now)
        if extra:
            for _ in range(extra):
                out.write("\x1b[E");
                out.write("\x1b[2K")
            out.write(f"\x1b[{extra}F")
            if phys_now > 1: out.write(f"\x1b[{phys_now - 1}E")
        out.write("\x1b[?7h");
        out.flush()
        self._prev_height = phys_now  # ← 오버레이 높이만 기억

    def _render_overlay_space(self, safe: List[str]) -> None:
        out = sys.__stdout__
        phys_need = len(safe)
        out.write("\x1b[?7l")  # autowrap off

        if not self._tty:
            out.write("\n".join(safe) + "\n");
            out.flush()
            self._prev_height = 0;
            return

        rows = term_rows() or 40

        # 1) 처음이거나 더 많은 줄이 필요하면, 화면을 위로 스크롤해 아래 공간 확보
        if not self._panel_opened:
            grow = phys_need
        else:
            grow = max(0, phys_need - self._prev_height)

        if grow > 0:
            out.write("\x1b7")  # DECSC save
            out.write("\x1b[r")  # 전체 스크롤 영역
            out.write(f"\x1b[{rows};1H")  # 마지막 줄로
            out.write(f"\x1b[{grow}S")  # CSI S: 위로 grow줄 스크롤(아래 grow줄 비워짐)
            out.write("\x1b8")  # DECRC restore
            self._panel_opened = True
            self._prev_height += grow

        # 2) 패널 시작 위치로 이동: (rows - prev_height + 1, col 1)
        start_row = max(1, (term_rows() or rows) - self._prev_height + 1)
        out.write(f"\x1b[{start_row};1H")

        # 3) 이번 프레임 그리기(남는 줄은 깨끗이 지움). 개행 없이 커서 이동만 사용
        for i in range(phys_need):
            out.write("\x1b[2K");
            out.write(safe[i])
            if i < phys_need - 1: out.write("\x1b[E")  # CNL next line

        extra = max(0, self._prev_height - phys_need)
        if extra:
            for _ in range(extra):
                out.write("\x1b[E");
                out.write("\x1b[2K")
            # 커서를 패널 맨 끝 줄에 놔둔다(다음 프레임 시작 시 기준 동일)

        out.write("\x1b[?7h");
        out.flush()
        # prev_height는 '확보된 패널 높이'(= 아래 전용 영역 크기)로 유지
        self._prev_height = max(self._prev_height, phys_need)

    def _render_reserve(self, safe: List[str], eff: int) -> None:
        out = sys.__stdout__
        need = len(safe)
        out.write("\x1b[?7l")
        if not self._tty:
            out.write("\n".join(safe) + "\n");
            out.flush()
            self._prev_height = 0;
            self._panel_opened = False;
            self._reserved_height = 0;
            return
        if not self._panel_opened:
            initial = max(need, self._reserve_hint)
            if initial > 0:
                out.write("\n" * initial)
                self._reserved_height = initial;
                self._panel_opened = True
        else:
            if need > self._reserved_height:
                grow_to = max(need, self._reserved_height + self._reserve_block)
                out.write("\n" * (grow_to - self._reserved_height))
                self._reserved_height = grow_to
        if self._reserved_height > 0:
            out.write("\r")
            if self._reserved_height > 1: out.write(f"\x1b[{self._reserved_height - 1}F")
        phys_now = min(need, self._reserved_height)
        for i in range(phys_now):
            out.write("\x1b[2K");
            out.write(safe[i])
            if i < phys_now - 1: out.write("\x1b[E")
        extra = max(0, self._reserved_height - phys_now)
        if extra:
            for _ in range(extra):
                out.write("\x1b[E");
                out.write("\x1b[2K")
            out.write(f"\x1b[{extra}F")
            if phys_now > 1: out.write(f"\x1b[{phys_now - 1}E")
        out.write("\x1b[?7h");
        out.flush()
        self._prev_height = self._reserved_height

    def _restore_all(self) -> None:
        try: self.disable_mouse()
        except Exception: pass
        try:
            sys.__stdout__.write("\x1b[?7h\x1b[?25h"); sys.__stdout__.flush()
        except Exception:
            pass
        try: _flush_input_buffer()
        except Exception: pass
        try: self.exit_alt()
        except Exception: pass
        _restore_vt_mode_windows()

    def close(self) -> None:
        if self._tty and self._reserved_height:
            sys.__stdout__.write("\n"); sys.__stdout__.flush()
        self._prev_height = 0
        self._panel_opened = False
        self._reserved_height = 0
        self._restore_all()
