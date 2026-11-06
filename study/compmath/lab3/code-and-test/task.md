# Лабораторная работа 3. Решение систем нелинейных уравнений: Метод простых итераций

Code&Test, задание `8ec3963e-d15d-4af4-b514-7859651b75da`, задача `0669b06f-3a33-432c-8d5e-a5eec29b43cc`. Порог 60, максимум 100. Вариант выдан после смены Перл 28.10.2026, снято 06.11.2026. Прежний вариант (метод Ньютона) — [task-old-newton.md](task-old-newton.md).

[ДИСКЛЕЙМЕР: Это не всё, что вам нужно сделать для сдачи лабораторной работы по курсу, но этого достаточно, чтобы получить вариант на следующую работу. Проверьте требования и вариант в методическом пособии в файлах Teams.]

Дана система нелинейных уравнений. По заданному начальному приближению необходимо найти решение системы с точностью до 5 верного знака после запятой при помощи метода простых итераций.

Формат входных данных:
k
n
x0
y0
...

где k - номер системы, n - количество уравнений и количество неизвестных, а остальные значения - начальные приближения для соответствующих неизвестных.

Формат выходных данных: список такого же типа данных, как списки входных данных, содержащие значения корня для каждой из неизвестных с точностью до 5 верного знака.

## Шаблон Python

```python
#!/bin/python3

import math
import os
import random
import re
import sys


def first_function(args: []) -> float:
    return math.sin(args[0])


def second_function(args: []) -> float:
    return (args[0] * args[1]) / 2


def third_function(args: []) -> float:
    return pow(args[0], 2) * pow(args[1], 2) - 3 * pow(args[0], 3) - 6 * pow(args[1], 3) + 8


def fourth_function(args: []) -> float:
    return pow(args[0], 4) - 9 * args[1] + 2


def fifth_function(args: []) -> float:
    return args[0] + pow(args[0], 2) - 2 * args[1] * args[2] - 0.1


def six_function(args: []) -> float:
    return args[1] + pow(args[1], 2) + 3 * args[0] * args[2] + 0.2


def seven_function(args: []) -> float:
    return args[2] + pow(args[2], 2) + 2 * args[0] * args[1] - 0.3


def default_function(args: []) -> float:
    return 0.0


# How to use this function:
# funcs = Result.get_functions(4)
# funcs[0](0.01)
def get_functions(n: int):
    if n == 1:
        return [first_function, second_function]
    elif n == 2:
        return [third_function, fourth_function]
    elif n == 3:
        return [fifth_function, six_function, seven_function]
    else:
        return [default_function]


#
# Complete the 'solve_by_fixed_point_iterations' function below.
#
# The function is expected to return a DOUBLE_ARRAY.
# The function accepts following parameters:
#  1. INTEGER system_id
#  2. INTEGER number_of_unknowns
#  3. DOUBLE_ARRAY initial_approximations
#

def solve_by_fixed_point_iterations(system_id, number_of_unknowns, initial_approximations):
    # Write your code here

if __name__ == '__main__':
    system_id = int(input().strip())

    number_of_unknowns = int(input().strip())

    initial_approximations = []

    for _ in range(number_of_unknowns):
        initial_approximations_item = float(input().strip())
        initial_approximations.append(initial_approximations_item)

    result = solve_by_fixed_point_iterations(system_id, number_of_unknowns, initial_approximations)

    print('\n'.join(map(str, result)))
```
