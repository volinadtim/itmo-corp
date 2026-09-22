"""Точечные оценки, доверительные интервалы, автокорреляция, гистограмма.

Формулы — из методички «Обработка результатов имитационного моделирования»
(LMS 7289) и презентации «Статистическая обработка результатов измерений» (6917).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# Объёмы выборок, которые требует форма 1 задания.
SAMPLE_SIZES = (10, 20, 50, 100, 200, 300)

# Доверительные вероятности из задания.
CONFIDENCE_LEVELS = (0.9, 0.95, 0.99)

# Таблица 1 методички: t_p = Φ⁻¹((1+p)/2), нормальное распределение.
# Берём табличные значения, а не пересчитываем через scipy: отчёт должен
# сходиться с методичкой (её 0,90 → 1,643 слегка огрублено, точное 1,645).
T_TABLE = {
    0.80: 1.282, 0.81: 1.310, 0.82: 1.340, 0.83: 1.371, 0.84: 1.404,
    0.85: 1.439, 0.86: 1.475, 0.87: 1.513, 0.88: 1.554, 0.89: 1.597,
    0.90: 1.643, 0.91: 1.694, 0.92: 1.750, 0.93: 1.810, 0.94: 1.880,
    0.95: 1.960, 0.96: 2.053, 0.97: 2.169, 0.98: 2.325, 0.99: 2.576,
    0.9973: 3.000, 0.999: 3.290,
}

# Сдвиги для формы 3.
AUTOCORR_LAGS = tuple(range(1, 11))


def t_value(p: float) -> float:
    """Коэффициент t_p по таблице 1 методички."""
    try:
        return T_TABLE[round(p, 4)]
    except KeyError:
        raise KeyError(
            f"p={p} нет в таблице методички; доступны {sorted(T_TABLE)}"
        ) from None


@dataclass(frozen=True)
class Moments:
    """Числовые моменты выборки."""

    n: int
    mean: float           # m̃  — оценка мат. ожидания
    variance: float       # D̃  — несмещённая оценка дисперсии (делитель n−1)
    std: float            # σ̃  = √D̃
    cv: float             # ν  = σ̃ / m̃
    std_of_mean: float    # σ̃_m = √(D̃/n) — СКО самой оценки m̃

    def half_interval(self, p: float) -> float:
        """Полуинтервал Δ_p = t_p · σ̃_m."""
        return t_value(p) * self.std_of_mean

    def interval(self, p: float) -> tuple[float, float]:
        """Границы (m_н, m_в)."""
        delta = self.half_interval(p)
        return self.mean - delta, self.mean + delta

    def relative_error(self, p: float) -> float:
        """Относительная погрешность δ = Δ/m̃ · 100 %."""
        return self.half_interval(p) / self.mean * 100.0


def moments(sample: list[float]) -> Moments:
    """Оценки по формулам (1), (4) методички.

    Дисперсия считается с делителем n−1 (несмещённая оценка) через сумму
    квадратов отклонений, а не через второй начальный момент: вторая форма
    численно неустойчива при большом среднем и малом разбросе.
    """
    n = len(sample)
    if n < 2:
        raise ValueError("для оценки дисперсии нужно хотя бы 2 значения")
    mean = sum(sample) / n
    variance = sum((x - mean) ** 2 for x in sample) / (n - 1)
    std = math.sqrt(variance)
    if mean <= 0:
        raise ValueError("коэффициент вариации определён только при m̃ > 0")
    return Moments(
        n=n,
        mean=mean,
        variance=variance,
        std=std,
        cv=std / mean,
        std_of_mean=math.sqrt(variance / n),
    )


def moments_by_size(
    sample: list[float], sizes: tuple[int, ...] = SAMPLE_SIZES
) -> dict[int, Moments]:
    """Моменты для префиксов выборки — колонки формы 1.

    Берутся именно первые n значений, а не случайное подмножество: так
    результат воспроизводим и совпадает с ручным расчётом в Excel.
    """
    result = {}
    for n in sizes:
        if n > len(sample):
            raise ValueError(f"запрошено n={n}, а в выборке {len(sample)} значений")
        result[n] = moments(sample[:n])
    return result


def autocorrelation(sample: list[float], lag: int) -> float:
    """Коэффициент автокорреляции со сдвигом k.

    Упрощённая форма, которую методичка разрешает при n >> k:
        r_k ≈ Σ(xᵢ − m̃)(x_{i+k} − m̃) / Σ(xᵢ − m̃)²
    """
    n = len(sample)
    if not 0 < lag < n:
        raise ValueError(f"сдвиг {lag} вне диапазона 1..{n - 1}")
    mean = sum(sample) / n
    deviations = [x - mean for x in sample]
    numerator = sum(deviations[i] * deviations[i + lag] for i in range(n - lag))
    denominator = sum(d * d for d in deviations)
    if denominator == 0:
        raise ValueError("все значения выборки одинаковы, корреляция не определена")
    return numerator / denominator


def autocorrelations(
    sample: list[float], lags: tuple[int, ...] = AUTOCORR_LAGS
) -> dict[int, float]:
    return {k: autocorrelation(sample, k) for k in lags}


def significance_threshold(n: int, p: float = 0.95) -> float:
    """Граница значимости коэффициента автокорреляции: ±t_p/√n.

    Для белого шума r_k при больших n распределён примерно нормально
    со средним 0 и СКО 1/√n. Систематический выход за эту границу означает,
    что последовательность нельзя считать случайной.
    """
    return t_value(p) / math.sqrt(n)


def correlation(xs: list[float], ys: list[float]) -> float:
    """Коэффициент корреляции двух последовательностей."""
    if len(xs) != len(ys):
        raise ValueError("последовательности разной длины")
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denominator = math.sqrt(sum(a * a for a in dx) * sum(b * b for b in dy))
    if denominator == 0:
        raise ValueError("нулевая дисперсия, корреляция не определена")
    return sum(a * b for a, b in zip(dx, dy)) / denominator


def sturges_bins(n: int) -> int:
    """Число интервалов гистограммы по формуле Стёрджеса: L = 1 + 3,322·lg n."""
    return max(1, round(1 + 3.322 * math.log10(n)))


@dataclass(frozen=True)
class Histogram:
    """Гистограмма частот.

    `density` — частоты, нормированные на n·Δx, чтобы площадь равнялась 1
    и гистограмму можно было наложить на плотность распределения (график 3).
    """

    edges: list[float]
    counts: list[int]
    density: list[float]

    @property
    def width(self) -> float:
        return self.edges[1] - self.edges[0]

    @property
    def centers(self) -> list[float]:
        return [(a + b) / 2 for a, b in zip(self.edges, self.edges[1:])]


def histogram(sample: list[float], bins: int | None = None) -> Histogram:
    n = len(sample)
    bins = bins or sturges_bins(n)
    low, high = min(sample), max(sample)
    if low == high:
        raise ValueError("все значения выборки одинаковы, гистограмма не строится")
    width = (high - low) / bins
    edges = [low + i * width for i in range(bins + 1)]
    edges[-1] = high  # страхуемся от накопленной ошибки округления
    counts = [0] * bins
    for x in sample:
        index = int((x - low) / width)
        counts[min(index, bins - 1)] += 1  # максимум попадает в последний интервал
    density = [c / (n * width) for c in counts]
    return Histogram(edges=edges, counts=counts, density=density)
