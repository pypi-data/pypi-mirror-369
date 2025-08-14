from __future__ import annotations
import os, sys, time, select, atexit
from dataclasses import dataclass
from typing import Optional, List, Tuple

@dataclass
class KeyEvent:
    key: str

@dataclass
class MouseEvent:
    x: int
    y: int
    pressed: bool

class Input:
    def __init__(self) -> None:
        self._unix = os.name != "nt"
        if self._unix:
            import termios, tty
            self._termios = termios; self._tty = tty; self._orig = None
        else:
            import msvcrt
            self._msvcrt = msvcrt
        atexit.register(self.exit)

    def enter(self) -> None:
        if self._unix:
            fd = sys.stdin.fileno()
            self._orig = self._termios.tcgetattr(fd)
            self._tty.setcbreak(fd)

    def exit(self) -> None:
        if self._unix and self._orig is not None:
            fd = sys.stdin.fileno()
            self._termios.tcsetattr(fd, self._termios.TCSADRAIN, self._orig)
            self._orig = None

    def _read_unix(self, timeout: float) -> str:
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if not r:
            return ""
        try:
            return os.read(sys.stdin.fileno(), 4096).decode(errors="ignore")
        except Exception:
            return ""

    def _read_win(self, timeout: float) -> str:
        start = time.time()
        buf = []
        while time.time() - start < timeout:
            if self._msvcrt.kbhit():
                ch = self._msvcrt.getwch()
                if ch in ("\x00", "\xe0") and self._msvcrt.kbhit():
                    code = self._msvcrt.getwch()
                    # arrow map
                    m = {"H": "\x1b[A", "P": "\x1b[B", "K": "\x1b[D", "M": "\x1b[C"}
                    buf.append(m.get(code, ""))
                else:
                    buf.append(ch)
                while self._msvcrt.kbhit():
                    buf.append(self._msvcrt.getwch())
                break
            time.sleep(0.01)
        return "".join(buf)

    def read(self, timeout: float = 0.0) -> str:
        return self._read_unix(timeout) if self._unix else self._read_win(timeout)

def parse_events(s: str) -> List[object]:
    out: List[object] = []
    i = 0
    L = len(s)
    while i < L:
        ch = s[i]
        if ch != "\x1b":
            if ch in ("\x7f", "\b"):
                out.append(KeyEvent("backspace"))
            elif ch == "\r" or ch == "\n":
                out.append(KeyEvent("enter"))
            elif ch == "\t":
                out.append(KeyEvent("tab"))
            else:
                out.append(KeyEvent(ch))
            i += 1
            continue
        if i + 1 >= L:
            break
        if s[i:i+3] in ("\x1b[A", "\x1bOA"):
            out.append(KeyEvent("up")); i += 3; continue
        if s[i:i+3] in ("\x1b[B", "\x1bOB"):
            out.append(KeyEvent("down")); i += 3; continue
        if s[i:i+3] in ("\x1b[D", "\x1bOD"):
            out.append(KeyEvent("left")); i += 3; continue
        if s[i:i+3] in ("\x1b[C", "\x1bOC"):
            out.append(KeyEvent("right")); i += 3; continue
        if s[i:i+2] == "\x1b[":
            j = i + 2
            while j < L and s[j] != "M" and s[j] != "m":
                j += 1
            if j < L and s[i+2] == "<":
                try:
                    body = s[i+3:j]
                    parts = body.split(";")
                    btn = int(parts[0])
                    x = int(parts[1])
                    y = int(parts[2])
                    pressed = s[j] == "M"
                    out.append(MouseEvent(x=x, y=y, pressed=pressed))
                    i = j + 1
                    continue
                except Exception:
                    pass
        out.append(KeyEvent("esc"))
        i += 1
    return out
