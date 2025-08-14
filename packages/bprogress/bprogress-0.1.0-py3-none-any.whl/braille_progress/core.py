from __future__ import annotations

import os, re, sys, time, shutil
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List, Iterable, Iterator, Callable

def _supports_tty() -> bool:
    try:
        return sys.stdout.isatty()
    except Exception:
        return False

def _enable_vt_mode_windows() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        for std in (-11, -12):  # STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
            handle = kernel32.GetStdHandle(std)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                ENABLE_PROCESSED_OUTPUT = 0x0001
                kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING | ENABLE_PROCESSED_OUTPUT)
    except Exception:
        pass

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def _vis_len(s: str) -> int:
    return len(_ANSI_RE.sub("", s))

def _pad_to(s: str, width: int) -> str:
    return s + (" " * max(0, width - _vis_len(s)))

def _trim_plain_to(s: str, width: int) -> str:
    p = _ANSI_RE.sub("", s)
    return p if len(p) <= width else p[:width]

def _term_columns(default: int = 120) -> int:
    try:
        cols = shutil.get_terminal_size().columns
        return cols if cols and cols > 0 else default
    except Exception:
        return default

def _env_true(name: str) -> bool:
    v = os.environ.get(name)
    return v is not None and v not in ("0", "false", "False", "")

def _color_enabled_default() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return True

def _color(s: str, fg: Optional[str] = None, bold: bool = False, dim: bool = False, enable: bool = True) -> str:
    if not enable:
        return s
    C = {
        "black":30,"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37,
        "bright_black":90,"bright_red":91,"bright_green":92,"bright_yellow":93,"bright_blue":94,
        "bright_magenta":95,"bright_cyan":96,"bright_white":97,
    }
    seq = []
    if bold: seq.append("1")
    if dim:  seq.append("2")
    if fg in C: seq.append(str(C[fg]))
    return f"\x1b[{';'.join(seq)}m{s}\x1b[0m" if seq else s

_DOT_ORDER = (1,2,3,7,4,5,6,8)
_EMPTY = "\u2800"  # ⠀
_FULL  = "\u28FF"  # ⣿

def _cell(dots: int) -> str:
    n = max(0, min(8, int(dots)))
    if n == 0: return _EMPTY
    mask = 0
    for k in range(n):
        d = _DOT_ORDER[k]; mask |= (1 << (d-1))
    return chr(0x2800 + mask)

def _braille_bar(ratio: float, cells: int, fill: str, empty: str, color_on: bool) -> str:
    ratio = max(0.0, min(1.0, float(ratio)))
    total_dots = int(round(ratio * cells * 8))
    full_cells, rem = divmod(total_dots, 8)
    fill_str  = (_FULL * full_cells) + (_cell(rem) if rem else "")
    empty_str = _EMPTY * (cells - full_cells - (1 if rem else 0))
    return _color(fill_str, fg=fill, enable=color_on) + _color(empty_str, fg=empty, dim=True, enable=color_on)

def _pct_block(ratio: float, color_on: bool) -> str:
    pct = f" {int(max(0,min(100,int(round(ratio*100))))):3d}%"
    return _color(pct, fg="bright_green" if ratio >= 1.0 else "green", enable=color_on)

@dataclass
class ProgressTheme:
    name_w:int=22
    bar_cells:int=18
    pct_w:int=5
    right_w:int=16
    mini_cells:int=10
    label_w:int=34
    color:bool=_color_enabled_default()

    colors:Dict[str,str]=field(default_factory=lambda:{
        "queue":"bright_black","opening":"bright_blue","scanning":"bright_blue",
        "validated":"bright_yellow","writing":"green","md_zip":"bright_green",
        "md_written":"bright_green","no_md":"bright_black",
        "done":"bright_green","error":"bright_red"
    })

    def stage_color(self, stage:str, failed:bool, finished:bool)->str:
        if failed: return self.colors["error"]
        if finished: return self.colors["done"]
        return self.colors.get((stage or "").lower(), "bright_white")

    @classmethod
    def auto_fit(cls, columns: Optional[int]=None) -> "ProgressTheme":
        columns = columns or _term_columns()
        base = cls()
        fixed = base.name_w + 3 + (2+base.bar_cells) + base.pct_w + 2 + base.right_w + 3 + (2+base.mini_cells) + 7 + 2
        base.label_w = max(20, columns - fixed)
        return base

@dataclass
class _TaskState:
    name:str
    total:int=0
    done:int=0
    stage:str="queue"
    label:str=""
    finished:bool=False
    failed:bool=False

