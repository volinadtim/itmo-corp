#!/bin/bash
# Проверки vtkm. Запуск: make && ./test.sh
# Модуль скрипт загружает и выгружает сам (нужен sudo).

ok=0
fail=0

check() {
  # check "название" команда-проверка
  if eval "$2"; then
    echo "OK   $1"
    ok=$((ok + 1))
  else
    echo "FAIL $1"
    fail=$((fail + 1))
  fi
}

# Значение поля из вывода vtkm-cli: field PID имя
field() {
  ./vtkm-cli "$1" | awk -v f="$2" '$1 == f { print $2 }'
}

# Значение строки из /proc/PID/status: status PID Имя
status() {
  awk -v f="$2:" '$1 == f { print $2 }' "/proc/$1/status"
}

sudo rmmod vtkm 2>/dev/null

# 1. Без модуля заглушка ядра отвечает ENOSYS
check "без модуля: ENOSYS и подсказка" \
  '[ "$(./vtkm-cli 1 2>&1)" = "vtkm: no handler, is module vtkm.ko loaded?" ]'

sudo insmod src/vtkm.ko

# 2. PID 1 сверяем с /proc/1/status
check "PID 1: comm"  '[ "$(field 1 comm)" = "$(status 1 Name)" ]'
check "PID 1: ppid"  '[ "$(field 1 ppid)" = "$(status 1 PPid)" ]'
check "PID 1: state" '[ "$(field 1 state)" = "$(status 1 State)" ]'

# 3. Свой процесс: sleep в фоне
sleep 30 &
p=$!
sleep 0.2
check "sleep: comm sleep"     '[ "$(field $p comm)" = "sleep" ]'
check "sleep: ppid = этот скрипт" '[ "$(field $p ppid)" = "$$" ]'
check "sleep: state S"        '[ "$(field $p state)" = "S" ]'
kill $p

# 4. nice 10 даёт static_prio 130
nice -n 10 sleep 30 &
p=$!
sleep 0.2
check "nice 10: static_prio 130" '[ "$(field $p static_prio)" = "130" ]'
kill $p

# 5. Поток ядра kthreadd (PID 2): mm нет, total_vm 0
check "PID 2: kthreadd, total_vm 0" \
  '[ "$(field 2 comm)" = "kthreadd" ] && [ "$(field 2 total_vm)" = "0" ]'

# 6. PID потока: pid = id потока, tgid = id процесса
for d in /proc/[0-9]*/task/*; do
  t=${d##*/}
  pr=$(echo "$d" | cut -d/ -f3)
  if [ "$t" != "$pr" ]; then tid=$t; break; fi
done
check "поток $tid: pid $tid, tgid $pr" \
  '[ "$(field $tid pid)" = "$tid" ] && [ "$(field $tid tgid)" = "$pr" ]'

# 7. Ошибки
check "нет такого PID: код 1" './vtkm-cli 4000000 >/dev/null 2>&1; [ $? -eq 1 ]'
check "буквы вместо PID: код 2" './vtkm-cli abc >/dev/null 2>&1; [ $? -eq 2 ]'
check "без аргумента: код 2"   './vtkm-cli >/dev/null 2>&1; [ $? -eq 2 ]'
check "PID 0: код 2"           './vtkm-cli 0 >/dev/null 2>&1; [ $? -eq 2 ]'

# 8. После выгрузки снова ENOSYS
sudo rmmod vtkm
check "после rmmod: код 1" './vtkm-cli 1 >/dev/null 2>&1; [ $? -eq 1 ]'

echo "passed $ok, failed $fail"
[ $fail -eq 0 ]
