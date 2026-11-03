"""Экспорт расчёта в JSON для typst-отчёта (study/modeling/reports/uir2).

Отчёт читает data.json через json(), поэтому числа в PDF совпадают с расчётом.
Математика в строках записана в синтаксисе typst, отчёт вставляет её через eval(mode: "math").
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .model import Chain, Device, Stats, solve
from .plots import compare, state_code, transition_graph
from .variants import CRITERIA, Variant


def _num(x: float, digits: int = 4) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def _rate(x: float) -> str:
    """Интенсивность для матрицы: без лишних нулей, с запятой."""
    if x == 0:
        return ""
    text = f"{x:.4f}".rstrip("0").rstrip(".")
    return text.replace(".", ",").replace("-", "−")


@dataclass
class SystemResult:
    name: str
    devices: tuple[Device, ...]
    chain: Chain
    p: list[float]
    stats: Stats


def _sum_expr(weights: dict[int, int]) -> str:
    """Σ w·p_j в записи typst: состояния группируются по весу,
    подряд идущие номера сворачиваются в p_a + … + p_b."""
    if not weights:
        return "0"
    by_w: dict[int, list[int]] = {}
    for j, w in sorted(weights.items()):
        by_w.setdefault(w, []).append(j)
    terms = []
    for w, idx in sorted(by_w.items()):
        runs, start, prev = [], idx[0], idx[0]
        for j in idx[1:] + [None]:
            if j is not None and j == prev + 1:
                prev = j
                continue
            if prev - start >= 2:
                runs.append(f"p_({start}) + dots.h + p_({prev})")
            else:
                runs.extend(f"p_({k})" for k in range(start, prev + 1))
            if j is not None:
                start = prev = j
        body = " + ".join(runs)
        if w == 1:
            terms.append(body)
        else:
            terms.append(f"{w} ({body})" if len(runs) > 1 or "dots" in body else f"{w} {body}")
    return " + ".join(terms)


def _formulas(res: SystemResult) -> list[dict]:
    """Расчётные формулы через вероятности конкретных состояний."""
    rows = []
    states = res.chain.states
    for d, dev in enumerate(res.devices):
        full = dev.buffer + 1
        busy = {j + 1: 1 for j, s in enumerate(states) if s[d][0] > 0}
        queue = {j + 1: s[d][0] - 1 for j, s in enumerate(states) if s[d][0] > 1}
        count = {j + 1: s[d][0] for j, s in enumerate(states) if s[d][0] > 0}
        lost = {j + 1: 1 for j, s in enumerate(states) if s[d][0] == full}
        i = d + 1
        rows.append({"device": dev.name, "items": [
            f"rho_{i} = {_sum_expr(busy)}",
            f"l_{i} = {_sum_expr(queue)}",
            f"m_{i} = {_sum_expr(count)}",
            f"pi_{i} = {_sum_expr(lost)}",
        ]})
    return rows


# Строки формы 2: ключ характеристики, название, формула для прибора i, формула для системы.
FORM2 = [
    ("load", "Нагрузка", "y_i = lambda p_i b", "Y = lambda b"),
    ("util", "Загрузка", "rho_i = sum_(k_i >= 1) p_j", "R = 1/K sum rho_i"),
    ("queue", "Длина очереди", "l_i = sum (k_i - 1) p_j", "L = sum l_i"),
    ("count", "Число заявок", "m_i = sum k_i p_j", "M = sum m_i"),
    ("wait", "Время ожидания, с", "w_i = l_i / lambda'_i", "W = L / Lambda'"),
    ("stay", "Время пребывания, с", "u_i = m_i / lambda'_i", "U = M / Lambda'"),
    ("loss", "Вероятность потери", "pi_i = sum_(k_i = r_i + 1) p_j", "Pi = 1 - Lambda' / lambda"),
    ("throughput", "Производительность, 1/с", "lambda'_i = lambda p_i (1 - pi_i)", "Lambda' = sum lambda'_i"),
]


def _form2(results: list[SystemResult]) -> list[dict]:
    k = max(len(r.devices) for r in results)
    out = []
    for key, label, f_dev, f_sys in FORM2:
        rows = []
        for d in range(k):
            vals = [_num(getattr(r.stats.devices[d], key)) if d < len(r.devices) else "–"
                    for r in results]
            rows.append({"device": f"П{d + 1}", "formula": f_dev.replace("_i", f"_{d + 1}"),
                         "values": vals})
        rows.append({"device": "Сист.", "formula": f_sys,
                     "values": [_num(getattr(r.stats.total, key)) for r in results]})
        out.append({"label": label, "rows": rows})
    return out


def _checks(res: SystemResult) -> list[list[str]]:
    """Проверка по фундаментальным зависимостям: ρ = λ'b, m = l + ρ, u = w + b."""
    b = res.chain.b
    rows = []
    for dev, s in zip(res.devices, res.stats.devices):
        rows.append([
            dev.name,
            _num(s.util), _num(s.throughput * b),
            _num(s.count), _num(s.queue + s.util),
            _num(s.stay, 3), _num(s.wait + b, 3),
        ])
    return rows