class TaskHandle:
    def __init__(self, board:"Progress", tid:int):
        self._board = board; self._tid = tid
    def advance(self, n:int=1, *, label:Optional[str]=None, stage:Optional[str]=None):
        self._board.update(self, advance=n, label=label, stage=stage); return self
    def update(self, *, done:Optional[int]=None, total:Optional[int]=None,
               stage:Optional[str]=None, label:Optional[str]=None,
               finished:Optional[bool]=None, failed:Optional[bool]=None):
        self._board.update(self, done=done, total=total, stage=stage, label=label,
                           finished=finished, failed=failed); return self
    def complete(self): self._board.done(self)
    def fail(self, stage:str="error"): self._board.fail(self, stage=stage)

class Progress:
    """
    DX-first facade.

    강제 옵션:
      - force_tty=True  : TTY 감지 무시, 같은 줄 갱신 강제
      - force_color=True: 색상 강제 (NO_COLOR 무시)
    환경변수:
      - BP_FORCE_TTY=1
      - BP_FORCE_COLOR=1
    """
    def __init__(self, theme: Optional[ProgressTheme]=None, *,
                 auto_vt:bool=True, auto_refresh:bool=True, refresh_interval:float=0.05,
                 force_tty:Optional[bool]=None, force_color:Optional[bool]=None):
        self.theme = theme or ProgressTheme.auto_fit()
        if auto_vt: _enable_vt_mode_windows()

        if force_tty is None and _env_true("BP_FORCE_TTY"): force_tty = True
        if force_color is None and _env_true("BP_FORCE_COLOR"): force_color = True

        self._force_tty = force_tty
        self._force_color = force_color

        self._tty = (self._force_tty if self._force_tty is not None else _supports_tty())
        self._color_on = (self.theme.color if self._force_color is None else self._force_color)

        self._tasks: Dict[int, _TaskState] = {}
        self._order: List[int] = []
        self._next_id = 0
        self._prev_height = 0
        self._auto_refresh = auto_refresh
        self._refresh_interval = max(0.01, float(refresh_interval))
        self._last_render = 0.0

    # task API
    def add(self, name:str, total:int=0) -> TaskHandle:
        tid = self._next_id; self._next_id += 1
        self._tasks[tid] = _TaskState(name=name, total=max(0,int(total)))
        self._order.append(tid)
        if self._auto_refresh: self.render(throttle=True)
        return TaskHandle(self, tid)

    def task(self, name:str, total:int=0):
        outer = self
        class _Ctx:
            def __enter__(self_non):
                self_non.h = outer.add(name, total)
                return self_non.h
            def __exit__(self_non, exc_type, exc, tb):
                if exc_type is None: outer.done(self_non.h)
                else: outer.fail(self_non.h, stage="error")
                if outer._auto_refresh: outer.render(throttle=True)
        return _Ctx()

    def update(self, handle_or_id, *, advance:int=0, done:Optional[int]=None, total:Optional[int]=None,
               stage:Optional[str]=None, label:Optional[str]=None,
               finished:Optional[bool]=None, failed:Optional[bool]=None) -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]
        if total is not None: t.total = max(0,int(total))
        if done  is not None: t.done  = max(0,int(done))
        if advance: t.done = max(0, t.done + int(advance))
        if stage is not None: t.stage = stage
        if label is not None: t.label = label
        if finished is not None: t.finished = bool(finished)
        if failed   is not None: t.failed   = bool(failed)
        if t.total and t.done >= t.total and not t.failed:
            t.finished = True
        if self._auto_refresh: self.render(throttle=True)

    def done(self, handle_or_id) -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]; t.finished = True; t.stage = "done"
        if self._auto_refresh: self.render(throttle=True)

    def fail(self, handle_or_id, *, stage:str="error") -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]; t.failed = True; t.finished = True; t.stage = stage
        if self._auto_refresh: self.render(throttle=True)

    def all_finished(self) -> bool:
        return len(self._tasks) > 0 and all(t.finished for t in self._tasks.values())

    def track(self, iterable: Iterable, *, total: Optional[int]=None,
              description: Optional[str]=None, label_from: Optional[Callable[[Any], str]]=None) -> Iterator:
        if total is None:
            try: total = len(iterable)  # type: ignore
            except Exception: total = 0
        h = self.add(description or "progress", total=total or 0)
        try:
            for _, item in enumerate(iterable, 1):
                yield item
                lbl = label_from(item) if label_from else None
                if total: h.advance(1, stage="writing", label=lbl)
                else:     h.update(stage="writing", label=lbl)
            h.complete()
        except Exception:
            h.fail(); raise
        finally:
            if self._auto_refresh: self.render(throttle=False)

    # rendering
    def render(self, *, throttle: bool=False) -> None:
        now = time.time()
        if throttle and (now - self._last_render) < self._refresh_interval:
            return
        lines = [self._render_line(self._tasks[tid]) for tid in self._order]
        if not self._tty:
            sys.stdout.write("\n".join(lines) + "\n"); sys.stdout.flush()
            self._last_render = now; return
        if self._prev_height > 0:
            sys.stdout.write(f"\x1b[{self._prev_height}A")
        for ln in lines:
            sys.stdout.write("\x1b[2K" + ln + "\n")
        sys.stdout.flush()
        self._prev_height = len(lines)
        self._last_render = now

    def close(self) -> None:
        if self._tty and self._prev_height:
            sys.stdout.write("\n"); sys.stdout.flush()
            self._prev_height = 0

    def bind_queue(self, queue, **keys) -> "QueueBinder":
        return QueueBinder(self, queue, **keys)

    def _ratio(self, t:_TaskState) -> float:
        if t.failed or t.finished: return 1.0
        s = (t.stage or "").lower()
        if s in ("opening","scanning"): return 0.05
        if s == "validated": return 0.10
        if s == "writing" and t.total > 0: return 0.10 + 0.80*(t.done/t.total)
        if s in ("md_zip","md_written","no_md"): return 0.95
        return 0.0

    def _render_line(self, t:_TaskState) -> str:
        th = self.theme; col_on = self._color_on
        # name
        name = _pad_to(_color(t.name[:th.name_w], fg="bright_cyan", enable=col_on), th.name_w)
        # main bar + percent
        ratio = self._ratio(t); color = th.stage_color(t.stage, t.failed, t.finished)
        left_br  = _color("[", fg="bright_black", dim=True, enable=col_on)
        right_br = _color("]", fg="bright_black", dim=True, enable=col_on)
        bar_in   = _braille_bar(ratio, th.bar_cells, color, "bright_black", col_on)
        bar_block = _pad_to(left_br + bar_in + right_br, 2 + th.bar_cells)
        pct_block = _pad_to(_pct_block(ratio, col_on), th.pct_w)
        # right status
        if t.failed:      rtxt = "✗ FAIL"
        elif t.finished:  rtxt = "✓ OK"
        else:
            s = (t.stage or "").lower()
            if   s=="writing":    rtxt="writing"
            elif s=="validated":  rtxt=f"validated {t.total}"
            elif s=="scanning":   rtxt="scanning"
            elif s=="md_written": rtxt="md saved"
            elif s=="md_zip":     rtxt="md packed"
            elif s=="no_md":      rtxt="no md"
            else:                 rtxt=s
        rtxt = _trim_plain_to(rtxt, th.right_w)
        right_col = _pad_to(_color(rtxt, fg=color, enable=col_on), th.right_w)
        # mini bar + numbers
        if t.total > 0:
            mini_in = _braille_bar((t.done/t.total), th.mini_cells, "cyan", "bright_black", col_on)
            mini_block = _pad_to(left_br + mini_in + right_br, 2+th.mini_cells)
            d = max(1, len(str(t.total)))
            nums = f" {t.done:>{d}}/{t.total:<{d}}"
            mini_nums = _pad_to(_color(nums, fg="bright_black", enable=col_on), 1 + d + 1 + d)
        else:
            mini_block = " " * (2 + th.mini_cells)
            mini_nums  = " " * 3
        # label
        lbl = t.label or ""
        if len(lbl) > th.label_w:
            lbl = "…" + lbl[-(th.label_w-1):]
        label_col = _pad_to(_color(lbl, fg="bright_black", enable=col_on), th.label_w)
        return f"{name} | {bar_block}{pct_block}  {right_col} | {mini_block}{mini_nums}  {label_col}"

