"""Марковская модель многоканальной СМО с раздельными накопителями.

Заявка, поступившая в систему, с вероятностью p_i направляется к прибору П_i
и становится в его очередь, а если накопитель заполнен или отсутствует,
теряется. Поэтому состояние системы складывается из состояний приборов:

* экспоненциальный прибор: число заявок k = 0 … r+1 (одна на обслуживании,
  до r в накопителе);
* прибор с законом Эрланга k-го порядка: то же число заявок и номер фазы,
  на которой обслуживается заявка: обслуживание представлено k
  последовательными экспоненциальными фазами со средним b/k каждая
  (Алиев, разд. 5.5.3).

Стационарные вероятности находятся из системы pG = 0, Σp = 1, как в программе
MARK. Характеристики считаются через вероятности состояний; формулы Литтла
используются только для проверки.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Device:
    """Прибор П_i: вероятность занятия, ёмкость накопителя, число фаз."""

    name: str
    p: float
    buffer: int
    phases: int = 1  # 1: экспоненциальное обслуживание, k: Эрланг k-го порядка

    @property
    def law(self) -> str:
        return "M" if self.phases == 1 else f"E{self.phases}"


# Состояние прибора: (число заявок, фаза). Фаза 0: прибор свободен
# или обслуживание экспоненциальное.
DeviceState = tuple[int, int]
State = tuple[DeviceState, ...]


def device_states(dev: Device) -> list[DeviceState]:
    states: list[DeviceState] = [(0, 0)]
    for k in range(1, dev.buffer + 2):
        if dev.phases == 1:
            states.append((k, 0))
        else:
            states.extend((k, ph) for ph in range(1, dev.phases + 1))
    return states


def device_moves(dev: Device, s: DeviceState, lam_i: float, b: float):
    """Переходы одного прибора: (новое состояние, интенсивность, символ дуги)."""
    k, ph = s
    moves = []
    # Поступление заявки: при заполненном накопителе заявка теряется.
    if k < dev.buffer + 1:
        nxt = (1, 1 if dev.phases > 1 else 0) if k == 0 else (k + 1, ph)
        moves.append((nxt, lam_i, "lam"))
    if k == 0:
        return moves
    if dev.phases == 1:
        moves.append(((k - 1, 0), 1.0 / b, "mu"))
    else:
        rate = dev.phases / b
        if ph < dev.phases:
            moves.append(((k, ph + 1), rate, "mu"))
        else:
            # Конец последней фазы: заявка уходит, следующая начинает с фазы 1.
            moves.append(((k - 1, 1 if k > 1 else 0), rate, "mu"))
    return moves


@dataclass
class Chain:
    devices: tuple[Device, ...]
    lam: float
    b: float
    states: list[State]
    # (i, j) → интенсивность перехода E_i → E_j
    rates: dict[tuple[int, int], float]
    # (i, j) → символ дуги для графа: ("lam" | "mu", номер прибора)
    symbols: dict[tuple[int, int], tuple[str, int]] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return len(self.states)

    def matrix(self) -> list[list[float]]:
        """Матрица интенсивностей переходов G: g_ii = −Σ g_ij."""
        g = [[0.0] * self.n for _ in range(self.n)]
        for (i, j), r in self.rates.items():
            g[i][j] += r
            g[i][i] -= r
        return g


def build(devices: tuple[Device, ...], lam: float, b: float) -> Chain:
    # Перебор всех сочетаний состояний приборов, первый прибор в старшем разряде.
    states: list[State] = [()]
    for dev in devices:
        states = [s + (d,) for s in states for d in device_states(dev)]
    index = {s: i for i, s in enumerate(states)}

    rates: dict[tuple[int, int], float] = {}
    symbols: dict[tuple[int, int], tuple[str, int]] = {}
    for i, s in enumerate(states):
        for d, dev in enumerate(devices):
            for nxt, r, sym in device_moves(dev, s[d], lam * dev.p, b):
                j = index[s[:d] + (nxt,) + s[d + 1:]]
                rates[(i, j)] = rates.get((i, j), 0.0) + r
                symbols[(i, j)] = (sym, d)
    return Chain(devices, lam, b, states, rates, symbols)


def stationary(chain: Chain) -> list[float]:
    """Решение pG = 0, Σp = 1 методом Гаусса с выбором главного элемента.

    Уравнения баланса линейно зависимы, поэтому последнее заменяется
    условием нормировки.
    """
    n = chain.n
    g = chain.matrix()
    # Транспонируем, чтобы строка j была уравнением Σ_i p_i g_ij = 0.
    a = [[g[i][j] for i in range(n)] + [0.0] for j in range(n)]
    a[-1] = [1.0] * n + [1.0]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(a[r][col]))
        a[col], a[pivot] = a[pivot], a[col]
        lead = a[col][col]
        for r in range(n):
            if r != col and a[r][col] != 0.0:
                f = a[r][col] / lead
                row_c = a[col]
                row_r = a[r]
                for c in range(col, n + 1):
                    row_r[c] -= f * row_c[c]
    return [a[i][n] / a[i][i] for i in range(n)]


@dataclass(frozen=True)
class DeviceStats:
    """Характеристики одного прибора (или системы в целом)."""

    load: float          # нагрузка y = λ_i·b
    util: float          # загрузка ρ
    queue: float         # средняя длина очереди l
    count: float         # среднее число заявок m
    wait: float          # среднее время ожидания w
    stay: float          # среднее время пребывания u
    loss: float          # вероятность потери π
    throughput: float    # производительность λ'


@dataclass(frozen=True)
class Stats:
    devices: tuple[DeviceStats, ...]
    total: DeviceStats


def characteristics(chain: Chain, p: list[float]) -> Stats:
    per: list[DeviceStats] = []
    for d, dev in enumerate(chain.devices):
        lam_i = chain.lam * dev.p
        full = dev.buffer + 1
        util = sum(pi for pi, s in zip(p, chain.states) if s[d][0] > 0)
        queue = sum(pi * max(s[d][0] - 1, 0) for pi, s in zip(p, chain.states))
        count = sum(pi * s[d][0] for pi, s in zip(p, chain.states))
        # Поток пуассоновский, поэтому вероятность потери равна вероятности
        # того, что прибор занят и накопитель заполнен.
        loss = sum(pi for pi, s in zip(p, chain.states) if s[d][0] == full)
        thr = lam_i * (1.0 - loss)
        per.append(DeviceStats(
            load=lam_i * chain.b,
            util=util,
            queue=queue,
            count=count,
            wait=queue / thr if thr else 0.0,
            stay=count / thr if thr else 0.0,
            loss=loss,
            throughput=thr,
        ))

    thr = sum(s.throughput for s in per)
    queue = sum(s.queue for s in per)
    count = sum(s.count for s in per)
    total = DeviceStats(
        load=chain.lam * chain.b,
        util=sum(s.util for s in per) / len(per),
        queue=queue,
        count=count,
        wait=queue / thr,
        stay=count / thr,
        loss=1.0 - thr / chain.lam,
        throughput=thr,
    )
    return Stats(tuple(per), total)


def solve(devices: tuple[Device, ...], lam: float, b: float) -> tuple[Chain, list[float], Stats]:
    chain = build(devices, lam, b)
    p = stationary(chain)
    return chain, p, characteristics(chain, p)
