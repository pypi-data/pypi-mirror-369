from __future__ import annotations
import time
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Union, Sequence

from .terminal import TerminalIO
from .theme import ProgressTheme
from .style import AnsiStyler
from .braille import BrailleRenderer
from .ratio import RatioStrategy, DefaultRatio
from .model import TaskHandle, TaskState
from .layout import Layout, default_layout, RenderContext, VLayout, VGap, Row
from .stats import TaskRuntime
from .background import Background

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
        auto_resize: bool = True,
        background: Optional[Background] = None,
        overlay_mode: str = "rows",
        reserve_bg_rows: int = 0,
        body_window: str = "tail",
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
        self.auto_resize = bool(auto_resize)
        self.background = background
        self.overlay_mode = overlay_mode
        self.reserve_bg_rows = max(0, int(reserve_bg_rows))
        self.body_window = body_window
        self._tasks: Dict[int, TaskState] = {}
        self._order: List[int] = []
        self._next_id = 0
        self._rt: Dict[int, TaskRuntime] = {}
        self._auto_refresh = auto_refresh
        self._refresh_interval = max(0.01, float(refresh_interval))
        self._last_render = 0.0

    def add(self, name: str, total: int = 0) -> TaskHandle:
        tid = self._next_id
        self._next_id += 1
        self._tasks[tid] = TaskState(name=name, total=max(0, int(total)))
        self._order.append(tid)
        rt = TaskRuntime()
        rt.on_create()
        self._rt[tid] = rt
        if self._auto_refresh:
            self.render(throttle=True)
        return TaskHandle(self, tid)

    def task(self, name: str, total: int = 0):
        outer = self
        class _Ctx:
            def __enter__(self_non):
                self_non.h = outer.add(name, total)
                return self_non.h
            def __exit__(self_non, et, ev, tb):
                if et is None:
                    outer.done(self_non.h)
                else:
                    outer.fail(self_non.h, stage="error")
                if outer._auto_refresh:
                    outer.render(throttle=True)
        return _Ctx()

    def update(
        self,
        handle_or_id,
        *,
        advance: int = 0,
        done: Optional[int] = None,
        total: Optional[int] = None,
        stage: Optional[str] = None,
        label: Optional[str] = None,
        finished: Optional[bool] = None,
        failed: Optional[bool] = None,
    ) -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]
        if total is not None:
            t.total = max(0, int(total))
        if done is not None:
            t.done = max(0, int(done))
        if advance:
            t.done = max(0, t.done + int(advance))
        if stage is not None:
            t.stage = stage
        if label is not None:
            t.label = label
        if finished is not None:
            t.finished = bool(finished)
        if failed is not None:
            t.failed = bool(failed)
        if t.total and t.done >= t.total and not t.failed:
            t.finished = True
            if t.stage not in ("error", "ERROR"):
                t.stage = "done"
        self._rt[tid].on_progress(t.done)
        if self._auto_refresh:
            self.render(throttle=True)

    def done(self, handle_or_id) -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]
        t.finished = True
        t.stage = "done"
        self._rt[tid].on_finish(False)
        if self._auto_refresh:
            self.render(throttle=True)

    def fail(self, handle_or_id, *, stage: str = "error") -> None:
        tid = handle_or_id._tid if isinstance(handle_or_id, TaskHandle) else int(handle_or_id)
        t = self._tasks[tid]
        t.failed = True
        t.finished = True
        t.stage = stage
        self._rt[tid].on_finish(True)
        if self._auto_refresh:
            self.render(throttle=True)

    def all_finished(self) -> bool:
        return len(self._tasks) > 0 and all(t.finished for t in self._tasks.values())

    def track(
        self,
        iterable: Iterable,
        *,
        total: Optional[int] = None,
        description: Optional[str] = None,
        label_from: Optional[Callable[[Any], str]] = None,
    ) -> Iterator:
        if total is None:
            try:
                total = len(iterable)  # type: ignore
            except Exception:
                total = 0
        h = self.add(description or "progress", total=total or 0)
        try:
            for item in iterable:
                yield item
                lbl = label_from(item) if label_from else None
                if total:
                    h.advance(1, stage="writing", label=lbl)
                else:
                    h.update(stage="writing", label=lbl)
            h.complete()
        except Exception:
            h.fail()
            raise
        finally:
            if self._auto_refresh:
                self.render(throttle=False)

    def _compute_frame_lines(self, cols: int, rows: Optional[int]) -> List[str]:
        ctx = RenderContext(self.theme, self.styler, self.bars, self.ratio, cols)
        header_lines: List[str] = self.header_layout.render(ctx) if self.header_layout else []
        body_all = [self.layout.render_line(self._tasks[tid], self._rt[tid], ctx) for tid in self._order]
        footer_lines: List[str] = self.footer_layout.render(ctx) if self.footer_layout else []
        if rows is None:
            need = max(self.min_body_rows, len(body_all))
            body_lines = body_all + ([" " * cols] * max(0, self.min_body_rows - len(body_all)))
            return header_lines + body_lines + footer_lines
        reserved = max(self.reserve_bg_rows, 0)
        avail_body = max(0, rows - len(header_lines) - len(footer_lines) - reserved)
        if self.min_body_rows:
            avail_body = max(avail_body, self.min_body_rows)
        if len(body_all) <= avail_body:
            body_lines = body_all + ([" " * cols] * (avail_body - len(body_all)))
        else:
            if self.body_window == "head":
                body_lines = body_all[:avail_body]
            else:
                body_lines = body_all[-avail_body:]
        base_lines = header_lines + body_lines + footer_lines
        missing = max(0, rows - len(base_lines))
        if missing:
            base_lines.extend([" " * cols] * missing)
        return base_lines

    def render(self, *, throttle: bool = False) -> None:
        now = time.time()
        if throttle and (now - self._last_render) < self._refresh_interval:
            return
        cols = self.term.columns if self.auto_resize else self.theme.label_w + self.theme.name_w
        rows = self.term.rows if self.auto_resize else None
        if cols <= 0:
            cols = 120
        if rows is not None and rows <= 0:
            rows = None
        if cols and hasattr(self.theme, "label_w"):
            pass
        ctx_cols = cols
        content_lines = self._compute_frame_lines(ctx_cols, rows)
        if self.background and rows:
            bg_lines = self.background.render(self.styler, ctx_cols, rows)
            out = []
            for i in range(min(len(content_lines), len(bg_lines))):
                out.append(content_lines[i] if content_lines[i].strip() else bg_lines[i])
            if len(bg_lines) > len(content_lines):
                out.extend(bg_lines[len(content_lines):])
            elif len(content_lines) > len(bg_lines):
                out.extend(content_lines[len(bg_lines):])
            self.term.write_frame(out)
        else:
            self.term.write_frame(content_lines)
        self._last_render = now

    def close(self) -> None:
        self.term.close()

    def bind_queue(self, queue, **keys) -> "QueueBinder":
        from .queue import QueueBinder
        return QueueBinder(self, queue, **keys)
