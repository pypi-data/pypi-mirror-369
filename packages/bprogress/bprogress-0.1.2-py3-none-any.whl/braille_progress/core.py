from __future__ import annotations
import os, re, sys, time, shutil
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List, Iterable, Iterator, Callable, Protocol, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# Utilities: ANSI, width, env
# ─────────────────────────────────────────────────────────────────────────────

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)

try:
    from wcwidth import wcswidth as _wcswidth, wcwidth as _wcwidth
    _HAS_WCWIDTH = True
except Exception:  # pragma: no cover
    _HAS_WCWIDTH = False

def _visible_width(s: str) -> int:
    """Visible width considering wide chars; ANSI-stripped."""
    p = _strip_ansi(s)
    if _HAS_WCWIDTH:
        return max(0, _wcswidth(p))
    return len(p)

def _pad_to(s: str, width: int) -> str:
    pad = max(0, width - _visible_width(s))
    return s + (" " * pad)

def _trim_plain_to(s: str, width: int) -> str:
    """Trim to width using plain(ANSI-removed) text; keep leftmost characters."""
    p = _strip_ansi(s)
    if _HAS_WCWIDTH:
        acc = []; w = 0
        for ch in p:
            cw = _wcwidth(ch) or 0
            if w + cw > width: break
            acc.append(ch); w += cw
        return "".join(acc) + (" " * max(0, width - w))
    return (p[:width] if len(p) > width else p + " " * (width - len(p)))

def _env_true(name: str) -> bool:
    v = os.environ.get(name)
    return v is not None and v not in ("0", "false", "False", "")

def _term_columns(default: int = 120) -> int:
    try:
        cols = shutil.get_terminal_size().columns
        return cols if cols and cols > 0 else default
    except Exception:
        return default

def _color_enabled_default() -> bool:
    return not bool(os.environ.get("NO_COLOR"))

# ─────────────────────────────────────────────────────────────────────────────
# Terminal I/O
# ─────────────────────────────────────────────────────────────────────────────

def _enable_vt_mode_windows() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        for std in (-11, -12):  # STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
            h = kernel32.GetStdHandle(std)
            mode = ctypes.c_uint32()
            if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                kernel32.SetConsoleMode(h, mode.value | 0x0004 | 0x0001)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING | ENABLE_PROCESSED_OUTPUT
    except Exception:
        pass

class TerminalIO:
    """단일 책임: 터미널 특성 확인 및 커서 제어/출력."""
    def __init__(self, *, force_tty: Optional[bool] = None, auto_vt: bool = True) -> None:
        if auto_vt: _enable_vt_mode_windows()
        if force_tty is None and _env_true("BP_FORCE_TTY"):
            force_tty = True
        self._tty = force_tty if force_tty is not None else self._isatty()
        self._prev_height = 0

    @staticmethod
    def _isatty() -> bool:
        try:
            return sys.stdout.isatty()
        except Exception:
            return False

    @property
    def is_tty(self) -> bool:
        return self._tty

    @property
    def columns(self) -> int:
        return _term_columns()

    def write_frame(self, lines: List[str]) -> None:
        """TTY 모드: 기존 프레임 위에 갱신. Non-TTY: 스냅샷 출력."""
        if not self._tty:
            sys.stdout.write("\n".join(lines) + "\n")
            sys.stdout.flush()
            self._prev_height = 0
            return

        if self._prev_height > 0:
            # 맨 앞으로 이동 후 이전 높이만큼 위로
            sys.stdout.write("\r")
            sys.stdout.write(f"\x1b[{self._prev_height}A")

        # 각 줄을 지우고 다시 그림
        for ln in lines:
            sys.stdout.write("\x1b[G")   # 맨 앞으로
            sys.stdout.write("\x1b[2K")  # 라인 지우기
            sys.stdout.write(ln)
            sys.stdout.write("\n")

        sys.stdout.flush()
        self._prev_height = len(lines)

    def close(self) -> None:
        if self._tty and self._prev_height:
            sys.stdout.write("\n")
            sys.stdout.flush()
            self._prev_height = 0

