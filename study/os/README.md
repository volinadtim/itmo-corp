# Операционные системы

Курс ОС ИТМО CSE (`secs-dev`).

## Репозитории

| Папка | Origin (приватный) | Upstream |
|---|---|---|
| `os-course/` | [volinadtim/os-course](https://github.com/volinadtim/os-course) | [secs-dev/os-course](https://github.com/secs-dev/os-course) |
| `xv6-riscv/` | — (ещё не создан) | [secs-dev/xv6-riscv](https://github.com/secs-dev/xv6-riscv) |

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
