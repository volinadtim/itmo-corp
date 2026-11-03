"""Аналитические формулы – независимая проверка численного решения СЛАУ.

Поток к прибору i – простейший с интенсивностью λ_i = q_i·λ (разрежение
простейшего потока), и приборы друг на друга не влияют. Поэтому процесс
распадается на независимые подсистемы, и вероятность состояния системы –
произведение вероятностей состояний приборов. Для каждого прибора есть
своя аналитика:

  * M/M/1/0 – Алиев, разд. 5.4.1:  p0 = 1/(1+y),  p1 = y/(1+y);
  * M/M/1/r – Алиев, разд. 5.4.3:  p_k = y^k·(1−y)/(1−y^(r+2));
  * M/E_k/1/r – формулы в явном виде у Алиева нет; считается методом
    вложенной цепи Маркова для M/G/1/K (моменты ухода заявок), это
    принципиально другой путь, чем граф переходов с фазами.
"""

from __future__ import annotations

from fractions import Fraction as F
from math import comb

from .ctmc import stationary


def mm10(y: F) -> list[F]:
    return [1 / (1 + y), y / (1 + y)]


def mm1r(y: F, r: int) -> list[F]:
    """Распределение числа заявок 0…r+1 в M/M/1/r."""
    if y == 1:
        return [F(1, r + 2)] * (r + 2)
    return [y**k * (1 - y) / (1 - y ** (r + 2)) for k in range(r + 2)]


def mek1(lam: F, b: F, k: int, capacity: int) -> list[F]:
    """Распределение числа заявок 0…K в M/E_k/1/K−1 через вложенную цепь.

    a_j – вероятность j поступлений за время обслуживания (Эрланг k-го
    порядка с интенсивностью фазы θ = k/b):  a_j = C(j+k−1, j)·s^k·(1−s)^j,
    s = θ/(λ+θ). Цепь в моменты ухода живёт на 0…K−1; стационарное
    распределение по времени (Gross & Harris, M/G/1/K):
        p_n = π_n / (π_0 + ρ),  n < K;   p_K = 1 − 1/(π_0 + ρ),  ρ = λb.
    """
    K = capacity
    theta = F(k) / b
    s = theta / (lam + theta)
    a = [comb(j + k - 1, j) * s**k * (1 - s) ** j for j in range(K)]

    # Матрица вероятностей переходов вложенной цепи (K−1 – «поглощает хвост»).
    P = [[F(0)] * K for _ in range(K)]
    for i in range(K):
        base = max(i - 1, 0)
        for j in range(base, K - 1):
            P[i][j] = a[j - base]
        P[i][K - 1] = 1 - sum(P[i][: K - 1])
    # π = π·P  ⇔  π·(P − I) = 0 – та же задача, что и для генератора.
    g = [[P[i][j] - (1 if i == j else 0) for j in range(K)] for i in range(K)]
    pi = stationary(g)
    rho = lam * b
    norm = pi[0] + rho
    return [pi[n] / norm for n in range(K)] + [1 - 1 / norm]


def device_distribution(lam: F, b: F, buffer: int, phases: int) -> list[F]:
    """Распределение числа заявок у прибора по аналитической формуле."""
    if phases == 1:
        return mm10(lam * b) if buffer == 0 else mm1r(lam * b, buffer)
    return mek1(lam, b, phases, buffer + 1)
