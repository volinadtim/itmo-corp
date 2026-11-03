"""Марковский процесс с непрерывным временем: матрица G и стационарный режим.

Стационарные вероятности – решение СЛАУ  P·G = 0,  Σ p_i = 1.
Одно из уравнений P·G = 0 линейно зависит от остальных (сумма строк G равна
нулю), поэтому последнее заменяется условием нормировки – так же поступает
и WinMark. Решение – метод Гаусса в точной арифметике (Fraction).
"""

from __future__ import annotations

from fractions import Fraction as F


def generator(n: int, rates: dict[tuple[int, int], F]) -> list[list[F]]:
    """Матрица интенсивностей переходов: g_ij – интенсивность i → j,
    диагональ g_ii = −Σ_{j≠i} g_ij (сумма каждой строки равна нулю)."""
    g = [[F(0)] * n for _ in range(n)]
    for (i, j), rate in rates.items():
        if i == j:
            raise ValueError("петля в графе переходов")
        g[i][j] += rate
    for i in range(n):
        g[i][i] = -sum(g[i][j] for j in range(n) if j != i)
    return g


def stationary(g: list[list[F]]) -> list[F]:
    """Стационарные вероятности: P·G = 0 с заменой последнего уравнения на Σp = 1."""
    n = len(g)
    # Уравнение j: Σ_i p_i g_ij = 0 – это j-я строка транспонированной G.
    a = [[g[i][j] for i in range(n)] + [F(0)] for j in range(n)]
    a[-1] = [F(1)] * n + [F(1)]

    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col] != 0), None)
        if pivot is None:
            raise ValueError("система вырождена: процесс не эргодический")
        a[col], a[pivot] = a[pivot], a[col]
        lead = a[col][col]
        a[col] = [v / lead for v in a[col]]
        for r in range(n):
            if r != col and a[r][col] != 0:
                k = a[r][col]
                a[r] = [vr - k * vc for vr, vc in zip(a[r], a[col])]
    return [a[i][n] for i in range(n)]


def residual(g: list[list[F]], p: list[F]) -> F:
    """max |(P·G)_j| – для точного решения равно нулю."""
    n = len(g)
    return max(abs(sum(p[i] * g[i][j] for i in range(n))) for j in range(n))
