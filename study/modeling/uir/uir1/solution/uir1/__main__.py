"""CLI: python -m uir1 --variant 49"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analysis import DEFAULT_SEED, analyse, render
from .approx import LAWS
from .variants import load_variant, load_variants

# Подпись на титульном листе — из shared/profile.yaml.
STUDENT = "Данилов Тимофей Николаевич"
GROUP = "P3331"
TEACHER = "Авксентьева Елена Юрьевна"

# .../study/modeling/uir/uir1/solution/uir1/__main__.py → parents[4] = study/modeling
DEFAULT_XLSX = (
    Path(__file__).resolve().parents[4]
    / "materials" / "lms" / "!_УИР1_Варианты_с.xlsx"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uir1",
        description="Расчёт УИР 1: формы 1–3, графики 1–3, выбор закона, генератор.",
    )
    parser.add_argument("-v", "--variant", type=int, required=True,
                        help="номер варианта (1..360)")
    parser.add_argument("-x", "--xlsx", type=Path, default=DEFAULT_XLSX,
                        help="файл вариантов (по умолчанию из materials/lms)")
    parser.add_argument("-o", "--out", type=Path, default=Path("out"),
                        help="каталог для отчёта (по умолчанию ./out)")
    parser.add_argument("-l", "--law", choices=sorted(LAWS), default="auto",
                        help="закон аппроксимации; auto — выбор по ν")
    parser.add_argument("-q", type=float, default=None,
                        help="параметр q гиперэкспоненциального закона")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help="seed генератора для воспроизводимости")
    parser.add_argument("--typst", type=Path, default=None,
                        help="каталог typst-отчёта: выгрузить туда data.json "
                             "и графики (обычно ../../../reports/uir1)")
    parser.add_argument("--list", action="store_true",
                        help="показать сводку по всем вариантам и выйти")
    args = parser.parse_args(argv)

    if not args.xlsx.exists():
        print(f"Файл вариантов не найден: {args.xlsx}", file=sys.stderr)
        return 2

    if args.list:
        for number, data in sorted(load_variants(args.xlsx).items()):
            result = analyse(data, number, seed=args.seed)
            full = result.full
            print(f"{number:>4}  m={full.mean:>10.4f}  ν={full.cv:>7.4f}  "
                  f"{result.law.name}")
        return 0

    try:
        sample = load_variant(args.xlsx, args.variant)
    except KeyError as exc:
        print(exc.args[0], file=sys.stderr)
        return 2

    result = analyse(sample, args.variant, law_name=args.law, q=args.q, seed=args.seed)
    out_dir = args.out / f"variant-{args.variant:03d}"
    path = render(result, out_dir)

    if args.typst is not None:
        from .typst_export import export

        data = export(
            result,
            args.typst,
            out_dir / "plots",
            student=STUDENT,
            group=GROUP,
            teacher=TEACHER,
        )
        print(f"Данные для typst: {data}")

    full = result.full
    print(f"Вариант {args.variant}: n={len(sample)}, m̃={full.mean:.4f}, "
          f"ν={full.cv:.4f} → {result.law.describe()}")
    for note in result.law.notes:
        print(f"  ⚠ {note}")
    print(f"Отчёт: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
