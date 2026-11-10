#set text(font: "PT Serif", size: 12pt, lang: "ru")
#set page(margin: (top: 20mm, bottom: 20mm, left: 30mm, right: 15mm))
#set par(justify: true, first-line-indent: (amount: 1.25cm, all: true), leading: 0.8em)
#set heading(numbering: "1.1")
#show heading: it => { v(0.6em); it; v(0.4em) }
#show raw.where(block: true): it => block(
  fill: luma(245), inset: 8pt, radius: 3pt, width: 100%,
  text(size: 8.5pt, font: "Menlo", it),
)
#show raw.where(block: false): it => text(size: 10pt, font: "Menlo", it)
#set table(stroke: 0.4pt + luma(120), inset: 4pt)
#show table: set text(size: 9.5pt)
#show table: set par(justify: false, first-line-indent: 0pt)

#import "title.typ": titlepage

#let out(name) = raw(read("out/" + name), block: true)

#titlepage(
  work-kind: "Отчёт по лабораторной работе № 2",
  title: [LNX-4 VTKM: вывод `struct task_struct`\ через системный вызов\ #text(size: 12pt, weight: "regular")[(демонстрационное решение)]],
  student: "Данилов Тимофей Николаевич",
  group: "P3331",
  teacher: "Максимов Андрей Николаевич",
)

#set page(numbering: "1")
#counter(page).update(1)

= Задание

Программа пользователя получает аргумент (не адрес), передаёт его в ядро и печатает
поля найденной ядром структуры. Загружаемый модуль ядра принимает запрос, находит
структуру через системные таблицы и возвращает данные.

Вариант: интерфейс *syscall*, структура задаётся именем из заголовков Linux.
Выбрана `struct task_struct`, аргумент — PID.

= Решение

```text
./vtkm-cli PID
   │  syscall(549, pid, &info, sizeof info)
   ▼
ядро: SYSCALL_DEFINE3(vtkm)      заглушка, вшита в ядро патчем
   │  вызывает обработчик модуля; без модуля -ENOSYS
   ▼
vtkm.ko: PID → struct pid → task_struct → struct vtkm_info → copy_to_user
```

*Почему патч ядра.* Модуль не может сам добавить системный вызов: `sys_call_table`
не экспортируется, а x86-64 с версии 6.9 выбирает обработчик через `switch` в
`x64_sys_call`, собранный при компиляции ядра. Поэтому в ядро (Linux 6.18) добавлены
номер 549 и заглушка, а вся логика осталась в модуле, который регистрирует свой
обработчик при загрузке.

== Заглушка в ядре

```c
SYSCALL_DEFINE3(vtkm, int, pid, void __user *, buf, size_t, size)
{
	long ret = -ENOSYS;

	mutex_lock(&vtkm_lock);
	if (vtkm_handler)
		ret = vtkm_handler(pid, buf, size);
	mutex_unlock(&vtkm_lock);
	return ret;
}
```

Модуль ставит обработчик через `vtkm_register` и снимает через `vtkm_unregister`.
Мьютекс держится и во время вызова, поэтому `rmmod` ждёт, пока текущие вызовы
выйдут из модуля, и код модуля не выполняется после выгрузки.

== Модуль

```c
  if (size != sizeof(info))
    return -EINVAL;
  p = find_get_pid(nr);                 /* таблица PID */
  if (p == NULL)
    return -ESRCH;
  task = get_pid_task(p, PIDTYPE_PID);  /* +1 ссылка на task_struct */
  put_pid(p);
  if (task == NULL)
    return -ESRCH;

  memset(&info, 0, sizeof(info));
  fill_info(task, &info);               /* comm, pid, tgid, ppid, state, prio, ... */
  put_task_struct(task);

  if (copy_to_user(buf, &info, sizeof(info)) != 0)
    return -EFAULT;
```

Наружу копируется своя структура `vtkm_info` (общий заголовок модуля и программы)
только со значениями полей, без указателей ядра. `total_vm` берётся из `mm_struct`
через `get_task_mm`/`mmput`; у потоков ядра `mm` нет, поле остаётся 0.

Программа `vtkm-cli` проверяет аргумент, делает `syscall` и печатает поля; на
`ENOSYS` подсказывает загрузить модуль, на `ESRCH` пишет, что процесса нет.

= Проверка

Окружение: виртуальная машина `vtkm` (Ubuntu 24.04, ядро 6.18 с патчем).

#block(breakable: false, grid(
  columns: (1fr, 1fr),
  gutter: 8pt,
  [*`./vtkm-cli 1`* #out("o_pid1")],
  [*`/proc/1/status`* #out("o_status1")],
))

Значения совпадают с `/proc/1/status`, в том числе переключения контекста (4524, 910)
и память: 5503 страницы × 4 КиБ = 22012 kB = `VmSize`.

Скрипт `test.sh` проверяет PID 1, свой процесс, `nice`, поток ядра, PID потока,
ошибки и работу без модуля:

#block(breakable: false, out("o_test"))

= Выводы

Системный вызов реализован как заглушка в ядре и обработчик в загружаемом модуле:
так модуль можно пересобирать без пересборки ядра, а выгрузка безопасна благодаря
мьютексу. Задача ищется через таблицу PID с подсчётом ссылок, пользователю
передаются только значения полей через `copy_to_user`. Вывод совпадает с
`/proc/<pid>/status`, все проверки проходят.

Код: репозиторий `~/projects/vtkm-example` в ВМ `vtkm`, порядок работы — в истории
коммитов.

= Использование LLM

Код этого демонстрационного решения и отчёт сгенерированы Claude Opus 5.5
(Claude Code) по просьбе студента как пример выполнения работы. По правилам курса
ключевую логику нельзя писать через LLM, поэтому решение используется только для
разбора и не сдаётся как собственная работа.
