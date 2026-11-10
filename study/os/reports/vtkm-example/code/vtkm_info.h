/*
 * Формат ответа системного вызова vtkm.
 * Этот файл подключают и модуль ядра, и программа vtkm-cli,
 * поэтому раскладка полей у них одинаковая.
 */
#ifndef VTKM_INFO_H
#define VTKM_INFO_H

#include <linux/types.h>

#define VTKM_SYSCALL_NR 549
#define VTKM_COMM_LEN 16

/* Значения полей struct task_struct (указатели не отдаём) */
struct vtkm_info {
  char comm[VTKM_COMM_LEN]; /* имя программы */
  __s32 pid;                /* id потока */
  __s32 tgid;               /* id процесса (группы потоков) */
  __s32 ppid;               /* id родителя */
  __s32 state;              /* символ состояния: R, S, D, T, Z ... */
  __s32 prio;               /* текущий приоритет планировщика */
  __s32 static_prio;        /* приоритет от nice: 120 + nice */
  __u32 policy;             /* политика: 0 SCHED_OTHER, 1 FIFO, 2 RR ... */
  __s32 nr_threads;         /* число потоков в процессе */
  __u64 utime_ns;           /* время в user mode, нс */
  __u64 stime_ns;           /* время в kernel mode, нс */
  __u64 nvcsw;              /* добровольные переключения контекста */
  __u64 nivcsw;             /* принудительные переключения контекста */
  __u64 total_vm;           /* размер виртуальной памяти, страниц (0 у потоков ядра) */
};

#endif
