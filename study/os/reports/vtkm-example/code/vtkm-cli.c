/*
 * vtkm-cli PID
 * Спрашивает у ядра через системный вызов vtkm поля struct task_struct
 * процесса PID и печатает их.
 */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "vtkm_info.h"

static const char *policy_name(unsigned int policy) {
  switch (policy) {
  case 0: return "SCHED_OTHER";
  case 1: return "SCHED_FIFO";
  case 2: return "SCHED_RR";
  case 3: return "SCHED_BATCH";
  case 5: return "SCHED_IDLE";
  case 6: return "SCHED_DEADLINE";
  case 7: return "SCHED_EXT";
  default: return "?";
  }
}

int main(int argc, char *argv[]) {
  struct vtkm_info info;
  char *end;
  long pid;
  long ret;

  if (argc != 2) {
    fprintf(stderr, "usage: %s PID\n", argv[0]);
    return 2;
  }

  pid = strtol(argv[1], &end, 10);
  if (*argv[1] == '\0' || *end != '\0' || pid <= 0 || pid > 4194304) {
    fprintf(stderr, "bad PID: %s\n", argv[1]);
    return 2;
  }

  ret = syscall(VTKM_SYSCALL_NR, (int)pid, &info, sizeof(info));
  if (ret != 0) {
    if (errno == ENOSYS)
      fprintf(stderr, "vtkm: no handler, is module vtkm.ko loaded?\n");
    else if (errno == ESRCH)
      fprintf(stderr, "vtkm: no process with PID %ld\n", pid);
    else
      fprintf(stderr, "vtkm: %s\n", strerror(errno));
    return 1;
  }

  printf("struct task_struct of PID %ld\n", pid);
  printf("  comm         %s\n", info.comm);
  printf("  pid          %d\n", info.pid);
  printf("  tgid         %d\n", info.tgid);
  printf("  ppid         %d\n", info.ppid);
  printf("  state        %c\n", info.state);
  printf("  prio         %d\n", info.prio);
  printf("  static_prio  %d (nice %d)\n", info.static_prio, info.static_prio - 120);
  printf("  policy       %u (%s)\n", info.policy, policy_name(info.policy));
  printf("  threads      %d\n", info.nr_threads);
  printf("  utime        %llu ns\n", (unsigned long long)info.utime_ns);
  printf("  stime        %llu ns\n", (unsigned long long)info.stime_ns);
  printf("  nvcsw        %llu\n", (unsigned long long)info.nvcsw);
  printf("  nivcsw       %llu\n", (unsigned long long)info.nivcsw);
  printf("  total_vm     %llu pages (%llu kB)\n",
         (unsigned long long)info.total_vm,
         (unsigned long long)info.total_vm * (unsigned long long)getpagesize() / 1024);
  return 0;
}
