# Операционные системы

Курс ОС ИТМО CSE (`secs-dev`).

## Репозитории

| Папка | Origin (приватный) | Upstream |
|---|---|---|
| `os-course/` | [volinadtim/os-course](https://github.com/volinadtim/os-course) | [secs-dev/os-course](https://github.com/secs-dev/os-course) |
| `xv6-riscv/` | [volinadtim/xv6-riscv](https://github.com/volinadtim/xv6-riscv) | [secs-dev/xv6-riscv](https://github.com/secs-dev/xv6-riscv) |

Клоны — отдельные git-репозитории, игнорируются в `itmo-corp`.

Подтянуть обновления курса:

```bash
git -C os-course fetch upstream && git -C os-course merge upstream/main
```

## Сдача

Ветка `lab-<slug>` → PR в `main` → CI → ревью преподавателя → защита.
Подробно: `os-course/doc/process.md`.

## 💡 Доп. баллы за баги

В лабораторных работах можно находить баги (в заданиях, тестах, CI, коде курса)
и исправлять их — за это дают **доп. балл**, если сдать эту работу **первым**.

### Найденные баги

**intro-exp**
- [x] `src/graph_traverse*.c`: на macOS `#include <sys/endian.h>` — такого файла нет
  (он из FreeBSD). Исправлено локально через `<libkern/OSByteOrder.h>` + макросы
  `le64toh/le32toh/htole64`. Не закоммичено.
- [ ] **`graph_traverse.c`: `--no-cache` не работает на Linux.** `O_DIRECT` требует
  выравнивания буфера/смещения/длины на 512 байт, а заголовок читается как 40 байт
  в невыровненный буфер → `read() = EINVAL`, программа падает с
  `Failed to read header`. Проверено strace на Ubuntu 24.04, ext4/NVMe.
  Следствие: холодный кэш на Linux приходится делать через `drop_caches`.
  Фикс: читать через выровненный буфер (`posix_memalign`, кратно 512) либо
  заменить `O_DIRECT` на `posix_fadvise(POSIX_FADV_DONTNEED)`.
- [ ] `gcc -Wall -O2` на Linux: `graph_traverse.c:232` — `'child' may be used
  uninitialized` (путь, где `degree == 0`). Проверить логику.
- [ ] **README, раздел 2: две «разные» топологии на деле одинаковы.** `--topology chain`
  лишь форсирует `fanout=1`, а он и так 1 по умолчанию; `--min-step-pages` в обеих
  командах одинаков (2). Единственное отличие — `backprob` 0.5 против 0.7.
  Замер медианы |Δ| между соседними вершинами обхода (16M, seed 427):
  `-b 0.5` → 641 стр., `-b 0.7` → 429 стр. Обе конфигурации «случайные»,
  локальности нет ни в одной, и время обхода совпадает в пределах ДИ.
  Настоящая локальность получается при `-b 0 --min-step-pages 0`: медиана 5 стр.,
  36% переходов внутри одной страницы.
- [ ] README: `-b/--branching` «фактор ветвления», а в `graphgen.py` это
  `-b/--backprob` — вероятность обратного перехода.
- [ ] `cheat-sheet.md`: разные seed (427 и 42), README требует одинаковый.
- [ ] README, каркас скрипта: `Elapsed (wall clock)` из `/usr/bin/time -v` в формате
  `m:ss.ss`, а колонка называется `wall_time_s` — нужна конвертация (проверить на Linux).

## Лабы

### os-course
- intro-exp 🟢, project 🔴
- Многозадачность: vtsh 🟢 → corosched 🟡, corohttp 🟡
- ФС: vtpc 🟡 → vtfs 🔴, fuse 🟡
- Linux: vtkm 🟢, bpf-xdp 🟡

### xv6-riscv
- Intro → backtrace 🟢 → flamegraph 🟡, halt 🟢
- ФС: shebang 🟡, symlink 🟡, ext 🔴
- Многозадачность: filealloc 🟢 → allocproc 🟡, mlfq 🟡; thread 🟡, alarm 🔴
- Память: pteprint → shmem 🟡, aslr 🔴, cow 🟡 → lazyalloc 🟡, hugepage 🔴, swap 🔴
- Сеть: nic 🔴
