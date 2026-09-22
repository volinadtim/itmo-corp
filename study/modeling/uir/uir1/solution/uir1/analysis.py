"""Полный прогон УИР 1: от выборки до готового отчёта."""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

from . import report
from .approx import LAWS, Distribution
from .estimates import (
    CONFIDENCE_LEVELS,
    Histogram,
    Moments,
    autocorrelations,
    correlation,
    histogram,
    moments,
    moments_by_size,
    significance_threshold,
    sturges_bins,
)

def _upper_first(text: str) -> str:
    """Заглавная первая буква без порчи остальной строки (в отличие от capitalize)."""
    return text[:1].upper() + text[1:]


def _instrumental(name: str) -> str:
    """Название закона в творительном падеже: «аппроксимируется ... законом»."""
    return name[:-2] + "ым" if name.endswith("ый") else name


DEFAULT_SEED = 20261105  # дата дедлайна — чтобы прогон был воспроизводим


@dataclass
class Result:
    variant: int
    given: list[float]
    generated: list[float]
    given_by_size: dict[int, Moments]
    generated_by_size: dict[int, Moments]
    given_autocorr: dict[int, float]
    generated_autocorr: dict[int, float]
    given_hist: Histogram
    generated_hist: Histogram
    law: Distribution
    cross_correlation: float
    seed: int

    @property
    def full(self) -> Moments:
        return self.given_by_size[max(self.given_by_size)]


def analyse(
    sample: list[float],
    variant: int,
    law_name: str = "auto",
    q: float | None = None,
    seed: int = DEFAULT_SEED,
) -> Result:
    given_by_size = moments_by_size(sample)
    full = given_by_size[max(given_by_size)]

    law = LAWS[law_name](full.mean, full.cv, q)

    # Генерируем столько же значений, сколько в заданной ЧП, чтобы формы 2 и 3
    # считались на сопоставимых объёмах.
    rng = random.Random(seed)
    generated = law.generate(len(sample), rng)

    bins = sturges_bins(len(sample))
    return Result(
        variant=variant,
        given=sample,
        generated=generated,
        given_by_size=given_by_size,
        generated_by_size=moments_by_size(generated),
        given_autocorr=autocorrelations(sample),
        generated_autocorr=autocorrelations(generated),
        given_hist=histogram(sample, bins),
        # Та же сетка интервалов, иначе кривые на графике 3 несопоставимы.
        generated_hist=_histogram_on_grid(generated, sample, bins),
        law=law,
        cross_correlation=correlation(sample, generated),
        seed=seed,
    )


def _histogram_on_grid(
    sample: list[float], reference: list[float], bins: int
) -> Histogram:
    """Гистограмма на сетке интервалов эталонной выборки."""
    low, high = min(reference), max(reference)
    width = (high - low) / bins
    edges = [low + i * width for i in range(bins + 1)]
    counts = [0] * bins
    for x in sample:
        index = int((x - low) / width)
        if 0 <= index < bins:
            counts[index] += 1
        elif index >= bins:
            counts[-1] += 1  # хвост за границей эталона — в последний интервал
        else:
            counts[0] += 1
    n = len(sample)
    return Histogram(edges=edges, counts=counts,
                     density=[c / (n * width) for c in counts])


# ------------------------------------------------------------------ выводы


def _series_character(sample: list[float]) -> str:
    """Грубая оценка тренда: сравнение средних первой и второй половин."""
    half = len(sample) // 2
    first = sum(sample[:half]) / half
    second = sum(sample[half:]) / (len(sample) - half)
    change = (second - first) / first * 100
    if abs(change) < 10:
        return (
            f"выраженного тренда нет: среднее первой половины {first:.3f}, "
            f"второй {second:.3f} (отличие {change:+.1f} %), "
            "последовательность колеблется вокруг общего среднего"
        )
    direction = "возрастающей" if change > 0 else "убывающей"
    return (
        f"заметен сдвиг уровня: среднее первой половины {first:.3f}, "
        f"второй {second:.3f} ({change:+.1f} %), последовательность "
        f"можно считать {direction}"
    )


