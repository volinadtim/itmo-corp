# Лабораторная работа 1. Аппроксимация и интерполяция: Аппроксимация по методу сигмоид

Code&Test, задание `1ebb3fea-2f9d-43fe-843e-d86e97465bb4`, задача `7e9ade3e-6f81-47cf-a6ae-6d545cdaa8e4`. Порог 60, максимум 100.

[ДИСКЛЕЙМЕР: Это не всё, что вам нужно сделать для сдачи лабораторной работы по курсу, но этого достаточно, чтобы получить вариант на следующую работу. Проверьте требования и вариант в методическом пособии в файлах Teams.]

Дан набор точек, по которым необходимо построить аппроксимацию по методу сигмоид. Необходимо найти значение наибольшего отклонения среди заданных точек относительно полученной аппроксимации.

Формат входных данных:
x1 x2 x3 ...
y1 y2 y3 ...


где x1...xn - список значений аргумента для узлов интерполяции, y1...yn - список значений функции для соответствующего значения аргумента для узлов интерполяции. В тестах также вначале задаётся количество задаваемых точек, однако, в функцию этот параметр не передаётся.

Формат выходных значений: вещественное число, являющееся значением наибольшего отклонения исходных данных от полученной аппроксимации.

## Шаблон Python

```python
#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'approximate_sigmoid' function below.
#
# The function is expected to return a DOUBLE.
# The function accepts following parameters:
#  1. DOUBLE_ARRAY x_axis
#  2. DOUBLE_ARRAY y_axis
#

def approximate_sigmoid(x_axis, y_axis):
    max_deviation = max(abs(y - 1 / (1 + math.exp(-x))) for x, y in zip(x_axis, y_axis))
    return max_deviation
if __name__ == '__main__':
    axis_count = int(input().strip())

    x_axis = list(map(float, input().rstrip().split()))

    y_axis = list(map(float, input().rstrip().split()))

    result = approximate_sigmoid(x_axis, y_axis)

    print(str(result) + '\n')

```