# ─────────────────────────────────────────────────────────────────────────────
# ANSI styling (colors, dim/bold)
# ─────────────────────────────────────────────────────────────────────────────

_COLOR_TABLE: Dict[str, int] = {
    "black":30,"red":31,"green":32,"yellow":33,"blue":34,"magenta":35,"cyan":36,"white":37,
    "bright_black":90,"bright_red":91,"bright_green":92,"bright_yellow":93,"bright_blue":94,
    "bright_magenta":95,"bright_cyan":96,"bright_white":97,
}

class AnsiStyler:
    """단일 책임: 색상/스타일 적용 및 off 스위치."""
    def __init__(self, *, enabled: Optional[bool] = None) -> None:
        if enabled is None and _env_true("BP_FORCE_COLOR"):
            enabled = True
        self.enabled = _color_enabled_default() if enabled is None else bool(enabled)

    def color(self, s: str, *, fg: Optional[str] = None, bold: bool = False, dim: bool = False) -> str:
        if not self.enabled:
            return s
        seq: List[str] = []
        if bold: seq.append("1")
        if dim:  seq.append("2")
        if fg in _COLOR_TABLE: seq.append(str(_COLOR_TABLE[fg]))
        return f"\x1b[{';'.join(seq)}m{s}\x1b[0m" if seq else s

# ─────────────────────────────────────────────────────────────────────────────
# Braille bar renderer
# ─────────────────────────────────────────────────────────────────────────────

_DOT_ORDER = (1,2,3,7,4,5,6,8)
_EMPTY = "\u2800"
_FULL  = "\u28FF"

def _cell(dots: int) -> str:
    n = max(0, min(8, int(dots)))
    if n == 0: return _EMPTY
    m = 0
    for k in range(n):
        d = _DOT_ORDER[k]
        m |= (1 << (d - 1))
    return chr(0x2800 + m)

class BrailleRenderer:
    """단일 책임: 비율→브라유 바/퍼센트 문자열 생성."""
    def __init__(self, styler: AnsiStyler) -> None:
        self.S = styler

    def bar(self, ratio: float, *, cells: int, fill_color: str, empty_color: str) -> str:
        ratio = max(0.0, min(1.0, float(ratio)))
        total = int(round(ratio * cells * 8))
        full, rem = divmod(total, 8)
        fs  = (_FULL * full) + (_cell(rem) if rem else "")
        es  = _EMPTY * (cells - full - (1 if rem else 0))
        return self.S.color(fs, fg=fill_color) + self.S.color(es, fg=empty_color, dim=True)

    def pct_text(self, ratio: float) -> str:
        pct = f" {int(max(0,min(100,int(round(ratio*100))))):3d}%"
        return self.S.color(pct, fg="bright_green" if ratio >= 1.0 else "green")

