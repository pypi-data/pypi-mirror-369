# braille-progress

점자 문자를 이용한 프로그레스 보드. 자유로운 레이아웃 커스터마이즈, 태스크별 로그 패널, 테스크 에러 리포트, Windows/Linux/macOS 터미널 복구까지 지원.

---

## 특징

* 줄바꿈/밀림 없는 안정 렌더링(가시폭 컷, 가드 컬럼), Windows VT I/O 지원, 종료 시 자동 복구(시그널+atexit), 마우스 모드 해제 및 입력 버퍼 플러시.
* 좌우 분할: 왼쪽 리스트(태스크), 오른쪽 패널(기본: 로그) + 세로 구분선.
* 인터랙션: 마우스 클릭, 키보드 `w/s` 또는 `↑/↓`, `Home/End`. (Linux계열 환경 한정)
* 행(Row) 레이아웃 자유 구성: 이름, 메인/서브 바, 퍼센트, 상태, 카운터, 라벨, 경과시간, 평균 처리속도, ETA, 임의 텍스트 등.
* 헤더/푸터 수직 레이아웃.
* 오른쪽 패널 렌더러 커스텀(메트릭, 표 등 임의 UI).
* 태스크 런타임 통계(EWMA 평균 처리속도, ETA).
* 종료 시 실패 태스크에 대한 컬러 트레이스백 리포트.
* 멀티프로세싱용 큐 바인더 및 메시지 스키마.
* ANSI/전각폭(CJK, ⣿) 안전한 가시폭 처리.
* 세로 정책: `fit`(내용만), `full`(터미널 높이 채움). ALT 스크린 옵션.

---

## 설치

```bash
pip install braille-progress  # 또는 저장소 경로에서 설치
```

Python ≥ 3.8. Windows는 Windows Terminal 등 VT 지원 콘솔 권장.

---

## 빠른 시작

```python
from braille_progress import Progress

p = Progress()
t = p.add("download", total=100)
for i in range(100):
    t.advance(1, stage="writing", label=f"chunk {i}")
p.close()
```

---

## 좌우 분할 + 선택 + 오른쪽 로그

```python
from braille_progress import Progress

p = Progress(split_ratio=0.55, show_vsep=True)
a = p.add("prepare", total=10)
b = p.add("train", total=500)

for i in range(10):
    a.advance(1, stage="writing"); p.log(a, f"prepare step {i}")
for i in range(50):
    b.advance(1, stage="writing"); p.log(b, f"loss={1/(i+1):.4f}")

p.loop()   # 마우스 클릭 또는 w/s, ↑/↓로 선택; 오른쪽에 해당 태스크 로그 표시
p.close()
```

조작:

* 키보드: `w`/`↑` 위, `s`/`↓` 아래, `Home`/`End`, `q` 또는 `Ctrl+C` 종료
* 마우스: 태스크 라인 클릭(SGR 마우스 모드 자동 활성화)

---

## stdout/stderr를 로그 패널에 출력

```python
from braille_progress import Progress

p = Progress()
h = p.add("convert", total=3)

with p.hijack_stdio(h):     # print()/traceback이 해당 태스크 로그 패널로 들어감
    print("converting...")
    try:
        1/0
    except Exception as e:
        h.fail(error=e)     # 종료 시 예쁜 트레이스백도 최종 리포트로 출력

p.close()
```

---

## 커스텀 헤더/푸터/행(Row) 레이아웃

```python
from braille_progress import (
    Progress, ProgressTheme, Layout, Name, Bar, Percent, Status,
    MiniBar, Counter, Label, Text, Gap, Elapsed, AvgRate, ETA,
    Rule, Now, VLayout, VGap, default_layout
)

theme = ProgressTheme.auto_fit()

row = Layout([
    Name(width=22),
    Text(" | "),
    Bar(cells=18),
    Percent(width=5),
    Gap(2),
    Status(width=16),
    Text(" | "),
    MiniBar(cells=10),
    Counter(),
    Gap(2),
    Label(width="flex")
], theme=theme)

header = VLayout([ Rule(), Text(" Jobs"), VGap(1) ])
footer = VLayout([ VGap(1), Rule(), Text(" Ready  "), Now() ])

p = Progress(layout=row, header=header, footer=footer, split_ratio=0.6, show_vsep=True)
a = p.add("aa.zip", total=100)
b = p.add("bb.zip", total=100)
a.advance(30, stage="writing", label="downloading")
b.advance(70, stage="writing", label="processing")
p.loop()
p.close()
```

메모:

* `Label(width="flex")` 가변 폭으로 남은 공간을 차지하며, 줄맞춤 필요 시 마지막에 축소됩니다.
* `Label`이 없더라도 마지막 세그먼트를 축소해 줄바꿈을 방지합니다.
* 가시폭(ANSI 제거, 전각폭 반영) 기준으로 폭을 계산합니다.

---

## 세로 크기 정책

