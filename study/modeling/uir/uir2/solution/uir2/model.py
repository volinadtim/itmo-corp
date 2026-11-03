"""Марковская модель СМО с раздельными накопителями.

Кодирование состояний. Поток заявок простейший, к прибору i заявка
направляется с вероятностью q_i, поэтому на прибор i приходит простейший поток
λ_i = q_i·λ. Состояние прибора – число заявок у него n_i = 0…r_i+1
(r_i – ёмкость накопителя), а при эрланговском обслуживании ещё и фаза f,
на которой обслуживается текущая заявка: «2₁» – две заявки, обслуживание
на первой фазе. Состояние системы – набор состояний всех приборов.

Переходы:
  * поступление к прибору i (если у него есть место): n_i → n_i + 1, λ_i;
  * экспоненциальное обслуживание: n_i → n_i − 1, μ = 1/b;
  * Эрланг k-го порядка: фаза f → f + 1 с интенсивностью kμ, после
    последней фазы заявка уходит (n_i → n_i − 1, следующая начинает с фазы 1).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from fractions import Fraction as F

from . import ctmc
from .variant import Device, SystemSpec

SUBSCRIPT = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

Local = tuple[int, int]  # (n – число заявок у прибора, f – фаза; f = 0 при n = 0)


def local_states(device: Device) -> list[Local]:
    states: list[Local] = [(0, 0)]
    for n in range(1, device.capacity + 1):
        for f in range(1, device.phases + 1):
            states.append((n, f))
    return states


def local_code(device: Device, local: Local) -> str:
    n, f = local
    if device.phases == 1 or n == 0:
        return str(n)
    return f"{n}{str(f).translate(SUBSCRIPT)}"


@dataclass(frozen=True)
class Transition:
    src: int
    dst: int
    rate: F
    label: str     # обозначение на графе: λ1, μ, 2μ
    element: str   # имя элемента WinMark: la1, mu, mu2
    device: int
    kind: str      # "arrival" | "phase" | "departure"


@dataclass
class Model:
    spec: SystemSpec
    states: list[tuple[Local, ...]]
    transitions: list[Transition]
    g: list[list[F]] = field(repr=False)
    p: list[F] = field(repr=False)

    @property
    def n(self) -> int:
        return len(self.states)

    def code(self, s: int) -> str:
        parts = (local_code(d, loc) for d, loc in zip(self.spec.devices, self.states[s]))
        return "(" + ", ".join(parts) + ")"

    def where(self, predicate) -> list[int]:
        """Номера состояний, для которых predicate(состояние) истинно."""
        return [i for i, st in enumerate(self.states) if predicate(st)]

    def prob(self, indices) -> F:
        return sum((self.p[i] for i in indices), F(0))

    def elements(self) -> dict[str, F]:
        """Элементы матрицы для WinMark: имя → значение."""
        out: dict[str, F] = {}
        for t in self.transitions:
            out.setdefault(t.element, t.rate)
        return dict(sorted(out.items(), key=lambda kv: (kv[0][0] != "l", kv[0])))


def _device_moves(spec: SystemSpec, device: Device, local: Local):
    """Переходы одного прибора из локального состояния: (новое, rate, label, element, kind)."""
    n, f = local
    lam = spec.lam_i(device)
    if n < device.capacity:
        yield (n + 1, f if n else 1), lam, f"λ{device.index}", f"la{device.index}", "arrival"
    if n == 0:
        return
    k = device.phases
    rate = k * spec.mu
    label = "μ" if k == 1 else f"{k}μ"
    element = "mu" if k == 1 else f"mu{k}"
    if f < k:
        yield (n, f + 1), rate, label, element, "phase"
    else:
        yield ((n - 1, 1) if n > 1 else (0, 0)), rate, label, element, "departure"


def build(spec: SystemSpec) -> Model:
    states = list(itertools.product(*(local_states(d) for d in spec.devices)))
    index = {st: i for i, st in enumerate(states)}

    transitions: list[Transition] = []
    for i, st in enumerate(states):
        for pos, device in enumerate(spec.devices):
            for new_local, rate, label, element, kind in _device_moves(spec, device, st[pos]):
                new = st[:pos] + (new_local,) + st[pos + 1:]
                transitions.append(
                    Transition(i, index[new], rate, label, element, device.index, kind)
                )

    rates = {(t.src, t.dst): t.rate for t in transitions}
    if len(rates) != len(transitions):
        raise AssertionError("два перехода между одной парой состояний")
    g = ctmc.generator(len(states), rates)
    p = ctmc.stationary(g)
    return Model(spec, states, transitions, g, p)
