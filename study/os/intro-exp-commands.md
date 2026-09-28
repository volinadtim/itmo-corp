# Команды для ЛР1 (intro-exp) на машине `home`

Вариант: Write, No cache, 10M vs 1M, Rand.
Рабочий каталог везде: `~/projects/itmo-corp/study/os/os-course/lab/intro-exp`.

## 0. Подключение и переход в каталог

```bash
ssh home
cd ~/projects/itmo-corp/study/os/os-course/lab/intro-exp
```

## 1. Паспорт системы (шаг 4.1)

| Команда | Что показывает |
|---|---|
| `uname -a` | версия ядра, архитектура |
| `lscpu` | модель CPU, ядра, частоты, кэши L1/L2/L3 |
| `lscpu -e` | какие логические CPU делят одно физическое ядро (для `taskset`) |
| `free -h` | объём RAM и размер page cache в колонке `buff/cache` |
| `nproc` | число логических процессоров |
| `numactl --hardware` | NUMA-узлы (у нас один) |
| `lsblk -d -o NAME,SIZE,ROTA,MODEL` | диски; `ROTA=0` — SSD/NVMe, `1` — HDD |
| `df -h .` | на каком разделе лежат данные |
| `sudo smartctl -i /dev/nvme0n1` | модель накопителя, размер логического блока |
| `uptime` | подтверждение, что машина простаивает |

Всё сразу и в файл:

```bash
./scripts/characterize.sh 2
```

## 2. Настройка окружения (шаг 4.2)

```bash
sudo cpupower frequency-set -g performance   # зафиксировать частоту
cpupower frequency-info | head -20           # проверить, что governor = performance
cat /sys/devices/system/cpu/intel_pstate/no_turbo   # 1 = Turbo выключен
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo   # выключить Turbo
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches    # сбросить файловый кэш
```

Эффект сброса кэша виден по колонке `buff/cache`:

```bash
free -h | head -2
```

## 3. Генерация графов варианта

```bash
python3 ../util/graphgen.py -s 10M --seed 427 --topology chain \
        -b 0.5 --min-step-pages 2 -o data-variant/graph-rand-10M.bin

python3 ../util/graphgen.py -s 1M --seed 427 --topology chain \
        -b 0.5 --min-step-pages 2 -o data-variant/graph-rand-1M.bin
```

Смысл ключей: `-s` размер файла, `--seed` зерно (одинаковое, чтобы отличался
только размер), `--topology chain` связный список, `-b 0.5` доля переходов
назад, `--min-step-pages 2` минимальный прыжок в две страницы (гарантия, что
переход уходит на другую страницу).

Посмотреть параметры:

```bash
python3 ../util/graphgen.py --help
```

## 4. Сборка обходчиков

```bash
mkdir -p out
gcc -o out/graph_traverse      src/graph_traverse.c      -Wall -O2
gcc -o out/graph_traverse_mmap src/graph_traverse_mmap.c -Wall -O2
```

## 5. Одиночные запуски (шаг 4.3)

```bash
# базовый прогон
time ./out/graph_traverse 1 data-variant/graph-rand-10M.bin

# конфигурация варианта: запись + обход кэша
time ./out/graph_traverse --write --no-cache 1 data-variant/graph-rand-10M.bin
time ./out/graph_traverse --write --no-cache 1 data-variant/graph-rand-1M.bin
time ./out/graph_traverse_mmap --write --no-cache 1 data-variant/graph-rand-10M.bin
time ./out/graph_traverse_mmap --write --no-cache 1 data-variant/graph-rand-1M.bin

# справка по ключам
./out/graph_traverse --help
```

Подробные метрики одного запуска:

```bash
/usr/bin/time -v taskset -c 2 nice -n -5 \
    ./out/graph_traverse --write --no-cache 1 data-variant/graph-rand-1M.bin
```

Что читать в выводе: `Elapsed (wall clock)`, `User time`, `System time`,
`Minor/Major page faults`, `Involuntary context switches`.

Профиль системных вызовов (на 10 МБ не завершится, поэтому с таймаутом):

```bash
timeout -s INT 60 strace -c -f ./out/graph_traverse --write --no-cache 1 \
        data-variant/graph-rand-1M.bin
```

Прогон под фоновой нагрузкой:

```bash
stress-ng --cpu 6 --io 2 --timeout 60s &
time ./out/graph_traverse --write --no-cache 1 data-variant/graph-rand-1M.bin
```

## 6. Серия измерений

```bash
# короткая демонстрация на защите (3 повтора, пара минут)
./scripts/collect_variant.sh /tmp/demo.csv 3 1 2

# полная серия варианта (15 повторов, около 45 минут)
./scripts/collect_variant.sh results-variant/variant.csv 15 1 2
```

Аргументы: файл результата, число повторов, число итераций обхода за запуск,
номер ядра для `taskset`.

Следить за прогрессом:

```bash
wc -l results-variant/variant.csv       # строк = запусков + заголовок
tail -3 results-variant/variant.csv
```

## 7. Обработка и графики

```bash
~/venvs/os/bin/python scripts/analyze_variant.py results-variant/variant.csv \
        --outdir report-variant/figures --warmup 3
```

Выводит среднее, СКО, доверительный интервал 95%, коэффициент вариации,
удельное время на вершину и требуемое N. Графики и `summary.csv` кладёт
в `report-variant/figures/`.

## 8. Сборка отчёта

```bash
typst compile report-variant/report.typ     # PDF варианта
typst compile report/report.typ             # полный отчёт
typst watch report-variant/report.typ       # пересборка при каждом сохранении
```

## 9. Git

```bash
git status
git add -A && git commit -m "ЛР(intro-exp) ..."
git push origin lab-intro-exp
git fetch upstream && git merge upstream/main    # подтянуть обновления курса
```

## 10. Что нужно уметь показать на защите

По требованиям README (раздел 8) преподаватель может попросить:

1. прогнать генерацию графов и скрипт сбора прямо при нём — это пункты 3 и 6;
2. объяснить каждую команду из пункта 2 и зачем она нужна;
3. объяснить, как считается доверительный интервал в `analyze_variant.py`;
4. обосновать размер файла относительно объёма RAM.

Минимальная демонстрация целиком:

```bash
cd ~/projects/itmo-corp/study/os/os-course/lab/intro-exp
python3 ../util/graphgen.py -s 1M --seed 427 --topology chain -b 0.5 \
        --min-step-pages 2 -o /tmp/demo.bin
gcc -o out/graph_traverse src/graph_traverse.c -Wall -O2
/usr/bin/time -v ./out/graph_traverse --write --no-cache 1 /tmp/demo.bin
./scripts/collect_variant.sh /tmp/demo.csv 3 1 2
~/venvs/os/bin/python scripts/analyze_variant.py /tmp/demo.csv --outdir /tmp/fig --warmup 0
```