```python
# 터미널 전체 높이 채움(대시보드)
p = Progress(row_policy="full", min_body_rows=8, use_alt_screen=True)

# 내용만 표시(화면 전체 점유 없음)
p = Progress(row_policy="fit", max_body_rows=12, use_alt_screen=False)
```

`row_policy`:

* `"full"`: 헤더+바디+푸터가 터미널 높이를 채움
* `"fit"`: 콘텐츠에 맞게 바디 행 개수를 결정(`min_body_rows`/`max_body_rows`로 상·하한 제어)

---

## 오른쪽 패널 렌더러 커스텀

```python
from braille_progress import Progress, DetailRenderer

class MetricsPanel(DetailRenderer):
    def render(self, *, width, height, styler, title, lines):
        out = [styler.color(f"[{title}] metrics", fg="bright_magenta").ljust(width)[:width]]
        for i in range(1, height):
            out.append(f"logs={len(lines)} row={i}".ljust(width)[:width])
        return out

p = Progress(right_renderer=MetricsPanel(), split_ratio=0.5)
h = p.add("task", total=10)
for i in range(10): p.log(h, f"event {i}")
p.loop(); p.close()
```

내장 렌더러:

* `ConsoleRenderer`(기본): 제목 + 끝부분 로그
* `StaticRenderer(lines)`: 고정 문자열 리스트

---

## 에러 리포트

실패한 태스크는 `Progress.close()` 시 컬러 트레이스백과 함께 요약됩니다.

```python
from braille_progress import Progress

p = Progress()
try:
    with p.task("upload", total=3) as h:
        raise RuntimeError("remote closed")
except Exception:
    pass

p.close()  # 실패 태스크의 파일/라인/함수/코드가 강조된 트레이스백 출력
```

`fail(error=..., error_tb=True)`에 예외를 넘기면 트레이스백이 예쁘게 포매팅됩니다.

---

## 큐 바인더(멀티프로세싱)

```python
from braille_progress import Progress, QueueBinder, progress_message

p = Progress()
h = p.add("worker-0", total=100)

# 부모 프로세스
binder = p.bind_queue(my_queue)
while True:
    changed = binder.drain()
    if changed: p.render(throttle=False)
    if p.all_finished(): break

# 워커 프로세스
my_queue.put(progress_message(0, stage="writing", done=5, total=100, label="chunk-5"))
my_queue.put(progress_message(0, final=True))  # DONE
```

메시지 스키마는 기본 키(`i`, `stage`, `case_done`, `case_total`, `case_label`)를 사용하며, `QueueBinder` 생성 시 키를 오버라이드할 수 있습니다.

---

## API

### `Progress`

```python
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
        layout: Optional["Layout"] = None,
        header: Optional["VLayout|Layout|Sequence[Row]"] = None,
        footer: Optional["VLayout|Layout|Sequence[Row]"] = None,
        row_policy: str = "fit",
        min_body_rows: int = 0,
        max_body_rows: Optional[int] = None,
        split_ratio: float = 0.55,
        show_vsep: bool = True,
        right_renderer: Optional["DetailRenderer"] = None,
        use_alt_screen: bool = False,
        handle_signals: bool = True,
    )
```

메서드:

* `add(name: str, total: int = 0) -> TaskHandle`
* `task(name: str, total: int = 0)` 컨텍스트 매니저(정상 종료 시 `done()`, 예외 시 `fail()`)
* `update(handle_or_id, *, advance=0, done=None, total=None, stage=None, label=None, finished=None, failed=None) -> None`
* `done(handle_or_id) -> None`
* `fail(handle_or_id, *, stage="error", error: Optional[Exception]=None, error_tb=True) -> None`
* `track(iterable, *, total=None, description=None, label_from=None) -> Iterator`
* `log(handle_or_id, msg: str) -> None`  (선택된 태스크의 오른쪽 패널 로그에 표시)
* `hijack_stdio(handle_or_id)` 컨텍스트(해당 태스크 로그로 stdout/stderr 리다이렉트)
* `set_right_renderer(renderer: DetailRenderer) -> None`
* `render(throttle: bool=False) -> None`
* `loop() -> None`  (인터랙티브 UI)
* `close() -> None` (UI 종료, 에러 리포트 출력, 터미널 복구)
* `bind_queue(queue, **keys) -> QueueBinder`

동작 요약:

* 렌더링은 가드 컬럼(`cols-1`)과 전각폭 안전 컷으로 줄바꿈을 원천 차단.
* Windows에서 VT 입력/출력을 활성화하고, 종료 시 마우스 모드 해제·입력 버퍼 플러시·ALT 스크린 종료·콘솔 모드 복구.

### `TaskHandle`

```python
class TaskHandle:
    def advance(self, n: int = 1, *, label: Optional[str] = None, stage: Optional[str] = None) -> "TaskHandle"
    def update(self, *, done=None, total=None, stage=None, label=None, finished=None, failed=None) -> "TaskHandle"
    def complete(self) -> None
    def fail(self, stage: str = "error") -> None
```

### `TaskState`

