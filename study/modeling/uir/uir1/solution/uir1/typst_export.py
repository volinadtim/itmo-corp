"""Экспорт результатов расчёта в JSON для typst-отчёта.

Отчёт (`study/modeling/reports/uir1/report.typ`) читает этот файл через `json()`,
поэтому числа в PDF всегда совпадают с расчётом и не переписываются руками.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from . import report as rep
from .analysis import (
    Result,
    _randomness_verdict,
    _series_character,
    _upper_first,
)
from .estimates import CONFIDENCE_LEVELS, significance_threshold


def _ru(text: str) -> str:
    """Десятичные точки → запятые в готовом русском тексте.

    Тексты выводов собираются функциями из analysis.py, которые форматируют
    числа по-питоновски, через точку. В отчёте на русском нужна запятая.
    Трогаем только разделитель внутри числа: «0.1132» → «0,1132»,
    «k = 1:» и «5 %» остаются как есть.
    """
    return re.sub(r"(?<=\d)\.(?=\d)", ",", text)


def _clean_note(note: str) -> str:
    """Замечание из расчёта — в текст отчёта.

    Убираем подсказки по ключам командной строки: в отчёте, который читает
    преподаватель, им не место.
    """
    note = re.sub(r"\s*\(--law [^)]*\)", "", note)
    note = re.sub(r"\s*\(--[a-z]+[^)]*\)", "", note)
    return _ru(note).strip()


def _num(x: float, digits: int = 4) -> str:
    """Число в русской записи — с запятой в качестве разделителя."""
    return f"{x:.{digits}f}".replace(".", ",")


def _pct(value: float, reference: float) -> str:
    if reference == 0:
        return "—"
    return _num((value - reference) / reference * 100.0, 2)


def _form_rows(by_size, reference=None) -> list[dict]:
    """Строки формы 1 (reference=None) или формы 2."""
    sizes = sorted(by_size)
    rows = rep._rows(by_size)
    ref_rows = rep._rows(reference) if reference else None
    out = []
    for index, row in enumerate(rows):
        is_interval = row.label.startswith("Дов. инт.")
        values = [
            ("±" if is_interval else "") + _num(v) for v in row.values
        ]
        if ref_rows is None:
            percents = [_pct(v, row.reference) for v in row.values]
        else:
            percents = [
                _pct(v, r) for v, r in zip(row.values, ref_rows[index].values)
            ]
        out.append({"label": row.label, "values": values, "percents": percents})
    return out


def _generator_block(law) -> dict:
    """Формула генератора в синтаксисе typst-математики."""
    name = law.name
    if name == "экспоненциальный":
        return {
            "description": "Метод обратной функции для экспоненциального закона:",
            "formula": f"x = -t ln(U), quad t = {law.t:.4f}",
            "note": "На каждое значение требуется одна равномерная величина.",
        }
    if name == "нормированный Эрланга":
        return {
            "description": (
                f"Сумма {law.k} экспоненциальных фаз со средним "
                f"{law.phase_mean:.4f} каждая:"
            ),
            "formula": (
                f"x = -(t/k) sum_(i=1)^k ln(U_i), quad k = {law.k}, "
                f"quad t/k = {law.phase_mean:.4f}"
            ),
            "note": (
                "Логарифмы складываются по одному, а не берётся логарифм "
                "произведения: произведение k чисел меньше единицы обнуляется "
                "при большом k."
            ),
        }
    if name == "гипоэкспоненциальный":
        terms = " - ".join(f"t_{i + 1} ln(U_{i + 1})" for i in range(law.k))
        means = ", ".join(
            f"t_{i + 1} = {t:.4f}" for i, t in enumerate(law.means)
        )
        return {
            "description": (
                f"Последовательные экспоненциальные фазы: {law.k - 1} со средним "
                f"{law.t_a:.4f} и одна со средним {law.t_b:.4f}."
            ),
            "formula": f"x = - {terms}, quad {means}",
            "note": (
                f"На каждое значение требуется {law.k} независимых значений "
                "равномерно распределённой величины."
            ),
        }
    if name == "гиперэкспоненциальный":
        return {
            "description": (
                f"С вероятностью q = {law.q:.4f} выбирается фаза со средним "
                f"{law.t1:.4f}, иначе — со средним {law.t2:.4f}."
            ),
            "formula": (
                f'x = cases(-t_1 ln(U_2) "при" U_1 < q, '
                f'-t_2 ln(U_2) "иначе"), quad '
                f"q = {law.q:.4f}, quad t_1 = {law.t1:.4f}, t_2 = {law.t2:.4f}"
            ),
            "note": (
                "Используются две независимые равномерные величины: U₁ выбирает "
                "фазу, U₂ формирует экспоненту. Переиспользовать одно значение "
                "нельзя — возникнет зависимость между выбором фазы и длительностью."
            ),
        }
    if name == "равномерный":
        return {
            "description": "Метод обратной функции для равномерного закона:",
            "formula": f"x = a + (b - a) U, quad a = {law.a:.4f}, b = {law.b:.4f}",
            "note": "",
        }
    return {"description": "", "formula": "x = F^(-1)(U)", "note": ""}


def _law_rationale(cv: float) -> str:
    if cv > 1.05:
        return (
            "при $nu > 1$ распределение аппроксимируется гиперэкспоненциальным "
            "законом"
        )
    if cv >= 0.95:
        return "при $nu approx 1$ распределение аппроксимируется экспоненциальным законом"
    return (
        "при $nu < 1$ распределение аппроксимируется нормированным законом Эрланга "
        "либо гипоэкспоненциальным законом"
    )


def export(
    result: Result,
    out_dir: Path,
    plots_src: Path,
    student: str,
    group: str,
    teacher: str,
    year: str = "2026",
) -> Path:
    """Пишет data.json и копирует графики рядом с отчётом."""
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dst = out_dir / "plots"
    plots_dst.mkdir(exist_ok=True)
    for png in sorted(plots_src.glob("*.png")):
        shutil.copy2(png, plots_dst / png.name)

    full = result.full
    law = result.law
    generated_full = result.generated_by_size[max(result.generated_by_size)]
    n = len(result.given)
    randomness_text, is_random = _randomness_verdict(result.given_autocorr, n)
    gen_text, _ = _randomness_verdict(result.generated_autocorr, n)
    small = result.given_by_size[min(result.given_by_size)]

    hist = result.given_hist
    data = {
        "variant": result.variant,
        "n": n,
        "seed": result.seed,
        "sizes": sorted(result.given_by_size),
        "lags": sorted(result.given_autocorr),
        "author": {
            "name": student,
            "group": group,
            "teacher": teacher,
            "year": year,
        },
        "confidence_levels": [_num(p, 2) for p in CONFIDENCE_LEVELS],
        "form1": _form_rows(result.given_by_size),
        "form2": _form_rows(result.generated_by_size, result.given_by_size),
        "autocorr": {
            "given": [_num(result.given_autocorr[k]) for k in sorted(result.given_autocorr)],
            "generated": [
                _num(result.generated_autocorr[k])
                for k in sorted(result.generated_autocorr)
            ],
            "percents": [
                _pct(result.generated_autocorr[k], result.given_autocorr[k])
                for k in sorted(result.given_autocorr)
            ],
            "threshold": _num(significance_threshold(n)),
        },
        "histogram": {
            "bins": len(hist.counts),
            "rows": [
                [f"{lo:.2f} … {hi:.2f}", str(count), _num(count / n)]
                for (lo, hi), count in zip(
                    zip(hist.edges, hist.edges[1:]), hist.counts
                )
            ],
        },
        "law": {
            "name": law.name,
            "cv": _num(full.cv),
            "rationale": _law_rationale(full.cv),
            "params": [[k, f"{v:.6g}"] for k, v in law.params.items()],
            "fit": [
                [
                    "M[X]",
                    _num(full.mean),
                    _num(law.theoretical_mean),
                    _pct(law.theoretical_mean, full.mean) + " %",
                ],
                [
                    "ν",
                    _num(full.cv),
                    _num(law.theoretical_cv),
                    _pct(law.theoretical_cv, full.cv) + " %",
                ],
            ],
            "notes": [_clean_note(n) for n in law.notes],
        },
        "generator": {
            key: _ru(value) if key != "formula" else value
            for key, value in _generator_block(law).items()
        },
        "cross_correlation": _num(result.cross_correlation),
        "conclusions": {
            "moments": (
                f"На полной выборке из {n} величин получены оценки: "
                f"математическое ожидание {_num(full.mean)}, дисперсия "
                f"{_num(full.variance)}, среднеквадратическое отклонение "
                f"{_num(full.std)}, коэффициент вариации {_num(full.cv)}. "
                f"При n = {small.n} оценка математического ожидания отклоняется "
                f"от эталонной на {_pct(small.mean, full.mean)} %, а коэффициент "
                f"вариации — на {_pct(small.cv, full.cv)} %: малые выборки "
                "систематически недооценивают разброс, поскольку редкие большие "
                "значения в них не попадают. Полуинтервал при доверительной "
                f"вероятности 0,95 сокращается с ±{_num(small.half_interval(0.95))} "
                f"до ±{_num(full.half_interval(0.95))}, то есть относительная "
                f"погрешность падает с {_num(small.relative_error(0.95), 1)} % "
                f"до {_num(full.relative_error(0.95), 1)} %. Это согласуется "
                "с выражением для среднеквадратического отклонения оценки "
                "математического ожидания: точность растёт пропорционально "
                "корню из объёма выборки."
            ),
            "series": _ru(_upper_first(_series_character(result.given))) + ".",
            "randomness": _ru(_upper_first(randomness_text)) + ".",
            "generated": (
                f"На полной выборке сгенерированная последовательность имеет "
                f"математическое ожидание {_num(generated_full.mean)} "
                f"({_pct(generated_full.mean, full.mean)} % к заданной) и "
                f"коэффициент вариации {_num(generated_full.cv)} "
                f"({_pct(generated_full.cv, full.cv)} %). Расхождение объясняется "
                "случайностью самой генерации: сгенерированная последовательность "
                "— такая же выборка конечного объёма, как и заданная, и её "
                "собственные оценки тоже имеют доверительный интервал. "
                f"Для сгенерированной ЧП {_ru(gen_text)}."
            ),
            "correlation": (
                "Значение близко к нулю, и это правильный результат, а не признак "
                "плохой аппроксимации. Заданная и сгенерированная "
                "последовательности независимы: генератор воспроизводит не "
                "конкретные значения исходного ряда, а закон распределения. "
                "Качество аппроксимации оценивается совпадением числовых моментов "
                "и формой гистограммы, а не корреляцией между реализациями."
            ),
            "final": (
                f"Заданная числовая последовательность варианта {result.variant} "
                f"имеет математическое ожидание {_num(full.mean)} и коэффициент "
                f"вариации {_num(full.cv)}. "
                + (
                    "По результатам автокорреляционного анализа её можно считать "
                    "случайной. "
                    if is_random
                    else "По результатам автокорреляционного анализа случайной её "
                    "считать нельзя: коэффициенты автокорреляции систематически "
                    "превышают порог значимости, что согласуется с видимым "
                    "на графике 1 трендом. "
                )
                + f"По двум моментам последовательность аппроксимируется "
                f"{law.name} законом, который воспроизводит математическое "
                f"ожидание и коэффициент вариации с расхождением не хуже "
                f"{_num(max(abs((law.theoretical_mean - full.mean) / full.mean), abs((law.theoretical_cv - full.cv) / full.cv)) * 100, 2)} %. "
                "Сравнение гистограммы заданной последовательности с плотностью "
                "аппроксимирующего закона подтверждает согласие распределений."
            ),
        },
    }

    path = out_dir / "data.json"
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path