def _randomness_verdict(autocorr: dict[int, float], n: int) -> tuple[str, bool]:
    """Вывод о случайности последовательности по коэффициентам автокорреляции.

    Порог ±t_p/√n рассчитан на одну проверку, а проверок здесь десять.
    Для истинно случайного ряда одно-два небольших превышения — ожидаемая
    случайность, а не признак зависимости (при уровне 5 % и 10 сдвигах
    в среднем 0,5 ложных срабатывания). Поэтому вердикт выносится по двум
    признакам сразу: сколько коэффициентов вышло за порог и насколько сильно.
    """
    threshold = significance_threshold(n)
    exceeded = {k: v for k, v in autocorr.items() if abs(v) > threshold}
    peak = max((abs(v) for v in autocorr.values()), default=0.0)

    if not exceeded:
        return (
            f"все коэффициенты автокорреляции по модулю меньше порога значимости "
            f"{threshold:.4f} (= 1,96/√{n}), наибольший равен {peak:.4f}. "
            "Систематической связи между значениями нет — последовательность "
            "можно считать случайной",
            True,
        )

    listed = ", ".join(f"k = {k}: {v:+.4f}" for k, v in sorted(exceeded.items()))
    borderline = len(exceeded) <= 2 and peak < 2 * threshold
    if borderline:
        return (
            f"порог значимости {threshold:.4f} превышен лишь при {listed}, причём "
            f"незначительно (максимум {peak:.4f} против порога {threshold:.4f}). "
            f"При десяти проверках уровня 5 % одно-два таких превышения ожидаемы "
            "даже для полностью случайной последовательности, поэтому "
            "систематической связи здесь нет — последовательность можно считать "
            "случайной",
            True,
        )
    return (
        f"порог значимости {threshold:.4f} превышен при {listed} "
        f"(максимум {peak:.4f}, это в {peak / threshold:.1f} раза больше порога). "
        "Превышения систематические, а значит, между значениями есть "
        "статистическая связь и считать последовательность случайной нельзя",
        False,
    )


