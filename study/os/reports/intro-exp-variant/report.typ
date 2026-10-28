#set text(font: "PT Serif", size: 12pt, lang: "ru")
#set page(margin: (top: 20mm, bottom: 20mm, left: 30mm, right: 15mm))
#set par(justify: true, first-line-indent: (amount: 1.25cm, all: true), leading: 0.8em)
#set heading(numbering: "1.1")
#show heading: it => { v(0.6em); it; v(0.4em) }
#show raw.where(block: true): it => block(
  fill: luma(245), inset: 8pt, radius: 3pt, width: 100%,
  text(size: 9pt, font: "Menlo", it),
)
#show raw.where(block: false): it => text(size: 10pt, font: "Menlo", it)
#set table(stroke: 0.4pt + luma(120), inset: 4pt)
#show table: set text(size: 9.5pt)
#show table: set par(justify: false, first-line-indent: 0pt)
#show figure.caption: it => text(size: 10pt, it)
#show figure: set block(breakable: true)

#import "title.typ": titlepage

#titlepage(
  title: [Introductory Experiment: время обхода графа\ при записи без кэширования, файлы 10 МиБ и 1 МиБ],
  student: "Данилов Тимофей Николаевич",
  group: "P3331",
  teacher: "Максимов Андрей Николаевич",
)

#set page(numbering: "1")
#counter(page).update(1)

#outline(title: [Содержание], depth: 2, indent: auto)
#pagebreak()

= Ход работы

Репозиторий и Pull Request: #link("https://github.com/volinadtim/os-course")[volinadtim/os-course],
ветка `lab-intro-exp`, каталог `lab/intro-exp`.

== Вариант

#table(
  columns: (auto, 1fr),
  [*Тип нагрузки*], [запись (`--write`)],
  [*Работа с кэшем*], [без системного кэша (`--no-cache`)],
  [*Размеры файла*], [10 МиБ и 1 МиБ],
  [*Модель доступа*], [случайная (Rand)],
)

Сравниваются два размера файла графа. Обе программы — `graph_traverse`
(`read`/`lseek`/`write`) и `graph_traverse_mmap` (`mmap`) — запускаются
с ключами `--write --no-cache`. Получается четыре конфигурации.
Метрика — время одного полного обхода графа.

= Паспорт системы

#table(
  columns: (auto, 1fr),
  [*Стенд*], [ПК `tim-homie`, без виртуализации],
  [*ОС*], [Ubuntu 24.04, ядро 7.0.0-34-generic, x86_64],
  [*CPU*], [Intel Core i5-11400F, 6 ядер / 12 потоков, L1d 48 КиБ, L2 512 КиБ на ядро, L3 12 МиБ],
  [*Частота*], [governor `performance`, Turbo Boost выключен (`no_turbo = 1`), 2,6 ГГц],
  [*RAM*], [32 ГБ (31 ГиБ доступно), swap не использовался],
  [*NUMA*], [1 узел],
  [*Накопитель*], [NVMe Kingston NV3 1 ТБ, логический блок 512 Б],
  [*ФС*], [ext4, файлы графов на основном разделе],
)

Полный вывод `uname -a`, `lscpu`, `lscpu -e`, `free -h`, `numactl`,
`lsblk`, `uptime`, `top` — `report-variant/characterization/system.txt`.

= Подготовка данных

```bash
python3 ../util/graphgen.py -s 10M --seed 427 --topology chain \
        -b 0.5 --min-step-pages 2 -o data-variant/graph-rand-10M.bin
python3 ../util/graphgen.py -s 1M  --seed 427 --topology chain \
        -b 0.5 --min-step-pages 2 -o data-variant/graph-rand-1M.bin
```

#table(
  columns: (auto, auto, auto),
  align: (left, right, right),
  table.header([*Файл*], [*Размер, байт*], [*Вершин*]),
  [`graph-rand-10M.bin`], [10 485 760], [436 905],
  [`graph-rand-1M.bin`], [1 048 576], [43 689],
)

Замеры выполняются на копиях `*.w.bin`, так как режим `--write` изменяет файл.

= Настройка окружения

#table(
  columns: (auto, 1fr),
  [*Частота CPU*], [`cpupower frequency-set -g performance`, Turbo выключен],
  [*Привязка*], [`taskset -c 2`, `nice -n -5`],
  [*Кэш*], [`sync` и `drop_caches` перед каждым запуском],
  [*Фоновые процессы*], [Firefox и окна обновлений приостановлены (`kill -STOP`) на время замеров],
  [*Нагрузка*], [`load average` ≈ 0,1 до серии],
)

