"""CLI: python -m uir2 [--typst ../../../reports/uir2]"""

from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import analyse, conclusions
from .report import render
from .typst_export import NAMES, num

# Подпись на титульном листе – из shared/profile.yaml.
STUDENT = "Данилов Тимофей Николаевич"
GROUP = "P3331"
TEACHER = "Авксентьева Елена Юрьевна"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uir2",
        description="Расчёт УИР 2 (вариант 60/60/31): марковские модели двух СМО.",
    )
    parser.add_argument("-o", "--out", type=Path, default=Path("out"),
                        help="каталог для markdown-сводки (по умолчанию ./out)")
    parser.add_argument("--typst", type=Path, default=None,
                        help="каталог typst-отчёта: выгрузить туда data.json "
                             "и рисунки (обычно ../../../reports/uir2)")
    args = parser.parse_args(argv)

    r = analyse()
    path = render(r, args.out)
    if args.typst is not None:
        from .typst_export import export

        data = export(r, args.typst, student=STUDENT, group=GROUP, teacher=TEACHER)
        print(f"Данные для typst: {data}")

    for n in NAMES:
        sm = r.metrics[n]
        bad = [c.name for c in r.checks[n] if not c.exact]
        print(f"{n}: {r.models[n].n} состояний; l = {num(sm.l)}, π = {num(sm.loss)}, "
              f"λ' = {num(sm.lam_acc)}, u = {num(sm.u)}; проверки "
              + ("пройдены" if not bad else f"НЕ пройдены: {bad}"))
    print(conclusions(r)["choice"])
    print(f"Сводка: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
