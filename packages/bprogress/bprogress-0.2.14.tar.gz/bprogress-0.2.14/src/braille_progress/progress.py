from __future__ import annotations
import sys, time, signal, atexit
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Union, Sequence
from .terminal import TerminalIO
from .theme import ProgressTheme
from .style import AnsiStyler
from .braille import BrailleRenderer
from .ratio import RatioStrategy, DefaultRatio
from .model import TaskHandle, TaskState
from .layout import Layout, default_layout, RenderContext, VLayout, Row
from .stats import TaskRuntime, fmt_hms
from .util import term_rows, pad_to, visible_width, cut_visible_preserve_ansi
from .widgets import DetailRenderer, ConsoleRenderer
from .ui import Input, parse_events, KeyEvent, MouseEvent

def _to_vlayout(x: Optional[Union[VLayout, Layout, Sequence[Row]]]) -> Optional[VLayout]:
    if x is None:
        return None
    if isinstance(x, VLayout):
        return x
    if isinstance(x, Layout):
        return VLayout([x])
    return VLayout(x)  # type: ignore

class Progress:
    def __init__(
        self,
        theme: Optional[ProgressTheme] = None,
        *,
        auto_vt: bool = True,
        auto_refresh: bool = True,
        refresh_interval: float = 0.05,
        force_tty: Optional[bool] = None,
        force_color: Optional[bool] = None,
        ratio_strategy: Optional[RatioStrategy] = None,
        layout: Optional[Layout] = None,
        header: Optional[Union[VLayout, Layout, Sequence[Row]]] = None,
        footer: Optional[Union[VLayout, Layout, Sequence[Row]]] = None,
        min_body_rows: int = 0,
        split_ratio: float = 0.55,
        show_vsep: bool = True,
        right_renderer: Optional[DetailRenderer] = None,
    ) -> None:
        self.term = TerminalIO(force_tty=force_tty, auto_vt=auto_vt)
        self.theme = theme or ProgressTheme.auto_fit(self.term.columns)
        self.styler = AnsiStyler(enabled=(self.theme.color if force_color is None else force_color))
        self.bars = BrailleRenderer(self.styler)
        self.ratio = ratio_strategy or DefaultRatio()
        self.layout = layout or default_layout(self.theme)
        self.header_layout = _to_vlayout(header)
        self.footer_layout = _to_vlayout(footer)
        self.min_body_rows = max(0, int(min_body_rows))
        self.split_ratio = max(0.1, min(0.9, float(split_ratio)))
        self.show_vsep = bool(show_vsep)
        self.right_renderer = right_renderer or ConsoleRenderer()
        self._tasks: Dict[int, TaskState] = {}
        self._order: List[int] = []
        self._next_id = 0
        self._rt: Dict[int, TaskRuntime] = {}
        self._logs: Dict[int, List[str]] = {}
        self._sel_idx = 0
        self._scroll_top = 0
        self._auto_refresh = auto_refresh
        self._refresh_interval = max(0.01, float(refresh_interval))
        self._last_render = 0.0
        self._interactive = False
        self._input = Input()
        self._stop = False
        if handle_signals:
            self._orig_handlers: Dict[int, Any] = {}
            for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None),
                        getattr(signal, "SIGHUP", None)):
                if sig is None: continue
                try:
                    self._orig_handlers[sig] = signal.getsignal(sig)
                    signal.signal(sig, self._on_signal)
                except Exception:
                    pass
        atexit.register(self._atexit_cleanup)

    def _on_signal(self, signum, frame):
        self._stop = True
        try:
            self.term.close()
        finally:
            h = self._orig_handlers.get(signum)
            if callable(h):
                try:
                    h(signum, frame)
                except Exception:
                    pass

    def _atexit_cleanup(self) -> None:
        try:
            self.term.close()
        except Exception:
            pass

    def add(self, name: str, total: int = 0) -> TaskHandle:
        tid = self._next_id
        self._next_id += 1
        self._tasks[tid] = TaskState(name=name, total=max(0, int(total)))
        self._order.append(tid)
        rt = TaskRuntime(); rt.on_create()
        self._rt[tid] = rt
        self._logs[tid] = []
        if self._auto_refresh:
            self.render(throttle=True)
        return TaskHandle(self, tid)

    def task(self, name: str, total: int = 0):
        outer = self
        class _Ctx:
            def __enter__(self_non):
                self_non.h = outer.add(name, total); return self_non.h
            def __exit__(self_non, et, ev, tb):
                if et is None: outer.done(self_non.h)
                else: outer.fail(self_non.h, stage="error", error=et)
                if outer._auto_refresh: outer.render(throttle=True)
        return _Ctx()

    def update(self, handle_or_id, *, advance: int = 0, done: Optional[int] = None, total: Optional[int] = None,
               stage: Optional[str] = None, label: Optional[str] = None,
               finished: Optional[bool] = None, failed: Optional[bool] = None) -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]
        if total is not None: t.total = max(0, int(total))
        if done  is not None: t.done  = max(0, int(done))
        if advance: t.done = max(0, t.done + int(advance))
        if stage is not None: t.stage = stage
        if label is not None: t.label = label
        if finished is not None: t.finished = bool(finished)
        if failed   is not None: t.failed   = bool(failed)
        if t.total and t.done >= t.total and not t.failed:
            t.finished = True
            if t.stage not in ("error", "ERROR"):
                t.stage = "done"
        self._rt[tid].on_progress(t.done)
        if self._auto_refresh: self.render(throttle=True)

    def done(self, handle_or_id) -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]; t.finished = True; t.stage = "done"
        self._rt[tid].on_finish(False)
        if self._auto_refresh: self.render(throttle=True)

    def fail(self, handle_or_id, *, stage: str = "error", error: Optional[Any] = None, error_tb: bool = True) -> None:
        from .errorfmt import format_error
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]; t.failed = True; t.finished = True; t.stage = stage
        if error is not None:
            t.error = format_error(error, with_tb=error_tb, pretty=True, width=self.term.columns-2)
        elif not t.error and t.label:
            t.error = t.label
        self._rt[tid].on_finish(True)
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
        except Exception as e:
            h.fail(error=e)
            raise
        finally:
            if self._auto_refresh: self.render(throttle=False)

    def log(self, handle_or_id, msg: str) -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        buf = self._logs.get(tid)
        if buf is None:
            buf = []; self._logs[tid] = buf
        ts = time.strftime("%H:%M:%S")
        buf.append(f"{ts} {msg}")
        if len(buf) > 2000:
            del buf[: len(buf)-2000]
        if self._auto_refresh and not self._interactive:
            self.render(throttle=True)

    def set_right_renderer(self, renderer: DetailRenderer) -> None:
        self.right_renderer = renderer

    def _visible_bounds(self, body_rows: int) -> None:
        n = len(self._order)
        if n == 0:
            self._sel_idx = 0
            self._scroll_top = 0
            return
        self._sel_idx = max(0, min(self._sel_idx, n-1))
        if self._sel_idx < self._scroll_top:
            self._scroll_top = self._sel_idx
        if self._sel_idx >= self._scroll_top + body_rows:
            self._scroll_top = self._sel_idx - body_rows + 1
        self._scroll_top = max(0, min(self._scroll_top, max(0, n - body_rows)))

    def _apply_select_style(self, s: str, width: int) -> str:
        return "\x1b[7m" + s + "\x1b[0m"

    def render(self, *, throttle: bool=False) -> None:
        now = time.time()
        if throttle and (now - self._last_render) < self._refresh_interval: return
        cols = self.term.columns or 120
        rows = term_rows() or 40
        guard = 1
        cols_eff = max(1, cols - guard)
        ctx_full = RenderContext(self.theme, self.styler, self.bars, self.ratio, cols_eff)
        header_lines = self.header_layout.render(ctx_full) if self.header_layout else []
        footer_lines = self.footer_layout.render(ctx_full) if self.footer_layout else []
        head_h, foot_h = len(header_lines), len(footer_lines)
        body_rows = max(self.min_body_rows, max(1, rows - head_h - foot_h))
        left_w = max(10, int(cols_eff * self.split_ratio)) - (1 if self.show_vsep else 0)
        right_w = max(0, cols_eff - left_w - (1 if self.show_vsep else 0))
        ctx_left = RenderContext(self.theme, self.styler, self.bars, self.ratio, left_w)
        self._visible_bounds(body_rows)
        left_lines: List[str] = []
        for vis_idx in range(body_rows):
            i = self._scroll_top + vis_idx
            if i < len(self._order):
                tid = self._order[i]
                s = self.layout.render_line(self._tasks[tid], self._rt[tid], ctx_left)
                s = cut_visible_preserve_ansi(s, left_w)
                if i == self._sel_idx: s = "\x1b[7m" + s + "\x1b[0m"
            else:
                s = " " * left_w
            left_lines.append(s)
        if len(self._order) > 0:
            sel_tid = self._order[self._sel_idx]
            title = f"{self._tasks[sel_tid].name}"
            r_lines = self.right_renderer.render(width=right_w, height=body_rows, styler=self.styler, title=title, lines=self._logs.get(sel_tid, []))
        else:
            r_lines = [" " * right_w for _ in range(body_rows)]
        vsep = "│" if self.show_vsep else ""
        lines = list(header_lines)
        for i in range(body_rows):
            right = r_lines[i] if i < len(r_lines) else " " * right_w
            if self.show_vsep: lines.append(left_lines[i] + vsep + right)
            else: lines.append(left_lines[i] + right)
        lines.extend(footer_lines)
        self.term.write_frame(lines); self._last_render = now

    def _handle_events(self, s: str) -> bool:
        quit_req = False
        for ev in parse_events(s):
            if isinstance(ev, KeyEvent):
                k = ev.key
                if k in ("q", "\x03"):
                    quit_req = True
                elif k in ("w", "up"):
                    self._sel_idx = max(0, self._sel_idx - 1)
                elif k in ("s", "down"):
                    self._sel_idx = min(max(0, len(self._order)-1), self._sel_idx + 1)
                elif k == "home":
                    self._sel_idx = 0
                elif k == "end":
                    self._sel_idx = max(0, len(self._order)-1)
            else:
                me = ev
                if isinstance(me, MouseEvent) and me.pressed:
                    y = me.y - (len(self.header_layout.rows) if self.header_layout else 0)
                    if y >= 1:
                        idx = self._scroll_top + (y - 1)
                        if 0 <= idx < len(self._order):
                            self._sel_idx = idx
        return quit_req

    def loop(self) -> None:
        self._interactive = True
        try:
            self.term.enter_alt(); self.term.enable_mouse(); self._input.enter()
            while not self._stop:
                self.render(throttle=False)
                buf = self._input.read(0.05)
                if buf and self._handle_events(buf): break
        finally:
            self._input.exit(); self.term.disable_mouse(); self.term.exit_alt(); self._interactive = False

    def close(self) -> None:
        self.term.close()
        self._print_error_report()

    def _print_error_report(self) -> None:
        failed: List[tuple[int, TaskState]] = [(tid, self._tasks[tid]) for tid in self._order if self._tasks[tid].failed]
        if not failed:
            return
        cols = self.term.columns or 120
        rule = "─" * cols
        lines: List[str] = []
        lines.append(self.styler.color(rule, fg="bright_black"))
        title = f"✗ ERROR REPORT ({len(failed)} failed)"
        lines.append(self.styler.color(title, fg="bright_red"))
        lines.append(self.styler.color(rule, fg="bright_black"))
        for tid, t in failed:
            rt = self._rt.get(tid, TaskRuntime())
            head = self.styler.color(f"✗ {t.name}", fg="bright_red", bold=True)
            stage = self.styler.color(f"[{t.stage}]", fg="bright_red")
            lines.append(f"{head} {stage}")
            if t.total > 0:
                ratio = int(round(100 * t.done / max(1, t.total)))
                prog = f"{t.done}/{t.total} ({ratio:3d}%)"
            else:
                prog = f"{t.done}"
            el = fmt_hms((rt.finished or rt.updated or rt.created) - (rt.started or rt.created) if (rt.updated or rt.finished) and (rt.started or rt.created) else 0.0)
            rate = f"{rt.ewma_rate:.2f} it/s" if rt.ewma_rate > 0 else "--"
            stats = self.styler.color(f"  progress: {prog}  elapsed: {el}  rate: {rate}", fg="bright_black")
            lines.append(stats)
            if t.error:
                for ln in str(t.error).splitlines():
                    lines.append("  " + ln)
            lines.append(self.styler.color(rule, fg="bright_black"))
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()

    def bind_queue(self, queue, **keys) -> "QueueBinder":
        from .queue import QueueBinder
        return QueueBinder(self, queue, **keys)

    def hijack_stdio(self, handle_or_id):
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        p = self

        class _Ctx:
            def __enter__(self_):
                self_.o1, self_.o2 = sys.stdout, sys.stderr
                sys.stdout = Progress._StdRedirect(lambda m: p.log(tid, m))
                sys.stderr = Progress._StdRedirect(lambda m: p.log(tid, m))
                return self_

            def __exit__(self_, et, ev, tb):
                sys.stdout, sys.stderr = self_.o1, self_.o2

        return _Ctx()

    class _StdRedirect:
        def __init__(self, cb): self.cb = cb
        def write(self, s):
            for ln in s.splitlines():
                if ln: self.cb(ln)
            return len(s)
        def flush(self): pass

    def capture_stdout(self, handle_or_id):
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        p = self

        class _Ctx:
            def __enter__(self_):
                self_.orig = sys.stdout
                sys.stdout = _StdRedirect(lambda msg: p.log(tid, msg))
                return self_

            def __exit__(self_, et, ev, tb):
                sys.stdout = self_.orig

        return _Ctx()