class QueueBinder:
    def __init__(self, progress:Progress, queue, *,
                 id_key="i", stage_key="stage", done_key="case_done",
                 total_key="case_total", label_key="case_label"):
        self.p = progress; self.q = queue
        self.id_key=id_key; self.stage_key=stage_key
        self.done_key=done_key; self.total_key=total_key; self.label_key=label_key
    def drain(self) -> int:
        changed = 0
        while True:
            try:
                m = self.q.get_nowait()
            except Exception:
                break
            tid = m.get(self.id_key)
            if tid is None or tid not in self.p._tasks:
                continue
            stage = m.get(self.stage_key)
            done  = m.get(self.done_key)
            total = m.get(self.total_key)
            label = m.get(self.label_key)
            finished=None; failed=None
            if stage in ("DONE","ERROR"):
                finished=True; failed=(stage=="ERROR")
            self.p.update(tid, done=done, total=total, stage=stage, label=label,
                          finished=finished, failed=failed)
            changed += 1
        return changed

def progress_message(i:int, *, stage:str|None=None, done:int|None=None,
                     total:int|None=None, label:str|None=None,
                     final:bool=False, failed:bool=False) -> Dict[str,Any]:
    m: Dict[str,Any] = {"i": int(i)}
    if stage is not None: m["stage"] = stage
    if done  is not None: m["case_done"]  = int(done)
    if total is not None: m["case_total"] = int(total)
    if label is not None: m["case_label"] = str(label)
    if final: m["stage"] = "ERROR" if failed else "DONE"
    return m
