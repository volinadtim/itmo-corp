"""Графики: размеченный граф переходов и сравнение систем при варьировании λ."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from .model import Chain, Device, State, solve

COLORS = ("#1f5fa8", "#c0392b")


def state_code(chain: Chain, s: State, math_mode: str = "mpl") -> str:
    """Код состояния: числа заявок у приборов, фаза Эрланга индексом.

    math_mode="mpl" для matplotlib ($3_2$), "typst" для eval(mode: "math").
    """
    parts = []
    for (k, ph), dev in zip(s, chain.devices):
        if dev.phases > 1 and k > 0:
            parts.append(f"{k}_{ph}")
        else:
            parts.append(str(k))
    body = ",".join(parts)
    return f"$({body})$" if math_mode == "mpl" else f"({', '.join(parts)})"


def _layout(chain: Chain) -> dict[int, tuple[float, float]]:
    """Расстановка вершин: прибор с наибольшим числом состояний идёт по горизонтали.

    Остальные приборы сдвигают «слой» вниз (второй) и наискосок (третий),
    так получается проекция решётки состояний без наложения вершин.
    """
    devs = chain.devices
    order = sorted(range(len(devs)), key=lambda d: -(devs[d].buffer + 2) * devs[d].phases)
    main, others = order[0], order[1:]
    step_x = 2.6
    main_phases = devs[main].phases
    height = 0.9 * (main_phases - 1)
    shifts = [(0.0, -(height + 2.2)), (0.42 * step_x, 1.0)]

    pos = {}
    for i, s in enumerate(chain.states):
        k, ph = s[main]
        # Фазы Эрланга идут «лесенкой»: следующая фаза на полшага правее и ниже,
        # чтобы вертикальные дуги соседнего слоя не проходили через вершины.
        x = k * step_x
        y = 0.0
        if main_phases > 1 and k > 0:
            x += (ph - 1) * step_x / main_phases
            y = -0.9 * (ph - 1)
        for d, (dx, dy) in zip(others, shifts):
            x += s[d][0] * dx
            y += s[d][0] * dy
        pos[i] = (x, y)
    return pos


def _rate_label(chain: Chain, sym: tuple[str, int]) -> str:
    kind, d = sym
    if kind == "lam":
        return rf"$\lambda_{d + 1}$"
    k = chain.devices[d].phases
    return r"$\mu$" if k == 1 else rf"${k}\mu$"


def transition_graph(chain: Chain, title: str, path: Path) -> Path:
    pos = _layout(chain)
    xs = [x for x, _ in pos.values()]
    ys = [y for _, y in pos.values()]
    w = max(xs) - min(xs) + 2.0
    h = max(ys) - min(ys) + 1.6
    fig, ax = plt.subplots(figsize=(w * 1.05, h * 1.05))
    ax.set_xlim(min(xs) - 1.0, max(xs) + 1.0)
    ax.set_ylim(min(ys) - 0.8, max(ys) + 0.8)
    ax.set_aspect("equal")
    ax.axis("off")

    for (i, j), _ in chain.rates.items():
        (x1, y1), (x2, y2) = pos[i], pos[j]
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle="arc3,rad=0.18",
            arrowstyle="-|>", mutation_scale=9,
            shrinkA=17, shrinkB=17, lw=0.7, color="#444",
        )
        ax.add_patch(arrow)
        # Подпись ставится сбоку от середины дуги, с той же стороны, куда она выгнута.
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1.0
        nx, ny = dy / length, -dx / length
        off = 0.18 * length * 0.5 + 0.12
        ax.text(mx + nx * off, my + ny * off, _rate_label(chain, chain.symbols[(i, j)]),
                fontsize=8, ha="center", va="center", color="#1f3d6b")

    for i, s in enumerate(chain.states):
        x, y = pos[i]
        ax.text(x, y, state_code(chain, s), fontsize=9, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#222", lw=0.9))
        ax.text(x - 0.5, y + 0.3, f"E{i + 1}", fontsize=7, ha="right", va="bottom", color="#666")

    ax.set_title(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def compare(systems: list[tuple[str, tuple[Device, ...]]], b: float, lam0: float,
            path: Path) -> tuple[Path, list[dict]]:
    """Характеристики обеих систем при λ от 0,05 до 2λ₀ (остальное не меняется)."""
    grid = [round(lam0 * 2 * t / 40, 4) for t in range(1, 41)]
    series = []
    for name, devs in systems:
        rows = [solve(devs, lam, b)[2].total for lam in grid]
        series.append({"name": name, "rows": rows})

    panels = [
        ("queue", "Суммарная длина очередей L"),
        ("loss", "Вероятность потери π"),
        ("throughput", "Производительность λ', 1/с"),
        ("stay", "Время пребывания u, с"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for ax, (key, label) in zip(axes.flat, panels):
        for color, s in zip(COLORS, series):
            ax.plot(grid, [getattr(r, key) for r in s["rows"]], color=color, label=s["name"])
        ax.axvline(lam0, color="#888", lw=0.8, ls="--")
        ax.set_title(label, fontsize=10)
        ax.set_xlabel("λ, 1/с")
        ax.grid(alpha=0.3)
    axes.flat[0].legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path, [{"lam": lam, **{s["name"]: s["rows"][i] for s in series}} for i, lam in enumerate(grid)]