def build_report(result: Result, plots_dir: Path, rel: str = ".") -> str:
    """Markdown-отчёт со всеми формами, графиками и выводами."""
    full = result.full
    law = result.law
    generated_full = result.generated_by_size[max(result.generated_by_size)]
    n = len(result.given)

    randomness_text, is_random = _randomness_verdict(result.given_autocorr, n)

    lines: list[str] = []
    add = lines.append

    add(f"# УИР 1 — вариант {result.variant}")
    add("")
    add("Статистический анализ числовой последовательности.")
    add("")
    add(f"Объём заданной ЧП: **{n}** значений. "
        f"Генератор запускался с seed = `{result.seed}` (прогон воспроизводим).")
    add("")

    add("## 1. Числовые моменты заданной ЧП (форма 1)")
    add("")
    add(report.form_table(result.given_by_size))
    add("")
    add("«%» — относительное отклонение от значения, полученного "
        "на полной выборке из 300 величин.")
    add("")
    add("**Выводы.**")
    add("")
    add(f"- На полной выборке: м.о. = {full.mean:.4f}, дисперсия = {full.variance:.4f}, "
        f"с.к.о. = {full.std:.4f}, коэффициент вариации ν = {full.cv:.4f}.")
    small = result.given_by_size[min(result.given_by_size)]
    add(f"- При n = {small.n} оценка мат. ожидания отклоняется от эталонной на "
        f"{(small.mean - full.mean) / full.mean * 100:+.2f} %, "
        f"а ν — на {(small.cv - full.cv) / full.cv * 100:+.2f} %. "
        "Малые выборки систематически недооценивают разброс: редкие большие "
        "значения в них просто не попадают.")
    add(f"- Полуинтервал при p = 0,95 сокращается с ±{small.half_interval(0.95):.4f} "
        f"(n = {small.n}) до ±{full.half_interval(0.95):.4f} (n = {n}), то есть "
        f"относительная погрешность падает с {small.relative_error(0.95):.1f} % "
        f"до {full.relative_error(0.95):.1f} %. Это согласуется с σ_m = √(D/n): "
        "точность растёт как √n.")
    add("")

    add("## 2. График значений заданной ЧП (график 1)")
    add("")
    add(f"![График 1]({rel}/{plots_dir.name}/plot1_series.png)")
    add("")
    add(f"**Вывод.** {_upper_first(_series_character(result.given))}.")
    add("")

    add("## 3. Автокорреляционный анализ заданной ЧП (форма 3)")
    add("")
    add(report.autocorr_table(result.given_autocorr))
    add("")
    add(f"![Автокорреляция]({rel}/{plots_dir.name}/plot_autocorr.png)")
    add("")
    add(f"**Вывод.** {_upper_first(randomness_text)}.")
    add("")

    add("## 4. Гистограмма распределения частот (график 2)")
    add("")
    add(f"Число интервалов по формуле Стёрджеса: L = 1 + 3,322·lg {n} = "
        f"{len(result.given_hist.counts)}.")
    add("")
    add(f"![График 2]({rel}/{plots_dir.name}/plot2_histogram.png)")
    add("")
    add("| Интервал | Частота | Отн. частота |")
    add("|---|---|---|")
    for (lo, hi), count in zip(
        zip(result.given_hist.edges, result.given_hist.edges[1:]),
        result.given_hist.counts,
    ):
        add(f"| {lo:.3f} … {hi:.3f} | {count} | {count / n:.4f} |")
    add("")

    add("## 5. Аппроксимирующий закон распределения")
    add("")
    add(f"Коэффициент вариации заданной ЧП: **ν = {full.cv:.4f}**.")
    add("")
    add(f"Выбранный закон: **{law.name}**.")
    add("")
    add("| Параметр | Значение |")
    add("|---|---|")
    for key, value in law.params.items():
        add(f"| {key} | {value:.6g} |")
    add("")
    add("Проверка подгонки по двум моментам:")
    add("")
    add("| Момент | Заданная ЧП | Закон | Расхождение |")
    add("|---|---|---|---|")
    add(f"| M[X] | {full.mean:.4f} | {law.theoretical_mean:.4f} | "
        f"{(law.theoretical_mean - full.mean) / full.mean * 100:+.4f} % |")
    add(f"| ν | {full.cv:.4f} | {law.theoretical_cv:.4f} | "
        f"{(law.theoretical_cv - full.cv) / full.cv * 100:+.4f} % |")
    add("")
    if law.notes:
        add("**Замечания по выбору закона:**")
        add("")
        for note in law.notes:
            add(f"- {note}")
        add("")

    add("## 6. Генератор случайных величин")
    add("")
    add(_generator_description(law))
    add("")

    add("## 7. Характеристики сгенерированной ЧП (форма 2)")
    add("")
    add(f"Закон распределения: **{law.describe()}**")
    add("")
    add(report.form_table(result.generated_by_size, reference=result.given_by_size))
    add("")
    add("«%» — отклонение от одноимённых значений заданной ЧП при том же n.")
    add("")
    add("**Выводы.**")
    add("")
    add(f"- На полной выборке: м.о. = {generated_full.mean:.4f} "
        f"({(generated_full.mean - full.mean) / full.mean * 100:+.2f} % к заданной), "
        f"ν = {generated_full.cv:.4f} "
        f"({(generated_full.cv - full.cv) / full.cv * 100:+.2f} %).")
    add("- Расхождение объясняется случайностью самой генерации: сгенерированная "
        "последовательность — такая же случайная выборка конечного объёма, как "
        "и заданная, и её собственные оценки тоже имеют доверительный интервал.")
    add("")

    add("## 8. Автокорреляция сгенерированной ЧП (форма 3, полностью)")
    add("")
    add(report.autocorr_table(result.given_autocorr, result.generated_autocorr))
    add("")
    gen_random_text, gen_is_random = _randomness_verdict(
        result.generated_autocorr, n
    )
    add(f"**Вывод.** Для сгенерированной ЧП {gen_random_text}.")
    if gen_is_random:
        add("")
        add("Это ожидаемый результат: генератор формирует значения независимо "
            "друг от друга, поэтому автокорреляции у него быть не должно.")
    else:
        add("")
        add("Для независимого по построению генератора это неожиданно — стоит "
            "перепроверить реализацию или повторить прогон с другим seed.")
    if not is_random:
        add("")
        add("Контраст с заданной ЧП показателен: там связь между значениями "
            "обнаружилась, а значит, аппроксимация одним законом распределения "
            "воспроизводит одномерное распределение, но не структуру связей.")
    add("")

    add("## 9. Сравнение распределений (график 3)")
    add("")
    add(f"![График 3]({rel}/{plots_dir.name}/plot3_fit.png)")
    add("")
    add("Гистограмма нормирована на n·Δx, поэтому её площадь равна единице "
        "и сопоставима с плотностью f(x).")
    add("")

    add("## 10. Корреляция заданной и сгенерированной ЧП")
    add("")
    add(f"Коэффициент корреляции: **r = {result.cross_correlation:.4f}**.")
    add("")
    add("**Вывод.** Значение близко к нулю, и это правильный результат, а не "
        "признак плохой аппроксимации. Заданная и сгенерированная "
        "последовательности независимы: генератор не воспроизводит конкретные "
        "значения исходного ряда, он воспроизводит закон распределения. "
        "Качество аппроксимации оценивается совпадением моментов (раздел 7) "
        "и формой гистограммы (раздел 9), а не корреляцией между реализациями.")
    add("")

    add("## 11. Итог")
    add("")
    add(f"Заданная числовая последовательность варианта {result.variant} "
        f"имеет мат. ожидание {full.mean:.4f} и коэффициент вариации ν = {full.cv:.4f}. "
        f"{'Её можно считать случайной' if is_random else 'Случайной её считать нельзя'} "
        "по результатам автокорреляционного анализа. "
        f"По двум моментам она аппроксимируется {_instrumental(law.name)} законом "
        f"({law.describe()}), который воспроизводит оба момента с расхождением "
        f"не хуже {max(abs((law.theoretical_mean - full.mean) / full.mean), abs((law.theoretical_cv - full.cv) / full.cv)) * 100:.2f} %.")
    add("")
    return "\n".join(lines)


