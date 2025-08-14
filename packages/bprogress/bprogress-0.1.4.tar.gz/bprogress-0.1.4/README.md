# braille-progress

Braille (U+2800–U+28FF) 기반 다중 프로그레스바 + ANSI 컬러.  
고정폭 레이아웃으로 퍼센트/상태/라벨 흔들림 없이 정갈하게 표시.

## Quick Start

```python
from braille_progress import Progress
p = Progress(force_tty=True, force_color=True)
with p.task("demo", total=50) as t:
    for i in range(50):
        t.advance(stage="writing", label=f"item_{i:03d}")
p.close()
```

## Multiprocess

```python
from braille_progress import Progress, progress_message
# 워커: q.put_nowait(progress_message(i, stage="WRITING", done=k, total=N, label="case")))
```

## CLI

```bash
braille-progress-demo --items 80 --force-tty --force-color
```

## License
MIT License

## `tests/test_basic.py`

```python
from braille_progress import Progress

def test_construct():
    p = Progress(force_tty=False, force_color=False)  # CI에서도 동작
    h = p.add("t", total=3)
    p.update(h, stage="validated", total=3)
    for _ in range(3):
        h.advance(stage="writing")
    p.done(h)
    assert p.all_finished()
```