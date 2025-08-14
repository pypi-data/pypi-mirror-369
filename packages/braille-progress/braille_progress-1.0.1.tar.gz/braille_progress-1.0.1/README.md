# braille-progress
<img width="1060" height="244" alt="image" src="https://github.com/user-attachments/assets/7b6d7929-3db5-4140-8570-989e5d2bcf35" />

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
pip install braille-progress
```

Python ≥ 3.8. Windows는 Windows Terminal 등 VT 지원 콘솔 권장.

---

## 빠른 시작


## 빠른 시작

```python
from braille_progress import Progress, ProgressTheme

p = Progress(
    row_policy="fit",          # 위 출력 보존, 필요한 줄만 아래에 확보
    split_ratio=0.58,          # 좌측:우측 폭 비율
    show_vsep=True,            # 세로 구분선 표시
)

t1 = p.add("download", total=100)
t2 = p.add("extract", total=30)

for i in range(10):
    t1.advance(1, stage="writing", label=f"part {i}")
    p.log(t1, f"chunk {i} ok")

p.loop()   # w/s 또는 ↑/↓로 선택, 마우스 클릭으로도 선택 가능
p.close()  # 종료 및 에러 리포트/터미널 상태 복구
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

# Progress 객체 API

---

## 생성자(파라미터)

```python
Progress(
  theme: Optional[ProgressTheme]=None,
  *,
  auto_vt: bool=True,
  auto_refresh: bool=True,
  refresh_interval: float=0.05,
  force_tty: Optional[bool]=None,
  force_color: Optional[bool]=None,
  ratio_strategy: Optional[RatioStrategy]=None,

  layout: Optional[Layout]=None,
  header: Optional[Union[VLayout, Layout, Sequence[Row]]]=None,
  footer: Optional[Union[VLayout, Layout, Sequence[Row]]]=None,

  # 좌우 분할/우측 패널
  split_ratio: float=0.55,
  show_vsep: bool=True,
  right_renderer: Optional[DetailRenderer]=None,

  # 세로 정책
  row_policy: str="fit",          # "fit" | "full"
  min_body_rows: int=0,           # 최소 표시 줄 수(fit/full 공통)
  max_body_rows: Optional[int]=None,  # fit 모드에서 최대 줄 수 제한

  # 스크린/시그널
  use_alt_screen: bool=False,
  handle_signals: bool=True
)
```

### 표시/갱신

* `auto_refresh`: 상태 변경 시 자동 리렌더.
* `refresh_interval`: 자동 리렌더 최소 간격(초).
* `theme`: 폭 계산/색상 팔레트. `ProgressTheme.auto_fit()` 권장.
* `force_color`: `True`면 ANSI 색 강제, `False`면 비활성.
* `force_tty`: 강제로 TTY 모드로 렌더(파이프 환경 테스트용).
* `ratio_strategy`: 진행률 계산 전략 커스터마이즈.

### 레이아웃(좌측 리스트 라인)

* `layout`: 한 줄을 구성하는 빌딩블록(Layout DSL). 미지정 시 기본 레이아웃.
* `header`/`footer`: 상/하단에 세로 레이아웃 추가. `VLayout`, `Layout`, `Row` 시퀀스 지원.

### 좌우 분할/우측 패널

* `split_ratio`: 좌측 리스트 폭 비율(0.1\~0.9).
* `show_vsep`: 좌우 사이에 `│` 표시.
* `right_renderer`: 우측 패널 콘텐츠 렌더러. 기본은 콘솔 로그(`ConsoleRenderer`).

### 세로 정책

* `row_policy="fit"`: 위 기존 출력은 그대로 두고, **아래에 필요한 줄만 확보하여** 그 안에서 갱신(스크린 전체를 채우지 않음).
* `row_policy="full"`: 현재 터미널 높이에 맞춰 본문 영역을 채움.
* `min_body_rows`: 최소 줄 보장.
* `max_body_rows`: `fit` 모드에서 최대 줄 제한.

### 스크린/시그널

* `use_alt_screen`: `True`면 ALT 스크린(별도 버퍼) 사용.
* `handle_signals`: SIGINT/SIGTERM/SIGHUP에서 터미널/입력 모드 안전 복구.

---

## 메서드

### 태스크 생성/갱신

```python
h = p.add(name: str, total: int = 0) -> TaskHandle
```

* 새 태스크 추가. 반환되는 `TaskHandle`로 갱신.

```python
p.update(handle_or_id, *, advance=0, done=None, total=None,
         stage=None, label=None, finished=None, failed=None) -> None
```

* 태스크 상태 갱신. `advance`는 `done`을 증가시킴.

```python
h.advance(n: int=1, *, label: Optional[str]=None, stage: Optional[str]=None) -> TaskHandle
```

* 진행 수치 간편 증가.

