#include <linux/init.h>
#include <linux/module.h>
#include <linux/printk.h>
#include <linux/pid.h>
#include <linux/sched.h>
#include <linux/sched/mm.h>
#include <linux/sched/signal.h>
#include <linux/sched/task.h>
#include <linux/string.h>
#include <linux/uaccess.h>
#include <linux/vtkm.h>

#include "vtkm_info.h"

#define MODULE_NAME "vtkm"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("secs-dev");
MODULE_DESCRIPTION("A simple kernel module");

#define LOG(fmt, ...) pr_info("[" MODULE_NAME "]: " fmt, ##__VA_ARGS__)

/* Скопировать нужные поля task_struct в ответ */
static void fill_info(struct task_struct *task, struct vtkm_info *info) {
  struct mm_struct *mm;

  get_task_comm(info->comm, task);
  info->pid = task->pid;
  info->tgid = task->tgid;
  info->ppid = task_ppid_nr(task);
  info->state = task_state_to_char(task);
  info->prio = task->prio;
  info->static_prio = task->static_prio;
  info->policy = task->policy;
  info->nr_threads = get_nr_threads(task);
  info->utime_ns = task->utime;
  info->stime_ns = task->stime;
  info->nvcsw = task->nvcsw;
  info->nivcsw = task->nivcsw;

  /* У потоков ядра нет mm, тогда get_task_mm вернёт NULL */
  mm = get_task_mm(task);
  if (mm != NULL) {
    info->total_vm = mm->total_vm;
    mmput(mm);
  }
}

/* Обработчик системного вызова vtkm(pid, buf, size) */
static long vtkm_handler(int nr, void __user *buf, size_t size) {
  struct pid *p;
  struct task_struct *task;
  struct vtkm_info info;

  if (size != sizeof(info))
    return -EINVAL;

  /* PID -> struct pid (таблица PID ядра), счётчик ссылок +1 */
  p = find_get_pid(nr);
  if (p == NULL)
    return -ESRCH;

  /* struct pid -> struct task_struct, счётчик ссылок задачи +1 */
  task = get_pid_task(p, PIDTYPE_PID);
  put_pid(p);
  if (task == NULL)
    return -ESRCH;

  memset(&info, 0, sizeof(info));
  fill_info(task, &info);
  put_task_struct(task);

  if (copy_to_user(buf, &info, sizeof(info)) != 0)
    return -EFAULT;

  LOG("answered for pid %d\n", nr);
  return 0;
}

static int __init vtkm_init(void) {
  int ret;

  ret = vtkm_register(vtkm_handler);
  if (ret != 0) {
    LOG("can't register handler: %d\n", ret);
    return ret;
  }
  LOG("VTKM joined the kernel\n");
  return 0;
}

static void __exit vtkm_exit(void) {
  vtkm_unregister();
  LOG("VTKM left the kernel\n");
}

module_init(vtkm_init);
module_exit(vtkm_exit);
