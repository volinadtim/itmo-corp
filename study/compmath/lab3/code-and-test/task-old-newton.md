# Лабораторная работа 3. Решение систем нелинейных уравнений: Метод Ньютона

Code&Test, задание `8ec3963e-d15d-4af4-b514-7859651b75da`, задача `e4589654-4c72-44aa-8566-3daf39085d43`. Порог 60, максимум 100.

[ДИСКЛЕЙМЕР: Это не всё, что вам нужно сделать для сдачи лабораторной работы по курсу, но этого достаточно, чтобы получить вариант на следующую работу. Проверьте требования и вариант в методическом пособии в файлах Teams.]

Дана система нелинейных уравнений. По заданному начальному приближению необходимо найти решение системы с точностью до 5 верного знака после запятой при помощи метода Ньютона.

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


k = 0.4
a = 0.9

def first_function(args: []) -> float:
    return math.sin(args[0])


def second_function(args: []) -> float:
    return (args[0] * args[1]) / 2


def third_function(args: []) -> float:
    return math.tan(args[0]*args[1] + k) - pow(args[0], 2)


def fourth_function(args: []) -> float:
    return a * pow(args[0], 2) + 2 * pow(args[1], 2) - 1


def fifth_function(args: []) -> float:
    return pow(args[0], 2) + pow(args[1], 2) + pow(args[2], 2) - 1


def six_function(args: []) -> float:
    return 2 * pow(args[0], 2) + pow(args[1], 2) - 4 * args[2]


def seven_function(args: []) -> float:
    return 3 * pow(args[0], 2) - 4 * args[1] + pow(args[2], 2)


def default_function(args: []) -> float:
    return 0.0


# How to use this function:
# funcs = Result.get_functions(4)
# funcs[0](0.01)
def get_functions(n: int):
    if n == 1:
        return [first_function, second_function]
    elif n == 2:
        k = 0.4
        a = 0.9
        return [third_function, fourth_function]
    elif n == 3:
        k = 0
        a = 0.5
        return [third_function, fourth_function]
    elif n == 4:
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
def first_deriative_1(args: []) -> float:
    return math.cos(args[0])


def first_deriative_2(args: []) -> float:
    return 1


def second_deriative_1(args: []) -> float:
    return args[0] / 2


def second_deriative_2(args: []) -> float:
    return args[1] / 2


def third_deriative_1(args: []) -> float:
    return (1 / math.cos(args[0] * args[1] + k) ** 2) * args[1] - 2 * args[0]


def third_deriative_2(args: []) -> float:
    return (1 / math.cos(args[0] * args[1] + k) ** 2) * args[0]


def fourth_deriative_1(args: []) -> float:
    return 2 * a * args[0]


def fourth_deriative_2(args: []) -> float:
    return 4 * args[1]


def fifth_deriative_1(args: []) -> float:
    return 2 * args[0]


def fifth_deriative_2(args: []) -> float:
    return 2 * args[1]


def fifth_deriative_3(args: []) -> float:
    return 2 * args[2]


def six_deriative_1(args: []) -> float:
    return 4 * args[0]


def six_deriative_2(args: []) -> float:
    return 2 * args[1]


def six_deriative_3(args: []) -> float:
    return -4


def seven_deriative_1(args: []) -> float:
    return 6 * args[0]


def seven_deriative_2(args: []) -> float:
    return -4


def seven_deriative_3(args: []) -> float:
    return 2 * args[2]


def jacobian(n: int, args: []):
    if n == 1:
        return [[first_deriative_1(args), first_deriative_2(args)], [second_deriative_1(args),
                                                                     second_deriative_2(args)]]
    if n == 2:
        return [[third_deriative_1(args), third_deriative_2(args)],
                [fourth_deriative_1(args), fourth_deriative_2(args)]]
    if n == 3:
        return [[third_deriative_1(args), third_deriative_2(args)],
                [fourth_deriative_1(args), fourth_deriative_2(args)]]
    if n == 4:
        return [[fifth_deriative_1(args), fifth_deriative_2(args), fifth_deriative_3(args)],
                [six_deriative_1(args), six_deriative_2(args), six_deriative_3(args)],
                [seven_deriative_1(args), seven_deriative_2(args), seven_deriative_3(args)]]
    else:
        return [[default_function(args)]]


def solve_by_fixed_point_iterations(system_id, number_of_unknowns, initial_approximations):
    if system_id > 2:
        return initial_approximations
    values = initial_approximations
    eps = 1e-5
    funcs = get_functions(system_id)
    iterations = 1000
    for _ in range(iterations):
        try:
            f = [funcs[i](values) for i in range(number_of_unknowns)]
        except ValueError:
            return values
        J = jacobian(system_id, values)
        J_inversion = [[J[j][i] for j in range(len(J))] for i in range(len(J[0]))]
        delta = []
        for i in range(number_of_unknowns):
            delta.append(-sum([J_inversion[i][k] * f[k] for k in range(number_of_unknowns)]))
        if abs(max(delta)) < eps:
            return values
        values = [values[i] + delta[i] for i in range(number_of_unknowns)]
    return values

if __name__ == '__main__':
    system_id = int(input().strip())

    number_of_unknowns = int(input().strip())

    initial_approximations = []

    for _ in range(number_of_unknowns):
        initial_approximations_item = float(input().strip())
        initial_approximations.append(initial_approximations_item)

    result = solve_by_fixed_point_iterations(system_id, number_of_unknowns, initial_approximations)

    print('\n'.join(map(str, result)))
    print('\n')
```
