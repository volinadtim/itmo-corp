"""Экспорт результатов в JSON для typst-отчёта (reports/uir2/report.typ).

Отчёт читает data.json через json(), поэтому числа в PDF всегда совпадают
с расчётом и не переписываются руками.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import plots
from .analysis import CRITERION_KEY, Result, conclusions
from .metrics import SystemMetrics
from .model import Model
from .variant import CRITERIA, N1, N2, NG, PROBS3

NAMES = ("СИСТЕМА_1", "СИСТЕМА_2")


def num(x, digits: int = 4) -> str:
    return f"{float(x):.{digits}f}".replace(".", ",")


def short(x) -> str:
    """Параметр без лишних нулей: 0,45; 10; 0,2."""
    return f"{float(x):g}".replace(".", ",")


# --------------------------------------------------------------- typst-math

def _math_label(label: str) -> str:
    """λ1 → lambda_1, μ → mu, 2μ → 2 mu."""
    if label.startswith("λ"):
        return f"lambda_{label[1:]}"
    return label.replace("μ", " mu").strip()


def equations(model: Model) -> list[str]:
    """Уравнения баланса для стационарного режима в виде typst-math:
    (сумма интенсивностей выхода)·p_j = Σ (интенсивность входа)·p_i."""
    out = []
    for j in range(model.n):
        outgoing = [t for t in model.transitions if t.src == j]
        incoming = [t for t in model.transitions if t.dst == j]
        labels: list[str] = []
        for t in outgoing:
            labels.append(_math_label(t.label))
        left = " + ".join(_merge(labels))
        right = " + ".join(f"{_math_label(t.label)} p_({t.src})" for t in incoming)
        out.append(f"({left}) p_({j}) = {right}")
    return out


def _merge(labels: list[str]) -> list[str]:
    """mu + mu → 2 mu (одинаковые слагаемые собираются)."""
    counts: dict[str, int] = {}
    for lab in labels:
        counts[lab] = counts.get(lab, 0) + 1
    merged = []
    for lab, c in counts.items():
        if c == 1:
            merged.append(lab)
        elif lab.startswith("2 "):
            merged.append(f"{2 * c} {lab[2:]}")
        else:
            merged.append(f"{c} {lab}")
    # Сначала поступления λ_i по номеру прибора, затем обслуживание.
    return sorted(merged, key=lambda x: (not x.startswith("lambda"), x))


def matrix(model: Model) -> list[list[str]]:
    """Матрица интенсивностей: вне диагонали – обозначения, на диагонали – число."""
    rows = []
    by_pair = {(t.src, t.dst): t.label for t in model.transitions}
    for i in range(model.n):
        row = []
        for j in range(model.n):
            if i == j:
                row.append("−" + num(-model.g[i][i], 2))
            else:
                row.append(by_pair.get((i, j), ""))
        rows.append(row)
    return rows


def describe(model: Model, s: int) -> str:
    """Словесное описание состояния: что происходит у каждого прибора."""
    parts = []
    for d, (n, f) in zip(model.spec.devices, model.states[s]):
        if n == 0:
            parts.append(f"П{d.index} свободен")
            continue
        text = f"П{d.index} занят"
        if d.phases > 1:
            text += f" (фаза {f})"
        if n > 1:
            text += f", в очереди {n - 1}"
        parts.append(text)
    return "; ".join(parts)


# --------------------------------------------------------------- форма 2

def _dev(sm: SystemMetrics, i: int):
    return sm.devices[i - 1] if i <= len(sm.devices) else None


FORM2 = [
    # (характеристика, атрибут прибора, формула прибора, атрибут суммы, формула суммы)
    ("Нагрузка", "y", "y_i = lambda_i b", "y", "Y = sum_i y_i"),
    ("Загрузка", "rho", "rho_i = sum_(n_i > 0) p(E)", "rho", "rho = 1/N sum_i rho_i"),
    ("Длина очереди", "l", "l_i = sum_(n_i > 1) (n_i - 1) p(E)", "l", "l = sum_i l_i"),
    ("Число заявок", "m", "m_i = sum_(n_i > 0) n_i p(E)", "m", "m = sum_i m_i"),
    ("Время ожидания", "w", "w_i = b/(1 - pi_i) sum_(0 < n_i <= r_i) tau(E) p(E)", "w",
     "w = (sum_i lambda'_i w_i) / lambda'"),
    ("Время пребывания", "u", "u_i = w_i + b", "u", "u = (sum_i lambda'_i u_i) / lambda'"),
    ("Вероятность потери", "loss", "pi_i = sum_(n_i = r_i + 1) p(E)", "loss",
     "pi = 1 - lambda' / lambda"),
    ("Производительность", "lam_acc", "lambda'_i = lambda_i (1 - pi_i)", "lam_acc",
     "lambda' = sum_i lambda'_i"),
]


def form2(r: Result) -> list[dict]:
    s1, s2 = (r.metrics[n] for n in NAMES)
    rows = []
    for title, attr, f_dev, sattr, f_sum in FORM2:
        devices = []
        for i in (1, 2, 3):
            d1, d2 = _dev(s1, i), _dev(s2, i)
            devices.append([f"П{i}",
                            num(getattr(d1, attr)) if d1 else "–",
                            num(getattr(d2, attr)) if d2 else "–"])
        rows.append({
            "title": title,
            "formula": f_dev,
            "devices": devices,
            "sum_formula": f_sum,
            "sum": [num(getattr(s1, sattr)), num(getattr(s2, sattr))],
        })
    rows.append({
        "title": "Ср. число занятых приборов",
        "formula": None,
        "devices": [],
        "sum_formula": "k = sum_i rho_i",
        "sum": [num(s1.busy), num(s2.busy)],
    })
    return rows


# --------------------------------------------------------------- экспорт

def _system(r: Result, name: str) -> dict:
    model = r.models[name]
    sm = r.metrics[name]
    spec = model.spec
    return {
        "name": name,
        "states": model.n,
        "transitions": len(model.transitions),
        "devices": [{
            "index": d.index,
            "buffer": d.buffer,
            "law": d.law,
            "law_short": "exp" if d.phases == 1 else f"E{d.phases}",
            "share": short(d.share),
            "lam": short(spec.lam_i(d)),
            "y": short(spec.lam_i(d) * spec.b),
        } for d in spec.devices],
        "codes": [model.code(i) for i in range(model.n)],
        "descriptions": [describe(model, i) for i in range(model.n)],
        "p": [num(x) for x in model.p],
        "p_exact": [f"{x.numerator}/{x.denominator}" for x in model.p],
        "matrix": matrix(model),
        "equations": equations(model),
        "elements": [{"name": k, "value": short(v)} for k, v in model.elements().items()],
        "winmark": [{"name": n, "formula": f, "desc": d} for n, f, d in r.winmark[name]],
        "checks": [{"name": c.name, "value": f"{c.value:.1e}" if c.value else "0",
                    "ok": c.exact} for c in r.checks[name]],
        "busy": num(sm.busy),
    }


def export(r: Result, typst_dir: Path, *, student: str, group: str, teacher: str) -> Path:
    typst_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = typst_dir / "plots"
    plot_dir.mkdir(exist_ok=True)

    for idx, name in enumerate(NAMES, start=1):
        plots.scheme(r.models[name], plot_dir / f"scheme{idx}.png")
        plots.state_graph(r.models[name], plot_dir / f"graph{idx}.png")
    nominal = float(r.metrics[NAMES[0]].lam)
    plots.sweep_criterion(r.sweep, nominal, plot_dir / "sweep_criterion.png")
    plots.sweep_panel(r.sweep, nominal, plot_dir / "sweep_panel.png")

    n_rows = max(r.models[n].n for n in NAMES)
    form1 = []
    for i in range(n_rows):
        row = [str(i)]
        for n in NAMES:
            m = r.models[n]
            row += [f"E{i} {m.code(i)}", num(m.p[i])] if i < m.n else ["", ""]
        form1.append(row)

    key, smaller = CRITERION_KEY[r.criterion]
    spec1 = r.models[NAMES[0]].spec
    data = {
        "author": {"name": student, "group": group, "teacher": teacher, "year": "2026"},
        "variant": {
            "n1": N1, "n2": N2, "ng": NG,
            "code": f"{N1}/{N2}/{NG}",
            "lam": short(spec1.lam), "b": short(spec1.b), "mu": short(spec1.mu),
            "probs3": [short(p) for p in PROBS3],
            "probs2": [short(PROBS3[0]), short(PROBS3[1] + PROBS3[2])],
            "criterion": r.criterion,
            "criterion_text": CRITERIA[r.criterion],
            "parity": "чётная" if (N1 + N2) % 2 == 0 else "нечётная",
            "sum": N1 + N2,
        },
        "systems": [_system(r, n) for n in NAMES],
        "form1": form1,
        "form2": form2(r),
        "winmark_points": {
            "lams": [short(p["lam"]) for p in r.winmark_points[NAMES[0]]],
            "rows": [
                {"name": label, "s1": [num(p[k]) for p in r.winmark_points[NAMES[0]]],
                 "s2": [num(p[k]) for p in r.winmark_points[NAMES[1]]]}
                for k, label in (("l", "Lsum"), ("loss", "lossS"), ("lam_acc", "LPsum"),
                                 ("rho", "Rsys"), ("u", "Usum"))
            ],
        },
        "alternative": {
            "states": r.alternative_states,
            "rho1": num(r.alternative.devices[0].rho),
            "l": num(r.alternative.l),
        },
        "best": r.best,
        "criterion_values": [num(getattr(r.metrics[n], key)) for n in NAMES],
        "conclusions": conclusions(r),
    }
    path = typst_dir / "data.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return path