= Ознакомительные измерения

Одиночные запуски с `--write --no-cache`:

#table(
  columns: (auto, auto, auto, auto, auto),
  align: (left, left, right, right, right),
  table.header([*Программа*], [*Файл*], [*wall, с*], [*user + sys, с*], [*major faults*]),
  [`graph_traverse`], [10 МиБ], [154,6], [6,7], [2],
  [`graph_traverse`], [1 МиБ], [11,1], [0,7], [2],
  [`graph_traverse_mmap`], [10 МиБ], [0,056], [0,02], [208],
  [`graph_traverse_mmap`], [1 МиБ], [0,013], [0,00], [22],
)

У `graph_traverse` wall во много раз больше user + sys: процесс ждёт ввода-вывода.

Профиль системных вызовов `strace -c`, 1 МиБ (43 689 вершин):

#table(
  columns: (auto, auto, auto),
  align: (left, right, right),
  table.header([*Вызов*], [*graph_traverse*], [*На вершину*]),
  [`lseek`], [132 433], [3,03],
  [`read`], [88 745], [2,03],
  [`write`], [43 691], [1,00],
)

`graph_traverse_mmap` выполняет только единичные вызовы `mmap`, `madvise`,
`msync`, `munmap`; полный вывод — `report-variant/characterization/`.

Утилита `perf stat` на стенде недоступна: `kernel.perf_event_paranoid = 4`.

= Гипотезы

+ *H1.* Время обхода `graph_traverse` для 10 МиБ примерно в 10 раз больше, чем для 1 МиБ: число вершин различается в 10 раз.
+ *H2.* У `graph_traverse` wall во много раз больше user + sys.
+ *H3.* `graph_traverse_mmap` быстрее `graph_traverse` на обоих размерах.

= План эксперимента

#table(
  columns: (auto, 1fr),
  [*Метрика*], [wall-clock одного обхода (`iterations = 1`) по таймеру bash `$EPOCHREALTIME` (разрешение 1 мкс). Сопутствующие счётчики — `/usr/bin/time -v`],
  [*Повторы*], [12 раундов; в раунде все 4 конфигурации, порядок внутри раунда случайный (`shuf`)],
  [*Прогрев*], [первые 2 раунда отбрасываются (решение принято до серии); N = 10 на конфигурацию],
  [*Выбросы*], [не отбрасываются],
  [*Кэш*], [одинаково для всех запусков: `--no-cache`, перед запуском `sync` + `drop_caches`],
  [*Инструменты*], [в серии только `/usr/bin/time -v`; `strace` — только в ознакомительных измерениях],
)

Сбор — `scripts/collect_variant.sh`, сырые данные — `results-variant/variant-10M-1M.csv`,
обработка — `scripts/analyze_variant.py`.
Параллельно серии записывался `iostat -dx nvme0n1` с интервалом 5 с.

= Результаты

#let rows = csv("figures/summary.csv")
#let head = rows.at(0)
#let col(name) = head.position(c => c == name)
#let get(r, name) = r.at(col(name))
#let f(v, d) = {
  let s = str(calc.round(float(v), digits: d))
  s.replace(".", ",")
}
#let label(r) = (
  if get(r, "traverser") == "graph_traverse" { "read" } else { "mmap" },
  if get(r, "size") == "1M" { "1 МиБ" } else { "10 МиБ" },
)

#figure(
  table(
    columns: 8,
    align: (left, left) + (right,) * 6,
    table.header([*Программа*], [*Файл*], [*N*], [*Среднее, с*], [*СКО, с*], [*ДИ 95%, ±с*], [*Медиана, с*], [*Мин–макс, с*]),
    ..rows.slice(1).map(r => {
      let d = if get(r, "traverser") == "graph_traverse" { 2 } else { 4 }
      label(r) + (
        get(r, "n"),
        f(get(r, "mean_s"), d), f(get(r, "std_s"), d), f(get(r, "ci95_s"), d),
        f(get(r, "median_s"), d),
        f(get(r, "min_s"), d) + "–" + f(get(r, "max_s"), d),
      )
    }).flatten()
  ),
  caption: [Время обхода, `--write --no-cache`, Rand],
) <tab-main>