# ─────────────────────────────────────────────────────────────────────────────
# Theme
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ProgressTheme:
    # 고정 폭들
    name_w:int=22; bar_cells:int=18; pct_w:int=5; right_w:int=16; mini_cells:int=10; label_w:int=34
    color:bool=_color_enabled_default()
    colors:Dict[str,str]=field(default_factory=lambda:{
        "queue":"bright_black","opening":"bright_blue","scanning":"bright_blue",
        "validated":"bright_yellow","writing":"green","md_zip":"bright_green",
        "md_written":"bright_green","no_md":"bright_black","done":"bright_green","error":"bright_red"
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

# ─────────────────────────────────────────────────────────────────────────────
# Ratio Strategy (단일 책임: Task → ratio 계산 규칙)
# ─────────────────────────────────────────────────────────────────────────────

class RatioStrategy(Protocol):
    def ratio(self, t: "TaskState") -> float: ...

class DefaultRatio(RatioStrategy):
    def ratio(self, t: "TaskState") -> float:
        if t.failed or t.finished: return 1.0
        s = (t.stage or "").lower()
        if s in ("opening","scanning"): return 0.05
        if s == "validated": return 0.10
        if s == "writing" and t.total > 0: return 0.10 + 0.80*(t.done/t.total)
        if s in ("md_zip","md_written","no_md"): return 0.95
        return 0.0

# ─────────────────────────────────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TaskState:
    name:str
    total:int=0
    done:int=0
    stage:str="queue"
    label:str=""
    finished:bool=False
    failed:bool=False

class TaskHandle:
    """사용자 API 핸들(상태 캡슐화는 Progress가 담당)."""
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

# ─────────────────────────────────────────────────────────────────────────────
# Line renderer (단일 책임: TaskState -> 문자열 한 줄)
# ─────────────────────────────────────────────────────────────────────────────

class LineRenderer:
    def __init__(self, theme: ProgressTheme, styler: AnsiStyler, bars: BrailleRenderer, ratio: RatioStrategy) -> None:
        self.T = theme; self.S = styler; self.B = bars; self.R = ratio
        self._left_br  = self.S.color("[", fg="bright_black", dim=True)
        self._right_br = self.S.color("]", fg="bright_black", dim=True)

    def _status_text(self, t: TaskState) -> Tuple[str, str]:
        color = self.T.stage_color(t.stage, t.failed, t.finished)
        if t.failed:     return "✗ FAIL", color
        if t.finished:   return "✓ OK", color
        s = (t.stage or "").lower()
        rtxt = {
            "writing":"writing",
            "validated": f"validated {t.total}",
            "scanning":"scanning",
            "md_written":"md saved",
            "md_zip":"md packed",
            "no_md":"no md"
        }.get(s, s)
        return rtxt, color

    def render_line(self, t: TaskState) -> str:
        th = self.T
        name = _pad_to(self.S.color(t.name[:th.name_w], fg="bright_cyan"), th.name_w)

        ratio = self.R.ratio(t)
        status_text, color = self._status_text(t)

        bar_in   = self.B.bar(ratio, cells=th.bar_cells, fill_color=color, empty_color="bright_black")
        bar_block = _pad_to(self._left_br + bar_in + self._right_br, 2 + th.bar_cells)
        pct_block = _pad_to(self.B.pct_text(ratio), th.pct_w)

        rtxt = _trim_plain_to(status_text, th.right_w)
        right_col = _pad_to(self.S.color(rtxt, fg=color), th.right_w)

        if t.total > 0:
            mini_in = self.B.bar((t.done/t.total), cells=th.mini_cells, fill_color="cyan", empty_color="bright_black")
            mini_block = _pad_to(self._left_br + mini_in + self._right_br, 2+th.mini_cells)
            d = max(1, len(str(t.total)))
            nums = f" {t.done:>{d}}/{t.total:<{d}}"
            mini_nums = _pad_to(self.S.color(nums, fg="bright_black"), 1 + d + 1 + d)
        else:
            mini_block = " " * (2 + th.mini_cells)
            mini_nums = " " * 3

        lbl = t.label or ""
        if _visible_width(lbl) > th.label_w:
            plain = _strip_ansi(lbl)
            if _HAS_WCWIDTH:
                acc = []; w = 0
                for ch in reversed(plain):
                    cw = _wcwidth(ch) or 0
                    if w + cw > th.label_w - 1: break
                    acc.append(ch); w += cw
                lbl = "…" + "".join(reversed(acc))
            else:
                lbl = "…" + plain[-(th.label_w-1):]
        label_col = _pad_to(self.S.color(lbl, fg="bright_black"), th.label_w)

        return f"{name} | {bar_block}{pct_block}  {right_col} | {mini_block}{mini_nums}  {label_col}"

# ─────────────────────────────────────────────────────────────────────────────
# Progress (오케스트레이션: 상태 관리 + 렌더 호출 + 스로틀)
# ─────────────────────────────────────────────────────────────────────────────

class Progress:
    def __init__(self, theme: Optional[ProgressTheme]=None, *,
                 auto_vt:bool=True, auto_refresh:bool=True, refresh_interval:float=0.05,
                 force_tty:Optional[bool]=None, force_color:Optional[bool]=None,
                 ratio_strategy: Optional[RatioStrategy]=None) -> None:

        # 단일 책임들을 조립
        self.term = TerminalIO(force_tty=force_tty, auto_vt=auto_vt)
        self.theme = theme or ProgressTheme.auto_fit(self.term.columns)
        self.styler = AnsiStyler(enabled=(self.theme.color if force_color is None else force_color))
        self.bars = BrailleRenderer(self.styler)
        self.ratio = ratio_strategy or DefaultRatio()
        self.renderer = LineRenderer(self.theme, self.styler, self.bars, self.ratio)

        # 상태
        self._tasks: Dict[int, TaskState] = {}
        self._order: List[int] = []
        self._next_id = 0

        # 렌더링 정책
        self._auto_refresh = auto_refresh
        self._refresh_interval = max(0.01, float(refresh_interval))
        self._last_render = 0.0

    # ── 공개 API ────────────────────────────────────────────────────────────

    def add(self, name:str, total:int=0) -> TaskHandle:
        tid = self._next_id; self._next_id += 1
        self._tasks[tid] = TaskState(name=name, total=max(0,int(total)))
        self._order.append(tid)
        if self._auto_refresh: self.render(throttle=True)
        return TaskHandle(self, tid)

    def task(self, name:str, total:int=0):
        outer = self
        class _Ctx:
            def __enter__(self_non):
                self_non.h = outer.add(name, total); return self_non.h
            def __exit__(self_non, et, ev, tb):
                if et is None: outer.done(self_non.h)
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
            if t.stage not in ("error", "ERROR"):
                t.stage = "done"
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
            for item in iterable:
                yield item
                lbl = label_from(item) if label_from else None
                if total: h.advance(1, stage="writing", label=lbl)
                else:     h.update(stage="writing", label=lbl)
            h.complete()
        except Exception:
            h.fail(); raise
        finally:
            if self._auto_refresh: self.render(throttle=False)

    def render(self, *, throttle: bool=False) -> None:
        now = time.time()
        if throttle and (now - self._last_render) < self._refresh_interval:
            return
        # 테마 label_w를 동적으로 갱신(터미널 폭이 바뀐 경우 대응)
        cols_now = self.term.columns
        if cols_now:  # 재계산
            fixed = self.theme.name_w + 3 + (2+self.theme.bar_cells) + self.theme.pct_w + 2 + self.theme.right_w + 3 + (2+self.theme.mini_cells) + 7 + 2
            self.theme.label_w = max(20, cols_now - fixed)

        lines = [self.renderer.render_line(self._tasks[tid]) for tid in self._order]
        self.term.write_frame(lines)
        self._last_render = now

    def close(self) -> None:
        self.term.close()

    def bind_queue(self, queue, **keys) -> "QueueBinder":
        return QueueBinder(self, queue, **keys)

# ─────────────────────────────────────────────────────────────────────────────
# Queue binder (메시지 ↔ 상태 갱신 변환)
# ─────────────────────────────────────────────────────────────────────────────

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
            try: m = self.q.get_nowait()
            except Exception: break
            tid = m.get(self.id_key)
            if tid is None or tid not in self.p._tasks: continue
            stage = m.get(self.stage_key); done  = m.get(self.done_key)
            total = m.get(self.total_key); label = m.get(self.label_key)
            finished=None; failed=None
            if stage in ("DONE","ERROR"):
                finished=True; failed=(stage=="ERROR")
            self.p.update(tid, done=done, total=total, stage=stage, label=label,
                          finished=finished, failed=failed)
            changed += 1
        return changed

# ─────────────────────────────────────────────────────────────────────────────
# Worker message format (기존 API 유지)
# ─────────────────────────────────────────────────────────────────────────────

def progress_message(i:int, *, stage:str|None=None, done:int|None=None,
                     total:int|None=None, label:str|None=None,
                     final:bool=False, failed:bool=False) -> Dict[str,Any]:
    """멀티프로세스 워커에서 쓰는 표준 메시지 포맷."""
    m: Dict[str,Any] = {"i": int(i)}
    if stage is not None: m["stage"] = stage
    if done  is not None: m["case_done"]  = int(done)
    if total is not None: m["case_total"] = int(total)
    if label is not None: m["case_label"] = str(label)
    if final: m["stage"] = "ERROR" if failed else "DONE"
    return m
