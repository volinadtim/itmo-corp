# Лабораторная работа 2. СЛАУ: Разложение Холецкого

Code&Test, задание `234ab1e0-ed1b-4a65-a8d4-88113ca21ea0`, задача `5c4b983d-fe24-4a18-b733-802a988a5fa5`. Порог 60, максимум 100.

[ДИСКЛЕЙМЕР: Это не всё, что вам нужно сделать для сдачи лабораторной работы по курсу, но этого достаточно, чтобы получить вариант на следующую работу. Проверьте требования и вариант в методическом пособии в файлах Teams.]

Решите систему линейных алгебраических уравнений, реализуя метод разложения Холецкого. Также выведите полученные промежуточные значения y.
Формат входных данных:
n
a11 a12 ... a1n b1
a21 a22 ... a2n b2
...
an1 an2 ... ann bn
Формат вывода:
x1
x2
...
xn
y1
y2
...
yn
, где x1..xn - значения неизвестных, а y1..yn - значения y.
Для систем, которые не имеют решений или имеют неограниченное количество решений, должно быть напечатано только следующее сообщение:
"The system has no roots of equations or has an infinite set of them.". Для этого задайте значение переменной isSolutionExists и сообщение об ошибке.

## Шаблон Python

```python
#!/bin/python3

import math
import os
import random
import re
import sys
class Solution:
    isSolutionExists = True
    errorMessage = ""

    #
    # Complete the 'solveByCholeskyDecomposition' function below.
    #
    # The function is expected to return a DOUBLE_ARRAY.
    # The function accepts following parameters:
    #  1. INTEGER n
    #  2. 2D_DOUBLE_ARRAY matrix
    #
    def solveByCholeskyDecomposition(n, matrix):
        if not Solution.checkSymmetry(n, matrix):
            return Solution.error()
        
        for i in range(1):
            for j in range(1):
                if matrix[i][j] <= 0:
                    return Solution.error()

        L = [[0] * n for i in range(n)]
        L[0][0] = matrix[0][0] ** 0.5
        for j in range(1, n):
            L[j][0] = matrix[j][0] / L[0][0]
        for i in range(1, n):
            L[i][i] = (matrix[i][i] - sum([L[i][p] ** 2 for p in range(i)])) ** 0.5   
            
            if L[i][i] == 0:
                return Solution.error()
            for j in range(i + 1, n):
                L[j][i] = (matrix[j][i] - sum([L[i][p] * L[j][p] for p in range(i)])) / L[i][i]

        B = [matrix[i][n] for i in range(n)]

        Lt = [[L[j][i] for j in range(len(L))][::-1] for i in range(len(L[0]))][::-1]

        Y = Solution.lin(n, L, B)
        X = Solution.lin(n, Lt, Y[::-1])[::-1]

        return X + Y


    def error():
        Solution.isSolutionExists = False
        Solution.errorMessage = 'The system has no roots of equations or has an infinite set of them'
        return None


    def checkSymmetry(n, matrix):
        for i in range(n):
            for j in range(i, n):
                if matrix[i][j] != matrix[j][i]:
                    return False
        return True
    
    def lin(n, L, B):
        Y = []

        for i in range(n):
            b = B[i]
            db = 0
            for j in range(i):
                db += Y[j] * L[i][j]
            y = (b - db) / L[i][i] 
            Y.append(y)
        
        return Y
if __name__ == '__main__':
    n = int(input().strip())

    matrix_rows = n
    matrix_columns = n + 1

    matrix = []

    for _ in range(matrix_rows):
        matrix.append(list(map(float, input().rstrip().split())))

    result = Solution.solveByCholeskyDecomposition(n, matrix)
    if Solution.isSolutionExists:
        print('\n'.join(map(str, result)))
    else:
        print(f"{Solution.errorMessage}")
    print("")

```
