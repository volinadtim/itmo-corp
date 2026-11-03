"""CLI: python -m uir2 --variant 60/60/31"""

from __future__ import annotations

import argparse
from pathlib import Path

from .model import solve
from .systems import devices
from .typst_export import SystemResult, export
from .variants import CRITERIA, load

# Подпись на титульном листе та же, что в УИР 1.
STUDENT = "Данилов Тимофей Николаевич"
GROUP = "P3331"
TEACHER = "Авксентьева Елена Юрьевна"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="uir2",
        description="Расчёт УИР 2: марковские модели СИСТЕМЫ_1 и СИСТЕМЫ_2.",
    )
    parser.add_argument("-v", "--variant", default="60/60/31",
                        help="вариант N1/N2/NG (по умолчанию 60/60/31)")
    parser.add_argument("--law-device", type=int, default=None,
                        help="номер прибора СИСТЕМЫ_2 (с 1) с неэкспоненциальным законом; "
                             "по умолчанию: прибор с самым большим накопителем")
    parser.add_argument("--typst", type=Path, default=None,
                        help="каталог typst-отчёта (обычно ../../../reports/uir2)")
    args = parser.parse_args(argv)

    n1, n2, ng = (int(x) for x in args.variant.split("/"))
    v = load(n1, n2, ng)
    law_device = None if args.law_device is None else args.law_device - 1

    results = []
    for name, spec, ld in (("СИСТЕМА_1", v.system1, None), ("СИСТЕМА_2", v.system2, law_device)):
        devs = devices(spec, v, ld)
        chain, p, stats = solve(devs, v.lam, v.b)
        results.append(SystemResult(name, devs, chain, p, stats))
        t = stats.total
        print(f"{name}: {', '.join(f'{d.name}({d.law}, r={d.buffer}, p={d.p:g})' for d in devs)}; "
              f"состояний {chain.n}")
        print(f"  L={t.queue:.4f}  π={t.loss:.4f}  λ'={t.throughput:.4f}  "
              f"u={t.stay:.3f}  ρ={t.util:.4f}")

    print(f"Критерий ({v.criterion}): {CRITERIA[v.criterion]}")
    if args.typst is not None:
        path = export(v, results, args.typst, student=STUDENT, group=GROUP, teacher=TEACHER)
        print(f"Данные для typst: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
