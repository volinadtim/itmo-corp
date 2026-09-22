"""Аппроксимация закона распределения по двум моментам и генераторы.

Закон выбирается по коэффициенту вариации ν = σ̃/m̃ (раздел 5 «Элементов теории
вероятностей», LMS 7276). Генерация — методом обратной функции.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

# Экспоненциальный закон даёт ровно ν = 1; считаем его подходящим, если
# выборочное ν отклонилось не больше чем на эту величину.
EXPONENTIAL_TOLERANCE = 0.05

# Равномерный закон возможен только при ν < 1/√3.
UNIFORM_MAX_CV = 1.0 / math.sqrt(3.0)

# Двухфазная гипоэкспонента подгоняет два момента точно лишь при ν ≥ 1/√2.
HYPOEXPONENTIAL_MIN_CV = 1.0 / math.sqrt(2.0)

# Насколько 1/ν² должно быть близко к целому, чтобы Эрланг считался точным.
ERLANG_INTEGER_TOLERANCE = 0.05


@dataclass
class Distribution:
    """Аппроксимирующий закон: параметры, плотность, генератор."""

    name: str
    params: dict[str, float]
    notes: list[str] = field(default_factory=list)

    def pdf(self, x: float) -> float:
        raise NotImplementedError

    def generate(self, n: int, rng: random.Random) -> list[float]:
        raise NotImplementedError

    @property
    def theoretical_mean(self) -> float:
        raise NotImplementedError

    @property
    def theoretical_cv(self) -> float:
        raise NotImplementedError

    def describe(self) -> str:
        parts = ", ".join(f"{k} = {v:.6g}" for k, v in self.params.items())
        return f"{self.name}: {parts}"


class Uniform(Distribution):
    """Равномерный на [a, b]: a = t − σ√3, b = t + σ√3."""

    def __init__(self, mean: float, cv: float):
        std = cv * mean
        spread = std * math.sqrt(3.0)
        self.a = mean - spread
        self.b = mean + spread
        super().__init__("равномерный", {"a": self.a, "b": self.b})
        if self.a < 0:
            self.notes.append(
                f"нижняя граница a = {self.a:.4g} < 0 — закон допускает "
                "отрицательные значения, чего у измеряемой величины быть не может"
            )

    def pdf(self, x: float) -> float:
        return 1.0 / (self.b - self.a) if self.a <= x <= self.b else 0.0

    def generate(self, n: int, rng: random.Random) -> list[float]:
        return [self.a + (self.b - self.a) * rng.random() for _ in range(n)]

    @property
    def theoretical_mean(self) -> float:
        return (self.a + self.b) / 2

    @property
    def theoretical_cv(self) -> float:
        return (self.b - self.a) / (math.sqrt(3.0) * (self.a + self.b))


class Exponential(Distribution):
    """Экспоненциальный: F(x) = 1 − e^(−αx), α = 1/t. Всегда ν = 1."""

    def __init__(self, mean: float):
        self.t = mean
        self.alpha = 1.0 / mean
        super().__init__("экспоненциальный", {"α": self.alpha, "t = 1/α": self.t})

    def pdf(self, x: float) -> float:
        return self.alpha * math.exp(-self.alpha * x) if x >= 0 else 0.0

    def generate(self, n: int, rng: random.Random) -> list[float]:
        # Метод обратной функции: x = −t·ln(U). random() даёт [0,1),
        # поэтому берём 1−U, чтобы не получить ln(0).
        return [-self.t * math.log(1.0 - rng.random()) for _ in range(n)]

    @property
    def theoretical_mean(self) -> float:
        return self.t

    @property
    def theoretical_cv(self) -> float:
        return 1.0


class NormalizedErlang(Distribution):
    """Нормированный Эрланг k-го порядка: k фаз по t/k каждая.

    M = t, ν = 1/√k, поэтому k = 1/ν² (округляется до целого).
    """

    def __init__(self, mean: float, cv: float):
        self.t = mean
        exact_k = 1.0 / (cv * cv)
        self.k = max(1, round(exact_k))
        self.phase_mean = self.t / self.k
        self.alpha = self.k / self.t
        super().__init__(
            "нормированный Эрланга",
            {"k": self.k, "t": self.t, "α = k/t": self.alpha},
        )
        if abs(exact_k - self.k) > ERLANG_INTEGER_TOLERANCE:
            self.notes.append(
                f"1/ν² = {exact_k:.4f} далеко от целого; округление до k = {self.k} "
                f"даёт ν = {self.theoretical_cv:.4f} вместо {cv:.4f}"
            )

    def pdf(self, x: float) -> float:
        if x < 0:
            return 0.0
        k, a = self.k, self.alpha
        # a^k x^(k−1) e^(−a x) / (k−1)!  — считаем через логарифм: при больших k
        # a^k и (k−1)! по отдельности переполняются.
        if x == 0:
            return a if k == 1 else 0.0
        log_pdf = k * math.log(a) + (k - 1) * math.log(x) - a * x - math.lgamma(k)
        return math.exp(log_pdf)

    def generate(self, n: int, rng: random.Random) -> list[float]:
        # Сумма k экспонент со средним t/k: x = −(t/k)·ln(U₁·…·U_k).
        # Логарифмы складываем по одному — произведение k чисел < 1
        # обнуляется при большом k.
        out = []
        for _ in range(n):
            total = 0.0
            for _ in range(self.k):
                total -= math.log(1.0 - rng.random())
            out.append(self.phase_mean * total)
        return out

    @property
    def theoretical_mean(self) -> float:
        return self.t

    @property
    def theoretical_cv(self) -> float:
        return 1.0 / math.sqrt(self.k)


class Hypoexponential(Distribution):
    """Две последовательные экспоненты с разными средними t₁, t₂.

    Подгоняет оба момента точно (в отличие от Эрланга с округлённым k),
    но существует только при 1/√2 ≤ ν < 1:
        t₁ + t₂ = t,  t₁² + t₂² = ν²t²  →  t₁,₂ = t(1 ± √(2ν² − 1))/2
    """

    def __init__(self, mean: float, cv: float):
        if not HYPOEXPONENTIAL_MIN_CV <= cv < 1.0:
            raise ValueError(
                f"двухфазная гипоэкспонента требует 0,707 ≤ ν < 1, получено ν = {cv:.4f}"
            )
        root = math.sqrt(2.0 * cv * cv - 1.0)
        self.t1 = mean * (1.0 + root) / 2.0
        self.t2 = mean * (1.0 - root) / 2.0
        super().__init__("гипоэкспоненциальный", {"t₁": self.t1, "t₂": self.t2})

    def pdf(self, x: float) -> float:
        if x < 0:
            return 0.0
        if math.isclose(self.t1, self.t2):
            return Erlang2Fallback(self.t1).pdf(x)
        return (math.exp(-x / self.t1) - math.exp(-x / self.t2)) / (self.t2 - self.t1)

    def generate(self, n: int, rng: random.Random) -> list[float]:
        return [
            -self.t1 * math.log(1.0 - rng.random())
            - self.t2 * math.log(1.0 - rng.random())
            for _ in range(n)
        ]

    @property
    def theoretical_mean(self) -> float:
        return self.t1 + self.t2

    @property
    def theoretical_cv(self) -> float:
        return math.sqrt(self.t1**2 + self.t2**2) / (self.t1 + self.t2)


class Erlang2Fallback:
    """Вырожденный случай t₁ = t₂ — это Эрланг 2-го порядка."""

    def __init__(self, t: float):
        self.t = t

    def pdf(self, x: float) -> float:
        return x * math.exp(-x / self.t) / (self.t**2)


class Hyperexponential(Distribution):
    """Двухфазный гиперэкспоненциальный (ν > 1).

    С вероятностью q — экспонента со средним t₁, иначе со средним t₂:
        q ≤ 2/(1 + ν²)
        t₁ = [1 + √((1−q)/(2q)·(ν²−1))]·t
        t₂ = [1 − √(q/(2(1−q))·(ν²−1))]·t

    Уравнений два (t и ν), неизвестных три, поэтому q задаётся свободно.
    По умолчанию берём q = 1/(1+ν²) — половина верхней границы: на самой
    границе t₂ обращается в ноль, и закон вырождается в одну фазу.
    """

    def __init__(self, mean: float, cv: float, q: float | None = None):
        cv2 = cv * cv
        self.q_max = 2.0 / (1.0 + cv2)
        self.q = q if q is not None else 1.0 / (1.0 + cv2)
        if not 0.0 < self.q < 1.0:
            raise ValueError(f"q должно лежать в (0, 1), получено {self.q}")
        if self.q > self.q_max:
            raise ValueError(
                f"q = {self.q:.4f} превышает допустимое 2/(1+ν²) = {self.q_max:.4f}"
            )
        self.t1 = mean * (1.0 + math.sqrt((1.0 - self.q) / (2.0 * self.q) * (cv2 - 1.0)))
        self.t2 = mean * (1.0 - math.sqrt(self.q / (2.0 * (1.0 - self.q)) * (cv2 - 1.0)))
        if self.t2 <= 0:
            raise ValueError(
                f"при q = {self.q:.4f} получается t₂ = {self.t2:.4g} ≤ 0; "
                "нужно уменьшить q"
            )
        super().__init__(
            "гиперэкспоненциальный",
            {"q": self.q, "t₁": self.t1, "t₂": self.t2},
        )

    def pdf(self, x: float) -> float:
        if x < 0:
            return 0.0
        return (
            self.q / self.t1 * math.exp(-x / self.t1)
            + (1.0 - self.q) / self.t2 * math.exp(-x / self.t2)
        )

    def generate(self, n: int, rng: random.Random) -> list[float]:
        # Две независимые случайные величины на каждое значение: одна выбирает
        # фазу, вторая формирует экспоненту. Переиспользовать одну нельзя —
        # появится искусственная зависимость между фазой и длительностью.
        out = []
        for _ in range(n):
            phase_mean = self.t1 if rng.random() < self.q else self.t2
            out.append(-phase_mean * math.log(1.0 - rng.random()))
        return out

    @property
    def theoretical_mean(self) -> float:
        return self.q * self.t1 + (1.0 - self.q) * self.t2

    @property
    def theoretical_cv(self) -> float:
        second = 2.0 * (self.q * self.t1**2 + (1.0 - self.q) * self.t2**2)
        mean = self.theoretical_mean
        return math.sqrt(second - mean**2) / mean


def choose(mean: float, cv: float, q: float | None = None) -> Distribution:
    """Выбор закона по коэффициенту вариации."""
    if cv > 1.0 + EXPONENTIAL_TOLERANCE:
        return Hyperexponential(mean, cv, q)
    if cv >= 1.0 - EXPONENTIAL_TOLERANCE:
        law = Exponential(mean)
        if not math.isclose(cv, 1.0, abs_tol=1e-9):
            law.notes.append(
                f"ν = {cv:.4f} принято за 1 (отклонение {abs(cv - 1) * 100:.1f} %)"
            )
        return law

    erlang = NormalizedErlang(mean, cv)
    # Задание требует аппроксимации по двум моментам, а округление k искажает
    # второй момент. Если искажение заметно и двухфазная гипоэкспонента
    # существует (ν ≥ 1/√2) — она подгоняет оба момента точно, берём её.
    if erlang.notes and cv >= HYPOEXPONENTIAL_MIN_CV:
        law = Hypoexponential(mean, cv)
        law.notes.append(
            f"нормированный Эрланг потребовал бы k = 1/ν² = {1 / cv**2:.4f}; "
            f"округление до k = {erlang.k} дало бы ν = {erlang.theoretical_cv:.4f} "
            f"вместо {cv:.4f}, поэтому взят гипоэкспоненциальный закон — "
            "он подгоняет оба момента точно (--law erlang, чтобы всё же взять Эрланг)"
        )
    else:
        law = erlang
    if cv < UNIFORM_MAX_CV:
        law.notes.append(
            f"ν < 1/√3 = {UNIFORM_MAX_CV:.4f}, поэтому формально возможен и "
            "равномерный закон (--law uniform) — выбирать по виду гистограммы"
        )
    return law


LAWS = {
    "auto": choose,
    "uniform": lambda mean, cv, q=None: Uniform(mean, cv),
    "exponential": lambda mean, cv, q=None: Exponential(mean),
    "erlang": lambda mean, cv, q=None: NormalizedErlang(mean, cv),
    "hypoexponential": lambda mean, cv, q=None: Hypoexponential(mean, cv),
    "hyperexponential": lambda mean, cv, q=None: Hyperexponential(mean, cv, q),
}
