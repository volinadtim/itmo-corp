"""Сводка в markdown: формы 1 и 2, данные для WinMark, проверки, выводы."""

from __future__ import annotations

from pathlib import Path

from .analysis import Result, conclusions
from .typst_export import NAMES, num


def render(r: Result, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# УИР 2 – расчёт по варианту 60/60/31", ""]

    lines += ["## Форма 1. Стационарные вероятности", "",
              "| № | СИСТЕМА_1 | p | СИСТЕМА_2 | p |", "|---|---|---|---|---|"]
    n_rows = max(r.models[n].n for n in NAMES)
    for i in range(n_rows):
        cells = [str(i)]
        for n in NAMES:
            m = r.models[n]
            cells += [m.code(i), num(m.p[i])] if i < m.n else ["", ""]
        lines.append("| " + " | ".join(cells) + " |")

    lines += ["", "## Форма 2. Характеристики", "",
              "| Характеристика | Прибор | СИСТЕМА_1 | СИСТЕМА_2 |", "|---|---|---|---|"]
    attrs = [("Нагрузка", "y"), ("Загрузка", "rho"), ("Длина очереди", "l"),
             ("Число заявок", "m"), ("Время ожидания", "w"), ("Время пребывания", "u"),
             ("Вероятность потери", "loss"), ("Производительность", "lam_acc")]
    s1, s2 = (r.metrics[n] for n in NAMES)
    for title, a in attrs:
        for i in range(3):
            v1 = num(getattr(s1.devices[i], a)) if i < len(s1.devices) else "–"
            v2 = num(getattr(s2.devices[i], a)) if i < len(s2.devices) else "–"
            lines.append(f"| {title} | П{i + 1} | {v1} | {v2} |")
        lines.append(f"| {title} | Сумм. | {num(getattr(s1, a))} | {num(getattr(s2, a))} |")
    lines.append(f"| Ср. число занятых приборов | Сумм. | {num(s1.busy)} | {num(s2.busy)} |")

    for n in NAMES:
        m = r.models[n]
        lines += ["", f"## WinMark: {n}", "",
                  f"Размер матрицы {m.n}×{m.n}, элементы: "
                  + ", ".join(f"{k} = {float(v):g}" for k, v in m.elements().items()), "",
                  "| Строка | Состояние | Ячейки: столбец = элемент | p |", "|---|---|---|---|"]
        for i in range(m.n):
            out = sorted((t for t in m.transitions if t.src == i), key=lambda t: t.dst)
            cells = ", ".join(f"{t.dst} = {t.element}" for t in out)
            lines.append(f"| {i} | {m.code(i)} | {cells} | {num(m.p[i])} |")
        lines += ["", "| Имя | Формула | Смысл |", "|---|---|---|"]
        lines += [f"| {a} | `{f}` | {d} |" for a, f, d in r.winmark[n]]
        lines += ["", "Проверки:", ""]
        lines += [f"- {'✅' if c.exact else '❌'} {c.name}: {c.value:.1e}" for c in r.checks[n]]

    lines += ["", "## Выводы", ""]
    lines += [v + "\n" for v in conclusions(r).values()]
    path = out_dir / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