```python
p.done(handle_or_id) -> None
h.complete() -> None
```

* 태스크 완료 처리(표시상 `stage="done"`).

```python
p.fail(handle_or_id, *, stage: str="error",
       error: Optional[Any]=None, error_tb: bool=True) -> None
h.fail(stage: str="error") -> None
```

* 실패 처리. `error`에 예외 객체를 넘기면 종료 시 **예쁜 traceback** 포함 에러 리포트 출력.

```python
p.all_finished() -> bool
```

* 모든 태스크 종료 여부.

### 컨텍스트 API

```python
with p.task("name", total=10) as h:
    ...
```

* 블록 내 예외 발생 시 자동 `fail()`, 정상 종료 시 자동 `done()`.

### 반복 도우미

```python
for item in p.track(iterable, total=None, description=None, label_from=None):
    ...
```

* 반복 중 자동 진행/라벨 갱신. 예외 시 자동 `fail()`.

### 로그/우측 패널

```python
p.log(handle_or_id, msg: str) -> None
```

* 해당 태스크의 로그를 우측 패널에 추가(최대 최근 2000줄 유지).

```python
p.set_right_renderer(renderer: DetailRenderer) -> None
```

* 우측 패널 렌더러 교체.

```python
with p.hijack_stdio(handle_or_id):
    # 이 블록의 stdout/stderr는 우측 패널 로그로 유입
    print("captured")
```

### 렌더/루프/종료

```python
p.render(throttle: bool=False) -> None
```

* 수동 렌더. `throttle=True`면 `refresh_interval`을 존중.

```python
p.loop() -> None
```

* 인터랙티브 UI 루프 시작.

  * 키보드: `w`/`s` 또는 `↑`/`↓`로 좌측 선택 이동.
  * 마우스: 좌측 리스트 영역 클릭으로 선택.
  * `q` 또는 `Ctrl+C`로 종료.

```python
p.close() -> None
```

* 화면 정리, 실패 태스크 에러 리포트 출력, 마우스/입력 모드/ALT 스크린/VT 모드 등 **완전 복구**.

### 큐 바인더(선택)

```python
qb = p.bind_queue(queue, id_key="i", stage_key="stage",
                  done_key="case_done", total_key="case_total",
                  label_key="case_label")
changed = qb.drain()
```

* 외부 워커 메시지를 UI에 반영.

---

## 우측 패널 커스텀 렌더러

```python
from braille_progress import DetailRenderer

class MyPanel(DetailRenderer):
    def render(self, *, width, height, styler, title, lines):
        out = [styler.color(f"[{title}] metrics", fg="bright_magenta").ljust(width)[:width]]
        for i in range(1, height):
            txt = f"rows={height}, logs={len(lines)}"
            out.append(txt.ljust(width)[:width])
        return out
```

* `width`/`height` 내에서만 출력하도록 반드시 패딩/절단 처리.

---

## 좌측 라인 레이아웃 교체(요약)

* DSL 구성요소 예: `Name()`, `Bar()`, `Percent()`, `Status()`, `MiniBar()`, `Counter()`, `Label()`, `Elapsed()`, `AvgRate()`, `ETA()`, `Text(" | ")`, `Gap(w)` 등.
* 예:

```python
from braille_progress import Layout, Name, Text, Bar, Percent, Status, MiniBar, Counter, Label

layout = Layout([
  Name(w=20), Text(" | "),
  Bar(cells=18), Percent(), Text("  "),
  Status(w=16), Text(" | "),
  MiniBar(cells=10), Counter(), Text("  "),
  Label(w=32)
])
p = Progress(layout=layout)
```

---

## 모드/환경 변수

* `use_alt_screen=True`: 메인 터미널과 분리된 버퍼에 렌더(외부 출력 간섭 줄임).
* `NO_COLOR=1`: 강제로 무채색.
* `BP_FORCE_TTY=1`: 강제로 TTY 모드.
* `BP_FORCE_COLOR=1`: 강제로 컬러 활성.

---

## 에러 리포트

* `p.close()` 시 실패 태스크를 수집하여:

  * 태스크명/스테이지/진행/경과/속도
  * 전달받은 `error` 예외의 **컬러 트레이스백**(파일/라인/함수/코드) 출력.

---

## 사용 팁

* 루프 동안 외부 `print()`가 필요하면 반드시 `hijack_stdio()`로 감싸 우측 로그로 보내라(레이아웃 깨짐 방지).
* `row_policy="fit"`은 기존 상단 출력 보존. 필요 줄이 늘면 아래로만 확장한다.
  `row_policy="full"`은 터미널 높이를 채우며 헤더/푸터와 함께 스테이블하게 갱신한다.
* Windows에서는 Windows Terminal + 고정폭 폰트 사용을 권장.


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