```python
@dataclass
class TaskState:
    name: str
    total: int = 0
    done: int = 0
    stage: str = "queue"
    label: str = ""
    finished: bool = False
    failed: bool = False
    error: str = ""
    error_obj: Any = None
```

### 레이아웃 구성요소

```python
from braille_progress import Layout, RenderContext
from braille_progress import Name, Bar, Percent, Status, MiniBar, Counter, Label
from braille_progress import Text, Gap, Elapsed, AvgRate, ETA, Spacer, Rule, Now
from braille_progress import VLayout, VGap, default_layout
```

세그먼트:

* `Name(width=int)`
* `Bar(cells=int)` 메인 브라유 바
* `Percent(width=int)`
* `Status(width=int)` 상태/스테이지 텍스트
* `MiniBar(cells=int)` `done/total` 서브 바
* `Counter()` `done/total` 숫자, 자동 폭
* `Label(width=int|"flex")` 사용자 라벨(남는 공간, 축소 대상)
* `Text(str)`, `Gap(n)`, `Spacer()`
* `Elapsed`, `AvgRate`, `ETA` 런타임 통계 기반
* `Rule()` 구분선, `Now()` 현재 시각
* `VLayout([row...])` 수직 스택(헤더/푸터)
* `VGap(n)` 빈 줄
* `default_layout(theme)` 기본 행 레이아웃

### 오른쪽 패널 렌더러

```python
from braille_progress import DetailRenderer, ConsoleRenderer, StaticRenderer
```

* `DetailRenderer.render(width, height, styler, title, lines) -> List[str]`
* `ConsoleRenderer`: 제목 + 로그 꼬리
* `StaticRenderer(lines)`: 고정 콘텐츠

### 테마

```python
from braille_progress import ProgressTheme
theme = ProgressTheme.auto_fit()
# 필드: name_w, bar_cells, pct_w, right_w, mini_cells, label_w, color, colors
# colors 키: queue, opening, scanning, validated, writing, md_zip, md_written, no_md, done, error
```

### 진행 비율 전략

```python
from braille_progress import RatioStrategy, DefaultRatio, TaskState

class MyRatio(RatioStrategy):
    def ratio(self, t: TaskState) -> float:
        # 0.0..1.0
        ...

p = Progress(ratio_strategy=MyRatio())
```

기본 규칙:

* opening/scanning=0.05, validated=0.10, writing=0.10+0.80\*(done/total), md\_\*≈0.95, finished/failed=1.0

### 큐 바인더/메시지

```python
from braille_progress import QueueBinder, progress_message
```

* `QueueBinder(progress, queue, id_key="i", stage_key="stage", done_key="case_done", total_key="case_total", label_key="case_label")`
* `drain() -> int`
* `progress_message(i, stage=None, done=None, total=None, label=None, final=False, failed=False) -> dict`

---

## 렌더링/터미널 동작

* 렌더링 중 자동줄바꿈을 끄고, 모든 줄을 `cols-1` 내로 가시폭 기준 절단. 마지막 줄은 개행 없이 출력해 스크롤을 막습니다.
* `loop()`에서 VT 입력·마우스 활성화, `close()`/종료 시 마우스/포커스/브래킷드 페이스트 모드 해제(`?1006/?1002/?1000/?1015/?1004/?2004`), 커서 보이기·wrap 복구, 입력 버퍼 플러시(Windows `FlushConsoleInputBuffer`, POSIX `tcflush`), ALT 스크린 종료, 콘솔 모드 원복.
* 렌더링 중 `print()` 호출은 화면을 흔듭니다. `p.log(...)` 또는 `p.hijack_stdio(handle)` 사용을 권장.

---

## 환경 변수

* `BP_FORCE_TTY=1` : TTY 모드 강제
* `BP_FORCE_COLOR=1` : 컬러 강제
* `NO_COLOR=1` : 컬러 비활성화

---

## 예시

### 에러 포함 최소 예시

```python
from braille_progress import Progress

p = Progress()
h = p.add("upload", total=3)
try:
    for i in range(3):
        if i == 2: raise RuntimeError("remote closed")
        h.advance(1, stage="writing")
except Exception as e:
    h.fail(error=e)
p.close()
```

### Fit 모드 대시보드(ALT 스크린 없이)

```python
from braille_progress import Progress, default_layout, ProgressTheme

p = Progress(
    layout=default_layout(ProgressTheme.auto_fit()),
    row_policy="fit",
    max_body_rows=10,
    split_ratio=0.6,
    show_vsep=True,
    use_alt_screen=False
)
# ... 태스크/로그 추가 ...
p.loop(); p.close()
```

---

## 공개 심볼

```python
from braille_progress import (
  Progress, ProgressTheme, TaskHandle, TaskState,
  RatioStrategy, DefaultRatio, QueueBinder, progress_message,
  Layout, default_layout, RenderContext,
  Name, Bar, Percent, Status, MiniBar, Counter, Label, Text, Gap,
  Elapsed, AvgRate, ETA, Spacer, Rule, Now, VGap, VLayout,
  DetailRenderer, ConsoleRenderer, StaticRenderer
)
```
