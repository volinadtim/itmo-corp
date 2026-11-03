"""Исходные данные варианта: таблицы 1 и 2 задания УИР 2.

Номер варианта УИР 2 выдаётся как N1/N2/NG. Для варианта 60 группы P3331:
N1 = N2 = 60 (строка 60 таблицы 1 для обеих систем), NG = 31 (последние две
цифры номера группы, строка 31 таблицы 2).

Все параметры хранятся как Fraction: стационарные вероятности тогда
получаются точными дробями, и проверки сходятся до последнего знака,
а не «в пределах 1e-9».
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

N1 = 60
N2 = 60
NG = 31

# Таблица 1, строка 60:
#   СИСТЕМА_1: П = 3, ЕН = 0/3/0, критерий варианта N1 – (д)
#   СИСТЕМА_2: П = 2 (E2), ЕН = 0/3, критерий варианта N2 – (д)
TABLE1_ROW = {
    "system1": {"devices": 3, "buffers": (0, 3, 0), "erlang": None},
    "system2": {"devices": 2, "buffers": (0, 3), "erlang": 2},
    "criterion1": "д",
    "criterion2": "д",
}

# Таблица 2, строка 31: λ = 0,6 1/с, b = 10 с, вероятности занятия П1/П2/П3.
LAMBDA = F(6, 10)
B = F(10)
PROBS3 = (F(75, 100), F(15, 100), F(10, 100))

CRITERIA = {
    "а": "максимальная производительность системы",
    "б": "минимальные потери заявок",
    "в": "максимальная загрузка системы",
    "г": "минимальное время пребывания заявок в системе",
    "д": "минимальная суммарная длина очередей заявок",
}


def criterion_letter(n1: int = N1, n2: int = N2) -> str:
    """Указание 3 к таблице 1: нечётная сумма – критерий N1, чётная – N2."""
    row = TABLE1_ROW
    return row["criterion1"] if (n1 + n2) % 2 else row["criterion2"]


def routing(devices: int) -> tuple[F, ...]:
    """Вероятности занятия приборов по указаниям к таблице 2."""
    p1, p2, p3 = PROBS3
    if devices == 3:
        return PROBS3
    if devices == 2:
        return (p1, p2 + p3)
    if devices == 1:
        return (F(1),)
    raise ValueError(f"нет правила для {devices} приборов")


@dataclass(frozen=True)
class Device:
    """Прибор со своим накопителем.

    buffer – ёмкость накопителя перед прибором (0 – накопителя нет);
    phases – порядок Эрланга длительности обслуживания (1 – экспонента);
    share – вероятность того, что заявка направляется к этому прибору.
    """

    index: int
    buffer: int
    phases: int
    share: F

    @property
    def capacity(self) -> int:
        """Сколько заявок может находиться у прибора: в накопителе + на обслуживании."""
        return self.buffer + 1

    @property
    def law(self) -> str:
        return "экспоненциальный" if self.phases == 1 else f"Эрланга {self.phases}-го порядка"


@dataclass(frozen=True)
class SystemSpec:
    name: str
    devices: tuple[Device, ...]
    lam: F
    b: F

    @property
    def mu(self) -> F:
        return 1 / self.b

    def lam_i(self, device: Device) -> F:
        return self.lam * device.share


def system1(lam: F = LAMBDA, b: F = B) -> SystemSpec:
    spec = TABLE1_ROW["system1"]
    shares = routing(spec["devices"])
    devices = tuple(
        Device(i + 1, buf, 1, shares[i]) for i, buf in enumerate(spec["buffers"])
    )
    return SystemSpec("СИСТЕМА_1", devices, F(lam), F(b))


# Задание: «в одном из приборов (любом) длительность обслуживания распределена
# по закону Эрланга». Выбран П2 – единственный прибор с накопителем. На П1
# (без накопителя) закон обслуживания на характеристики не влияет вовсе
# (инвариантность систем с потерями), см. README и тесты.
ERLANG_DEVICE = 2


def system2(lam: F = LAMBDA, b: F = B, erlang_device: int = ERLANG_DEVICE) -> SystemSpec:
    spec = TABLE1_ROW["system2"]
    shares = routing(spec["devices"])
    devices = tuple(
        Device(i + 1, buf, spec["erlang"] if i + 1 == erlang_device else 1, shares[i])
        for i, buf in enumerate(spec["buffers"])
    )
    return SystemSpec("СИСТЕМА_2", devices, F(lam), F(b))
