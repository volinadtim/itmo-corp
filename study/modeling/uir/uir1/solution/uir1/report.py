"""Формы 1–3, графики 1–3 и сборка markdown-отчёта."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # рендер в файл, без окна
import matplotlib.pyplot as plt  # noqa: E402

from .approx import Distribution  # noqa: E402
from .estimates import (  # noqa: E402
    AUTOCORR_LAGS,
    CONFIDENCE_LEVELS,
    Histogram,
    Moments,
    significance_threshold,
)

PLOT_DPI = 150
FIGSIZE_WIDE = (11, 4.5)
FIGSIZE = (8, 5)


def _fmt(x: float, digits: int = 4) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def _pct(value: float, reference: float) -> str:
    """Относительное отклонение в процентах."""
    if reference == 0:
        return "—"
    return _fmt((value - reference) / reference * 100.0, 2)


@dataclass
class FormRow:
    label: str
    values: list[float]
    reference: float  # эталон для колонки «%»


def _rows(by_size: dict[int, Moments]) -> list[FormRow]:
    """Строки формы 1/2 в порядке из задания."""
    sizes = sorted(by_size)
    last = by_size[sizes[-1]]
    rows = [FormRow("Мат.ож.", [by_size[n].mean for n in sizes], last.mean)]
    for p in CONFIDENCE_LEVELS:
        rows.append(
            FormRow(
                f"Дов. инт. ({_fmt(p, 2)})",
                [by_size[n].half_interval(p) for n in sizes],
                last.half_interval(p),
            )
        )
    rows.append(FormRow("Дисперсия", [by_size[n].variance for n in sizes], last.variance))
    rows.append(FormRow("С.к.о.", [by_size[n].std for n in sizes], last.std))
    rows.append(FormRow("К-т вариации", [by_size[n].cv for n in sizes], last.cv))
    return rows


def form_table(
    by_size: dict[int, Moments],
    reference: dict[int, Moments] | None = None,
    interval_prefix: str = "±",
) -> str:
    """Форма 1 (reference=None) или форма 2 (reference — заданная ЧП).

    В форме 1 эталон для «%» — собственная колонка n=300.
    В форме 2 эталон — одноимённые значения заданной ЧП при том же n.
    """
    sizes = sorted(by_size)
    rows = _rows(by_size)
    ref_rows = _rows(reference) if reference else None

    head = " | ".join(str(n) for n in sizes)
    out = [f"| Характеристика | | {head} |", "|---|---|" + "---|" * len(sizes)]
    for index, row in enumerate(rows):
        is_interval = row.label.startswith("Дов. инт.")
        cells = []
        for value in row.values:
            text = _fmt(value)
            cells.append(f"{interval_prefix}{text}" if is_interval else text)
        out.append(f"| {row.label} | Знач. | " + " | ".join(cells) + " |")

        if ref_rows is None:
            pcts = [_pct(v, row.reference) for v in row.values]
        else:
            pcts = [_pct(v, r) for v, r in zip(row.values, ref_rows[index].values)]
        out.append("| | % | " + " | ".join(pcts) + " |")
    return "\n".join(out)


def autocorr_table(
    given: dict[int, float], generated: dict[int, float] | None = None
) -> str:
    """Форма 3."""
    lags = sorted(given)
    out = [
        "| Сдвиг ЧП | " + " | ".join(str(k) for k in lags) + " |",
        "|---|" + "---|" * len(lags),
        "| К-т АК для задан. ЧП | "
        + " | ".join(_fmt(given[k]) for k in lags)
        + " |",
    ]
    if generated:
        out.append(
            "| К-т АК для сгенерир. ЧП | "
            + " | ".join(_fmt(generated[k]) for k in lags)
            + " |"
        )
        out.append(
            "| % | " + " | ".join(_pct(generated[k], given[k]) for k in lags) + " |"
        )
    return "\n".join(out)


def write_csv(
    path: Path,
    by_size: dict[int, Moments],
    reference: dict[int, Moments] | None = None,
) -> None:
    """Формы в CSV — чтобы вставить в Excel при оформлении отчёта.

    Эталон для строки «%» разный у двух форм (см. бланки в задании):
    форма 1 (reference=None) — значения этой же ЧП при n = 300;
    форма 2 (reference — заданная ЧП) — одноимённые значения заданной ЧП
    при том же объёме выборки.
    """
    sizes = sorted(by_size)
    rows = _rows(by_size)
    ref_rows = _rows(reference) if reference else None
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["Характеристика", ""] + sizes)
        for index, row in enumerate(rows):
            writer.writerow([row.label, "Знач."] + [f"{v:.6f}" for v in row.values])
            if ref_rows is None:
                percents = [_pct(v, row.reference) for v in row.values]
            else:
                percents = [
                    _pct(v, r) for v, r in zip(row.values, ref_rows[index].values)
                ]
            writer.writerow(["", "%"] + percents)


# ---------------------------------------------------------------- графики
#
# Заголовок внутри изображения намеренно не рисуется: в отчёте у каждого
# рисунка есть подпись, и заголовок на картинке дублировал бы её.


def plot_series(sample: list[float], path: Path) -> None:
    """График 1: значения ЧП по номеру измерения.

    Заданием требуется только линия значений; м.о., линия тренда и скользящее
    среднее добавлены, чтобы вывод о характере последовательности опирался на
    числа, а не на впечатление от картинки.
    """
    n = len(sample)
    xs = list(range(1, n + 1))
    mean = sum(sample) / n

    # линейный тренд по МНК: X ~ a + b*i
    mid = (n + 1) / 2
    denom = sum((i - mid) ** 2 for i in xs)
    slope = sum((xs[k] - mid) * (sample[k] - mean) for k in range(n)) / denom
    intercept = mean - slope * mid

    # скользящее среднее — гасит шум, проявляет движение уровня
    window = max(5, n // 15)
    half = window // 2
    smooth = [
        sum(sample[max(0, k - half):min(n, k + half + 1)])
        / len(sample[max(0, k - half):min(n, k + half + 1)])
        for k in range(n)
    ]

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    ax.plot(xs, sample, linewidth=0.9, label="значения ЧП")
    ax.plot(xs, smooth, color="tab:orange", linewidth=1.8,
            label=f"скользящее среднее (окно {window})")
    ax.plot(xs, [intercept + slope * i for i in xs], color="black",
            linestyle="--", linewidth=1.6,
            label="тренд: " + f"{intercept:.1f} + {slope:.3f}".replace(".", ",") + "·i")
    ax.axhline(mean, color="tab:red", linestyle=":", linewidth=1.4,
               label="м.о. = " + f"{mean:.3f}".replace(".", ","))
    ax.set_xlabel("Номер измерения")
    ax.set_ylabel("Значение")
    ax.set_xlim(1, n)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=PLOT_DPI)
    plt.close(fig)


def plot_histogram(hist: Histogram, path: Path) -> None:
    """График 2: гистограмма частот."""
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(hist.centers, hist.counts, width=hist.width * 0.95,
           edgecolor="black", linewidth=0.5)
    ax.set_xlabel("Значение")
    ax.set_ylabel("Частота")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=PLOT_DPI)
    plt.close(fig)


def plot_fit(
    hist: Histogram, law: Distribution, path: Path,
    generated_hist: Histogram | None = None,
) -> None:
    """График 3: нормированная гистограмма + плотность аппроксимирующего закона.

    Гистограмма нормирована на n·Δx, иначе она и f(x) окажутся в разных
    масштабах и сравнение будет бессмысленным.
    """
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar(hist.centers, hist.density, width=hist.width * 0.95, alpha=0.6,
           edgecolor="black", linewidth=0.5, label="заданная ЧП (норм. частоты)")
    if generated_hist is not None:
        ax.step(generated_hist.centers, generated_hist.density, where="mid",
                color="tab:green", linewidth=1.3, label="сгенерированная ЧП")
    xs = [hist.edges[0] + i * (hist.edges[-1] - hist.edges[0]) / 400 for i in range(401)]
    ax.plot(xs, [law.pdf(x) for x in xs], color="tab:red", linewidth=2,
            label=f"f(x): {law.name}")
    ax.set_xlabel("Значение")
    ax.set_ylabel("Плотность")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=PLOT_DPI)
    plt.close(fig)


def plot_autocorrelation(
    given: dict[int, float], n: int, path: Path,
    generated: dict[int, float] | None = None,
) -> None:
    """Коэффициенты автокорреляции с границами значимости ±t_p/√n."""
    lags = sorted(given)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.plot(lags, [given[k] for k in lags], marker="o", label="заданная ЧП")
    if generated:
        ax.plot(lags, [generated[k] for k in lags], marker="s",
                label="сгенерированная ЧП")
    threshold = significance_threshold(n)
    ax.axhline(threshold, color="tab:red", linestyle="--", linewidth=1,
               label="порог значимости ±" + f"{threshold:.3f}".replace(".", ","))
    ax.axhline(-threshold, color="tab:red", linestyle="--", linewidth=1)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Сдвиг k")
    ax.set_ylabel("Коэффициент автокорреляции")
    ax.set_xticks(list(AUTOCORR_LAGS))
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=PLOT_DPI)
    plt.close(fig)