def _describe(spec_devices: tuple[Device, ...]) -> list[list[str]]:
    rows = []
    for dev in spec_devices:
        law = "экспоненциальный" if dev.phases == 1 else f"Эрланга {dev.phases}-го порядка"
        rows.append([dev.name, _num(dev.p, 2), str(dev.buffer), law])
    return rows


def _conclusions(v: Variant, results: list[SystemResult], alt: Stats,
                 sweep: list[dict]) -> dict[str, str]:
    s1, s2 = (r.stats for r in results)
    n1, n2 = (r.name for r in results)
    t1, t2 = s1.total, s2.total
    winner, loser = (n1, n2) if t1.queue < t2.queue else (n2, n1)
    gen = {n: n.replace("СИСТЕМА", "СИСТЕМЫ") for n in (n1, n2)}
    always = all((row[winner].queue < row[loser].queue) for row in sweep)
    lam_lo, lam_hi = _num(sweep[0]["lam"], 2), _num(sweep[-1]["lam"], 2)

    p1 = s1.devices[0]
    common = (
        f"П1 в обеих системах одинаковый: накопителя у него нет, а приходит к нему "
        f"{_num(v.probs[0] * 100, 0)} % заявок, нагрузка y₁ = {_num(p1.load, 1)}. "
        f"Он занят с вероятностью {_num(p1.util, 3)} и с той же вероятностью теряет "
        f"пришедшую заявку. Отсюда большие общие потери: {_num(t1.loss, 3)} "
        f"и {_num(t2.loss, 3)}. Разница между системами только в приборе с накопителем."
    )

    d2a, d2b = s1.devices[1], s2.devices[1]
    queue = (
        f"Очередь есть только перед П2. В СИСТЕМЕ_1 к нему идёт "
        f"{_num(v.probs[1] * 100, 0)} % заявок (y₂ = {_num(d2a.load, 2)}), в СИСТЕМЕ_2 "
        f"{_num((v.probs[1] + v.probs[2]) * 100, 0)} % (y₂ = {_num(d2b.load, 2)}), потому что "
        f"туда же уходят заявки, которые в СИСТЕМЕ_1 обслуживал П3. Очередь в СИСТЕМЕ_2 "
        f"из-за этого в {_num(d2b.queue / d2a.queue, 1)} раза длиннее: {_num(d2b.queue, 3)} "
        f"против {_num(d2a.queue, 3)}."
    )

    if alt.queue > t2.queue:
        effect = (
            "Обслуживание по Эрлангу (ν = 0,707) регулярнее экспоненциального, и очередь "
            "при нём немного короче. По сравнению с нагрузкой это мелочь."
        )
    else:
        effect = (
            f"С Эрлангом (ν = 0,707) очередь даже чуть длиннее. П2 перегружен (y₂ > 1), "
            f"при более регулярном обслуживании он теряет немного меньше заявок "
            f"(общие потери {_num(t2.loss, 4)} против {_num(alt.loss, 4)}), принимает "
            f"больше, и они ждут в очереди. По сравнению с нагрузкой это мелочь."
        )
    law = (
        f"Чтобы понять, сколько здесь от закона обслуживания, я пересчитал СИСТЕМУ_2 "
        f"с экспоненциальным П2. Суммарная очередь вышла {_num(alt.queue, 3)}, "
        f"с Эрлангом {_num(t2.queue, 3)}. " + effect
    )

    if always:
        sweep_text = (
            f"При λ от {lam_lo} до {lam_hi} 1/с очередь у {gen[winner]} короче во всём диапазоне."
        )
    else:
        sweep_text = (
            f"При λ от {lam_lo} до {lam_hi} 1/с {winner} выигрывает по очереди не везде, "
            f"см. рисунок."
        )

    w_stats, l_stats = (t1, t2) if winner == n1 else (t2, t1)
    better = [
        "производительность выше" if w_stats.throughput > l_stats.throughput
        else "производительность ниже",
        "потери меньше" if w_stats.loss < l_stats.loss else "потери больше",
        "время пребывания меньше" if w_stats.stay < l_stats.stay else "время пребывания больше",
    ]
    choice = (
        f"По критерию «{CRITERIA[v.criterion]}» лучше {winner}: L = {_num(w_stats.queue, 3)}, "
        f"у {gen[loser]} {_num(l_stats.queue, 3)}. Ещё у {gen[winner]} "
        f"{', '.join(better)}: Λ' = {_num(w_stats.throughput, 4)} 1/с "
        f"против {_num(l_stats.throughput, 4)}, π = {_num(w_stats.loss, 3)} против "
        f"{_num(l_stats.loss, 3)}, u = {_num(w_stats.stay, 2)} с против {_num(l_stats.stay, 2)} с. "
        f"Загрузка у {gen[n2]} выше ({_num(t2.util, 3)} против {_num(t1.util, 3)}), но только "
        f"потому, что приборов в ней на один меньше."
    )
    return {"common": common, "queue": queue, "law": law, "sweep": sweep_text, "choice": choice,
            "winner": winner}