#figure(
  table(
    columns: 8,
    align: (left, left) + (right,) * 6,
    table.header([*Программа*], [*Файл*], [*мкс/вершину*], [*user, с*], [*sys, с*], [*vol. ctx*], [*major faults*], [*FS in / out*]),
    ..rows.slice(1).map(r => label(r) + (
      f(get(r, "per_node_us"), 2),
      f(get(r, "user_s"), 2), f(get(r, "sys_s"), 2),
      str(int(float(get(r, "vol_ctx")))),
      str(int(float(get(r, "majflt")))),
      str(int(float(get(r, "fs_in")))) + " / " + str(int(float(get(r, "fs_out")))),
    )).flatten()
  ),
  caption: [Сопутствующие метрики, средние по серии. FS in / out — в блоках по 512 Б],
) <tab-metrics>

#figure(
  image("figures/ci_points.png", width: 100%),
  caption: [Среднее с 95% ДИ и отдельные запуски],
) <fig-ci>

#figure(
  image("figures/distribution.png", width: 100%),
  caption: [Распределение запусков по времени на одну вершину, 1 МиБ и 10 МиБ],
) <fig-dist>

= Выводы

== Сравнение

*H1 подтверждается.* У `graph_traverse` отношение средних 10 МиБ / 1 МиБ — 10,3 при
отношении числа вершин 10,0. Время на вершину — 339 и 349 мкс, интервалы
пересекаются.

*H2 подтверждается.* 10 МиБ: обход длился 152,4 с, из них процессор работал
6,7 с (user + sys). Остальное время процесс ждал диск.

*H3 подтверждается.* `graph_traverse_mmap` быстрее примерно в 420 раз (1 МиБ)
и в 2000 раз (10 МиБ). Отношение 10 МиБ / 1 МиБ у неё 2,2 по средним и 4,7 по
медианам, а не 10. Для `graph_traverse_mmap` ключ `--no-cache` реализован
вызовами `madvise` и `msync` и не отключает page cache; файл читается
страницами (208 major faults на 10 МиБ) и записывается одним `msync`.

== Погрешность

Интервалы 1 МиБ и 10 МиБ не пересекаются у обеих программ (@fig-ci);
t-тест Уэлча: $p < 10^(-11)$ для `graph_traverse`, $p = 0,04$ для `graph_traverse_mmap`.

Разброс большой: CV 35% (`graph_traverse`, 1 МиБ), 9% (10 МиБ), 44–136% у
`graph_traverse_mmap`. Распределение двугорбое (@fig-dist). Во время
медленных запусков `r_await` устройства растёт с ≈ 0,11 до ≈ 0,30 мс, а число
чтений в секунду падает с ≈ 8000 до ≈ 3000 (лог `results-variant/logs/iostat-series.log`).

== Достаточность

Для полуширины ДИ 5% от среднего по формуле $N approx (t dot s \/ E)^2$ нужно
17 запусков (`graph_traverse`, 10 МиБ) и 256 (1 МиБ). Для сделанных выводов N = 10
достаточно: интервалы сравниваемых конфигураций не пересекаются. Увеличение N
сузит интервалы пропорционально $1 \/ sqrt(N)$.

== Условия измерения

- Состояние кэша определяет результат `graph_traverse_mmap`: без `drop_caches`
  файл остаётся в page cache. Для `graph_traverse` с `O_DIRECT` оно не влияет.
- Фоновые процессы. В первой серии (28.09) с работающим Firefox CV у
  `graph_traverse` был 68–79%, серия переделана.
- Разрешение таймера. `/usr/bin/time` даёт 10 мс; для `graph_traverse_mmap`
  использован таймер bash.

#include "intrusiveness.typ"

#pagebreak()
= Приложение А. Воспроизведение

```bash
cd lab/intro-exp
mkdir -p out
gcc -O2 -o out/graph_traverse      src/graph_traverse.c
gcc -O2 -o out/graph_traverse_mmap src/graph_traverse_mmap.c

sudo cpupower frequency-set -g performance
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo

./scripts/characterize_variant.sh 2
./scripts/collect_variant.sh results-variant/variant-10M-1M.csv 12 1 2
python3 scripts/analyze_variant.py results-variant/variant-10M-1M.csv report-variant/figures
```

= Приложение Б. Использование LLM

#table(
  columns: (auto, 1fr),
  [*Где*], [*Характер использования*],
  [Скрипты], [каркас скриптов сбора и обработки],
  [Отчёт], [вёрстка на Typst, таблицы из `summary.csv`],
)