def _generator_description(law: Distribution) -> str:
    """Описание алгоритма генерации — пункт 6 содержания отчёта."""
    base = (
        "Генерация методом обратной функции: если U равномерно распределена "
        "на (0;1), то X = F⁻¹(U) распределена по закону F.\n\n"
    )
    name = law.name
    if name == "экспоненциальный":
        body = (
            f"```\nx = −t·ln(U),   t = {law.t:.6g}\n```\n\n"
            "Одно обращение к генератору равномерных чисел на значение."
        )
    elif name == "нормированный Эрланга":
        body = (
            f"```\nx = −(t/k)·Σ ln(Uᵢ),   i = 1..k,   k = {law.k}, "
            f"t/k = {law.phase_mean:.6g}\n```\n\n"
            "Сумма k экспоненциальных фаз. Логарифмы складываются по одному, "
            "а не берётся ln от произведения: произведение k чисел меньше "
            "единицы обнуляется при большом k."
        )
    elif name == "гипоэкспоненциальный":
        terms = " − ".join(f"t_{i + 1}·ln(U_{i + 1})" for i in range(law.k))
        means = ", ".join(f"t_{i + 1} = {t:.6g}" for i, t in enumerate(law.means))
        body = (
            f"```\nx = − {terms}\n\n{means}\n```\n\n"
            f"Последовательные экспоненциальные фазы: {law.k - 1} по "
            f"{law.t_a:.6g} и одна {law.t_b:.6g}. На каждое значение требуется "
            f"{law.k} независимых равномерных величин."
        )
    elif name == "гиперэкспоненциальный":
        body = (
            f"```\nесли U₁ < q:  x = −t₁·ln(U₂)\nиначе:        x = −t₂·ln(U₂)\n\n"
            f"q = {law.q:.6g}, t₁ = {law.t1:.6g}, t₂ = {law.t2:.6g}\n```\n\n"
            "Две **независимые** равномерные величины на каждое значение: U₁ "
            "выбирает фазу, U₂ формирует экспоненту. Переиспользовать одно и то "
            "же U нельзя — возникнет искусственная зависимость между выбором "
            "фазы и длительностью."
        )
    elif name == "равномерный":
        body = (
            f"```\nx = a + (b − a)·U,   a = {law.a:.6g}, b = {law.b:.6g}\n```"
        )
    else:
        body = "```\nx = F⁻¹(U)\n```"
    return base + body


def render(result: Result, out_dir: Path) -> Path:
    """Пишет отчёт, графики и CSV. Возвращает путь к отчёту."""
    out_dir.mkdir(parents=True, exist_ok=True)
    plots = out_dir / "plots"
    plots.mkdir(exist_ok=True)

    report.plot_series(result.given, plots / "plot1_series.png")
    report.plot_histogram(result.given_hist, plots / "plot2_histogram.png")
    report.plot_fit(result.given_hist, result.law, plots / "plot3_fit.png",
                    generated_hist=result.generated_hist)
    report.plot_autocorrelation(result.given_autocorr, len(result.given),
                                plots / "plot_autocorr.png",
                                generated=result.generated_autocorr)

    report.write_csv(out_dir / "form1.csv", result.given_by_size)
    report.write_csv(
        out_dir / "form2.csv", result.generated_by_size, result.given_by_size
    )

    path = out_dir / "report.md"
    path.write_text(build_report(result, plots), encoding="utf-8")
    return path