def export(v: Variant, results: list[SystemResult], out: Path, *,
           student: str, group: str, teacher: str) -> Path:
    plots = out / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    systems = []
    for i, r in enumerate(results, start=1):
        transition_graph(r.chain, "", plots / f"graph{i}.png")
        g = r.chain.matrix()
        systems.append({
            "name": r.name,
            "devices": _describe(r.devices),
            "n": r.chain.n,
            "states": [state_code(r.chain, s, "typst") for s in r.chain.states],
            "probs": [_num(x, 5) for x in r.p],
            "psum": _num(sum(r.p), 5),
            "matrix": [[_rate(x) for x in row] for row in g],
            "formulas": _formulas(r),
            "checks": _checks(r),
            "rates": [
                [f"lambda_{d + 1}", f"lambda p_{d + 1}", _num(v.lam * dev.p, 3)]
                for d, dev in enumerate(r.devices)
            ],
        })

    # Сравнение: та же СИСТЕМА_2, но П2 экспоненциальный: вклад закона Эрланга.
    alt_devices = tuple(Device(d.name, d.p, d.buffer) for d in results[1].devices)
    alt = solve(alt_devices, v.lam, v.b)[2].total
    _, sweep = compare([(r.name, r.devices) for r in results], v.b, v.lam, plots / "compare.png")

    data = {
        "variant": v.code,
        "n1": v.n1, "n2": v.n2, "ng": v.ng,
        "author": {"name": student, "group": group, "teacher": teacher, "year": "2026"},
        "lam": _num(v.lam, 1), "b": _num(v.b, 0),
        "mu": _num(1 / v.b, 1),
        "probs": [_num(x, 2) for x in v.probs],
        "criterion_letter": v.criterion,
        "criterion": CRITERIA[v.criterion],
        "criterion_rule": "чётная" if (v.n1 + v.n2) % 2 == 0 else "нечётная",
        "criterion_from": v.n2 if (v.n1 + v.n2) % 2 == 0 else v.n1,
        "systems": systems,
        "form1_rows": max(s["n"] for s in systems),
        "form2": _form2(results),
        "alt": {"queue": _num(alt.queue), "loss": _num(alt.loss), "stay": _num(alt.stay, 3),
                "throughput": _num(alt.throughput)},
        "sweep": [
            [_num(row["lam"], 2)] + [_num(getattr(row[r.name], k), 3)
                                     for k in ("queue", "loss", "stay") for r in results]
            for row in sweep[::4]
        ],
        "conclusions": _conclusions(v, results, alt, sweep),
    }
    path = out / "data.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return path
